"""bk_manifiesto: una fila por tabla gold (filas, columnas, rango, sha256, quién la produjo) y una por universo
(último corte). Se arma una sola vez, después de que todos los pasos publicaron (actualizar.py).

El comando que produjo cada tabla sale de su procedencia en ``datos/derivado/`` (almacen.publicar_gold).
"""
from __future__ import annotations

import sys

import pandas as pd

import almacen as A
import bancos as B
import reglas_gold as RG


# Universos con tabla gold: (nombre, tabla, nota). Publicado y REF se añaden cuando existan, sin corte inventado.
UNIVERSOS = [
    (B.PANEL, "bk_panel", "IF.Data prudencial, trimestral"),
    ("Sistema", "bk_sistema_m", "SGS, mensual (bk_sistema_m, encargo 61)"),
    ("SCR", "bk_scr", "SCR.data, mensual, por segmento de institución (bk_scr, encargo 67)"),
]


def _rango(df: pd.DataFrame) -> str | None:
    r = RG.rango(df)
    return None if r is None else f"{r[1]}–{r[2]}"


def _corte(tabla: str) -> str | None:
    ruta = A.GOLD / f"{tabla}.parquet"
    if not ruta.exists():
        print(f"aviso: falta {ruta.name}; su universo queda fuera del manifiesto", file=sys.stderr)
        return None
    return str(pd.to_datetime(pd.read_parquet(ruta, columns=["fecha"])["fecha"]).max().date())


def construir() -> pd.DataFrame:
    productores = A.productores_gold()
    filas = []
    for ruta in sorted(A.GOLD.glob("bk_*.parquet")):
        if ruta.name == "bk_manifiesto.parquet":
            continue
        df = pd.read_parquet(ruta)
        filas.append({"tipo": "tabla", "tabla": ruta.stem, "archivo": ruta.name, "filas": len(df),
                      "columnas": df.shape[1], "rango": _rango(df), "sha256": A.sha256_archivo(ruta),
                      "bytes": ruta.stat().st_size,
                      "producido_por": productores.get(ruta.name, "sin procedencia en datos/derivado/"),
                      "universo": None, "ultimo_corte": None, "nota": None})
    for nombre, tabla, nota in UNIVERSOS:
        corte = _corte(tabla)
        if corte is not None:
            filas.append({"tipo": "universo", "tabla": None, "archivo": None, "filas": None, "columnas": None,
                          "rango": None, "sha256": None, "bytes": None, "producido_por": None,
                          "universo": nombre, "ultimo_corte": corte, "nota": nota})
    return pd.DataFrame(filas)


def main(argv: list[str] | None = None) -> int:
    man = construir()
    A.publicar_gold("bk_manifiesto", man, dataset="bancos_gold",
                    desde=sorted(f"gold/{t}.parquet" for t in man["tabla"].dropna()))
    print(f"bk_manifiesto: {len(man)} filas ({int((man['tipo'] == 'tabla').sum())} tablas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
