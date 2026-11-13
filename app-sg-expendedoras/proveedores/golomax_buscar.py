"""Busca artículos en el catálogo público de Golomax y devuelve precio unitario final.
Uso: python3 golomax_buscar.py consultas.json salida.json   (consultas.json = {"clave": "texto a buscar", ...})"""
import json, re, sys, time, urllib.parse, requests
BASE = "https://www.golomax.com.ar"
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0"
def token():
    h = s.get(BASE + "/catalogo/buscar?search_text=alfajor", timeout=30).text
    return re.search(r'csrf-token" content="([^"]+)', h).group(1)
TOK = None
def buscar(q, n=24):
    global TOK
    TOK = TOK or token()
    slug = urllib.parse.quote(q)
    body = {"order": "relevancia", "filters": {"search_text": q, "refresh_filters": True, "is_search": True}, "offset": n, "page": 1}
    r = s.post(f"{BASE}/catalogo/buscar/{slug}/filtros", json=body, timeout=30,
               headers={"X-Requested-With": "XMLHttpRequest", "X-CSRF-TOKEN": TOK, "Accept": "application/json"})
    arts = (((r.json().get("data") or {}).get("items") or {}).get("articles")) or []
    return [{"codigo": a.get("Codigo"), "nombre": a.get("Nombre"), "precioUnit": round(a.get("PrecioFinalUnitario") or 0, 2),
             "precioSinPromo": round(a.get("PrecioSinDescUnitario") or 0, 2), "promo": bool(a.get("EnPromocion")),
             "unidadesBulto": a.get("UnidadNivel2"), "ean": a.get("CodigoBarrasFacturacionElectronica"),
             "porCantidad": a.get("PreciosPorCantidad") or [], "stock": a.get("StockDisponible"),
             "url": a.get("UrlDetalle"), "img": a.get("Imagen"), "cps": a.get("CantidadPrecioSugerido"), "precioItem": round(a.get("PrecioFinal") or 0, 2)} for a in arts]
if __name__ == "__main__":
    qs = json.load(open(sys.argv[1])); out = {}
    for k, q in qs.items():
        try: out[k] = {"q": q, "res": buscar(q)}
        except Exception as e: out[k] = {"q": q, "error": str(e)}
        time.sleep(0.4)
    json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
