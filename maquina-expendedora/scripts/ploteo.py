"""Maquetas del ploteo (vinilo) de la máquina: color del gabinete + gráficos e instrucciones.

Uso:
    python3 scripts/ploteo.py            # genera las 3 versiones y una comparativa
Salidas en salida/ploteo_<version>.png y salida/ploteo_comparativa.jpg
"""
import os, sys
import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import componer as C

F = "/usr/share/fonts/opentype/inter/"
def fnt(w, s): return ImageFont.truetype(F + {"black": "Inter-Black.otf", "xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf",
                                                "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf"}[w], s)

WHATSAPP = "11 0000-0000"          # reemplazar por el número real
MAQ_N = "001"

VERSIONES = {
    "a_rojo": dict(nombre="A · Rojo S&G",
        pal=dict(body=(196, 22, 32), dark=(140, 12, 20), light=(226, 52, 58), bevel=(214, 40, 46), zocalo=(120, 10, 18), zocalo_l=(160, 20, 28), push=(170, 16, 26), panel=None),
        fg=(255, 255, 255), acc=(255, 204, 0), acc_fg=(25, 25, 25), card=(255, 255, 255), card_fg=(30, 30, 34), num=(196, 22, 32), sub=(255, 225, 225)),
    "b_negro": dict(nombre="B · Negro con rojo",
        pal=dict(body=(30, 30, 34), dark=(12, 12, 14), light=(70, 70, 76), bevel=(196, 22, 32), zocalo=(10, 10, 12), zocalo_l=(45, 45, 50), push=(18, 18, 20), panel=None),
        fg=(255, 255, 255), acc=(214, 30, 40), acc_fg=(255, 255, 255), card=(255, 255, 255), card_fg=(30, 30, 34), num=(214, 30, 40), sub=(190, 190, 196)),
    "c_bicolor": dict(nombre="C · Rojo y negro",
        pal=dict(body=(196, 22, 32), dark=(140, 12, 20), light=(226, 52, 58), bevel=(214, 40, 46), zocalo=(10, 10, 12), zocalo_l=(45, 45, 50), push=(170, 16, 26), panel=(30, 30, 34)),
        fg=(255, 255, 255), acc=(255, 204, 0), acc_fg=(25, 25, 25), card=(255, 255, 255), card_fg=(30, 30, 34), num=(196, 22, 32), sub=(255, 225, 225)),
}


def centro(d, xy, txt, f, fill):
    d.text(xy, txt, font=f, fill=fill, anchor="mm")


def flecha_abajo(d, cx, cy, s, fill):
    d.polygon([(cx - s, cy - s * 0.4), (cx + s, cy - s * 0.4), (cx, cy + s * 0.7)], fill=fill)
    d.rectangle((cx - s * 0.35, cy - s * 1.3, cx + s * 0.35, cy - s * 0.38), fill=fill)


def icono_qr(d, x, y, s, fill, bg):
    d.rounded_rectangle((x, y, x + s, y + s), s * 0.12, fill=fill)
    q = s * 0.36
    for (ox, oy) in [(0.1, 0.1), (0.54, 0.1), (0.1, 0.54)]:
        d.rectangle((x + s * ox, y + s * oy, x + s * ox + q, y + s * oy + q), fill=bg)
        d.rectangle((x + s * ox + q * 0.25, y + s * oy + q * 0.25, x + s * ox + q * 0.75, y + s * oy + q * 0.75), fill=fill)
    d.rectangle((x + s * 0.6, y + s * 0.6, x + s * 0.82, y + s * 0.82), fill=bg)


def icono_tarjeta(d, x, y, s, fill, bg):
    d.rounded_rectangle((x, y + s * 0.15, x + s, y + s * 0.85), s * 0.1, fill=fill)
    d.rectangle((x, y + s * 0.3, x + s, y + s * 0.42), fill=bg)
    d.rounded_rectangle((x + s * 0.1, y + s * 0.6, x + s * 0.4, y + s * 0.72), 3, fill=bg)


def icono_billete(d, x, y, s, fill, bg):
    d.rounded_rectangle((x, y + s * 0.2, x + s, y + s * 0.8), s * 0.08, fill=fill)
    d.ellipse((x + s * 0.36, y + s * 0.34, x + s * 0.64, y + s * 0.66), fill=bg)
    centro(d, (x + s * 0.5, y + s * 0.5), "$", fnt("black", int(s * 0.24)), fill)


