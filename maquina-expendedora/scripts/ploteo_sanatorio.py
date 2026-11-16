"""Ploteo de la máquina del sanatorio (solo pago con QR): versiones negra y gris oscura.

Uso:
    python3 scripts/ploteo_sanatorio.py
Salidas en salida/ploteo_sanatorio_<version>.png y salida/ploteo_sanatorio_comparativa.jpg
"""
import os, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import componer as C
from ploteo import fnt, centro, flecha_abajo

WHATSAPP = "11 2160-0427"
MAQ_N = "001"
ROJO = (214, 30, 40)

VERSIONES = {
    "negro": dict(nombre="Negro",
        pal=dict(body=(30, 30, 34), dark=(12, 12, 14), light=(70, 70, 76), bevel=ROJO, zocalo=(10, 10, 12), zocalo_l=(45, 45, 50), push=(18, 18, 20), panel=None),
        caja=(14, 14, 16), linea2=(90, 90, 98)),
    "gris": dict(nombre="Gris oscuro",
        pal=dict(body=(66, 68, 74), dark=(34, 35, 39), light=(110, 112, 120), bevel=ROJO, zocalo=(28, 29, 32), zocalo_l=(80, 82, 88), push=(44, 45, 50), panel=None),
        caja=(24, 25, 28), linea2=(150, 152, 160)),
}
BLANCO, GRIS_T = (255, 255, 255), (185, 187, 194)


def lineas_diagonales(d, x0, y0, n, largo, sep, ancho, colores, sube=True):
    """Haz de líneas en diagonal (45°) para cortar lo cuadrado del diseño."""
    for i in range(n):
        c = colores[i % len(colores)]
        ox = x0 + i * sep
        d.line((ox, y0, ox + largo, y0 - largo if sube else y0 + largo), fill=c, width=ancho)


