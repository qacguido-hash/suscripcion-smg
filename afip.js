export async function onRequest(context) {
  const url = new URL(context.request.url);
  const cuit = url.searchParams.get('cuit');

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  if (!cuit) return new Response(JSON.stringify({ error: 'CUIT requerido' }), { status: 400, headers });

  const cuitLimpio = cuit.replace(/\D/g, '');

  const intentar = async (fn) => { try { return await fn(); } catch(e) { return null; } };

  const [r1, r2, r3] = await Promise.all([
    intentar(async () => {
      const res = await fetch('https://soa.afip.gob.ar/sr-padron/v2/persona/' + cuitLimpio, {
        headers: { 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0' },
        signal: AbortSignal.timeout(7000)
      });
      if (!res.ok) return null;
      const j = await res.json();
      const p = j && j.data;
      if (!p) return null;
      const nombre = p.razonSocial || [p.nombre, p.apellido].filter(Boolean).join(' ').trim();
      if (!nombre) return null;
      return { razon_social: nombre, tipo: p.tipoPersona === 'JURIDICA' ? 'Persona juridica' : 'Persona fisica', encontrado: true };
    }),
    intentar(async () => {
      const res = await fetch('https://afip.tangofactura.com/Rest/GetContribuyenteFull?cuit=' + cuitLimpio, {
        headers: { 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0' },
        signal: AbortSignal.timeout(7000)
      });
      if (!res.ok) return null;
      const j = await res.json();
      const nombre = j && j.Contribuyente && (j.Contribuyente.razonSocial || j.Contribuyente.nombre);
      if (!nombre) return null;
      return { razon_social: nombre, tipo: 'Registrado', encontrado: true };
    }),
    intentar(async () => {
      const res = await fetch('https://api.cuitonline.com/data/' + cuitLimpio, {
        headers: { 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0' },
        signal: AbortSignal.timeout(7000)
      });
      if (!res.ok) return null;
      const j = await res.json();
      const nombre = j && (j.nombre || j.razon_social || j.denominacion);
      if (!nombre) return null;
      return { razon_social: nombre, tipo: (j && j.tipo) || 'Registrado', encontrado: true };
    }),
  ]);

  const resultado = r1 || r2 || r3;
  if (resultado && resultado.razon_social) {
    return new Response(JSON.stringify(resultado), { status: 200, headers });
  }
  return new Response(JSON.stringify({ encontrado: false, razon_social: null, tipo: null }), { status: 200, headers });
}
