"""Recorta cada foto: quita las franjas de marketing de Carrefour/Día/Jumbo, quita el fondo (rembg)
y guarda un PNG con transparencia en productos/<slug>.png."""
import json, os, sys
import numpy as np
from PIL import Image
from rembg import remove, new_session
from scipy import ndimage

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Recortes manuales previos (fracciones x0,y0,x1,y1) para fotos con varias unidades.
MANUAL = json.load(open(f"{BASE}/scripts/recortes_manuales.json"))

def quitar_franjas(im):
    """Detecta la franja vertical de color a la derecha y la barra inferior que agregan las tiendas."""
    a = np.asarray(im.convert("RGB")).astype(int)
    H, W, _ = a.shape
    ink = (a.min(axis=2) < 225)
    x1, y1 = W, H
    col = ink.mean(axis=0)
    x = W - 1
    while x > 0 and col[x] < 0.05 and W - x < 0.04 * W: x -= 1
    xr = x
    while x > 0 and col[x] > 0.6: x -= 1
    if xr - x > 0.05 * W and x > 0.55 * W:
        x1 = x - 2
    row = ink[:, :x1].mean(axis=1)
    y = H - 1
    while y > 0 and row[y] < 0.05 and H - y < 0.04 * H: y -= 1
    yb = y
    while y > 0 and row[y] > 0.55: y -= 1
    if yb - y > 0.04 * H and y > 0.6 * H:
        y1 = y - 2
    # también el recuadro de gramaje (abajo a la derecha) queda fuera si hubo franja
    return im.crop((0, 0, x1, y1)), (x1 < W, y1 < H)

def mascara_relleno(im, umbral=242):
    a = np.asarray(im.convert("RGB"))
    blanco = (a.min(axis=2) >= umbral)
    lab, n = ndimage.label(blanco)
    borde = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fondo = np.isin(lab, list(borde))
    fg = ~fondo
    fg = ndimage.binary_opening(fg, iterations=2)      # saca pelusas
    fg = ndimage.binary_erosion(fg, iterations=1)      # evita borde blanco
    lab2, n2 = ndimage.label(fg)
    if n2:
        tam = ndimage.sum(fg, lab2, range(1, n2 + 1))
        fg = np.isin(lab2, [i + 1 for i, t in enumerate(tam) if t > 0.01 * fg.size])
    alpha = ndimage.gaussian_filter(fg.astype(np.float32) * 255, 0.8)
    return alpha

def sacar_franjas(al, pad=20):
    """Elimina los componentes que son franjas/etiquetas de marketing pegadas al borde
    derecho o inferior de la foto original (no forman parte del envase)."""
    H, W = al.shape
    fg = al > 100
    lab, n = ndimage.label(fg)
    quitados = 0
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        # franja vertical o recuadro de gramaje en el tercio derecho
        franja_der = x0 > 0.65 * W and ((y1 - y0) > 0.45 * H or y0 > 0.6 * H)
        # barra horizontal con el nombre, pegada abajo
        barra_abajo = y0 > 0.7 * H and y1 > 0.85 * H
        if franja_der or barra_abajo:
            al = np.where(lab == i, 0, al); quitados += 1
    # restos chicos (pelusas, textos sueltos)
    fg = al > 100
    lab, n = ndimage.label(fg)
    if n > 1:
        tam = ndimage.sum(fg, lab, range(1, n + 1))
        chicos = [i + 1 for i, t in enumerate(tam) if t < 0.02 * tam.max()]
        al = np.where(np.isin(lab, chicos), 0, al)
    # suavizar: lo que quedó "medio transparente" lejos del objeto principal se descarta
    cerca = ndimage.binary_dilation(al > 100, iterations=3)
    al = np.where(cerca, al, 0)
    return al, quitados

def main(only=None):
    sess = new_session("isnet-general-use")
    os.makedirs(f"{BASE}/productos", exist_ok=True)
    log = {}
    for slug, *_ in json.load(open(f"{BASE}/scripts/seleccion.json")):
        if only and slug not in only: continue
        im = Image.open(f"{BASE}/productos_raw/{slug}.img").convert("RGB")
        if slug in MANUAL:
            fx0, fy0, fx1, fy1 = MANUAL[slug]
            W, H = im.size
            im = im.crop((int(fx0 * W), int(fy0 * H), int(fx1 * W), int(fy1 * H)))
            fr = ("manual",)
        else:
            fr = ("componentes",)
        # margen blanco para que la segmentación no toque bordes
        pad = Image.new("RGB", (im.width + 40, im.height + 40), (255, 255, 255)); pad.paste(im, (20, 20))
        out = remove(pad, session=sess, post_process_mask=True)
        al = np.asarray(out)[:, :, 3].astype(np.float32)
        # Máscara por "relleno" desde el borde: todo lo blanco conectado al borde es fondo.
        # Se une con la de rembg: rembg resuelve envases blancos, el relleno los envases muy saturados.
        al = np.maximum(al, mascara_relleno(pad))
        al, quitados = sacar_franjas(al)
        fr = fr + (quitados,)
        al = np.where(al < 20, 0, al).astype(np.uint8)
        out = pad.convert("RGBA"); out.putalpha(Image.fromarray(al))
        bbox = out.getbbox()
        out = out.crop(bbox)
        out.save(f"{BASE}/productos/{slug}.png")
        log[slug] = {"franjas_quitadas": list(fr), "tamano": out.size}
        print(slug, fr, out.size)
    return log

if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
