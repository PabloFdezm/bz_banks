"""Compara celda por celda dos carpetas de parquets gold (misma forma, mismas columnas, mismos valores).

Uso: python -X utf8 herramientas/comparar_gold.py <carpeta_a> <carpeta_b>
Los floats se comparan con tolerancia relativa 1e-12 (solo ruido de redondeo); todo lo demás exacto.
`bk_manifiesto` se compara sin las columnas que dependen del momento de la corrida (bytes, sha256, generado).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

VOLATILES = {"bk_manifiesto": {"bytes", "sha256", "generado", "generado_en", "actualizado"}}


def comparar(a: Path, b: Path) -> list[str]:
    dif = []
    nombres = sorted({p.name for p in a.glob("*.parquet")} | {p.name for p in b.glob("*.parquet")})
    for n in nombres:
        pa, pb = a / n, b / n
        if not (pa.exists() and pb.exists()):
            dif.append(f"{n}: solo en {'a' if pa.exists() else 'b'}")
            continue
        x, y = pd.read_parquet(pa), pd.read_parquet(pb)
        fuera = VOLATILES.get(pa.stem, set())
        x = x[[c for c in x.columns if c not in fuera]]
        y = y[[c for c in y.columns if c not in fuera]]
        if list(x.columns) != list(y.columns):
            dif.append(f"{n}: columnas distintas")
            continue
        if x.shape != y.shape:
            dif.append(f"{n}: forma {x.shape} vs {y.shape}")
            continue
        celdas = 0
        for c in x.columns:
            u, v = x[c], y[c]
            if pd.api.types.is_float_dtype(u) and pd.api.types.is_float_dtype(v):
                igual = np.isclose(u.to_numpy(), v.to_numpy(), rtol=1e-12, atol=0, equal_nan=True)
            else:
                igual = (u.astype(object).where(u.notna(), None) == v.astype(object).where(v.notna(), None)).to_numpy() | (u.isna() & v.isna()).to_numpy()
            if not igual.all():
                dif.append(f"{n}.{c}: {int((~igual).sum())} celdas distintas (ej. fila {int(np.argmin(igual))}: {u.iloc[int(np.argmin(igual))]!r} vs {v.iloc[int(np.argmin(igual))]!r})")
            celdas += len(u)
        print(f"{n}: {x.shape[0]:,} filas, {celdas:,} celdas comparadas")
    return dif


if __name__ == "__main__":
    d = comparar(Path(sys.argv[1]), Path(sys.argv[2]))
    print("\nIDÉNTICO" if not d else "\nDIFERENCIAS:\n" + "\n".join(d))
    sys.exit(1 if d else 0)
