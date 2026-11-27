"""Ploteo gris oscuro del sanatorio volcado sobre el esquema del importador (lateral izq · frente · lateral der).

Medidas tomadas del esquema que mandó el importador (coordenadas de la franja gris, 1220 x 647 px)
y escaladas S veces. Las posiciones de pantalla, lector, billetero, ranura y puerta PUSH son las del
esquema: el diseño se adapta a ellas.
Uso: python3 scripts/esquema_importador.py  ->  salida/esquema_importador.png (+ _liviana.jpg)
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESQ = os.environ.get("ESQ", "")            # PNG de la franja del esquema (captura del importador)
F = "/usr/share/fonts/opentype/inter/"
def fnt(w, s): return ImageFont.truetype(F + {"black": "Inter-Black.otf", "xb": "Inter-ExtraBold.otf", "b": "Inter-Bold.otf", "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf"}[w], int(s))

S = 7
ROJO, BLANCO, GRIS_T = (214, 30, 40), (255, 255, 255), (185, 187, 194)
BODY, CAJA, L2, DARK = (66, 68, 74), (24, 25, 28), (150, 152, 160), (34, 35, 39)
WHATSAPP, MAQ_N = "11 2160-0427", os.environ.get("MAQ_N", "001")

# --- geometría del esquema (px de la franja) ---
FRENTE = (403, 70, 755, 568); ZOC = (403, 568, 755, 576)
LAT_IZQ = (41, 70, 264, 576); LAT_DER = (921, 70, 1145, 576)
VIDRIO = (419, 84, 633, 395); COSTURA = 652.5
PANTALLA = (671, 133.5, 741, 255)
LECTOR = (667.5, 296.5, 688.5, 324); BILLETERO = (712.5, 296, 736.5, 324)
RANURA = (692.5, 492.5, 718.5, 514); PUSH = (460, 435, 596.5, 480)


def s(*v): return [round(x * S) for x in v]


def centro(d, xy, t, f, c): d.text(xy, t, font=f, fill=c, anchor="mm")


def diagonales(d, x0, y0, n, largo, sep, ancho, colores):
    for i in range(n):
        d.line((x0 + i * sep, y0, x0 + i * sep + largo, y0 - largo), fill=colores[i % len(colores)], width=ancho)


def main():
    fondo = Image.open(ESQ).convert("RGB") if ESQ else Image.new("RGB", (1220, 647), (100, 100, 100))
    W, H = fondo.width * S, fondo.height * S
    img = fondo.resize((W, H), Image.LANCZOS)          # ruedas, patas y fondo gris del esquema
    d = ImageDraw.Draw(img)

    # ---------- laterales ----------
    for x0, y0, x1, y1 in (LAT_IZQ, LAT_DER):
        X0, Y0, X1, Y1 = s(x0, y0, x1, y1)
        d.rectangle((X0, Y0, X1, Y1), fill=BODY, outline=(20, 20, 22), width=6)
        d.line((X0 + 90, Y0 + 120, X0 + 90, Y1 - 260), fill=ROJO, width=14)
        diagonales(d, X1 - 560, Y1 - 120, 5, 120, 100, 18, [ROJO, L2])
    # cerradura/bisagra del lateral derecho (como en el esquema)
    d.rounded_rectangle(s(1136, 278, 1144, 300), 6, fill=(30, 30, 32), outline=L2, width=3)

    # ---------- frente ----------
    fx0, fy0, fx1, fy1 = s(*FRENTE)
    d.rectangle((fx0, fy0, fx1, fy1), fill=BODY, outline=(20, 20, 22), width=6)
    d.rectangle(s(*ZOC), fill=(28, 29, 32))
    d.line((s(COSTURA)[0], fy0, s(COSTURA)[0], fy1), fill=DARK, width=8)

    # vidrio (no se plotea) con marco rojo y diagonales arriba
    vx0, vy0, vx1, vy1 = s(*VIDRIO)
    d.rectangle((vx0 - 26, vy0 - 26, vx1 + 26, vy1 + 26), fill=ROJO)
    vid = os.path.join(os.path.dirname(ESQ) if ESQ else BASE, "vidrio.png")
    if os.path.exists(vid):
        img.paste(Image.open(vid).convert("RGB").resize((vx1 - vx0, vy1 - vy0), Image.LANCZOS), (vx0, vy0))
    else:
        d.rectangle((vx0, vy0, vx1, vy1), fill=(222, 246, 255))
    diagonales(d, vx0 + 40, fy0 + 82, 6, 60, 60, 9, [ROJO, L2])
    d.line((vx0 + 470, fy0 + 40, vx1, fy0 + 40), fill=ROJO, width=5)
    d.line((s(653)[0] - 60, fy0 + 70, s(653)[0] - 60, fy1 - 90), fill=DARK, width=2)
    # cerradura de la puerta (como en el esquema)
    d.rounded_rectangle(s(643.5, 302, 652, 325), 6, fill=(30, 30, 32), outline=L2, width=3)

    # PUSH -> Retirá tu producto
    px0, py0, px1, py1 = s(*PUSH)
    d.rounded_rectangle((px0 - 12, py0 - 12, px1 + 12, py1 + 12), 14, fill=(44, 45, 50))
    d.rounded_rectangle((px0, py0, px1, py1), 10, outline=BLANCO, width=8)
    centro(d, ((px0 + px1) / 2, py0 + (py1 - py0) * 0.40), "RETIRÁ TU PRODUCTO", fnt("black", 70), BLANCO)
    centro(d, ((px0 + px1) / 2, py0 + (py1 - py0) * 0.76), "Empujá la tapa", fnt("sb", 48), GRIS_T)

    # WhatsApp + N° de máquina
    wx0, wy0, wx1, wy1 = s(424, 494, 630, 556)
    d.rounded_rectangle((wx0, wy0, wx1, wy1), 26, fill=CAJA, outline=L2, width=4)
    d.rectangle((wx0 + 4, wy0 + 34, wx0 + 16, wy1 - 34), fill=ROJO)
    d.text((wx0 + 60, wy0 + 52), "¿Problemas con tu compra?", font=fnt("xb", 50), fill=BLANCO)
    d.text((wx0 + 60, wy0 + 140), f"WhatsApp {WHATSAPP}", font=fnt("black", 72), fill=ROJO)
    d.rounded_rectangle((wx1 - 300, wy0 + 70, wx1 - 40, wy1 - 70), 18, outline=L2, width=4)
    centro(d, (wx1 - 170, (wy0 + wy1) / 2 - 30), "MÁQUINA N°", fnt("b", 30), GRIS_T)
    centro(d, (wx1 - 170, (wy0 + wy1) / 2 + 26), MAQ_N, fnt("black", 60), BLANCO)

    # ---------- panel derecho ----------
    rx0, rx1 = s(655)[0], fx1 - 30
    # Elegí en la pantalla (sobre la pantalla del esquema)
    sx0, sy0, sx1, sy1 = s(*PANTALLA)
    cx = (sx0 + sx1) / 2
    ey1 = sy0 - 70; ey0 = ey1 - 110
    d.rounded_rectangle((sx0 - 20, ey0, sx1 + 20, ey1), 55, fill=ROJO)
    d.polygon([(cx - 30, ey1 - 2), (cx + 30, ey1 - 2), (cx, ey1 + 34)], fill=ROJO)
    centro(d, (cx, (ey0 + ey1) / 2), "Elegí en la pantalla", fnt("xb", 50), BLANCO)
    # pantalla: marco + contenido del diseño
    d.rounded_rectangle((sx0 - 24, sy0 - 24, sx1 + 24, sy1 + 24), 18, fill=(16, 16, 18))
    pan = os.path.join(os.path.dirname(ESQ) if ESQ else BASE, "pantalla.png")
    if os.path.exists(pan):
        img.paste(Image.open(pan).convert("RGB").resize((sx1 - sx0, sy1 - sy0), Image.LANCZOS), (sx0, sy0))
    else:
        d.rectangle((sx0, sy0, sx1, sy1), fill=(240, 242, 245))

    # No da vuelto (entre pantalla y lectores)
    ny0, ny1 = sy1 + 70, s(290)[0]
    d.rounded_rectangle((rx0 + 20, ny0, rx1 - 10, ny1), 18, outline=ROJO, width=5)
    centro(d, ((rx0 + rx1) / 2 + 5, ny0 + (ny1 - ny0) * 0.36), "NO DA VUELTO", fnt("black", 46), BLANCO)
    centro(d, ((rx0 + rx1) / 2 + 5, ny0 + (ny1 - ny0) * 0.72), "Pagá el monto justo", fnt("sb", 32), GRIS_T)

    # lector y billetero (hardware del esquema)
    for box, etq in ((LECTOR, ""), (BILLETERO, "BILLETES")):
        bx0, by0, bx1, by1 = s(*box)
        d.rounded_rectangle((bx0, by0, bx1, by1), 10, fill=(12, 12, 14), outline=L2, width=4)
        d.rectangle((bx0 + 18, by0 + 26, bx1 - 18, by0 + 46), fill=(50, 50, 54))
        centro(d, ((bx0 + bx1) / 2, by1 + 34), etq, fnt("xb", 28), (255, 204, 0) if etq == "BILLETES" else GRIS_T)
    # billetes aceptados
    by = s(330)[0] + 30
    d.text((rx0 + 24, by), "BILLETES ACEPTADOS", font=fnt("xb", 30), fill=BLANCO)
    for i, b in enumerate(["$500", "$1.000", "$2.000", "$10.000", "$20.000"]):
        col, fila = divmod(i, 3)
        d.text((rx0 + 24 + col * 250, by + 52 + fila * 46), b, font=fnt("b", 34), fill=GRIS_T)

    # Cómo comprar
    cx0, cy0, cx1, cy1 = rx0 + 14, by + 210, rx1 - 4, s(484)[0]
    d.rounded_rectangle((cx0, cy0, cx1, cy1), 24, fill=CAJA, outline=L2, width=3)
    d.text((cx0 + 30, cy0 + 26), "CÓMO COMPRAR", font=fnt("black", 46), fill=BLANCO)
    d.line((cx0 + 30, cy0 + 92, cx0 + 180, cy0 + 92), fill=ROJO, width=7)
    pasos = [(["Elegí tu producto"], ["¿Más de uno? Al carrito."]), (["Tocá «Comprar ahora»"], []),
             (["Seleccioná QR", "o Efectivo"], []), (["Pagá"], []), (["Retirá abajo"], [])]
    y, alto_total = cy0 + 124, cy1 - (cy0 + 124) - 26
    hs = [44 * len(t) + 34 * len(sb) for t, sb in pasos]
    gap = (alto_total - sum(max(66, h) for h in hs)) / (len(pasos) - 1)
    for i, (tit, sub) in enumerate(pasos):
        h = max(66, hs[i])
        d.ellipse((cx0 + 28, y, cx0 + 94, y + 66), fill=ROJO)
        centro(d, (cx0 + 61, y + 34), str(i + 1), fnt("black", 40), BLANCO)
        ty = y + (12 if len(tit) == 1 and not sub else 0)
        for j, ln in enumerate(tit):
            d.text((cx0 + 116, ty + j * 44), ln, font=fnt("xb", 36), fill=BLANCO)
        for j, ln in enumerate(sub):
            d.text((cx0 + 116, ty + len(tit) * 44 + 2 + j * 34), ln, font=fnt("m", 27), fill=GRIS_T)
        if i < len(pasos) - 1:
            ym = (y + 66 + y + h + gap) / 2
            for k in range(4):
                yy = ym + (k - 1.5) * 15
                d.ellipse((cx0 + 57, yy - 4, cx0 + 65, yy + 4), fill=BLANCO)
        y += h + gap

    # ranura inferior del esquema (devolución) + diagonales
    rx0_, ry0, rx1_, ry1 = s(*RANURA)
    d.rounded_rectangle((rx0_, ry0, rx1_, ry1), 8, fill=(12, 12, 14), outline=L2, width=3)
    d.line((rx0_ + 20, (ry0 + ry1) / 2, rx1_ - 20, (ry0 + ry1) / 2), fill=(60, 60, 64), width=8)
    diagonales(d, rx0 + 40, fy1 - 60, 5, 46, 62, 9, [ROJO, L2])

    # rótulos
    for (x0, _, x1, _), t in ((LAT_IZQ, "LATERAL IZQUIERDO"), (FRENTE, "FRENTE"), (LAT_DER, "LATERAL DERECHO")):
        centro(d, (s((x0 + x1) / 2)[0], s(40)[0]), t, fnt("xb", 70), (235, 235, 238))
    out = os.path.join(BASE, "salida", "esquema_importador" + ("" if MAQ_N == "001" else "_maq" + MAQ_N))
    img.save(out + ".png", optimize=True)
    img.resize((W // 3, H // 3), Image.LANCZOS).save(out + "_liviana.jpg", quality=88)
    img.crop((fx0 - 200, 0, fx1 + 200, H)).save(out + "_frente.png", optimize=True)
    print(out, img.size)


if __name__ == "__main__":
    main()
