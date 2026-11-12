"""Genera FUENTES.md: canal por canal, foto usada, sitio de origen y escala aplicada."""
import json, os, sys
# uso: informe.py [distribucion.json escalas_completa.json FUENTES.md]
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST, ESC, OUT = (sys.argv[1:4] if len(sys.argv) > 3 else ("distribucion.json", "escalas_completa.json", "FUENTES.md"))
f = json.load(open(f"{BASE}/scripts/fuentes.json"))
e = json.load(open(f"{BASE}/salida/{ESC}"))
cfg = json.load(open(f"{BASE}/scripts/{DIST}"))
host = {"carrefour": "Carrefour Argentina", "jumbo": "Jumbo", "dia": "Día Online", "vea": "Vea"}
L = ["# Fuentes de las fotos y diferencias con la lista", "",
     f"Todas las fotos son del envase real argentino. Escala base: {e['px_por_cm']} px por cm "
     "(canal de unos 7 cm de ancho; 14 cm en el estante 6).", "",
     "| Canal | Producto | Foto usada | Sitio | Escala |", "|---|---|---|---|---|"]
for est in sorted(cfg["estantes"], key=lambda x: -x["n"]):
    for i, c in enumerate(est["canales"]):
        k = c["slug"]; v = f[k]; sc = e["productos"][k]
        site = host.get(v["tienda"], v["imagen"].split("/")[2])
        link = v["pagina"] if str(v["pagina"]).startswith("http") else v["imagen"]
        L.append(f"| {'ABCDEF'[6 - est['n']]}{i + 1} (estante {est['n']}) | {v['producto']} | "
                 f"{v['nombre_en_tienda'] or 'ver enlace'} | [{site}]({link}) | "
                 f"{int(sc['escala_aplicada'] * 100)}%{' · parado' if sc['rotado'] else ''} |")
open(f"{BASE}/{OUT}", "w").write("\n".join(L) + "\n")
