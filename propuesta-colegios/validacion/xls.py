import json,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
out=json.load(open('out.json'))
ORD={'Confirmado en web':0,'Corregido con la web':1,'Válido (oficial DGCyE)':2,'Corregido':3,'Dominio activo':4,'Corregido (probable)':5,'No figura en la web':6,'Sin confirmar':7,'Personal':8,'Inválido':9}
COL={'Confirmado en web':'C6EFCE','Corregido con la web':'C6EFCE','Válido (oficial DGCyE)':'DDEBF7','Corregido':'DDEBF7','Dominio activo':'DDEBF7','Corregido (probable)':'FFF2CC','No figura en la web':'FFF2CC','Sin confirmar':'FFF2CC','Personal':'FCE4D6','Inválido':'F8CBAD'}
wb=openpyxl.Workbook(); ws=wb.active; ws.title='Privados validados'
H=['Colegio','Dirección','Localidad','C.P.','Niveles','Correo a usar','Estado','Correos del padrón','Resultado por correo','Detalle','Web consultada','Correos publicados en la web','Teléfono','CUE']
ws.append(H)
for o in sorted(out,key=lambda o:(ORD.get(o['stat'],9),o['loc'],o['name'])):
    ws.append([o['name'],o['addr'],o['loc'],o['cp'],o['niv'],o['best'],o['stat'],o['padron'],o['detalle'],o['notas'],o['web'],o['webmails'],o['tel'],o['cue']])
    ws.cell(ws.max_row,7).fill=PatternFill('solid',fgColor=COL.get(o['stat'],'FFFFFF'))
for c in ws[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1F4E78'); c.alignment=Alignment(wrap_text=True,vertical='center')
W=[34,30,18,7,16,38,22,45,60,60,32,45,16,11]
for i,w in enumerate(W,1): ws.column_dimensions[get_column_letter(i)].width=w
ws.freeze_panes='B2'; ws.auto_filter.ref=ws.dimensions
n=wb.create_sheet('Estados')
n.append(['Estado','Qué significa','Filas'])
from collections import Counter; c=Counter(o['stat'] for o in out)
D={'Confirmado en web':'El correo del padrón aparece publicado en la web, Facebook o Instagram oficial del colegio (link en "Web consultada").',
'Corregido con la web':'El correo del padrón no está en la web (o es personal); se usa el que publica la web para ese nivel.',
'Válido (oficial DGCyE)':'Casilla oficial @abc.gob.ar del establecimiento.',
'Corregido':'Error de tipeo del padrón corregido (abc.gov.ar → abc.gob.ar, abc.go → abc.gob.ar).',
'Dominio activo':'Dominio propio del colegio que recibe correo, pero la web no carga o no publica direcciones.',
'Corregido (probable)':'gmail.com.ar no existe; se cambió a gmail.com.',
'No figura en la web':'Dominio propio activo, pero la web publica otras direcciones.',
'Sin confirmar':'Cuenta gratuita (gmail/yahoo/hotmail) que no aparece en ninguna web del colegio. Puede funcionar, pero no se pudo verificar.',
'Personal':'Solo hay correos a nombre de una persona; pueden estar desactualizados.',
'Inválido':'El dominio no existe: el correo rebota.'}
for k in sorted(D,key=lambda k:ORD[k]): n.append([k,D[k],c.get(k,0)]); n.cell(n.max_row,1).fill=PatternFill('solid',fgColor=COL[k])
n.append([]); n.append(['Total',f'{len(out)} filas (cada nivel de cada colegio por separado; fuente: Padrón Oficial de Establecimientos, solo gestión privada).',len(out)])
n.append(['Método','Para cada dominio se consultó si tiene servidor de correo (registro MX) y se recorrió la web del colegio (inicio, contacto y páginas de niveles) buscando direcciones publicadas; además se buscó cada dirección en la web y en las redes oficiales de cada colegio (sin contar directorios que copian el padrón). Revisado el 13/11/2026.'])
for c_ in n[1]: c_.font=Font(bold=True)
n.column_dimensions['A'].width=24; n.column_dimensions['B'].width=100
for r in n.iter_rows():
    for c_ in r: c_.alignment=Alignment(wrap_text=True,vertical='top')
wb.save('/home/user/suscripcion-smg/propuesta-colegios/colegios_privados_quilmes_validados.xlsx')
