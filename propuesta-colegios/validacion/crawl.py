import sys,re,json,subprocess,urllib.parse
def get(u):
    try:
        r=subprocess.run(['curl','-sL','--max-time','15','-A','Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120','-w','\n__URL__%{url_effective}',u],capture_output=True,timeout=25)
        t=r.stdout.decode('utf-8','ignore'); i=t.rfind('\n__URL__'); return t[:i],t[i+8:]
    except Exception: return '',u
def cf(h):
    k=int(h[:2],16); return ''.join(chr(int(h[i:i+2],16)^k) for i in range(2,len(h),2))
def emails(t):
    t2=t.replace('&#64;','@').replace('[at]','@').replace('(at)','@').replace('%40','@')
    s=set(e.lower().strip('.') for e in re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',t2))
    s|={cf(h).lower() for h in re.findall(r'data-cfemail="([0-9a-f]+)"',t)}
    return {e for e in s if not re.search(r'\.(png|jpe?g|webp|svg|gif|css|js)$|sentry|wixpress|example|ejemplo|lab6|typemade|@2x|godaddy|domain\.com',e)}
KW=re.compile(r'contact|nivel|secundari|primari|inicial|institu|nosotros|admisi|inscrip|superior|terciari|escuela|informes',re.I)
out={}
for d in sys.argv[1:]:
    seen=set(); found={}
    html,base=get('https://'+d)
    if not html.strip(): html,base=get('http://www.'+d)
    pages=[(base,html)]
    host=urllib.parse.urlparse(base).netloc
    links=set()
    for h in re.findall(r'href=["\']([^"\'#]+)',html):
        u=urllib.parse.urljoin(base,h); p=urllib.parse.urlparse(u)
        if p.netloc==host and KW.search(p.path) and not re.search(r'\.(pdf|jpg|png|zip|docx?)$',p.path,re.I): links.add(u.split('?')[0])
    for u in sorted(links)[:20]:
        pages.append((u,get(u)[0]))
    for u,t in pages:
        for e in emails(t): found.setdefault(e,u)
    out[d]={'base':base,'emails':found}
    print(d,base,json.dumps(found,ensure_ascii=False),flush=True)
json.dump(out,open(sys.argv[0].replace('crawl.py','crawl_%s.json'%abs(hash(' '.join(sys.argv[1:])))) ,'w'),ensure_ascii=False)
