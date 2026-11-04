# -*- coding: utf-8 -*-
"""Exposición de cada banco al deterioro del sistema: bk_exposicion (spec de datos §3.6, esqueleto B4-04 y B8-03).

POR QUÉ EXISTE
--------------
El NPL de un banco mezcla dos cosas: en qué carteras está (mix) y qué tan bien originó dentro de cada una.
La «mora implícita» separa la primera: es la mora que tendría el banco si cada modalidad de su cartera se
comportara como el promedio del sistema (SGS). Contra ella, el NPL observado dice si el banco está mejor o
peor que su mix; su cambio en 12 meses se abre en efecto mix (el banco movió su cartera) y efecto mora
(el sistema se deterioró en lo que el banco ya tenía).

Las definiciones no son iguales (panel ≥ 15 días; SGS > 90 días): la brecha se lee en su evolución, no en
nivel. Las modalidades sin serie del SGS quedan fuera y la columna `cobertura` dice qué parte de la
cartera entra en el cálculo; con cobertura < 50 % (bancos de desarrollo, cartera dirigida) todo queda vacío. Equivalencias en definiciones/bancos__equivalencias_mora.json.

Entradas: datos/gold/bk_cartera.parquet, datos/gold/bk_sistema_q.parquet.
Salida:   datos/gold/bk_exposicion.parquet (banco × trimestre), con almacen.guardar_derivado.
Uso:      python -X utf8 preparar_gold_bancos_exposicion.py
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import almacen as A

RAIZ = Path(__file__).resolve().parents[1]
BANKS = RAIZ / "datos" / "gold"
EQUIV = RAIZ / "definiciones" / "bancos__equivalencias_mora.json"
COMANDO = "python -X utf8 preparar_gold_bancos_exposicion.py"
COBERTURA_MIN = 0.5   # bajo esto la mora implícita describe una parte menor de la cartera: se deja vacía


def construir() -> pd.DataFrame:
    eq = json.loads(EQUIV.read_text(encoding="utf-8"))["equivalencias"]
    cart = pd.read_parquet(BANKS / "bk_cartera.parquet")
    sis = pd.read_parquet(BANKS / "bk_sistema_q.parquet")
    sis["periodo"] = pd.to_datetime(sis["fecha"]).dt.strftime("%Y%m")
    mora = sis.pivot_table(index="periodo", columns="serie_id", values="valor")

    cart = cart.copy()
    cart["serie_id"] = cart["modalidad_id"].map(lambda m: eq[m]["serie_id"])
    cart["mora_sis"] = [mora.at[p, s] if (s is not None and p in mora.index and s in mora.columns) else np.nan
                        for p, s in zip(cart["periodo"], cart["serie_id"])]
    tot = cart.groupby(["cod_inst", "periodo"])["saldo"].transform("sum")
    cart["w"] = cart["saldo"] / tot
    cub = cart[cart["mora_sis"].notna()]

    g = cub.groupby(["cod_inst", "periodo"])
    out = pd.DataFrame({
        "cobertura": g["w"].sum(),
        "mora_implicita": g.apply(lambda x: (x["w"] * x["mora_sis"]).sum() / x["w"].sum(), include_groups=False),
    })
    obs = cart.groupby(["cod_inst", "periodo"]).agg(v=("vencido15", "sum"), s=("saldo", "sum"))
    out["npl_observado"] = (obs["v"] / obs["s"]).reindex(out.index)
    out["brecha_pp"] = (out["npl_observado"] - out["mora_implicita"]) * 100
    out = out.reset_index()

    # Δ 4 trimestres de la mora implícita: efecto mix = Σ (w_t − w_t4) × mora_t4; efecto mora = Σ w_t × (mora_t − mora_t4),
    # con pesos renormalizados a la cartera cubierta en cada fecha. La suma de los dos es la Δ total.
    cub = cub.assign(wn=cub["w"] / cub.groupby(["cod_inst", "periodo"])["w"].transform("sum"))
    clave = ["cod_inst", "modalidad_id"]
    prev = cub[["cod_inst", "modalidad_id", "periodo", "wn", "mora_sis"]].copy()
    prev["periodo"] = (pd.to_datetime(prev["periodo"], format="%Y%m") + pd.DateOffset(months=12)).dt.strftime("%Y%m")
    par = cub[["cod_inst", "modalidad_id", "periodo", "wn", "mora_sis"]].merge(
        prev.rename(columns={"wn": "wn4", "mora_sis": "mora4"}), on=["periodo", *clave], how="outer")
    par[["wn", "wn4"]] = par[["wn", "wn4"]].fillna(0)
    mora_ref = par["mora4"].fillna(par["mora_sis"])
    par["mix"] = (par["wn"] - par["wn4"]) * mora_ref
    par["mor"] = par["wn"] * (par["mora_sis"] - par["mora4"]).fillna(0)
    ok = par.groupby(["cod_inst", "periodo"])["mora4"].transform(lambda s: s.notna().any())
    d = par[ok].groupby(["cod_inst", "periodo"])[["mix", "mor"]].sum() * 100
    d.columns = ["efecto_mix_pp", "efecto_mora_pp"]
    out = out.merge(d.reset_index(), on=["cod_inst", "periodo"], how="left")
    out["d_mora_implicita_aa_pp"] = out["efecto_mix_pp"] + out["efecto_mora_pp"]
    baja = out["cobertura"] < COBERTURA_MIN
    out.loc[baja | out["mora_implicita"].isna(), ["mora_implicita", "brecha_pp", "efecto_mix_pp", "efecto_mora_pp",
                                                   "d_mora_implicita_aa_pp"]] = np.nan
    out["fecha"] = pd.to_datetime(out["periodo"], format="%Y%m") + pd.offsets.MonthEnd(0)
    out["trimestre"] = out["periodo"].map(lambda p: f"{(int(p[4:]) - 1) // 3 + 1}T{p[2:4]}")
    quiebre = cart.groupby("cod_inst")["quiebre_2025"].first()
    out["quiebre_2025"] = out["cod_inst"].map(quiebre)
    cols = ["cod_inst", "periodo", "fecha", "trimestre", "cobertura", "mora_implicita", "npl_observado", "brecha_pp",
            "efecto_mix_pp", "efecto_mora_pp", "d_mora_implicita_aa_pp", "quiebre_2025"]
    return out[cols].sort_values(["periodo", "cod_inst"]).reset_index(drop=True)


def main() -> int:
    t = construir()
    b = io.BytesIO(); t.to_parquet(b, index=False); datos = b.getvalue()
    A.guardar_derivado("bcb_ifdata", "bancos_gold_exposicion", "bk_exposicion.parquet", datos,
                       desde=["bcb_ifdata/valores", "bcb_sgs/bancos_sistema"], como=COMANDO)
    A.escribir_atomico(BANKS / "bk_exposicion.parquet", datos)
    print(f"bk_exposicion: {len(t):,} filas, {t['periodo'].min()}–{t['periodo'].max()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
