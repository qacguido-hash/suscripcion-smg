import json,re,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
rows=json.load(open('priv.json')); mx=json.load(open('mx.json'))
# correos publicados en cada web (crawl)
web={}
for l in open('crawl1.txt'):
    d,base,js=l.split(' ',2); web[d]=(base,json.loads(js))
web['holmbergschule.edu.ar']=('https://holmbergschule.edu.ar/v4/contacto/',{e:'https://holmbergschule.edu.ar/v4/contacto/' for e in open('holm.txt').read().split()})
web['qhs.com.ar']=('https://qhs.com.ar/',{'info@qhs.com.ar':'https://qhs.com.ar/'})
web['stgeorge.org.ar']=web['stgeorges.edu.ar']
web['cruzroja.org.ar']=('https://www.cruzroja.org.ar/',{'info@cruzroja.org.ar':'https://www.cruzroja.org.ar/'})
NX={'escuelacimdipmcane.com.ar','psicologiasocialquilmes.com.ar','abc.go','gmail.com.ar'}
FREE={'gmail.com','yahoo.com.ar','yahoo.com','hotmail.com','hotmail.com.ar','live.com.ar','outlook.com','outlook.es'}
PERS=set('camilaioszt andnatbel lorena-marini ale15bravo cecliatisera40 sandradelorenzi marianaferreres lauracanterob nancyrosanaibarra marianaaguayo33 almendrapellegrino aliciacanga75 norma_bielli torres_estela_73 mafaco ramosada alejandra.cano62 rubiesvictor nahuel95_ndm lorenagiliberto fabian luciana.mura barbara daniela nferro vpeirano payeras.martin mspinella1 cavera maria.castillo aurorai aurora'.split())
WEBDOWN={'colegioalmafuerte.com.ar','donboscobernal.edu.ar','escueladelencuentro.com.ar','institutolaprovidencia.com.ar','nspsocorro.com.ar','inmaculadaquilmes.com.ar','benitogonzalez.com.ar','sanfelipeobisquil.com.ar','njypater.com','instjosehernandez.com','imabernal.org','cei.edu.ar','colegiodelaltosol.com','sinectis.com.ar','isip.edu.ar','psicologiasocialhoy.com.ar','belgranovigil.com.ar','innova.net.ar','proyeccionxxi.com.ar','sagradoquilmes.edu.ar','sjobrero.com.ar','ibq.edu.ar','nes.edu.ar','irabernal.edu.ar','institutoenricofermi.edu.ar','qhs.com.ar'}
def lvl_pick(cands,niv):
    k={'Secundario':'secund|second|college','Primario':'primari|primary|prep','Terciario':'terciar|superior|magist','Inicial':'inicial|kinder'}
    for n in niv.split(', ')[::-1]:
        for e in cands:
            if re.search(k.get(n,'zz'),e): return e
    for e in cands:
        if re.match(r'(info|consultas|institucional|informes|infoquilmes|secretaria|administracion)@',e): return e
    return None
def check(e):
    user,dom=e.split('@'); dom=dom.lower()
    if dom=='abc.go': return 'Corregido','dpp0851747@abc.gob.ar','Dirección truncada en el padrón ("abc.go"); se completa con abc.gob.ar.'
    if dom=='abc.gov.ar': return 'Corregido',user+'@abc.gob.ar','Dominio viejo abc.gov.ar; el oficial de la DGCyE es abc.gob.ar (es la casilla oficial del establecimiento).'
    if dom=='gmail.com.ar': return 'Corregido (probable)',user+'@gmail.com','gmail.com.ar no existe (no recibe correo); casi seguro es @gmail.com.'
    if dom in NX: return 'Inválido','', 'El dominio no existe: el correo rebota.'
    if dom=='abc.gob.ar':
        if user in PERS: return 'Personal',e,'Casilla abc.gob.ar a nombre de un docente o directivo.'
        return 'Válido (oficial DGCyE)',e,'Casilla oficial del establecimiento en abc.gob.ar.'
    if dom in FREE:
        if user in PERS: return 'Personal',e,'Cuenta gratuita a nombre de una persona; puede estar desactualizada.'
        return 'Sin confirmar',e,'Cuenta gratuita ('+dom+'): el dominio recibe correo, pero no figura en una web del colegio.'
    if not mx.get(dom): return 'Inválido','','El dominio no tiene servidor de correo.'
    w=web.get(dom)
    if w and e.lower() in w[1]: return 'Confirmado en web',e,'Publicado en '+w[1][e.lower()]
    if user in PERS: return 'Personal',e,'Dirección a nombre de una persona; la web no la publica.'
    if w and w[1]:
        alt=lvl_pick([x for x in w[1] if x.endswith(dom.replace('stgeorge.org.ar','stgeorges.edu.ar'))],'')
        return 'No figura en la web',e,'El dominio recibe correo, pero la web no publica esta dirección.'
    return 'Dominio activo',e,'El dominio recibe correo; la web '+('no carga o no publica correos.' )
ORDER=['Confirmado en web','Válido (oficial DGCyE)','Dominio activo','Corregido','Corregido (probable)','No figura en la web','Sin confirmar','Personal','Inválido']
out=[]
for r in rows:
    name,addr,loc,cp,mails,tel,gest,niv,cue=r[:9]
    es=[x.strip() for x in (mails or '').split(';') if '@' in x]
    res=[(e,)+check(e) for e in es]
    doms={e.split('@')[1].lower() for e in es}-FREE-{'abc.gob.ar','abc.gov.ar','abc.go','gmail.com.ar'}
    webmails={}; src=''
    for d in doms:
        w=web.get(d)
        if w and w[1]: webmails.update(w[1]); src=w[0]
    best=None; stat=None
    OVR={('INSTITUTO SAN JORGE','Secundario'):'secretaria.college.quilmes@stgeorges.edu.ar',('COLEGIO SAN JORGE','Primario'):'prepschool@stgeorges.edu.ar'}
    conf=[x for x in res if x[1]=='Confirmado en web']
    good=[x for x in res if x[1] in ('Válido (oficial DGCyE)','Corregido','Dominio activo','No figura en la web')]
    pick=lvl_pick(sorted(webmails),niv)
    if (name,niv) in OVR: best=OVR[(name,niv)]; stat='Corregido con la web'
    elif conf: best=conf[0][2]; stat='Confirmado en web'
    elif good:
        good.sort(key=lambda x:ORDER.index(x[1])); best=good[0][2]; stat=good[0][1]
    elif pick: best=pick; stat='Corregido con la web'
    else:
        for st in ('Corregido (probable)','Sin confirmar','Personal','Inválido'):
            c=[x for x in res if x[1]==st]
            if c: best=c[0][2]; stat=st; break
    if not stat: stat='Sin correo'
    out.append(dict(name=name.title(),addr=addr,loc=loc,cp=cp,niv=niv,tel=tel,cue=cue,best=best,stat=stat,
        padron=mails,detalle=' | '.join(f'{e}: {s}' + (f' → {f}' if f and f!=e else '') for e,s,f,_ in res),
        notas=' '.join(dict.fromkeys(n for *_,n in res)),web=src,webmails='; '.join(sorted(webmails))))
json.dump(out,open('out.json','w'),ensure_ascii=False)
from collections import Counter; print(Counter(o['stat'] for o in out))
