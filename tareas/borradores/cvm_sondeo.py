# -*- coding: utf-8 -*-
"""Sondeo: para cada banco y referencia, las cuentas candidatas a cada línea mínima (borrador).

    Set-Location C:\\dev\\bz_banks
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_sondeo.py [referencia]
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pipeline"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cvm                   # noqa: E402
from cvm_cuentas import derivados, ultima   # noqa: E402

pd.set_option("display.width", 260)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.max_colwidth", 100)

CLAVES = {
    "ativo": ["Ativo Total"],
    "credito": ["Operações de Crédito", "Operacoes de Credito"],
    "pdd": ["Provisão para Perda Esperada", "Provisao para Perda Esperada", "Perda Esperada"],
    "depositos": ["Depósitos", "Depositos"],
    "pl": ["Patrimônio Líquido", "Patrimonio Liquido"],
    "interm": ["Intermediação Financeira", "Intermediacao Financeira"],
    "lucro": ["Lucro/Prejuízo Consolidado do Período", "Atribuído a Sócios", "Lucro Líquido do Período",
              "Lucro/Prejuízo do Período"],
}


def candidatos(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["valor"] = d["vl_conta"].str.replace(",", ".", regex=False).astype(float) / 1e6   # R$ mil → R$ bn
    patrones = {k: "|".join(pd.Series(v).str.replace("(", r"\(", regex=False)
                            .str.replace(")", r"\)", regex=False).str.replace("/", r"\/", regex=False))
                for k, v in CLAVES.items()}
    d["linea"] = ""
    for k, p in patrones.items():
        d.loc[d["ds_conta"].str.contains(p, case=False, regex=True, na=False), "linea"] = k
    return d[d["linea"] != ""]


if __name__ == "__main__":
    refer = sys.argv[1] if len(sys.argv) > 1 else "2026-06-30"
    df = derivados()
    mapa = cvm.mapa_bancos()
    mapa = mapa[mapa["entrega"]]
    for _, b in mapa.iterrows():
        d = ultima(df, b["cod_inst"], refer)
        if d.empty:
            print(f"\n### {b['nombre_corto']} ({b['cod_inst']}): sin {refer}")
            continue
        c = candidatos(d)
        print(f"\n### {b['nombre_corto']} ({b['cod_inst']}) {refer} · {b['tipo_estado']} · "
              f"{sorted(set(d['documento'] + ' v' + d['versao']))}")
        cols = ["estado", "cd_conta", "ds_conta", "valor", "st_conta_fixa", "linea"]
        if (c["estado"] == "DRE").any():
            cols.insert(3, "dt_ini_exerc")
        print(c[cols].sort_values(["linea", "estado", "cd_conta"]).to_string(index=False))
