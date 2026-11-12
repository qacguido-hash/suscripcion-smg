"""Descarga la foto de cada producto elegido (scripts/seleccion.json) a productos_raw/ y registra la fuente."""
import json, glob, os, requests, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
idx = {}
for f in sorted(glob.glob(f"{BASE}/scripts/candidatos*.json")):
    for l in json.load(open(f)).values():
        for c in l:
            if "name" in c: idx.setdefault((c["store"], c["name"]), c)
sel = json.load(open(f"{BASE}/scripts/seleccion.json"))
fuentes = {}
for slug, label, store, name, i in sel:
    if store == "web":
        url, page = name, name
    else:
        c = idx.get((store, name))
        if not c: print("NO ENCONTRADO", slug, name); continue
        url, page = c["imgs"][i], c["link"]
    if not url: print("SIN URL", slug); continue
    out = f"{BASE}/productos_raw/{slug}.img"
    if not os.path.exists(out) or slug in sys.argv[1:]:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"}); r.raise_for_status()
        open(out, "wb").write(r.content)
    fuentes[slug] = {"producto": label, "tienda": store, "nombre_en_tienda": name if store != "web" else "", "imagen": url, "pagina": page}
json.dump(fuentes, open(f"{BASE}/scripts/fuentes.json", "w"), ensure_ascii=False, indent=1)
print(len(fuentes), "descargados")
