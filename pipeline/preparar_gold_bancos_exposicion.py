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
Salida:   datos/gold/bk_exposicion.parquet (banco × trimestre).
Uso:      python -X utf8 pipeline/preparar_gold_bancos_exposicion.py
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import almacen as A
import periodos as PER
import reglas_gold as RG
from mora_sistema import equivalencias_mora, mora_sistema



def construir() -> pd.DataFrame:
    cart = pd.read_parquet(A.GOLD / "bk_cartera.parquet")
    sin_equivalencia = sorted(set(cart["modalidad_id"]) - set(equivalencias_mora()))
    if sin_equivalencia:
        raise KeyError(f"modalidades sin equivalencia en bancos__equivalencias_mora.json: {sin_equivalencia}")
    cart["mora_sis"] = mora_sistema(cart["periodo"], cart["modalidad_id"])
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
    prev["periodo"] = PER.previo_serie(prev["periodo"], -4)
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
    baja = out["cobertura"] < RG.COBERTURA_MIN
    out.loc[baja | out["mora_implicita"].isna(), ["mora_implicita", "brecha_pp", "efecto_mix_pp", "efecto_mora_pp",
                                                   "d_mora_implicita_aa_pp"]] = np.nan
    out["fecha"] = PER.fin_de_mes(out["periodo"])
    out["trimestre"] = out["periodo"].map(PER.etiqueta_trimestre)
    quiebre = cart.groupby("cod_inst")["quiebre_2025"].first()
    out["quiebre_2025"] = out["cod_inst"].map(quiebre)
    cols = ["cod_inst", "periodo", "fecha", "trimestre", "cobertura", "mora_implicita", "npl_observado", "brecha_pp",
            "efecto_mix_pp", "efecto_mora_pp", "d_mora_implicita_aa_pp", "quiebre_2025"]
    return out[cols].sort_values(["periodo", "cod_inst"]).reset_index(drop=True)


def main(argv: list[str] | None = None) -> int:
    t = construir()
    A.publicar_gold("bk_exposicion", t, dataset="bancos_gold_exposicion",
                    desde=["gold/bk_cartera.parquet", "gold/bk_sistema_q.parquet"])
    print(f"bk_exposicion: {len(t):,} filas, {t['periodo'].min()}–{t['periodo'].max()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
