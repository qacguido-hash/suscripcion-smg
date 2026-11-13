"""Baja el catálogo completo de Distribuidora OKs (WooCommerce Store API) a JSON.
Uso: python3 distrioks_catalogo.py salida.json"""
import json, sys, time, requests
URL = "https://distrioks.com.ar/wp-json/wc/store/v1/products"
out, page = [], 1
while True:
    r = requests.get(URL, params={"per_page": 100, "page": page}, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    items = r.json()
    if not items: break
    for a in items:
        p = a["prices"]; div = 10 ** p.get("currency_minor_unit", 2)
        out.append({"id": a["id"], "sku": a.get("sku"), "nombre": a["name"], "precio": int(p["price"]) / div,
                    "regular": int(p["regular_price"]) / div, "stock": a.get("is_in_stock"), "url": a.get("permalink"),
                    "cats": [c["name"] for c in a.get("categories", [])], "img": (a.get("images") or [{}])[0].get("src")})
    if page >= int(r.headers.get("X-WP-TotalPages", page)): break
    page += 1; time.sleep(0.3)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print(len(out), "productos")
