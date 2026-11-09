# -*- coding: utf-8 -*-
"""Exploración de la fuente CVM (borrador, no entra al pipeline): quiénes entregan ITR/DFP.

    Set-Location C:\\dev\\bz_banks
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_explorar.py
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pipeline"))
import almacen as A          # noqa: E402
import bancos as B           # noqa: E402
import cvm                   # noqa: E402

pd.set_option("display.width", 220)


def raiz(cnpj: str) -> str:
    d = "".join(ch for ch in str(cnpj) if ch.isdigit())
    return d[:8]


def cnpj_ifdata() -> pd.DataFrame:
    """CNPJ líder del conglomerado, tomado del cadastro del IF.Data (varios trimestres: el último no nulo)."""
    universo = {b["cod_inst"]: b["nombre_corto"] for b in B.universo()}
    rutas = sorted(A.ruta_cruda("bcb_ifdata", "cadastro").glob("cadastro_*.parquet"))
    filas = {}
    for r in rutas:
        d = pd.read_parquet(r, columns=["CodInst", "NomeInstituicao", "CnpjInstituicaoLider",
                                        "CodConglomeradoPrudencial"])
        d = d[d["CodInst"].isin(universo) | d["CodConglomeradoPrudencial"].isin(universo)]
        for _, f in d.iterrows():
            cod = f["CodInst"] if f["CodInst"] in universo else f["CodConglomeradoPrudencial"]
            c = str(f["CnpjInstituicaoLider"]).strip()
            if c and c.lower() != "null" and c.isdigit():
                filas.setdefault(cod, {"cod_inst": cod, "cnpj": c})
                filas[cod]["cnpj"] = c          # se queda con el último trimestre con dato
                filas[cod]["nombre_ifdata"] = f["NomeInstituicao"]
    out = pd.DataFrame(filas.values())
    out["nombre_corto"] = out["cod_inst"].map(universo)
    out["raiz"] = out["cnpj"].map(raiz)
    return out.sort_values("nombre_corto").reset_index(drop=True)


def cadastro() -> pd.DataFrame:
    return pd.read_csv(cvm.ruta_cadastro(), sep=";", dtype=str, keep_default_na=False,
                       encoding="cp1252", usecols=cvm.COLUMNAS_CADASTRO)


def estado(documento: str, anio: int, estado_: str, cnpjs: set[str] | None = None) -> pd.DataFrame:
    """Las filas consolidadas de un estado, enteras si cnpjs es None o filtradas por raíz de CNPJ."""
    partes = []
    with zipfile.ZipFile(cvm.ruta_zip(documento, anio)) as z:
        nombre = cvm._nombre_interno(z, documento, estado_, anio)
        cols = cvm.columnas_estado(z, nombre)
        for parte in cvm.leer_estado(z, nombre, cols):
            if cnpjs is not None:
                parte = parte[parte["CNPJ_CIA"].map(raiz).isin(cnpjs)]
            partes.append(parte)
    df = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    if "DT_INI_EXERC" not in df.columns:
        df["DT_INI_EXERC"] = ""
    df["raiz"] = df["CNPJ_CIA"].map(raiz)
    return df


if __name__ == "__main__":
    ifdata = cnpj_ifdata()
    print("=== CNPJ líder de IF.Data contra el universo del panel ===")
    print(ifdata.to_string())
    universo = {b["cod_inst"]: b["nombre_corto"] for b in B.universo()}
    sin = sorted(set(universo) - set(ifdata["cod_inst"]))
    print(f"\nsin CNPJ en el cadastro del IF.Data ({len(sin)}): " + ", ".join(f"{universo[c]}={c}" for c in sin))

    cad = cadastro()
    cad["raiz"] = cad["CNPJ_CIA"].map(raiz)
    print("\n=== sectores del registro de la CVM que suenan a banco ===")
    print(sorted(s for s in cad["SETOR_ATIV"].unique() if "anc" in s or "nterm" in s or "inan" in s))

    banc = cad[cad["SETOR_ATIV"].str.contains("Banc", na=False)]
    print(f"\n=== {len(banc)} compañías con SETOR_ATIV «Banc*» (SIT: {sorted(banc['SIT'].unique())}) ===")
    print(banc.groupby(["SETOR_ATIV", "SIT"]).size().to_string())

    print("\n=== del universo del panel, quiénes están en el registro bancario de la CVM ===")
    cruz = ifdata.merge(cad[["raiz", "DENOM_SOCIAL", "CD_CVM", "SETOR_ATIV", "SIT", "CATEG_REG"]],
                        on="raiz", how="left")
    print(cruz[["nombre_corto", "cod_inst", "cnpj", "DENOM_SOCIAL", "CD_CVM", "SETOR_ATIV", "SIT", "CATEG_REG"]]
          .to_string())

    print("\n=== compañías bancarias del registro que NO están en el panel por CNPJ líder ===")
    raices_panel = set(ifdata["raiz"])
    extra = banc[~banc["raiz"].isin(raices_panel)]
    print(extra[["DENOM_SOCIAL", "CD_CVM", "CNPJ_CIA", "SETOR_ATIV", "SIT"]].sort_values("DENOM_SOCIAL").to_string())
