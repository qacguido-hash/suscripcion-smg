"""Arma la imagen de la máquina expendedora cargada con los productos recortados.

Uso:
    python3 scripts/componer.py                # los 6 estantes
    python3 scripts/componer.py --estantes 1 2 # versión parcial (solo esos estantes)

Salidas en salida/: maquina_<sufijo>.png (alta, 2600x3560) y maquina_<sufijo>_liviana.jpg.
Todo se dibuja a escala única (px por cm) para que los tamaños sean coherentes con los reales.
"""
import argparse, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageEnhance

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_M = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
if not os.path.exists(FONT_M):
    FONT_M = FONT_B

# ---------------------------------------------------------------- geometría
CW, CH = 2600, 3560                     # lienzo
MX0, MY0, MW, MH = 150, 120, 2300, 3220  # gabinete
def mx(f): return int(MX0 + f * MW)
def my(f): return int(MY0 + f * MH)
GLASS = (mx(0.085), my(0.075), mx(0.655), my(0.715))   # vidriera (x0,y0,x1,y1)
PANEL_X = mx(0.705)                                      # costura con el panel derecho
SCREEN = (mx(0.738), my(0.17), mx(0.925), my(0.43))
BILL = (mx(0.795), my(0.47), mx(0.885), my(0.575))
PUSH = (mx(0.165), my(0.785), mx(0.545), my(0.86))

RED = (196, 22, 32)
RED_DARK = (140, 12, 20)
RED_LIGHT = (226, 52, 58)


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(w, h, top, bottom):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t
    return Image.fromarray(np.repeat(a, w, axis=1).astype(np.uint8))


def hgrad(w, h, left, right):
    t = np.linspace(0, 1, w)[None, :, None]
    a = np.array(left)[None, None, :] * (1 - t) + np.array(right)[None, None, :] * t
    return Image.fromarray(np.repeat(a, h, axis=0).astype(np.uint8))


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    return m


# ---------------------------------------------------------------- fondo y gabinete
def fondo():
    bg = vgrad(CW, CH, (236, 237, 240), (214, 216, 220))
    # piso apenas más oscuro con brillo
    floor_y = MY0 + MH + 40
    floor = vgrad(CW, CH - floor_y, (205, 207, 211), (226, 228, 231))
    bg.paste(floor, (0, floor_y))
    return bg, floor_y


