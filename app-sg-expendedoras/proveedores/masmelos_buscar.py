import json, sys, time, subprocess, urllib.parse, http.cookiejar, urllib.request
B = "https://secure.sig2k.com/webs/bWFzbWVsb3NAc2lnbWEtYXI.defaultKart/sigkart/3.1/"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "Mozilla/5.0")]
op.open(B, timeout=30).read()
def buscar(q, rows=40):
    data = urllib.parse.urlencode({"txtbuscar": q, "catego": "", "chkcatego": "false", "orden": "", "ver": "", "nocache": "", "rows": rows, "skip": 0}).encode()
    r = op.open(B + "swexecute.php?sql=articulos", data=data, timeout=30).read()
    try: return json.loads(r)
    except Exception: return []
if __name__ == "__main__":
    qs = json.load(open(sys.argv[1])); out = {}
    for q in qs:
        out[q] = [{k: it.get(k) for k in ("ITEMID","TITULO","SUBTIT","CATTXT","PRBASE","STOCK","FOTOID","VERIMG","SUBPRE")} for it in buscar(q)]
        time.sleep(0.4)
    json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=0)
