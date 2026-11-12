"""Busca productos en tiendas VTEX argentinas y lista candidatos (nombre, tienda, URL de imagen)."""
import json, sys, urllib.parse, requests
STORES = {
    "carrefour": "www.carrefour.com.ar",
    "jumbo": "www.jumbo.com.ar",
    "dia": "diaonline.supermercadosdia.com.ar",
    "vea": "www.vea.com.ar",
}
def search(q, n=8):
    out = []
    for name, host in STORES.items():
        url = f"https://{host}/api/catalog_system/pub/products/search?ft={urllib.parse.quote(q)}&_from=0&_to={n-1}"
        try:
            for p in requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).json():
                it = p["items"][0]
                out.append({"store": name, "name": p["productName"], "link": p.get("link"),
                            "img": it["images"][0]["imageUrl"].split("?")[0],
                            "imgs": [i["imageUrl"].split("?")[0] for i in it["images"]]})
        except Exception as e:
            out.append({"store": name, "error": str(e)})
    return out
if __name__ == "__main__":
    queries = json.load(open(sys.argv[1]))
    res = {q: search(q) for q in queries}
    json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