def gabinete(img, floor_y):
    d = ImageDraw.Draw(img)
    # sombra en el piso
    sh = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(sh).ellipse((MX0 - 60, floor_y - 40, MX0 + MW + 60, floor_y + 70), fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(40))
    img.paste((40, 40, 45), (0, 0), sh)
    # patas / ruedas
    for fx in (0.06, 0.94):
        x = mx(fx)
        d.rounded_rectangle((x - 45, MY0 + MH - 10, x + 45, floor_y + 5), 10, fill=(35, 35, 38))
        d.rectangle((x - 30, MY0 + MH + 8, x + 30, MY0 + MH + 18), fill=(70, 70, 75))
    # cuerpo con sombreado lateral
    body = hgrad(MW, MH, (0, 0, 0), (0, 0, 0))
    base = Image.new("RGB", (MW, MH), RED)
    t = np.linspace(0, 1, MW)
    shade = 1 - 0.18 * np.exp(-((t - 0.0) / 0.025) ** 2) - 0.25 * np.exp(-((t - 1.0) / 0.03) ** 2) + 0.05 * np.exp(-((t - 0.35) / 0.25) ** 2)
    arr = np.asarray(base).astype(float) * shade[None, :, None]
    tv = np.linspace(0, 1, MH)
    arr *= (1 - 0.10 * tv)[:, None, None]
    body = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    img.paste(body, (MX0, MY0), rounded_mask((MW, MH), 18))
    # borde superior y zócalo
    d.rounded_rectangle((MX0, MY0, MX0 + MW, MY0 + 22), 12, fill=RED_LIGHT)
    d.rectangle((MX0 + 8, MY0 + MH - 70, MX0 + MW - 8, MY0 + MH - 8), fill=(120, 10, 18))
    d.rectangle((MX0 + 8, MY0 + MH - 70, MX0 + MW - 8, MY0 + MH - 64), fill=(160, 20, 28))
    # costura puerta / panel
    d.rectangle((PANEL_X - 5, MY0 + 22, PANEL_X + 5, MY0 + MH - 70), fill=RED_DARK)
    d.line((PANEL_X + 6, MY0 + 22, PANEL_X + 6, MY0 + MH - 70), fill=RED_LIGHT, width=2)
    # marco de la vidriera (bisel)
    gx0, gy0, gx1, gy1 = GLASS
    d.rounded_rectangle((gx0 - 34, gy0 - 34, gx1 + 34, gy1 + 34), 22, fill=RED_DARK)
    d.rounded_rectangle((gx0 - 28, gy0 - 28, gx1 + 28, gy1 + 28), 18, fill=(214, 40, 46))
    d.rounded_rectangle((gx0 - 14, gy0 - 14, gx1 + 14, gy1 + 14), 10, fill=(25, 25, 28))
    # cerradura
    lx, ly = mx(0.675), my(0.475)
    d.rounded_rectangle((lx - 22, ly - 60, lx + 22, ly + 60), 10, fill=(150, 150, 155))
    d.rounded_rectangle((lx - 16, ly - 54, lx + 16, ly + 54), 8, fill=(205, 205, 210))
    d.ellipse((lx - 11, ly - 11, lx + 11, ly + 11), fill=(90, 90, 95))
    d.rectangle((lx - 3, ly - 9, lx + 3, ly + 9), fill=(40, 40, 45))
    # puerta de retiro PUSH
    px0, py0, px1, py1 = PUSH
    d.rounded_rectangle((px0 - 10, py0 - 10, px1 + 10, py1 + 10), 10, fill=(170, 16, 26))
    d.rounded_rectangle((px0, py0, px1, py1), 6, outline=(255, 255, 255), width=7)
    f = font(FONT_B, int((py1 - py0) * 0.55))
    d.text(((px0 + px1) / 2, (py0 + py1) / 2 + 4), "PUSH", font=f, fill=(255, 255, 255), anchor="mm")


