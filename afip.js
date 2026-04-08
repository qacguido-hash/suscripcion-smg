export async function onRequest(context) {
  const url = new URL(context.request.url);
  const cuit = url.searchParams.get('cuit');
  const tipo = url.searchParams.get('tipo') || 'deudas';

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  if (!cuit) return new Response(JSON.stringify({ error: 'CUIT requerido' }), { status: 400, headers });

  const endpoint = tipo === 'cheques'
    ? 'https://api.bcra.gob.ar/centraldedeudores/v1.0/Deudas/ChequesRechazados/' + cuit
    : 'https://api.bcra.gob.ar/centraldedeudores/v1.0/Deudas/' + cuit;

  try {
    const res = await fetch(endpoint, {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'Accept-Language': 'es-AR'
      }
    });

    if (res.status === 404) {
      return new Response(JSON.stringify({
        results: { deudas: [], periodo: null, denominacion: null },
        sin_deuda: true
      }), { status: 200, headers });
    }

    if (!res.ok) {
      const txt = await res.text();
      return new Response(JSON.stringify({ error: 'BCRA respondio ' + res.status, detail: txt }), { status: res.status, headers });
    }

    const data = await res.json();
    return new Response(JSON.stringify(data), { status: 200, headers });

  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500, headers });
  }
}
