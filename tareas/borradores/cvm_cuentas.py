# -*- coding: utf-8 -*-
"""Vuelca el plan de cuentas de un banco y referencia desde el derivado (borrador de trabajo).

    Set-Location C:\\dev\\bz_banks
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_cuentas.py C0080099 2026-06-30 [BPA BPP DRE]
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_cuentas.py C0080099 2026-06-30 --solo-fijas
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_cuentas.py --todos 2026-06-30 DRE
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pipeline"))
import almacen as A          # noqa: E402
import cvm                   # noqa: E402

pd.set_option("display.width", 260)
pd.set_option("display.max_rows", 800)
pd.set_option("display.max_colwidth", 95)


def derivados() -> pd.DataFrame:
    partes = [pd.read_parquet(p) for p in sorted(A.ruta_derivada(cvm.FUENTE, cvm.DS_DERIVADO)
                                                 .glob("estados_*.parquet"))]
    return pd.concat(partes, ignore_index=True)


def ultima(df: pd.DataFrame, cod: str, refer: str) -> pd.DataFrame:
    """La versión mayor (por documento), con ORDEM_EXERC=ÚLTIMO, de un banco y referencia."""
    d = df[(df["cod_inst"] == cod) & (df["dt_refer"] == refer) & (df["ordem_exerc"] == "ÚLTIMO")].copy()
    if d.empty:
        return d
    d["versao_n"] = pd.to_numeric(d["versao"], errors="coerce").fillna(0).astype(int)
    return d[d["versao_n"] == d.groupby("documento")["versao_n"].transform("max")]


if __name__ == "__main__":
    args = sys.argv[1:]
    solo_fijas = "--solo-fijas" in args
    args = [a for a in args if not a.startswith("--")]
    df = derivados()
    if args[0] == "--todos":
        refer = args[1]
        estados = args[2:] or list(cvm.ESTADOS)
        for cod in sorted(df["cod_inst"].unique()):
            d = ultima(df, cod, refer)
            if d.empty:
                continue
            d = d[d["estado"].isin(estados)]
            if solo_fijas:
                d = d[d["st_conta_fixa"] == "S"]
            nom = d["nombre_corto"].iloc[0]
            print(f"\n{'=' * 30} {nom} ({cod}) {refer} {len(d)} cuentas")
            print(d[["estado", "cd_conta", "ds_conta", "vl_conta", "st_conta_fixa"]]
                  .sort_values(["estado", "cd_conta"]).to_string(index=False))
        sys.exit(0)

    cod, refer = args[0], args[1]
    estados = args[2:] or list(cvm.ESTADOS)
    d = ultima(df, cod, refer)
    if d.empty:
        print(f"{cod} {refer}: sin filas")
        sys.exit(1)
    d = d[d["estado"].isin(estados)]
    if solo_fijas:
        d = d[d["st_conta_fixa"] == "S"]
    cols = ["estado", "cd_conta", "ds_conta", "vl_conta", "st_conta_fixa"]
    if (d["estado"] == "DRE").any():
        cols.insert(3, "dt_ini_exerc")
    print(f"{d['nombre_corto'].iloc[0]} ({cod}) {refer} — {len(d)} cuentas, "
          f"documentos: {sorted(set(d['documento'] + ' v' + d['versao']))}")
    print(d[cols].sort_values(["estado", "dt_ini_exerc", "cd_conta"] if "dt_ini_exerc" in cols
                              else ["estado", "cd_conta"]).to_string(index=False))