def pantalla(img, thumbs):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = SCREEN
    d.rounded_rectangle((x0 - 26, y0 - 26, x1 + 26, y1 + 26), 18, fill=(22, 22, 26))
    d.rounded_rectangle((x0 - 20, y0 - 20, x1 + 20, y1 + 20), 14, fill=(40, 40, 46))
    w, h = x1 - x0, y1 - y0
    scr = vgrad(w, h, (238, 242, 247), (224, 230, 238))
    sd = ImageDraw.Draw(scr)
    sd.rectangle((0, 0, w, int(h * 0.11)), fill=RED)
    sd.text((w / 2, h * 0.055), "Elegí tu producto", font=font(FONT_B, int(h * 0.05)), fill="white", anchor="mm")
    cols, rows = 3, 4
    gx0, gy0, gw, gh = int(w * 0.06), int(h * 0.15), int(w * 0.88), int(h * 0.70)
    cw, ch = gw / cols, gh / rows
    for i, t in enumerate(thumbs[: cols * rows]):
        c, r = i % cols, i // cols
        bx, by = int(gx0 + c * cw + 6), int(gy0 + r * ch + 6)
        bw, bh = int(cw - 12), int(ch - 12)
        sd.rounded_rectangle((bx, by, bx + bw, by + bh), 12, fill="white", outline=(210, 214, 222), width=2)
        tt = t.copy(); tt.thumbnail((int(bw * 0.8), int(bh * 0.8)), Image.LANCZOS)
        scr.paste(tt, (bx + (bw - tt.width) // 2, by + (bh - tt.height) // 2), tt)
    sd.rounded_rectangle((int(w * 0.12), int(h * 0.885), int(w * 0.88), int(h * 0.955)), 24, fill=(30, 140, 70))
    sd.text((w / 2, h * 0.92), "Pagá con QR, tarjeta o efectivo", font=font(FONT_M, int(h * 0.023)), fill="white", anchor="mm")
    img.paste(scr, (x0, y0), rounded_mask((w, h), 8))
    # reflejo del vidrio de la pantalla
    refl = Image.new("L", (w, h), 0)
    ImageDraw.Draw(refl).polygon([(0, 0), (int(w * 0.45), 0), (0, int(h * 0.35))], fill=28)
    img.paste((255, 255, 255), (x0, y0), refl.filter(ImageFilter.GaussianBlur(20)))


def billetero(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = BILL
    d.rounded_rectangle((x0 - 10, y0 - 10, x1 + 10, y1 + 10), 10, fill=(18, 18, 20))
    d.rounded_rectangle((x0, y0, x1, y1), 8, fill=(36, 36, 40))
    w = x1 - x0
    # etiqueta superior amarilla/blanca como en la foto base
    d.rounded_rectangle((x0 + 12, y0 + 14, x1 - 12, y0 + 60), 5, fill=(240, 196, 40))
    d.text(((x0 + x1) / 2, y0 + 37), "BILLETES", font=font(FONT_B, 26), fill=(30, 30, 30), anchor="mm")
    # boca del billetero
    d.rounded_rectangle((x0 + 18, y0 + 95, x1 - 18, y0 + 150), 6, fill=(8, 8, 10))
    d.rectangle((x0 + 30, y0 + 118, x1 - 30, y0 + 126), fill=(60, 60, 64))
    for i, col in enumerate([(40, 200, 90), (230, 60, 50)]):
        d.ellipse((x0 + 24 + i * 28, y1 - 46, x0 + 40 + i * 28, y1 - 30), fill=col)
    # lector de tarjeta / QR debajo
    cx0, cy0 = x0 - 10, y1 + 60
    d.rounded_rectangle((cx0, cy0, x1 + 10, cy0 + 150), 12, fill=(28, 28, 32))
    d.rounded_rectangle((cx0 + 14, cy0 + 14, x1 - 4, cy0 + 136), 8, fill=(48, 48, 54))
    cx, cy = (cx0 + x1 + 10) // 2, cy0 + 75
    for r in (18, 32, 46):
        d.arc((cx - r - 10, cy - r, cx + r - 10, cy + r), -45, 45, fill=(235, 235, 240), width=6)


# ---------------------------------------------------------------- interior
def interior(gw, gh):
    """Fondo iluminado de la vidriera con paredes laterales y tiras LED."""
    inn = vgrad(gw, gh, (226, 228, 232), (200, 203, 208))
    arr = np.asarray(inn).astype(float)
    t = np.linspace(-1, 1, gw)
    arr *= (1 - 0.12 * t ** 4)[None, :, None]
    inn = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(inn)
    side = int(gw * 0.045)
    # paredes laterales en perspectiva
    d.polygon([(0, 0), (side, side), (side, gh - side // 2), (0, gh)], fill=(178, 180, 186))
    d.polygon([(gw, 0), (gw - side, side), (gw - side, gh - side // 2), (gw, gh)], fill=(170, 172, 178))
    d.polygon([(0, 0), (gw, 0), (gw - side, side), (side, side)], fill=(150, 152, 158))
    # tiras LED verticales
    glow = Image.new("L", (gw, gh), 0)
    gd = ImageDraw.Draw(glow)
    for x in (int(side * 0.45), gw - int(side * 0.45)):
        gd.rectangle((x - 7, side, x + 7, gh - side), fill=255)
    halo = glow.filter(ImageFilter.GaussianBlur(28))
    inn.paste((255, 255, 255), (0, 0), ImageChops.add(halo.point(lambda v: int(v * 0.9)), glow))
    return inn, side


def preparar(slug, spec):
    im = Image.open(f"{BASE}/productos/{slug}.png").convert("RGBA")
    if spec.get("rotar"):
        im = im.rotate(90, expand=True, resample=Image.BICUBIC)
    return im


def sombra_producto(size, strength=150):
    w, h = size
    m = Image.new("L", (w + 80, 60), 0)
    ImageDraw.Draw(m).ellipse((40, 18, 40 + w, 42), fill=strength)
    return m.filter(ImageFilter.GaussianBlur(10))


def oscurecer(im, factor):
    rgb = ImageEnhance.Brightness(im.convert("RGB")).enhance(factor)
    rgb.putalpha(im.getchannel("A"))
    return rgb


def sombreado_base(im):
    """Leve oclusión/sombra hacia la base del envase para integrarlo con la luz interior."""
    w, h = im.size
    g = np.ones((h, 1))
    t = np.linspace(0, 1, h)
    g[:, 0] = 1 - 0.18 * np.clip((t - 0.7) / 0.3, 0, 1) - 0.06 * np.clip((0.12 - t) / 0.12, 0, 1)
    arr = np.asarray(im).astype(float)
    arr[:, :, :3] *= g[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def componer(estantes_a_llenar, sufijo):
    cfg = json.load(open(f"{BASE}/scripts/distribucion.json"))
    img, floor_y = fondo()
    gabinete(img, floor_y)
    gx0, gy0, gx1, gy1 = GLASS
    gw, gh = gx1 - gx0, gy1 - gy0
    inn, side = interior(gw, gh)
    idraw = ImageDraw.Draw(inn)

    total_cm = sum(e["alto_cm"] for e in cfg["estantes"]) + 4   # 4 cm de techo
    pxcm = gh / total_cm
    usable_w = gw - 2 * side - 20
    eye_y = gh * 0.48                       # altura de cámara (centro de la vidriera)
    reporte = {}
    thumbs = []
    lip_h = int(1.9 * pxcm)
    label_font = font(FONT_B, int(lip_h * 0.46))

    y_cursor = gh
    shelf_rows = []
    for e in cfg["estantes"]:
        base_y = y_cursor - lip_h
        top_y = y_cursor - int(e["alto_cm"] * pxcm)
        shelf_rows.append((e, base_y, top_y))
        y_cursor = top_y

    for e, base_y, top_y in shelf_rows:
        n = len(e["canales"])
        chw = usable_w / n
        x_start = side + 10
        # bandeja (fondo metálico) y sombra del estante superior
        idraw.rectangle((side, base_y - 6, gw - side, base_y), fill=(150, 152, 158))
        ceiling = Image.new("L", (gw, 50), 0)
        ImageDraw.Draw(ceiling).rectangle((0, 0, gw, 18), fill=90)
        inn.paste((60, 60, 70), (0, top_y + lip_h), ceiling.filter(ImageFilter.GaussianBlur(14)))
        clearance = base_y - (top_y + lip_h) - 8
        for i, c in enumerate(e["canales"]):
            slug = c["slug"]
            if e["n"] not in estantes_a_llenar:
                continue
            im = preparar(slug, c)
            if "alto_cm" in c:
                th = c["alto_cm"] * pxcm; tw = im.width * th / im.height
            else:
                tw = c["ancho_cm"] * pxcm; th = im.height * tw / im.width
            real = (tw / pxcm, th / pxcm)
            fit = min(1.0, (chw - 8) / tw, clearance / th)
            tw, th = tw * fit, th * fit
            im = im.resize((max(1, int(tw)), max(1, int(th))), Image.LANCZOS)
            im = sombreado_base(im)
            if len(thumbs) < 12 and e["n"] in (1, 3, 6):
                thumbs.append(Image.open(f"{BASE}/productos/{slug}.png").convert("RGBA"))
            cx = x_start + chw * (i + 0.5)
            # unidades de atrás (cargado en profundidad): se ven corridas según la altura de cámara
            depth = 3
            dy_step = (base_y - eye_y) * 0.022      # >0 si el estante está debajo del ojo -> las de atrás asoman arriba
            for k in range(depth - 1, -1, -1):
                s = 1 - 0.035 * k
                u = im if k == 0 else im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
                u = oscurecer(u, 1 - 0.13 * k)
                ux = int(cx - u.width / 2 + (gw / 2 - cx) * 0.02 * k)
                uy = int(base_y - u.height - dy_step * k * 1.0)
                if k == 0:
                    sh = sombra_producto((u.width, u.height))
                    inn.paste((20, 20, 25), (ux - 40, base_y - 32), sh)
                inn.paste(u, (ux, uy), u)
            reporte[slug] = {
                "medida_real_cm": [round(real[0], 1), round(real[1], 1)],
                "escala_aplicada": round(fit, 2),
                "rotado": bool(c.get("rotar")),
            }
        # labio frontal rojo con etiquetas de canal (como en la máquina de referencia)
        idraw.rectangle((side - 6, base_y, gw - side + 6, base_y + lip_h), fill=(178, 18, 28))
        idraw.rectangle((side - 6, base_y, gw - side + 6, base_y + 4), fill=(225, 60, 64))
        idraw.rectangle((side - 6, base_y + lip_h - 4, gw - side + 6, base_y + lip_h), fill=(120, 8, 16))
        fila = "ABCDEF"[6 - e["n"]]
        for i in range(n):
            cx = x_start + chw * (i + 0.5)
            lw = min(chw * 0.62, lip_h * 2.2)
            idraw.rounded_rectangle((cx - lw / 2, base_y + lip_h * 0.2, cx + lw / 2, base_y + lip_h * 0.8), 4, fill=(250, 250, 250))
            idraw.text((cx, base_y + lip_h * 0.5), f"{fila}{i + 1}", font=label_font, fill=(40, 40, 45), anchor="mm")

    # reflejos del vidrio
    refl = Image.new("L", (gw, gh), 0)
    rd = ImageDraw.Draw(refl)
    rd.polygon([(int(gw * 0.08), 0), (int(gw * 0.30), 0), (int(gw * 0.02), int(gh * 0.55)), (0, int(gh * 0.55)), (0, int(gh * 0.2))], fill=34)
    rd.polygon([(int(gw * 0.62), gh), (int(gw * 0.70), gh), (gw, int(gh * 0.55)), (gw, int(gh * 0.42))], fill=22)
    inn.paste((255, 255, 255), (0, 0), refl.filter(ImageFilter.GaussianBlur(30)))
    img.paste(inn, (gx0, gy0), rounded_mask((gw, gh), 8))

    if not thumbs:
        thumbs = [Image.open(f"{BASE}/productos/{c['slug']}.png").convert("RGBA") for c in cfg["estantes"][0]["canales"]]
    pantalla(img, thumbs)
    billetero(img)

    os.makedirs(f"{BASE}/salida", exist_ok=True)
    out = f"{BASE}/salida/maquina_{sufijo}.png"
    img.save(out, optimize=True)
    lite = img.convert("RGB").resize((int(CW * 1400 / CH), 1400), Image.LANCZOS)
    lite.save(f"{BASE}/salida/maquina_{sufijo}_liviana.jpg", quality=85, optimize=True, progressive=True)
    json.dump({"px_por_cm": round(pxcm, 2), "productos": reporte}, open(f"{BASE}/salida/escalas_{sufijo}.json", "w"), indent=1, ensure_ascii=False)
    print(out, f"{pxcm:.2f} px/cm")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--estantes", type=int, nargs="*", default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--sufijo", default=None)
    a = ap.parse_args()
    suf = a.sufijo or ("completa" if len(a.estantes) == 6 else "parcial_" + "_".join(map(str, a.estantes)))
    componer(set(a.estantes), suf)
