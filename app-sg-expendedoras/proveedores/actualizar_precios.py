"""Actualización diaria de precios de proveedores para la app S&G Expendedoras.

Lee los precios de hoy de Masmelos, Golomax, Distribuidora OKs y Distribuidora Pop para los
productos de mapeo.json, los compara con lo que tiene la app y arma los cambios a escribir.

Uso:
  python3 actualizar_precios.py <carpeta_dump_productos> <salida_dir>

  <carpeta_dump_productos>: carpeta con un JSON por producto, tal como la deja
  ArtifactData list con out_dir (…/productos/<id>.json).
  <salida_dir>: acá deja
    - cambios/<id>.json  -> datos para un ArtifactData update de ese producto (merge)
    - resumen.json       -> lista de cambios, errores y productos no encontrados
    - resumen.md         -> el mismo resumen legible
No escribe nada en la app: eso lo hace quien corre el script, con los archivos de cambios/.
"""
import json, os, re, sys, time, glob, datetime, urllib.parse, http.cookiejar, urllib.request
import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
HOY = datetime.date.today().isoformat()
UA = {"User-Agent": "Mozilla/5.0"}
TOL = 0.005  # cambios menores a 0,5% se ignoran

# ---------- Masmelos ----------
MB = "https://secure.sig2k.com/webs/bWFzbWVsb3NAc2lnbWEtYXI.defaultKart/sigkart/3.1/"
_mop = None
def masmelos_buscar(q):
    global _mop
    if _mop is None:
        _mop = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        _mop.addheaders = [("User-Agent", "Mozilla/5.0")]
        _mop.open(MB, timeout=30).read()
    data = urllib.parse.urlencode({"txtbuscar": q, "catego": "", "chkcatego": "false", "orden": "", "ver": "", "nocache": "", "rows": 40, "skip": 0}).encode()
    try: return json.loads(_mop.open(MB + "swexecute.php?sql=articulos", data=data, timeout=30).read())
    except Exception: return []
def precio_masmelos(m):
    norm = lambda s: re.sub(r"\s+", " ", (s or "").strip().upper())
    for q in (m["titulo"], " ".join(m["titulo"].split()[:3])):
        for it in masmelos_buscar(q):
            if norm(it.get("TITULO")) == norm(m["titulo"]) or (m.get("codigo") and it.get("SUBTIT") == m["codigo"]):
                if it.get("PRBASE") is None: return None, "sin precio"
                return {"precioBulto": round(float(it["PRBASE"]), 2), "unidadesBulto": m["unidades"], "stock": it.get("STOCK") == "S"}, None
        time.sleep(0.3)
    return None, "no encontrado"

# ---------- Golomax ----------
GB = "https://www.golomax.com.ar"
_gs, _gtok = None, None
def golomax_buscar(q):
    global _gs, _gtok
    if _gs is None:
        _gs = requests.Session(); _gs.headers.update(UA)
        h = _gs.get(GB + "/catalogo/buscar?search_text=alfajor", timeout=30).text
        _gtok = re.search(r'csrf-token" content="([^"]+)', h).group(1)
    body = {"order": "relevancia", "filters": {"search_text": q, "refresh_filters": True, "is_search": True}, "offset": 48, "page": 1}
    r = _gs.post(f"{GB}/catalogo/buscar/{urllib.parse.quote(q)}/filtros", json=body, timeout=30,
                 headers={"X-Requested-With": "XMLHttpRequest", "X-CSRF-TOKEN": _gtok, "Accept": "application/json"})
    return (((r.json().get("data") or {}).get("items") or {}).get("articles")) or []
def consultas_golomax(nombre):
    pal = nombre.replace("'", " ").split(); qs = []
    i = next((k for k, w in enumerate(pal) if len(w) > 1 and w.isupper()), None)
    if i is not None:
        resto = [w for w in pal[i:] if not re.match(r"^\d|^x\d|^\d+u\.?$", w, re.I)]
        qs += [" ".join(resto[:3]), " ".join(resto[:2]), resto[0]]
    qs += [" ".join(pal[:3]), nombre]
    out = []
    for q in qs:
        if q and q not in out: out.append(q)
    return out
def precio_golomax(m):
    for q in consultas_golomax(m["nombre"]):
        for a in golomax_buscar(q):
            if str(a.get("Codigo")) == str(m["codigo"]):
                unit = a.get("PrecioFinalUnitario")
                if not unit: return None, "sin precio"
                d = m.get("divisor", 1)
                return {"precioBulto": round(unit, 2), "unidadesBulto": d, "promo": bool(a.get("EnPromocion")), "stock": (a.get("StockDisponible") or 0) > 0}, None
        time.sleep(0.3)
    return None, "no encontrado"