def ploteo(v):
    C.PAL = v["pal"]; C.DIBUJAR_PUSH = False; C.TEXTO_PAGO = "Comprar ahora"
    # En la máquina real el billetero está casi pegado al borde derecho del panel
    _, by0_, _, by1_ = C.BILL
    bw = C.BILL[2] - C.BILL[0]
    C.BILL = (C.MX0 + C.MW - 70 - bw, by0_, C.MX0 + C.MW - 70, by1_)
    img = C.componer({1, 2, 3, 4, 5, 6}, "tmp", "distribucion.json", guardar=False).convert("RGB")
    d = ImageDraw.Draw(img)
    caja, l2 = v["caja"], v["linea2"]
    gx0, gy0, gx1, gy1 = C.GLASS
    L, R, T, B = C.MX0, C.MX0 + C.MW, C.MY0, C.MY0 + C.MH
    P = C.PANEL_X
    sx0_, sy0_, sx1_, sy1_ = C.SCREEN

    # Líneas decorativas (todas por detrás de los textos): diagonales arriba a la izquierda,
    # una franja que acompaña la costura del panel y diagonales abajo a la derecha.
    lineas_diagonales(d, gx0 - 10, 300, 6, 150, 70, 10, [ROJO, l2])
    d.line((gx0 + 470, 230, gx1 + 34, 230), fill=ROJO, width=6)
    d.line((gx0 + 520, 262, gx1 - 120, 262), fill=l2, width=3)
    d.line((P + 34, T + 60, P + 34, B - 130), fill=ROJO, width=5)
    lineas_diagonales(d, R - 400, B - 82, 5, 55, 70, 8, [ROJO, l2])

    # Elegí en la pantalla (centrado con la pantalla)
    cx = (sx0_ + sx1_) / 2
    ex0, ex1 = sx0_ - 26, sx1_ + 26            # mismo ancho que el marco de la pantalla
    ey1 = sy0_ - 26 - 46; ey0 = ey1 - 92       # separado del marco por la altura del piquito
    d.rounded_rectangle((ex0, ey0, ex1, ey1), 46, fill=ROJO)
    d.polygon([(cx - 26, ey1 - 2), (cx + 26, ey1 - 2), (cx, ey1 + 28)], fill=ROJO)
    centro(d, (cx, (ey0 + ey1) / 2), "Elegí en la pantalla", fnt("xb", 42), BLANCO)

    # Billetero: por si se habilita el efectivo. Todo a su izquierda, en una sola columna.
    bx0, by0, bx1, by1 = C.BILL
    lx0, lx1 = P + 62, bx0 - 34
    lc = (lx0 + lx1) / 2
    d.rounded_rectangle((lx0, by0, lx1, by0 + 118), 18, outline=ROJO, width=4)
    centro(d, (lc, by0 + 42), "NO DA VUELTO", fnt("black", 34), BLANCO)
    centro(d, (lc, by0 + 86), "Pagá el monto justo", fnt("sb", 26), GRIS_T)
    d.text((lx0 + 4, by0 + 150), "BILLETES ACEPTADOS", font=fnt("xb", 24), fill=BLANCO)
    billetes = ["$500", "$1.000", "$2.000", "$10.000", "$20.000"]
    for i, b in enumerate(billetes):
        col, fila = divmod(i, 3)
        d.text((lx0 + 4 + col * 160, by0 + 192 + fila * 44), b, font=fnt("b", 29), fill=GRIS_T)

    # Cómo comprar (fondo negro, letras claras, borde de línea)
    sx0, sx1, sy0 = P + 70, R - 70, by1 + 260
    sy1 = B - 150
    d.rounded_rectangle((sx0, sy0, sx1, sy1), 30, fill=caja, outline=l2, width=3)
    d.text((sx0 + 40, sy0 + 40), "CÓMO COMPRAR", font=fnt("black", 50), fill=BLANCO)
    d.line((sx0 + 40, sy0 + 115, sx0 + 200, sy0 + 115), fill=ROJO, width=7)
    # cada paso: líneas del título (en blanco) + líneas de aclaración (en gris)
    pasos = [(["Elegí tu producto"], ["¿Más de uno? Al carrito."]),
             (["Tocá «Comprar", "ahora»"], []),
             (["Seleccioná QR", "o Efectivo"], []),
             (["Pagá"], []),
             (["Retirá abajo"], [])]
    alto = lambda t, s: max(80, 50 * len(t) + 40 * len(s))
    libre = (sy1 - 40) - (sy0 + 150) - sum(alto(t, s) for t, s in pasos)
    gap = libre / (len(pasos) - 1)
    y = sy0 + 150
    for i, (tit, sub) in enumerate(pasos):
        h = alto(tit, sub)
        d.ellipse((sx0 + 40, y, sx0 + 120, y + 80), fill=ROJO)
        centro(d, (sx0 + 80, y + 41), str(i + 1), fnt("black", 46), BLANCO)
        ty = y + (14 if len(tit) == 1 and not sub else 0)
        for j, ln in enumerate(tit):
            d.text((sx0 + 145, ty + j * 50), ln, font=fnt("xb", 40), fill=BLANCO)
        for j, ln in enumerate(sub):
            d.text((sx0 + 145, ty + len(tit) * 50 + 6 + j * 40), ln, font=fnt("m", 30), fill=GRIS_T)
        if i < len(pasos) - 1:                # línea punteada que une los pasos
            for yy in range(int(y + 92), int(y + h + gap - 10), 18):
                d.ellipse((sx0 + 76, yy, sx0 + 84, yy + 8), fill=l2)
        y += h + gap

    # Puerta de retiro
    qx0, qy0, qx1, qy1 = C.PUSH
    d.rounded_rectangle((qx0 - 10, qy0 - 10, qx1 + 10, qy1 + 10), 14, fill=v["pal"]["push"])
    d.rounded_rectangle((qx0, qy0, qx1, qy1), 10, outline=BLANCO, width=8)
    centro(d, ((qx0 + qx1) / 2, qy0 + (qy1 - qy0) * 0.40), "RETIRÁ TU PRODUCTO", fnt("black", 64), BLANCO)
    centro(d, ((qx0 + qx1) / 2, qy0 + (qy1 - qy0) * 0.76), "Empujá la tapa", fnt("sb", 46), GRIS_T)

    # Soporte: WhatsApp y número de máquina
    wy0, wy1 = qy1 + 80, B - 150
    wx0, wx1 = gx0 - 20, gx1 + 20
    d.rounded_rectangle((wx0, wy0, wx1, wy1), 26, fill=caja, outline=l2, width=3)
    d.rectangle((wx0 + 3, wy0 + 30, wx0 + 13, wy1 - 30), fill=ROJO)
    d.text((wx0 + 60, wy0 + 40), "¿Problemas con tu compra?", font=fnt("xb", 46), fill=BLANCO)
    d.text((wx0 + 60, wy0 + 112), f"WhatsApp {WHATSAPP}", font=fnt("black", 60), fill=ROJO)
    d.rounded_rectangle((wx1 - 300, wy0 + 50, wx1 - 40, wy1 - 50), 18, outline=l2, width=3)
    centro(d, (wx1 - 170, (wy0 + wy1) / 2 - 26), "MÁQUINA N°", fnt("b", 28), GRIS_T)
    centro(d, (wx1 - 170, (wy0 + wy1) / 2 + 24), MAQ_N, fnt("black", 54), BLANCO)
    return img


if __name__ == "__main__":
    out = os.path.join(C.BASE, "salida")
    imgs = []
    for k, v in VERSIONES.items():
        im = ploteo(v)
        im.save(f"{out}/ploteo_sanatorio_{k}.png", optimize=True)
        im.resize((im.width * 1400 // im.height, 1400), Image.LANCZOS).save(f"{out}/ploteo_sanatorio_{k}_liviana.jpg", quality=86)
        imgs.append((v["nombre"], im)); print(k)
    h = 1600; ws = [im.width * h // im.height for _, im in imgs]
    comp = Image.new("RGB", (sum(ws) + 60 * (len(imgs) + 1), h + 160), (244, 245, 247))
    dc = ImageDraw.Draw(comp); x = 60
    for (n, im), w in zip(imgs, ws):
        comp.paste(im.resize((w, h), Image.LANCZOS), (x, 120))
        dc.text((x + w / 2, 60), n, font=fnt("xb", 52), fill=(30, 30, 34), anchor="mm")
        x += w + 60
    comp.save(f"{out}/ploteo_sanatorio_comparativa.jpg", quality=86)
