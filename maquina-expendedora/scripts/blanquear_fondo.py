"""Pasa a blanco el fondo liso (negro, gris, etc.) conectado al borde, para fotos que no vienen sobre blanco.
Uso: python3 scripts/blanquear_fondo.py <slug> [tolerancia]"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage
slug = sys.argv[1]; tol = float(sys.argv[2]) if len(sys.argv) > 2 else 28
p = f"productos_raw/{slug}.img"; im = Image.open(p).convert("RGB"); a = np.asarray(im).astype(int)
esquinas = np.array([a[2,2], a[2,-3], a[-3,2], a[-3,-3]]); ref = np.median(esquinas, axis=0)
cerca = np.abs(a - ref).max(axis=2) <= tol
lab, n = ndimage.label(cerca); borde = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:,0], lab[:,-1]]))) - {0}
fondo = ndimage.binary_dilation(np.isin(lab, list(borde)), iterations=1)
a[fondo] = 255; Image.fromarray(a.astype(np.uint8)).save(p, format="PNG"); print(slug, "fondo", ref, "→ blanco", round(fondo.mean()*100), "%")
