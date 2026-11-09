# -*- coding: utf-8 -*-
"""Exploración 2: quiénes entregan ITR/DFP de verdad (no lo que dice el registro).

    Set-Location C:\\dev\\bz_banks
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_explorar2.py
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pipeline"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bancos as B           # noqa: E402
import cvm                   # noqa: E402
from cvm_explorar import cadastro, cnpj_ifdata, estado, raiz   # noqa: E402

pd.set_option("display.width", 250)

SALIDA = Path(__file__).resolve().parent / "cvm_inventario.csv"


def inventario() -> pd.DataFrame:
    """Una fila por compañía × documento × año × estado × DT_REFER, con versiones y cuentas."""
    filas = []
    for doc, anios in (("itr", (2025, 2026)), ("dfp", (2023, 2024, 2025, 2026))):
        for anio in anios:
            with zipfile.ZipFile(cvm.ruta_zip(doc, anio)) as z:
                for est in cvm.ESTADOS:
                    nombre = cvm._nombre_interno(z, doc, est, anio)
                    if nombre is None:
                        print(f"[!] {doc} {anio} {est}: no está en el ZIP")
                        continue
                    cols = cvm.columnas_estado(z, nombre)
                    usar = [c for c in ["CNPJ_CIA", "DENOM_CIA", "CD_CVM", "VERSAO", "DT_REFER", "ORDEM_EXERC",
                                        "DT_FIM_EXERC", "DT_INI_EXERC", "GRUPO_DFP", "ESCALA_MOEDA", "MOEDA",
                                        "CD_CONTA"] if c in cols]
                    for parte in cvm.leer_estado(z, nombre, usar):
                        parte["raiz"] = parte["CNPJ_CIA"].map(raiz)
                        g = parte.groupby(["raiz", "DENOM_CIA", "CD_CVM", "DT_REFER", "ORDEM_EXERC", "DT_FIM_EXERC",
                                           "DT_INI_EXERC" if "DT_INI_EXERC" in parte else "DT_FIM_EXERC",
                                           "GRUPO_DFP", "ESCALA_MOEDA", "MOEDA", "VERSAO"], dropna=False).size()
                        for clave, n in g.items():
                            d = dict(zip(["raiz", "DENOM_CIA", "CD_CVM", "DT_REFER", "ORDEM_EXERC", "DT_FIM_EXERC",
                                          "DT_INI_EXERC", "GRUPO_DFP", "ESCALA_MOEDA", "MOEDA", "VERSAO"], clave))
                            filas.append({**d, "documento": doc.upper(), "anio_zip": anio, "estado": est,
                                          "n_cuentas": n})
            print(f"[+] {doc.upper()} {anio}: {len(filas)} combinaciones acumuladas", flush=True)
    df = pd.DataFrame(filas)
    df.to_csv(SALIDA, index=False, encoding="utf-8-sig")
    return df


if __name__ == "__main__":
    if SALIDA.exists() and "--rehacer" not in sys.argv:
        df = pd.read_csv(SALIDA, dtype=str, keep_default_na=False)
        print(f"[=] leyendo {SALIDA.name} ({len(df):,} filas)")
    else:
        df = inventario()
    df = df.astype(str)

    ifdata = cnpj_ifdata()
    panel = set(ifdata["raiz"])
    nombre_panel = dict(zip(ifdata["raiz"], ifdata["nombre_corto"]))
    cad = cadastro()
    cad["raiz"] = cad["CNPJ_CIA"].map(raiz)
    sector = cad.sort_values("SIT").drop_duplicates("raiz", keep="last").set_index("raiz")

    df["en_panel"] = df["raiz"].isin(panel)
    df["banco_cvm"] = df["raiz"].map(sector["SETOR_ATIV"]).fillna("")

    print("\n=== compañías del PANEL que entregan algo ===")
    p = df[df["en_panel"]]
    if p.empty:
        print("  (ninguna)")
    else:
        resumen = (p.groupby(["raiz", "DENOM_CIA", "documento"])
                     .agg(anios=("anio_zip", lambda s: ",".join(sorted(set(s)))),
                          referencias=("DT_REFER", lambda s: ",".join(sorted(set(s))[:12])),
                          versiones=("VERSAO", lambda s: ",".join(sorted(set(s)))),
                          estados=("estado", lambda s: ",".join(sorted(set(s)))),
                          escalas=("ESCALA_MOEDA", lambda s: ",".join(sorted(set(s)))),
                          grupos=("GRUPO_DFP", "nunique"))
                     .reset_index())
        resumen["panel"] = resumen["raiz"].map(nombre_panel)
        print(resumen[["panel", "raiz", "DENOM_CIA", "documento", "anios", "referencias", "versiones", "estados",
                       "escalas", "grupos"]].sort_values(["panel", "documento"]).to_string(index=False))

    print("\n=== compañías con sector bancario CVM que entregan algo y NO están en el panel ===")
    q = df[(~df["en_panel"]) & (df["banco_cvm"].str.contains("Banc|Interm", na=False))]
    r = (q.groupby(["raiz", "DENOM_CIA", "banco_cvm", "documento"])
          .agg(anios=("anio_zip", lambda s: ",".join(sorted(set(s)))),
               referencias=("DT_REFER", lambda s: ",".join(sorted(set(s))[:12])))
          .reset_index().sort_values(["banco_cvm", "DENOM_CIA"]))
    print(r.to_string(index=False))

    print("\n=== bancos del panel SIN ninguna entrega ===")
    presentes = set(df["raiz"])
    for _, f in ifdata.iterrows():
        if f["raiz"] in presentes:
            continue
        s = sector.loc[f["raiz"]] if f["raiz"] in sector.index else None
        registro = "—" if s is None else "{} ({}, {})".format(s["DENOM_SOCIAL"], s["SETOR_ATIV"], s["SIT"])
        print(f"  {f['nombre_corto']:22} {f['cod_inst']}  CNPJ {f['raiz']}  registro CVM: {registro}")

    print("\n=== dominio de GRUPO_DFP y ORDEM_EXERC por documento/estado ===")
    print(df.groupby(["documento", "estado", "GRUPO_DFP"])["n_cuentas"].sum().to_string())
    print(df.groupby(["documento", "estado", "ORDEM_EXERC"])["n_cuentas"].sum().to_string())
    print("\n=== escalas y monedas ===")
    print(df.groupby(["documento", "ESCALA_MOEDA", "MOEDA"])["n_cuentas"].sum().to_string())