def ploteo(v):
    C.PAL = v["pal"]; C.DIBUJAR_PUSH = False
    img = C.componer({1, 2, 3, 4, 5, 6}, "tmp", "distribucion.json", guardar=False).convert("RGB")
    d = ImageDraw.Draw(img)
    fg, acc, acc_fg, card, card_fg, num, sub = (v[k] for k in ("fg", "acc", "acc_fg", "card", "card_fg", "num", "sub"))
    gx0, gy0, gx1, gy1 = C.GLASS
    L, R = C.MX0, C.MX0 + C.MW
    P = C.PANEL_X

    # 1) Marca arriba de la vidriera
    by = 150
    d.rounded_rectangle((gx0, by, gx0 + 150, by + 150), 26, fill=fg)
    centro(d, (gx0 + 75, by + 77), "S&G", fnt("black", 54), v["pal"]["body"])
    d.text((gx0 + 180, by + 8), "EXPENDEDORAS", font=fnt("black", 78), fill=fg)
    d.text((gx0 + 184, by + 100), "Snacks, bebidas y comida al paso", font=fnt("sb", 40), fill=sub)

    # 2) Arriba de la pantalla: medios de pago
    px0, px1 = P + 50, R - 50
    centro(d, ((px0 + px1) / 2, 200), "PAGÁ COMO QUIERAS", fnt("xb", 40), fg)
    iw, gap = 120, 80
    xs = (px0 + px1) / 2 - (3 * iw + 2 * gap) / 2
    for i, (ic, lab) in enumerate([(icono_qr, "QR"), (icono_tarjeta, "Tarjeta"), (icono_billete, "Efectivo")]):
        x = xs + i * (iw + gap)
        ic(d, x, 270, iw, fg, v["pal"]["panel"] or v["pal"]["body"])
        centro(d, (x + iw / 2, 430), lab, fnt("b", 34), fg)
    d.rounded_rectangle((px0 + 40, 490, px1 - 40, 580), 45, fill=acc)
    centro(d, ((px0 + px1) / 2, 535), "Elegí en la pantalla  ↓", fnt("xb", 38), acc_fg)

    # 3) Billetero: billetes aceptados y "no da vuelto"
    bx0, byy0, bx1, byy1 = C.BILL
    lx0, lx1 = P + 30, bx0 - 30
    d.text((lx0, byy0 + 10), "BILLETES", font=fnt("xb", 30), fill=fg)
    for i, b in enumerate(["$500", "$1.000", "$2.000", "$10.000", "$20.000"]):
        d.text((lx0, byy0 + 60 + i * 50), b, font=fnt("b", 34), fill=fg)
    d.polygon([(lx1 - 6, byy0 + 150), (lx1 + 18, byy0 + 175), (lx1 - 6, byy0 + 200)], fill=acc)
    rx0, rx1 = bx1 + 30, R - 30
    d.rounded_rectangle((rx0, byy0 + 10, rx1, byy0 + 300), 18, fill=acc)
    for i, t in enumerate(["NO DA", "VUELTO"]):
        centro(d, ((rx0 + rx1) / 2, byy0 + 60 + i * 52), t, fnt("black", 40), acc_fg)
    for i, t in enumerate(["Pagá justo", "o con QR"]):
        centro(d, ((rx0 + rx1) / 2, byy0 + 185 + i * 44), t, fnt("sb", 32), acc_fg)
    # lector de tarjeta
    ny = byy1 + 60 + 75
    d.text((lx0, ny - 40), "Tarjeta", font=fnt("b", 32), fill=fg)
    d.text((lx0, ny), "o celular", font=fnt("b", 32), fill=fg)
    d.text((rx0, ny - 40), "Apoyá", font=fnt("b", 32), fill=fg)
    d.text((rx0, ny), "acá  ←", font=fnt("b", 32), fill=fg)

    # 4) Instrucciones (panel derecho, debajo del lector)
    sx0, sx1, sy0 = P + 45, R - 45, byy1 + 255
    sy1 = C.MY0 + C.MH - 110
    d.rounded_rectangle((sx0, sy0, sx1, sy1), 30, fill=card)
    centro(d, ((sx0 + sx1) / 2, sy0 + 70), "CÓMO COMPRAR", fnt("black", 50), card_fg)
    pasos = [("Elegí tu producto", ["Tocalo en la pantalla.", "¿Más de uno? Al carrito."]),
             ("Tocá «Pagar»", ["Revisá el total."]),
             ("Pagá", ["QR, tarjeta o billetes.", "Billetes: monto justo."]),
             ("Retirá abajo", ["Empujá la tapa."])]
    y = sy0 + 140
    for i, (t, lines) in enumerate(pasos):
        d.ellipse((sx0 + 30, y, sx0 + 110, y + 80), fill=num)
        centro(d, (sx0 + 70, y + 41), str(i + 1), fnt("black", 46), (255, 255, 255))
        d.text((sx0 + 135, y + 2), t, font=fnt("xb", 40), fill=card_fg)
        for j, ln in enumerate(lines):
            d.text((sx0 + 135, y + 56 + j * 38), ln, font=fnt("m", 31), fill=(80, 80, 88))
        y += 90 + len(lines) * 38
    d.line((sx0 + 30, y, sx1 - 30, y), fill=(220, 220, 226), width=3)
    d.text((sx0 + 30, y + 22), "¿No cayó? No pagues de", font=fnt("b", 31), fill=card_fg)
    d.text((sx0 + 30, y + 60), "nuevo: escribinos ↙", font=fnt("b", 31), fill=card_fg)

    # 5) Puerta de retiro
    qx0, qy0, qx1, qy1 = C.PUSH
    d.rounded_rectangle((qx0 - 10, qy0 - 10, qx1 + 10, qy1 + 10), 14, fill=v["pal"]["push"])
    d.rounded_rectangle((qx0, qy0, qx1, qy1), 10, outline=fg, width=8)
    centro(d, ((qx0 + qx1) / 2, qy0 + (qy1 - qy0) * 0.40), "RETIRÁ TU PRODUCTO", fnt("black", 64), fg)
    centro(d, ((qx0 + qx1) / 2, qy0 + (qy1 - qy0) * 0.76), "Empujá la tapa", fnt("sb", 46), sub)
    for k in (-1, 1):
        flecha_abajo(d, (qx0 + qx1) / 2 + k * 560, qy0 + (qy1 - qy0) * 0.55, 46, acc)
    centro(d, ((qx0 + qx1) / 2, qy0 - 70), "Tu compra cae acá abajo", fnt("b", 44), fg)

    # 6) Soporte por WhatsApp + número de máquina + aviso de cámaras
    wy0, wy1 = qy1 + 70, C.MY0 + C.MH - 110
    wx0, wx1 = gx0 - 20, gx1 + 20
    d.rounded_rectangle((wx0, wy0, wx1, wy1), 26, fill=card)
    qr = segno.make(f"https://wa.me/549{WHATSAPP.replace(' ', '').replace('-', '')}", error="m")
    mat = np.array([[0 if c else 255 for c in row] for row in qr.matrix], dtype=np.uint8)
    mat = np.pad(mat, 1, constant_values=255)
    qimg = Image.fromarray(mat).convert("RGB")
    qs = wy1 - wy0 - 40
    qimg = qimg.resize((qs, qs), Image.NEAREST)
    img.paste(qimg, (wx0 + 20, wy0 + 20))
    tx = wx0 + qs + 60
    d.text((tx, wy0 + 26), "¿Problemas con tu compra?", font=fnt("xb", 44), fill=card_fg)
    d.text((tx, wy0 + 90), f"WhatsApp {WHATSAPP}", font=fnt("black", 54), fill=num)
    d.text((tx, wy0 + 160), "Escaneá el QR o escribinos con una foto del ticket o de la pantalla.", font=fnt("m", 30), fill=(80, 80, 88))
    d.rounded_rectangle((wx1 - 290, wy0 + 24, wx1 - 24, wy0 + 120), 16, fill=(30, 30, 34))
    centro(d, (wx1 - 157, wy0 + 52), "MÁQUINA N°", fnt("b", 26), (200, 200, 205))
    centro(d, (wx1 - 157, wy0 + 94), MAQ_N, fnt("black", 44), (255, 255, 255))
    d.ellipse((tx, wy1 - 50, tx + 20, wy1 - 30), fill=(214, 30, 40))
    d.text((tx + 32, wy1 - 58), "Lugar monitoreado por cámaras", font=fnt("sb", 28), fill=(110, 110, 118))
    return img


if __name__ == "__main__":
    out = os.path.join(C.BASE, "salida")
    imgs = []
    for k, v in VERSIONES.items():
        im = ploteo(v)
        im.save(f"{out}/ploteo_{k}.png", optimize=True)
        im.resize((im.width * 1400 // im.height, 1400), Image.LANCZOS).save(f"{out}/ploteo_{k}_liviana.jpg", quality=86)
        imgs.append((v["nombre"], im))
        print(k)
    h = 1500; ws = [im.width * h // im.height for _, im in imgs]
    comp = Image.new("RGB", (sum(ws) + 60 * (len(imgs) + 1), h + 160), (244, 245, 247))
    dc = ImageDraw.Draw(comp); x = 60
    for (n, im), w in zip(imgs, ws):
        comp.paste(im.resize((w, h), Image.LANCZOS), (x, 120))
        dc.text((x + w / 2, 60), n, font=fnt("xb", 52), fill=(30, 30, 34), anchor="mm")
        x += w + 60
    comp.save(f"{out}/ploteo_comparativa.jpg", quality=86)
