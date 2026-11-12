# Máquina expendedora cargada (propuesta sanatorio)

- `salida/maquina_completa.png`: imagen final en alta resolución (2600×3560).
- `salida/maquina_completa_liviana.jpg`: versión liviana para la presentación.
- `FUENTES.md`: de dónde salió cada foto y a qué escala quedó.
- Versión colegio: `salida/maquina_colegio.png`, `salida/maquina_colegio_liviana.jpg` y `FUENTES_colegio.md`
  (distribución en `scripts/distribucion_colegio.json`; regenerar con
  `python3 scripts/componer.py --distribucion distribucion_colegio.json --sufijo colegio` y
  `python3 scripts/informe.py distribucion_colegio.json escalas_colegio.json FUENTES_colegio.md`).

## Para corregir algo
1. Cambiar un producto: editar `scripts/seleccion.json` (tienda + nombre exacto, o URL directa con tienda `web`) y correr
   `python3 -I scripts/descargar.py <slug>` y luego `python3 scripts/recortar.py <slug>`.
2. Cambiar distribución o tamaños reales: `scripts/distribucion.json`.
3. Regenerar la imagen: `python3 scripts/componer.py` (o `--estantes 1 2` para una versión parcial) y el informe: `python3 scripts/informe.py`.

Requiere Python con Pillow, numpy, scipy y `rembg` (modelo isnet-general-use).
