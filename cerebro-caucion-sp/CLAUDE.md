# Instrucciones para Claude – Cerebro Caución San Patricio

Este directorio es la base de conocimiento del suscriptor de Caución de San Patricio Seguros (Argentina). Leé `00-como-usar.md` para la estructura completa.

## Al responder consultas de suscripción

1. Buscá primero en `casos/` negocios parecidos (misma actividad, ramo, rango de monto, tipo de asegurado). Citá el archivo y la fecha: "Parecido a `casos/2026-12-03-...`: se emitió con contragarantía de socios porque...".
2. Después revisá `criterios/`. Distinguí entre criterios `🟢 confirmado` (de la casa) y `🟡 a validar`.
3. Si no hay nada en el cerebro, decilo explícitamente y respondé con criterio general de mercado, aclarando que no es criterio de la casa todavía.
4. Nunca inventes casos, montos ni decisiones que no estén escritos.

## Al cargar información nueva

- Notas sueltas → `bitacora.md`, con fecha, al principio de la sección del día.
- Un negocio decidido → nuevo archivo en `casos/` con `casos/_plantilla.md`.
- Una regla que se repite → `criterios/` (indicar fuente y estado).
- Pasos de una tarea o del sistema → `procesos/`.
- Al ordenar la bitácora, marcar con ✅ lo ya procesado.

## Cuidados

- No incorporar documentos confidenciales de otras aseguradoras (en particular de su empleador anterior). Solo conceptos y estructura.
- Tomadores identificados con nombre genérico o código; sin CUIT ni datos personales.
- Escribir en español rioplatense, claro y directo.
