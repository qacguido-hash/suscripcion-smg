# Actualización diaria de precios de proveedores

App: https://claude.ai/artifact/LECc5G6xbvVBwaq7J8PNcR (colección `productos`).
Proveedores que se actualizan solos: Golomax, Distribuidora OKs (`distrioks`), Distribuidora Pop (`pop`).
**Masmelos no**: su web sin cuenta muestra otros precios que los del cliente; se carga a mano.
`mapeo.json` dice qué artículo de cada proveedor corresponde a cada producto de la app.

## Pasos
1. Bajar los productos: ArtifactData `list` de `productos` con `query.limit=300` y `out_dir=<dir>`.
   Anotar la versión de cada documento (sale en el resultado del list).
2. `python3 app-sg-expendedoras/proveedores/actualizar_precios.py <dir>/productos <salida>`
3. Por cada archivo `<salida>/cambios/<id>.json`: ArtifactData `update` de `productos/<id>` con
   `file_path` = ese archivo e `if_version` = la versión anotada. En lotes de hasta 50 con `batch`.
   Si un lote falla por versión, volver a listar y reintentar solo esos productos.
4. Copiar `<salida>/resumen.md` a `historial/AAAA-MM-DD.md`, commit y push.

Reglas: no tocar `proveedorElegido`, `precioVenta` ni ningún otro campo; no borrar precios de un proveedor
aunque un artículo no aparezca (queda en el resumen como "no encontrado"). Cambios menores a 0,5% se ignoran.
