# -*- coding: utf-8 -*-
"""Sondeo fino: cuentas de balance y resultado de cada banco, solo las que pueden ser una línea mínima.

    Set-Location C:\\dev\\bz_banks
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_sondeo2.py 2026-06-30
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pipeline"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cvm                   # noqa: E402
from cvm_cuentas import derivados, ultima   # noqa: E402

pd.set_option("display.width", 240)
pd.set_option("display.max_rows", 1200)
pd.set_option("display.max_colwidth", 95)

# Qué se busca en cada estado, por palabra clave del nombre de la cuenta.
BUSCA = {
    "BPA": r"crédito|credito|arrendamento mercantil|perda esperada|provisão|provisao",
    "BPP": r"depósito|deposito|patrimônio|patrimonio|perda esperada|provisão|provisao|controlador",
    "DRE": r"intermediação|intermediacao|lucro|prejuízo|atribu|controladora|perda esperada|provisão",
}


def nivel(cd: str) -> int:
    return cd.count(".")


if __name__ == "__main__":
    refer = sys.argv[1] if len(sys.argv) > 1 else "2026-06-30"
    df = derivados()
    mapa = cvm.mapa_bancos()
    for _, b in mapa[mapa["entrega"]].iterrows():
        d = ultima(df, b["cod_inst"], refer)
        if d.empty:
            print(f"\n### {b['nombre_corto']}: sin {refer}")
            continue
        d = d.copy()
        d["valor"] = d["vl_conta"].str.replace(",", ".", regex=False).astype(float) / 1e6
        d["nivel"] = d["cd_conta"].map(nivel)
        print(f"\n### {b['nombre_corto']} ({b['cod_inst']}) {refer} · {b['tipo_estado']} · "
              f"{sorted(set(d['documento'] + ' v' + d['versao']))}")
        for est in ("BPA", "BPP", "DRE"):
            e = d[(d["estado"] == est) & (d["nivel"] <= 3) &
                  d["ds_conta"].str.contains(BUSCA[est], case=False, regex=True, na=False)]
            if est == "DRE":
                e = e[~e["dt_ini_exerc"].eq("")].drop_duplicates(subset=["cd_conta", "ds_conta", "valor"])
            if e.empty:
                print(f"  {est}: (nada)")
                continue
            cols = ["cd_conta", "ds_conta", "valor", "st_conta_fixa"]
            if est == "DRE":
                cols.insert(2, "dt_ini_exerc")
            print(e[cols].sort_values(["cd_conta", "dt_ini_exerc"] if est == "DRE" else ["cd_conta"])
                  .to_string(index=False, header=(est == "BPA")))