# ---------- WooCommerce (Distribuidora OKs y Pop) ----------
WOO = {"distrioks": "https://distrioks.com.ar", "pop": "https://www.distribuidorapop.com.ar"}
def precio_woo(prov, m):
    try:
        r = requests.get(f"{WOO[prov]}/wp-json/wc/store/v1/products/{m['id']}", headers=UA, timeout=60)
        if r.status_code == 404: return None, "no encontrado"
        a = r.json(); p = a["prices"]; v = int(p["price"]) / 10 ** p.get("currency_minor_unit", 2)
        if not v: return None, "sin precio"
        return {"precioBulto": round(v, 2), "unidadesBulto": m["unidades"], "stock": bool(a.get("is_in_stock"))}, None
    except Exception as e:
        return None, "error: " + str(e)[:80]

# Masmelos NO se actualiza solo: la web sin iniciar sesión muestra precios distintos (≈5% más caros)
# a los que ve el cliente con su cuenta. Sus precios se cargan a mano. precio_masmelos queda para uso manual.
FUENTES = {"golomax": precio_golomax,
           "distrioks": lambda m: precio_woo("distrioks", m), "pop": lambda m: precio_woo("pop", m)}

def main(dump, out):
    mapeo = json.load(open(os.path.join(AQUI, "mapeo.json")))
    actuales = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(os.path.join(dump, "*.json"))}
    os.makedirs(os.path.join(out, "cambios"), exist_ok=True)
    cambios, errores, sin_cambio = [], [], 0
    for pid, m in mapeo.items():
        p = actuales.get(pid)
        if p is None: continue  # producto borrado de la app
        provs = p.get("proveedores") or {}
        upd = {}; costos = list(p.get("costos") or [])
        for prov, fn in FUENTES.items():
            if prov not in m: continue
            nuevo, err = fn(m[prov])
            if err: errores.append({"pid": pid, "nombre": p.get("nombre"), "proveedor": prov, "error": err}); continue
            nuevo["costoUnit"] = round(nuevo["precioBulto"] / (nuevo["unidadesBulto"] or 1), 2)
            ant = provs.get(prov) or {}
            old = ant.get("costoUnit")
            if old and abs(nuevo["costoUnit"] - old) / old < TOL:
                sin_cambio += 1
                if ant.get("fecha") != HOY: upd.setdefault("proveedores", {})[prov] = {"fecha": HOY, "verificado": HOY}
                continue
            entrada = {"precioBulto": nuevo["precioBulto"], "unidadesBulto": nuevo["unidadesBulto"], "costoUnit": nuevo["costoUnit"], "fecha": HOY}
            if "promo" in nuevo: entrada["promo"] = nuevo["promo"]
            if nuevo.get("stock") is False: entrada["sinStock"] = True
            upd.setdefault("proveedores", {})[prov] = entrada
            costos.append({"fecha": HOY, "proveedorId": prov, "precioBulto": entrada["precioBulto"], "unidadesBulto": entrada["unidadesBulto"], "costoUnit": entrada["costoUnit"]})
            cambios.append({"pid": pid, "nombre": p.get("nombre"), "proveedor": prov, "antes": old, "ahora": nuevo["costoUnit"],
                            "variacion": round((nuevo["costoUnit"] / old - 1) * 100, 1) if old else None})
        if upd:
            if len(costos) != len(p.get("costos") or []): upd["costos"] = costos[-60:]
            json.dump(upd, open(os.path.join(out, "cambios", pid + ".json"), "w"), ensure_ascii=False)
    res = {"fecha": HOY, "cambios": cambios, "errores": errores, "sin_cambio": sin_cambio,
           "productos_a_actualizar": sorted(f[:-5] for f in os.listdir(os.path.join(out, "cambios")))}
    json.dump(res, open(os.path.join(out, "resumen.json"), "w"), ensure_ascii=False, indent=1)
    md = [f"# Precios de proveedores · {HOY}", "", f"Cambios: {len(cambios)} · sin cambio: {sin_cambio} · errores: {len(errores)}", ""]
    if cambios:
        md += ["| Producto | Proveedor | Antes | Ahora | Var. |", "|---|---|---:|---:|---:|"]
        for c in sorted(cambios, key=lambda c: -(abs(c["variacion"] or 0))):
            md.append(f"| {c['nombre']} | {c['proveedor']} | {c['antes'] or '—'} | {c['ahora']} | {'' if c['variacion'] is None else ('%+.1f%%' % c['variacion'])} |")
    if errores:
        md += ["", "## No se pudo leer", ""] + [f"- {e['nombre']} · {e['proveedor']}: {e['error']}" for e in errores]
    open(os.path.join(out, "resumen.md"), "w").write("\n".join(md) + "\n")
    print(json.dumps({"cambios": len(cambios), "errores": len(errores), "sin_cambio": sin_cambio, "a_actualizar": len(res["productos_a_actualizar"])}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
