"""Fachada Urquiza 1180: 3 conceptos distintos, sin tocar el balcón.
A) Atardecer: caja de luz con volumen sobre la vidriera + vidriera limpia mostrando las máquinas.
B) Noche: letras corpóreas retroiluminadas en la pared + neón colgado DENTRO de la vidriera.
C) Día: vinilo impreso en toda la vidriera (como tenía el estudio contable) + vinilo en la puerta.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance
from scipy import ndimage
import fachada as B

D = B.D; W, H = B.W, B.H; fnt = B.fnt; warp = B.warp; mq = B.mask_quad
BASE = B.BASE
SP = "/tmp/claude-0/-home-user-suscripcion-smg/9c85f6b1-136a-5732-b45b-719a946f7de0/scratchpad/"
VID = B.VIDRIERA; PUE = B.PUERTA
CART = [(78, 748), (508, 730), (508, 836), (72, 856)]       # pared terracota sobre la vidriera
PIL_ = B.PILAR


def ruido(im, k=5):
    a = np.asarray(im).astype(float); a += np.random.default_rng(1).normal(0, k, a.shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def reflejo(im, quad, k=0.22):
    """Devuelve parte del reflejo original del vidrio (árboles, autos)."""
    ref = ImageChops.screen(im, ImageEnhance.Brightness(BASE).enhance(k))
    return Image.composite(ref, im, mq(quad))


def sombra(im, layer, dx=6, dy=10, blur=8, op=0.55):
    a = layer.split()[3].point(lambda p: int(p * op))
    s = Image.new("L", (W, H), 0); s.paste(a, (dx, dy)); s = s.filter(ImageFilter.GaussianBlur(blur))
    return Image.composite(Image.new("RGB", (W, H), 0), im, s)


def pegar_interior(im, quad, luz, maquinas=True, k=1.0):
    it = warp(ImageEnhance.Brightness(B.interior(luz, maquinas=maquinas)).enhance(k).convert("RGBA"), quad)
    it.putalpha(ImageChops.multiply(it.split()[3], mq(quad)))
    im.paste(it, (0, 0), it); return im


def tubo(txt, font, size, color, grosor=7):
    """Texto como tubo de neón (contorno), sobre lienzo RGBA."""
    m = Image.new("L", size, 0); ImageDraw.Draw(m).text((size[0] / 2, size[1] / 2), txt, font=font, fill=255, anchor="mm")
    a = np.asarray(m) > 128
    borde = ndimage.binary_dilation(a, iterations=grosor // 2) & ~ndimage.binary_erosion(a, iterations=grosor // 2 + 2)
    out = np.zeros((size[1], size[0], 4), np.uint8); out[borde] = color + (255,)
    return Image.fromarray(out)


# ---------------- A) caja de luz, atardecer ----------------
def version_a():
    im = B.atardecer(BASE, 0.62, (0.95, 0.93, 1.08))
    im = pegar_interior(im, VID, (255, 238, 215), k=1.25)
    im = pegar_interior(im, PUE, (255, 238, 215), maquinas=False, k=1.1)
    im = reflejo(im, VID, 0.25)
    # caja de luz: frente + canto inferior/derecho (volumen) + sombra
    cw, ch = 1000, 250
    frente = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(frente)
    d.rounded_rectangle((0, 0, cw, ch), 26, fill=(250, 248, 244, 255))
    d.rounded_rectangle((0, 0, 250, ch), 26, fill=(200, 20, 30, 255)); d.rectangle((200, 0, 250, ch), fill=(200, 20, 30, 255))
    d.text((125, ch / 2), "S&G", font=fnt("black", 96), fill=(255, 255, 255, 255), anchor="mm")
    d.text((290, 70), "KIOSCO AUTOMÁTICO", font=fnt("black", 64), fill=(28, 28, 30, 255), anchor="lm")
    d.text((292, 175), "Snacks y bebidas · abierto 24 hs", font=fnt("sb", 42), fill=(200, 20, 30, 255), anchor="lm")
    canto = [(x + 8, y + 12) for x, y in CART]
    lado = warp(Image.new("RGBA", (cw, ch), (120, 118, 116, 255)), canto)
    capa = warp(frente, CART)
    im = sombra(im, capa, 14, 22, 14, 0.6)
    im.paste(lado, (0, 0), lado); im.paste(capa, (0, 0), capa)
    halo = capa.filter(ImageFilter.GaussianBlur(30))
    im = ImageChops.add(im, ImageEnhance.Brightness(Image.composite(halo.convert("RGB"), Image.new("RGB", (W, H)), halo.split()[3])).enhance(0.25))
    # vinilo de corte blanco en la puerta (horario) y en el pilar gris
    p = Image.new("RGBA", (500, 720), (0, 0, 0, 0)); dp = ImageDraw.Draw(p)
    dp.text((250, 300), "ABIERTO", font=fnt("black", 78), fill=(255, 255, 255, 240), anchor="mm")
    dp.text((250, 380), "LAS 24 HS", font=fnt("xb", 56), fill=(255, 255, 255, 240), anchor="mm")
    dp.text((250, 470), "Pagá con QR o efectivo", font=fnt("sb", 34), fill=(255, 255, 255, 220), anchor="mm")
    v = warp(p, PUE); im.paste(v, (0, 0), v)
    # aplique de luz sobre la puerta (en la pared propia, bajo el alero)
    luz = Image.new("L", (W, H), 0); ImageDraw.Draw(luz).polygon([(790, 840), (850, 840), (1000, 1280), (640, 1280)], fill=60)
    im = Image.composite(ImageChops.add(im, Image.new("RGB", (W, H), (90, 80, 60))), im, luz.filter(ImageFilter.GaussianBlur(40)))
    return im


# ---------------- B) letras retroiluminadas + neón interior, noche ----------------
def version_b():
    im = B.atardecer(BASE, 0.3, (0.8, 0.86, 1.25))
    im = pegar_interior(im, VID, (230, 236, 255), k=0.9)
    im = pegar_interior(im, PUE, (230, 236, 255), maquinas=False, k=0.7)
    # letras corpóreas: halo detrás (en la pared) + letra oscura delante
    cw, ch = 1000, 250
    let = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); ImageDraw.Draw(let).text((cw / 2, ch / 2), "SNACK 24", font=fnt("black", 200), fill=(30, 30, 34, 255), anchor="mm")
    capa = warp(let, CART)
    halo = capa.split()[3].filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(14))
    im = Image.composite(ImageChops.add(im, Image.new("RGB", (W, H), (255, 245, 225))), im, halo.point(lambda p: int(p * 0.85)))
    im.paste(capa, (0, 0), capa)
    # neón colgado dentro de la vidriera (detrás del vidrio)
    nw, nh = 800, 900
    n = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    n.alpha_composite(tubo("ABIERTO 24 HS", fnt("black", 110), (nw, 200), (255, 70, 190), 7), (0, 20))
    neon_v = [(VID[0][0] + 30, VID[0][1] + 20), (VID[1][0] - 30, VID[1][1] + 20), (VID[1][0] - 30, VID[1][1] + 200), (VID[0][0] + 30, VID[0][1] + 210)]
    neon_v = [neon_v[0], neon_v[1], (neon_v[1][0], neon_v[1][1] + 90), (neon_v[0][0], neon_v[0][1] + 92)]
    capa_n = warp(n.crop((0, 0, nw, 240)), neon_v)
    im = ImageChops.add(im, B.glow(capa_n))
    # cartel "ABIERTO" de neón chico en la puerta
    p = Image.new("RGBA", (500, 720), (0, 0, 0, 0)); p.alpha_composite(tubo("OPEN 24H", fnt("black", 96), (500, 200), (255, 70, 190), 6), (0, 200))
    im = ImageChops.add(im, B.glow(warp(p, PUE)))
    im = reflejo(im, VID, 0.12)
    # pequeño farol en el pilar
    f = Image.new("RGBA", (160, 740), (0, 0, 0, 0)); ImageDraw.Draw(f).rounded_rectangle((55, 60, 105, 130), 10, fill=(255, 240, 210, 255))
    im = ImageChops.add(im, B.glow(warp(f, PIL_), (6, 30, 70), (0.8, 0.5, 0.4)))
    return im


# ---------------- C) vinilo impreso en vidriera, de día ----------------
def producto(nombre):
    for p in (SP + "tanda1/", SP + "dulc/out/", SP + "casalito/out/"):
        try: return Image.open(p + nombre + ".webp").convert("RGBA")
        except FileNotFoundError: pass


def version_c():
    im = BASE.copy()
    vw, vh = 900, 1100
    v = Image.new("RGBA", (vw, vh), (196, 22, 32, 255)); d = ImageDraw.Draw(v)
    d.polygon([(0, vh * 0.62), (vw, vh * 0.48), (vw, vh), (0, vh)], fill=(250, 196, 30, 255))
    d.text((50, 70), "KIOSCO", font=fnt("black", 118), fill=(255, 255, 255, 255))
    d.text((50, 200), "AUTOMÁTICO", font=fnt("black", 74), fill=(255, 255, 255, 255))
    d.rounded_rectangle((50, 350, 560, 470), 22, fill=(255, 255, 255, 255))
    d.text((305, 410), "ABIERTO 24 HS", font=fnt("black", 66), fill=(196, 22, 32, 255), anchor="mm")
    d.text((50, 500), "Snacks · bebidas frías · golosinas", font=fnt("sb", 40), fill=(255, 255, 255, 255))
    prods = ["pepsi_500", "gatorade_tropical_500", "oblea_bonobon_leche_30", "galletitas_opera_55", "baggio_fresh_naranja", "diversion_400"]
    xs = [40, 190, 330, 480, 630, 740]
    for i, (n, x) in enumerate(zip(prods, xs)):
        p = producto(n)
        if p is None: continue
        p.thumbnail((200, 280)); v.alpha_composite(p, (x, int(vh * 0.68) + (i % 2) * 40))
    # ventana sin vinilo para ver una máquina (recorte)
    d.rounded_rectangle((640, 70, 860, 470), 18, fill=(0, 0, 0, 0))
    capa = warp(v, VID)
    it = warp(B.interior((255, 245, 230)).convert("RGBA"), VID); it.putalpha(mq(VID))
    im.paste(it, (0, 0), it); im.paste(capa, (0, 0), capa)
    im = reflejo(im, VID, 0.18)
    # puerta: vinilo esmerilado con franja roja y horario
    p = Image.new("RGBA", (500, 720), (0, 0, 0, 0)); dp = ImageDraw.Draw(p)
    dp.rectangle((0, 0, 500, 720), fill=(222, 226, 230, 248))
    dp.rectangle((0, 260, 500, 470), fill=(196, 22, 32, 255))
    dp.text((250, 330), "ENTRÁ", font=fnt("black", 80), fill=(255, 255, 255, 255), anchor="mm")
    dp.text((250, 415), "abierto todo el día", font=fnt("sb", 40), fill=(255, 255, 255, 255), anchor="mm")
    vp = warp(p, PUE); im.paste(vp, (0, 0), vp)
    # nombre en letras de vinilo sobre la pared terracota
    t = Image.new("RGBA", (1000, 250), (0, 0, 0, 0)); dt = ImageDraw.Draw(t)
    dt.text((500, 95), "S&G 24", font=fnt("black", 150), fill=(255, 255, 255, 245), anchor="mm")
    dt.text((500, 205), "local automático", font=fnt("sb", 54), fill=(255, 255, 255, 235), anchor="mm")
    ct = warp(t, CART); im = sombra(im, ct, 3, 4, 2, 0.35); im.paste(ct, (0, 0), ct)
    # bandera (cartel perpendicular) en la columna, con su sombra
    bw, bh = 220, 220
    bd = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); db = ImageDraw.Draw(bd)
    db.ellipse((0, 0, bw, bh), fill=(250, 196, 30, 255)); db.ellipse((14, 14, bw - 14, bh - 14), fill=(196, 22, 32, 255))
    db.text((bw / 2, bh / 2 - 22), "24", font=fnt("black", 96), fill=(255, 255, 255, 255), anchor="mm")
    db.text((bw / 2, bh / 2 + 52), "HS", font=fnt("black", 44), fill=(255, 255, 255, 255), anchor="mm")
    q = [(522, 880), (602, 884), (602, 990), (522, 996)]
    cb = warp(bd, q); ImageDraw.Draw(im).line((508, 938, 522, 938), fill=(60, 60, 60), width=6)
    im = sombra(im, cb, -10, 16, 6, 0.4); im.paste(cb, (0, 0), cb)
    return im


def terminar(im):
    im = im.filter(ImageFilter.GaussianBlur(0.6)); im = ruido(im, 3)
    return im.crop((0, 330, W, 1480))


if __name__ == "__main__":
    outs = []
    for k, fn in (("A_caja_de_luz", version_a), ("B_neon_interior", version_b), ("C_vinilo_dia", version_c)):
        im = terminar(fn()); im.save(D + f"fachada2_{k}.jpg", quality=90); outs.append(im); print(k)
    w = 600; h = int(outs[0].height * w / outs[0].width)
    comp = Image.new("RGB", (w * 3 + 40, h), (20, 20, 22))
    for i, o in enumerate(outs): comp.paste(o.resize((w, h)), (i * (w + 20), 0))
    comp.save(D + "comparativa2.jpg", quality=88)
