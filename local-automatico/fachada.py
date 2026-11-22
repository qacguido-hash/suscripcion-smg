"""Simulación de fachada: local automático 24 hs en Urquiza 1180 (Quilmes). 3 versiones."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance
from scipy import ndimage

D = "/tmp/claude-0/-home-user-suscripcion-smg/9c85f6b1-136a-5732-b45b-719a946f7de0/scratchpad/fachada/"
F = "/usr/share/fonts/opentype/inter/"
SAL = "/home/user/suscripcion-smg/maquina-expendedora/salida/"
def fnt(w, s): return ImageFont.truetype(F + {"black": "Inter-Black.otf", "xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf"}[w], s)

BASE = Image.open(D + "base.png").convert("RGB")
W, H = BASE.size
# Zonas medidas sobre la foto (x, y): esquinas TL, TR, BR, BL
VIDRIERA = [(110, 875), (402, 858), (384, 1238), (38, 1198)]
CARTEL = [(70, 742), (512, 722), (512, 838), (64, 860)]        # pared terracota sobre la vidriera
PUERTA = [(698, 916), (944, 909), (984, 1266), (701, 1252)]
FAJA = [(575, 704), (1150, 692), (1150, 768), (575, 798)]       # frente gris del balcón sobre la puerta
PILAR = [(604, 870), (686, 868), (688, 1240), (606, 1246)]     # pared gris entre la columna y la puerta
ALERO = [(548, 806), (1220, 772)]                               # borde del alero de madera


def coeffs(dst, src):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def warp(flat, quad):
    """Lleva una imagen plana RGBA a un cuadrilátero de la foto."""
    w, h = flat.size
    c = coeffs(quad, [(0, 0), (w, 0), (w, h), (0, h)])
    return flat.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC, fillcolor=(0, 0, 0, 0))


def mask_quad(quad):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(quad, fill=255); return m


def glow(layer, radios=(3, 10, 26), fuerza=(0.55, 0.4, 0.3)):
    """Neón: suma la capa con versiones desenfocadas de sí misma."""
    out = Image.new("RGB", layer.size, 0)
    rgb = Image.new("RGB", layer.size, 0); rgb.paste(layer, (0, 0), layer)
    for r, f in zip(radios, fuerza):
        b = rgb.filter(ImageFilter.GaussianBlur(r))
        out = ImageChops.add(out, ImageEnhance.Brightness(b).enhance(f))
    return ImageChops.add(out, rgb)


def atardecer(im, k=0.42, tinte=(0.85, 0.9, 1.18)):
    a = np.asarray(im).astype(float) * k * np.array(tinte)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def maquina():
    m = Image.open(SAL + "maquina_completa.png").convert("RGB")
    a = np.asarray(m).astype(int); bg = a[5, 5]
    fondo = np.abs(a - bg).max(axis=2) < 12
    lab, _ = ndimage.label(fondo); borde = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    al = np.where(np.isin(lab, list(borde)), 0, 255).astype(np.uint8)
    m = m.convert("RGBA"); m.putalpha(Image.fromarray(al)); return m.crop(m.getbbox())


MAQ = maquina()


def interior(color_luz, piso=(40, 36, 44), maquinas=True):
    """Vista del interior por la vidriera: local iluminado con 2 máquinas."""
    w, h = 600, 760
    im = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(h):                                      # pared con luz cálida arriba
        t = y / h; c = tuple(int(c0 * 0.62 * (1 - t * 0.5)) for c0 in color_luz); d.line((0, y, w, y), fill=c)
    d.rectangle((0, int(h * 0.82), w, h), fill=piso)
    for i, x in enumerate((20, 305) if maquinas else ()):
        mq = MAQ.copy(); mq.thumbnail((280, 640))
        im.paste(mq, (x, int(h * 0.84) - mq.height), mq)
    d.rectangle((0, 0, w, 14), fill=(255, 255, 255))         # tubo LED del techo
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    return im.convert("RGBA")


def texto_centrado(d, box, txt, font, fill):
    x0, y0, x1, y1 = box
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), txt, font=font, fill=fill, anchor="mm")


def render(v):
    im = atardecer(BASE, *v["noche"])
    # 1) Vidriera con el interior iluminado + reflejo leve
    inter = warp(interior(v["luz"]), VIDRIERA)
    inter.putalpha(ImageChops.multiply(inter.split()[3], mask_quad(VIDRIERA)))
    im.paste(inter, (0, 0), inter)
    vid = BASE.copy(); ref = Image.blend(im, atardecer(vid, 0.5), 0.12); im.paste(ref, (0, 0), mask_quad(VIDRIERA))

    neon = Image.new("RGBA", (W, H), (0, 0, 0, 0))          # todo lo que brilla
    plano = Image.new("RGBA", (W, H), (0, 0, 0, 0))         # carteles opacos (no brillan solos)

    # 2) Cartel principal sobre la vidriera
    cw, ch = 900, 230
    c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); dc = ImageDraw.Draw(c)
    v["cartel"](dc, cw, ch)
    capa = warp(c, CARTEL)
    if v.get("cartel_caja"):
        plano.alpha_composite(warp(v["cartel_caja"](cw, ch), CARTEL))
    neon.alpha_composite(capa)

    # 3) Faja sobre la puerta
    fw, fh = 1300, 160
    f = Image.new("RGBA", (fw, fh), (0, 0, 0, 0)); v["faja"](ImageDraw.Draw(f), fw, fh, f)
    (plano if v.get("faja_opaca") else neon).alpha_composite(warp(f, FAJA))

    # 4) Puerta: vidrio con interior iluminado (tapa los carteles de la inmobiliaria)
    pin = warp(interior(v['luz'], maquinas=False).crop((300, 0, 600, 760)), PUERTA); pin.putalpha(ImageChops.multiply(pin.split()[3], mask_quad(PUERTA)))
    im.paste(pin, (0, 0), pin)
    pw, ph = 500, 720
    p = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); v["puerta"](ImageDraw.Draw(p), pw, ph)
    neon.alpha_composite(warp(p, PUERTA))

    # 5) Pilar vertical 24 HS
    lw, lh = 160, 740
    l = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); v["pilar"](ImageDraw.Draw(l), lw, lh)
    neon.alpha_composite(warp(l, PILAR))

    # 6) Tira LED en el alero y marco de la vidriera
    dn = ImageDraw.Draw(neon)
    dn.line(ALERO, fill=v["led"] + (255,), width=5)
    if v.get("marco"):
        dn.line(VIDRIERA + [VIDRIERA[0]], fill=v["marco"] + (255,), width=5, joint="curve")

    im.paste(plano, (0, 0), plano)
    im = ImageChops.add(im, glow(neon))
    # luz que cae sobre la vereda
    piso = Image.new("L", (W, H), 0); dp = ImageDraw.Draw(piso)
    dp.ellipse((-60, 1180, 520, 1500), fill=90); dp.ellipse((620, 1220, 1100, 1480), fill=70)
    piso = piso.filter(ImageFilter.GaussianBlur(60))
    im = Image.composite(ImageChops.add(im, Image.new("RGB", (W, H), v["luz_piso"])), im, piso)
    return im.crop((0, 300, W, 1500))


# ---------- versiones ----------
ROJO, BLANCO, AMAR = (255, 40, 50), (255, 255, 255), (255, 200, 30)


def v1_cartel(d, w, h):
    texto_centrado(d, (0, 0, w, h * 0.62), "S&G SNACKS", fnt("black", 130), ROJO + (255,))
    texto_centrado(d, (0, h * 0.6, w, h), "AUTOSERVICIO · ABIERTO 24 HS", fnt("xb", 50), BLANCO + (255,))


def v1_faja(d, w, h, im):
    d.rounded_rectangle((20, 18, w - 20, h - 18), 18, outline=ROJO + (255,), width=8)
    texto_centrado(d, (0, 0, w, h), "SNACKS Y BEBIDAS 24 HS", fnt("black", 96), BLANCO + (255,))


def v1_puerta(d, w, h):
    d.rounded_rectangle((60, 170, w - 60, 400), 30, outline=ROJO + (255,), width=10)
    texto_centrado(d, (60, 170, w - 60, 290), "ABIERTO", fnt("black", 96), ROJO + (255,))
    texto_centrado(d, (60, 280, w - 60, 400), "24 HS", fnt("black", 96), BLANCO + (255,))
    texto_centrado(d, (0, 470, w, 540), "Pagá con QR", fnt("b", 46), BLANCO + (230,))


def v1_pilar(d, w, h):
    for i, ch in enumerate("24HS"):
        d.text((w / 2, 110 + i * 160), ch, font=fnt("black", 130), fill=(ROJO if i < 2 else BLANCO) + (255,), anchor="mm")


def v2_cartel(d, w, h):
    texto_centrado(d, (0, 0, w, h * 0.58), "AUTO SNACK", fnt("black", 124), (0, 230, 255, 255))
    texto_centrado(d, (0, h * 0.56, w, h), "abierto 24/7 · sin esperas", fnt("xb", 54), (255, 60, 200, 255))


def v2_faja(d, w, h, im):
    for i in range(0, w, 34):                                # tira de puntos LED
        d.ellipse((i + 8, 14, i + 22, 28), fill=(255, 60, 200, 255)); d.ellipse((i + 8, h - 28, i + 22, h - 14), fill=(0, 230, 255, 255))
    texto_centrado(d, (0, 0, w, h), "KIOSCO AUTOMÁTICO", fnt("black", 96), BLANCO + (255,))


def v2_puerta(d, w, h):
    d.ellipse((90, 120, w - 90, 120 + w - 180), outline=(0, 230, 255, 255), width=12)
    texto_centrado(d, (90, 120, w - 90, 120 + w - 180), "24/7", fnt("black", 130), (255, 60, 200, 255))
    texto_centrado(d, (0, 500, w, 580), "ABIERTO", fnt("black", 80), (0, 230, 255, 255))


def v2_pilar(d, w, h):
    d.line((w / 2 - 40, 30, w / 2 - 40, h - 30), fill=(0, 230, 255, 255), width=10)
    d.line((w / 2 + 40, 30, w / 2 + 40, h - 30), fill=(255, 60, 200, 255), width=10)


def v3_caja(w, h):
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(c).rounded_rectangle((0, 0, w, h), 24, fill=(18, 18, 20, 255)); return c


def v3_cartel(d, w, h):
    d.rounded_rectangle((8, 8, w - 8, h - 8), 22, outline=AMAR + (255,), width=10)
    texto_centrado(d, (0, 0, w * 0.68, h), "SNACK", fnt("black", 150), AMAR + (255,))
    d.rounded_rectangle((w * 0.68, 34, w - 34, h - 34), 18, fill=AMAR + (255,))
    texto_centrado(d, (w * 0.68, 34, w - 34, h - 34), "24HS", fnt("black", 96), (18, 18, 20, 255))


def v3_faja(d, w, h, im):
    d.rectangle((0, 0, w, h), fill=AMAR + (255,))
    texto_centrado(d, (0, 0, w, h), "SNACKS · BEBIDAS · 24 HS", fnt("black", 96), (18, 18, 20, 255))


def v3_puerta(d, w, h):
    d.rounded_rectangle((60, 170, w - 60, 340), 20, outline=AMAR + (255,), width=10)
    texto_centrado(d, (60, 170, w - 60, 340), "ABIERTO", fnt("black", 96), AMAR + (255,))
    texto_centrado(d, (0, 350, w, 450), "LAS 24 HORAS", fnt("xb", 56), AMAR + (255,))


def v3_pilar(d, w, h):
    for i in range(9):
        d.rounded_rectangle((30, 40 + i * 78, w - 30, 40 + i * 78 + 44), 10, fill=AMAR + (255,))


VERS = {
    "1_rojo_sg": dict(noche=(0.42, (0.9, 0.9, 1.15)), luz=(255, 236, 214), led=ROJO, marco=None, luz_piso=(60, 20, 20),
                      cartel=v1_cartel, faja=v1_faja, puerta=v1_puerta, pilar=v1_pilar),
    "2_neon": dict(noche=(0.32, (0.8, 0.85, 1.25)), luz=(225, 240, 255), led=(255, 60, 200), marco=(0, 230, 255), luz_piso=(20, 40, 60),
                   cartel=v2_cartel, faja=v2_faja, puerta=v2_puerta, pilar=v2_pilar),
    "3_amarillo": dict(noche=(0.45, (0.95, 0.92, 1.05)), luz=(255, 244, 220), led=AMAR, marco=AMAR, luz_piso=(60, 50, 15),
                       cartel=v3_cartel, cartel_caja=v3_caja, faja=v3_faja, faja_opaca=True, puerta=v3_puerta, pilar=v3_pilar),
}

if __name__ == "__main__":
    outs = []
    for k, v in VERS.items():
        im = render(v); im.save(D + f"fachada_{k}.jpg", quality=90); outs.append(im); print(k)
    w = 600; hs = [int(o.height * w / o.width) for o in outs]
    comp = Image.new("RGB", (w * 3 + 40, max(hs)), (20, 20, 22))
    for i, o in enumerate(outs): comp.paste(o.resize((w, hs[i])), (i * (w + 20), 0))
    comp.save(D + "comparativa.jpg", quality=88)
