# -*- coding: utf-8 -*-
"""Cartera de crédito por banco × modalidad (capa gold del dashboard de bancos): bk_cartera, bk_cartera_totales,
bk_cartera_grupo, bk_cartera_mix7 y las copias bk_cre_*.

POR QUÉ EXISTE
--------------
`preparar_credito_paginas_powerbi.py` ya lee los informes 11 (PF) y 13 (PJ) de IF.data y arma, por banco,
el saldo y el vencido ≥15 días de cada modalidad; pero solo publica agregados por grupo (`cre_*`), porque
la hoja del PBIP compara grupos, nunca bancos sueltos. La ficha por banco del dashboard web necesita el
dato por banco. En vez de copiar el parser (y dejar dos lecturas del mismo crudo que pueden divergir),
este módulo **importa** sus funciones (`periodos_credito`, `bancos`, `leer_credito`, `rupturas_frontera`)
y solo agrega lo que el panel por banco necesita. No toca `cre_*` ni el PBIP.

Reglas heredadas, que no se tocan (docstring de preparar_credito_paginas_powerbi.py):
- Cartera activa en Brasil de los informes 11 y 13; financeiro hasta 2024-T4 (vía cadastro) y prudencial desde 2025.
- NPL por modalidad = atraso ≥ 15 días.
- 2024-T4 vacío (trimestre anómalo del BCB, `trimestres_anomalos` en definiciones).
- Bancos con cambio de cobertura en la frontera 2025 (`rupturas_frontera`): su nivel se publica, pero
  quedan fuera de las variaciones que cruzan 2025-T1 (columna `quiebre_2025`).

Salidas (spec de datos §3.5 y decisión del arquitecto del 2026-11-02 sobre la tabla auxiliar):
- datos/gold/bk_cartera.parquet          banco × trimestre × tipo × modalidad
- datos/gold/bk_cartera_totales.parquet  totales publicados por el BCB (para que el verificador valide Σ modalidades)
- datos/gold/bk_cartera_grupo.parquet    mix y NPL por modalidad por grupo y panel, con la mora del sistema al lado (B8-03);
                                       desde 78b, columna `dirigido_peso` (ver abajo)
- datos/gold/bk_cartera_mix7.parquet     (78b) mix en 7 categorías por banco, grupo y panel (B3-03-0)
- datos/gold/bk_cre_panorama / bk_cre_calidad / bk_cre_contexto: copia de cre_* (aportes, calidad, ROE/NIM/CDI por grupo) para el sitio
Se escriben con almacen.guardar_derivado en datos/derivado/bcb_ifdata/bancos_gold_cartera/ y se copian a datos/gold/.

78b · Mix en 7 categorías (B3-03-0) y peso del dirigido aproximado
-------------------------------------------------------------------
Categorías: tarjeta, personal, consignado, vehículos, hipotecario, rural (personas) y PJ (empresas, todas las
modalidades, incluida Rural y agroindustrial de empresas). «Personal» = Personal sin consignación + Otros (personas).
Mapeo en `MIX7_PF` (personas) y regla por tipo (PJ → «PJ»); una modalidad sin mapeo hace fallar el script.

«Dirigido aproximado» (modalidades con fondeo o tasa regulada): Hipotecario + Rural y agroindustrial (personas)
+ Rural (empresas) + Inmobiliario (empresas) + Infraestructura y proyectos. Es una APROXIMACIÓN por modalidad del
informe 11/13 de IF.data; NO es el dirigido contable del BCB (que se define por destino del crédito y tasa,
no por nombre de modalidad).

`dirigido_peso` se publica en bk_cartera_mix7 (banco, grupo y panel, repetido en cada categoría del mismo
trimestre) y en bk_cartera_grupo (grupo y panel). Es el peso del dirigido aproximado sobre la cartera de Brasil.

Uso:  python -X utf8 preparar_gold_bancos_cartera.py               (reconstruye desde el crudo vía el parser de cre_*)
      python -X utf8 preparar_gold_bancos_cartera.py --solo-mix7  (lee datos/gold/bk_cartera*.parquet; reescribe
                                                                   solo bk_cartera_grupo y bk_cartera_mix7)
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import almacen as A
import preparar_credito_paginas_powerbi as C

RAIZ = Path(__file__).resolve().parents[1]
BANKS = RAIZ / "datos" / "gold"
FUENTE, DATASET = "bcb_ifdata", "bancos_gold_cartera"
COMANDO = "python -X utf8 preparar_gold_bancos_cartera.py"

# 78b: constante para el manifiesto (el arquitecto la integra en `base`).
TABLA_MIX7 = "bk_cartera_mix7"

# Personas: modalidad_id → categoría de 7. Empresas (tipo PJ) van todas a «PJ».
MIX7_PF = {
    "pf_tarjeta": "tarjeta",
    "pf_consignado": "consignado",
    "pf_personal": "personal",      # Personal sin consignación
    "pf_otros": "personal",         # Otros (personas) se suma a «Personal»
    "pf_vehiculos": "vehiculos",
    "pf_hipotecario": "hipotecario",
    "pf_rural": "rural",            # Rural y agroindustrial (personas)
}
ETIQUETA_MIX7 = {
    "tarjeta": "Tarjeta de crédito",
    "personal": "Personal (sin consignación y otros personas)",
    "consignado": "Consignado",
    "vehiculos": "Vehículos",
    "hipotecario": "Hipotecario",
    "rural": "Rural y agroindustrial (personas)",
    "PJ": "Empresas (todas las modalidades, incluida rural)",
}
# Dirigido aproximado (ver docstring): nombres de modalidad_id de bk_cartera.
DIRIGIDO = ["pf_hipotecario", "pf_rural", "pj_rural", "pj_inmobiliario", "pj_infra"]
ETIQUETA_DIRIGIDO = "Dirigido aproximado (modalidades con fondeo o tasa regulada)"


def _trimestre(periodo: str) -> str:
    return f"{(int(periodo[4:]) - 1) // 3 + 1}T{periodo[2:4]}"


def _menos(periodo: str, k: int) -> str:
    p = pd.Period(f"{periodo[:4]}-{periodo[4:]}", "M") - 3 * k
    return f"{p.year}{p.month:02d}"


def _modelo_por_banco() -> dict:
    raiz = Path(__file__).resolve().parents[1]
    return {b["cod_inst"]: b["modelo_negocio"] for b in
            json.loads((raiz / "definiciones" / "bcb_ifdata__bancos_balances.json").read_text(encoding="utf-8"))["bancos"]}


def construir() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    defs = json.loads(C.DEF_MODALIDADES.read_text(encoding="utf-8"))
    inst = C.bancos()
    panel = inst["cod_inst"].tolist()
    periodos = C.periodos_credito()
    credito, totales = C.leer_credito(periodos, panel, defs)
    anomalos = list(defs.get("trimestres_anomalos", {}))
    credito = credito[~credito["periodo"].isin(anomalos)]
    totales = totales[~totales["periodo"].isin(anomalos)]
    bal = pd.read_parquet(BANKS / "bank_balances.parquet")
    ruptura = C.rupturas_frontera(credito, bal, periodos, panel, anomalos)

    etiqueta = {m["id"]: m["etiqueta"] for t in defs["tipos"].values() for m in t["modalidades"]}
    ancho = (credito.pivot_table(index=["periodo", "cod_inst", "tipo", "modalidad"], columns="medida",
                                 values="valor", aggfunc="sum")
             .reset_index().rename(columns={"vencido": "vencido15"}))
    ancho.columns.name = None
    ancho["modalidad_id"] = ancho["modalidad"]
    ancho["modalidad"] = ancho["modalidad_id"].map(etiqueta)
    ancho["npl15"] = np.where(ancho["saldo"] > 0, ancho["vencido15"] / ancho["saldo"], np.nan)
    total_banco = ancho.groupby(["periodo", "cod_inst"])["saldo"].transform("sum")
    ancho["peso_banco"] = np.where(total_banco > 0, ancho["saldo"] / total_banco, np.nan)
    total_mod = ancho.groupby(["periodo", "modalidad_id"])["saldo"].transform("sum")
    ancho["cuota_modalidad"] = np.where(total_mod > 0, ancho["saldo"] / total_mod, np.nan)

    # Δ cuota a/a con muestra constante: la cuota de t−4 se recalcula solo con los bancos presentes en t y
    # en t−4 en esa modalidad; los bancos con ruptura de cobertura quedan fuera si el par cruza 2025-T1.
    clave = ["cod_inst", "modalidad_id"]
    previo = ancho[["periodo", *clave, "saldo"]].copy()
    previo["periodo"] = previo["periodo"].map(lambda p: _menos(p, -4))  # t−4 desplazado a t
    par = ancho.merge(previo.rename(columns={"saldo": "saldo_t4"}), on=["periodo", *clave], how="left")
    cruza = (par["periodo"] >= C.PRIMER_PRUDENCIAL) & (par["periodo"].map(lambda p: _menos(p, 4)) < C.PRIMER_PRUDENCIAL)
    valido = par["saldo"].notna() & par["saldo_t4"].notna() & ~(cruza & par["cod_inst"].isin(ruptura))
    sub = par[valido]
    tot_t = sub.groupby(["periodo", "modalidad_id"])["saldo"].transform("sum")
    tot_t4 = sub.groupby(["periodo", "modalidad_id"])["saldo_t4"].transform("sum")
    d = (sub["saldo"] / tot_t - sub["saldo_t4"] / tot_t4) * 100
    par["d_cuota_aa"] = np.nan
    par.loc[sub.index, "d_cuota_aa"] = d.values
    par["quiebre_2025"] = par["cod_inst"].isin(ruptura)
    par["fecha"] = pd.to_datetime(par["periodo"], format="%Y%m") + pd.offsets.MonthEnd(0)
    par["trimestre"] = par["periodo"].map(_trimestre)
    cartera = par[["cod_inst", "periodo", "fecha", "trimestre", "tipo", "modalidad_id", "modalidad", "saldo",
                   "vencido15", "npl15", "peso_banco", "cuota_modalidad", "d_cuota_aa", "quiebre_2025"]]
    cartera = cartera.sort_values(["periodo", "cod_inst", "tipo", "modalidad_id"]).reset_index(drop=True)

    tot = totales.copy()
    tot["brasil"] = tot["publicado"] - tot["exterior"].fillna(0)
    tot = tot[["cod_inst", "periodo", "tipo", "publicado", "exterior", "brasil"]].sort_values(
        ["periodo", "cod_inst", "tipo"]).reset_index(drop=True)
    return cartera, tot, ruptura


def cartera_grupo(cartera: pd.DataFrame) -> pd.DataFrame:
    """Mix y NPL por modalidad para cada grupo de Modelo de negocio y para el panel (B8-03).

    Agregados por suma (saldo y vencido) con los bancos que tienen dato en el trimestre; la mora del sistema por
    modalidad (SGS > 90 días, equivalencias de definiciones/bancos__equivalencias_mora.json) va en su propia columna
    para que la tarjeta la muestre al lado, nunca en el mismo eje que el NPL.
    78b: `dirigido_peso` = saldo de las modalidades DIRIGIDO / saldo de Brasil del grupo y trimestre (aproximación).
    """
    raiz = Path(__file__).resolve().parents[1]
    eq = json.loads((raiz / "definiciones" / "bancos__equivalencias_mora.json").read_text(encoding="utf-8"))["equivalencias"]
    modelo = _modelo_por_banco()
    c = cartera.assign(grupo=cartera["cod_inst"].map(modelo))
    partes = []
    for optica, col in (("Modelo de negocio", "grupo"), ("Total panel", None)):
        claves = ["periodo", "tipo", "modalidad_id", "modalidad"] + ([col] if col else [])
        g = c.groupby(claves, as_index=False).agg(saldo=("saldo", "sum"), vencido15=("vencido15", "sum"),
                                                 n_bancos=("cod_inst", "nunique"))
        if not col:
            g["grupo"] = "Total panel"
        g["optica"] = optica
        partes.append(g)
    g = pd.concat(partes, ignore_index=True)
    # Filas de total por tipo (PF, PJ) y de la cartera completa, para el NPL agregado del grupo y del panel.
    tot = []
    for tipo, f in (("PF", g["tipo"] == "PF"), ("PJ", g["tipo"] == "PJ"), ("total", g["tipo"].notna())):
        t = g[f].groupby(["optica", "grupo", "periodo"], as_index=False).agg(
            saldo=("saldo", "sum"), vencido15=("vencido15", "sum"), n_bancos=("n_bancos", "max"))
        t["tipo"], t["modalidad_id"] = tipo, f"total_{tipo.lower()}"
        t["modalidad"] = {"PF": "Total personas", "PJ": "Total empresas", "total": "Total cartera"}[tipo]
        tot.append(t)
    g = pd.concat([g, *tot], ignore_index=True)
    g["npl15"] = np.where(g["saldo"] > 0, g["vencido15"] / g["saldo"], np.nan)
    es_mod = ~g["modalidad_id"].str.startswith("total_")
    base = g[es_mod].groupby(["optica", "grupo", "periodo"])["saldo"].sum()
    g["peso"] = g["saldo"] / g.set_index(["optica", "grupo", "periodo"]).index.map(base)
    # 78b: peso del dirigido aproximado por grupo (y panel) y trimestre; mismo valor en todas las filas del grupo.
    keys = ["optica", "grupo", "periodo"]
    dsal = g[g["modalidad_id"].isin(DIRIGIDO)].groupby(keys)["saldo"].sum().rename("dir").reset_index()
    bsal = g[es_mod].groupby(keys)["saldo"].sum().rename("tot").reset_index()
    m = g[keys].merge(dsal, on=keys, how="left").merge(bsal, on=keys, how="left")
    g["dirigido_peso"] = np.where(m["tot"] > 0, m["dir"].fillna(0) / m["tot"], np.nan)
    sis = pd.read_parquet(BANKS / "bk_sistema_q.parquet")
    sis["periodo"] = pd.to_datetime(sis["fecha"]).dt.strftime("%Y%m")
    mora = sis.set_index(["periodo", "serie_id"])["valor"]
    g["mora_sistema"] = [mora.get((p, eq[m]["serie_id"]), np.nan) if m in eq and eq[m]["serie_id"] else np.nan
                         for p, m in zip(g["periodo"], g["modalidad_id"])]
    g["calidad_equivalencia"] = g["modalidad_id"].map(lambda m: eq[m]["calidad"] if m in eq else None)
    g["fecha"] = pd.to_datetime(g["periodo"], format="%Y%m") + pd.offsets.MonthEnd(0)
    g["trimestre"] = g["periodo"].map(_trimestre)
    cols = ["optica", "grupo", "periodo", "fecha", "trimestre", "tipo", "modalidad_id", "modalidad", "saldo",
            "vencido15", "npl15", "peso", "n_bancos", "mora_sistema", "calidad_equivalencia", "dirigido_peso"]
    return g[cols].sort_values(["periodo", "optica", "grupo", "tipo", "modalidad_id"]).reset_index(drop=True)


def categoria_mix7(tipo: str, modalidad_id: str) -> str:
    """Categoría de 7 del mix (B3-03-0). Modalidad de persona sin mapeo lanza KeyError: no se adivina."""
    return "PJ" if tipo == "PJ" else MIX7_PF[modalidad_id]


def mix7(cartera: pd.DataFrame) -> pd.DataFrame:
    """Mix en 7 categorías por banco (nivel 'banco'), por grupo de Modelo de negocio ('grupo') y panel ('panel').

    Grupo y panel son cociente de sumas de saldos de los bancos con dato en el trimestre (nunca promedio de pesos).
    `peso` = saldo de la categoría / saldo de Brasil del mismo nivel, trimestre y banco o grupo.
    `dirigido_peso` = saldo de DIRIGIDO / saldo de Brasil (aproximación, ver docstring del módulo), repetido en cada
    categoría del mismo trimestre; sirve para leer el dirigido sin sumar categorías.
    """
    modelo = _modelo_por_banco()
    c = cartera[["cod_inst", "periodo", "fecha", "trimestre", "tipo", "modalidad_id", "saldo"]].copy()
    c["categoria"] = [categoria_mix7(t, m) for t, m in zip(c["tipo"], c["modalidad_id"])]
    c["dirigido"] = c["modalidad_id"].isin(DIRIGIDO)
    c["modelo"] = c["cod_inst"].map(modelo).fillna("Sin modelo")
    a = pd.concat([
        c.assign(nivel="banco", optica="Banco", grupo=c["modelo"], cod=c["cod_inst"]),
        c.assign(nivel="grupo", optica="Modelo de negocio", grupo=c["modelo"], cod=""),
        c.assign(nivel="panel", optica="Total panel", grupo="Total panel", cod=""),
    ], ignore_index=True)
    keys = ["nivel", "optica", "grupo", "cod", "periodo", "fecha", "trimestre"]
    s = a.groupby(keys + ["categoria"], as_index=False)["saldo"].sum()
    tot = a.groupby(keys, as_index=False)["saldo"].sum().rename(columns={"saldo": "total"})
    dir_ = a[a["dirigido"]].groupby(keys, as_index=False)["saldo"].sum().rename(columns={"saldo": "dirigido"})
    s = s.merge(tot, on=keys, how="left").merge(dir_, on=keys, how="left")
    s["dirigido"] = s["dirigido"].fillna(0.0)
    s["peso"] = np.where(s["total"] > 0, s["saldo"] / s["total"], np.nan)
    s["dirigido_peso"] = np.where(s["total"] > 0, s["dirigido"] / s["total"], np.nan)
    s["categoria_etiqueta"] = s["categoria"].map(ETIQUETA_MIX7)
    s = s.rename(columns={"cod": "cod_inst"})
    s["cod_inst"] = s["cod_inst"].replace("", None)
    cols = ["nivel", "optica", "grupo", "cod_inst", "periodo", "fecha", "trimestre", "categoria", "categoria_etiqueta",
            "saldo", "peso", "total", "dirigido_peso"]
    return s[cols].sort_values(["nivel", "optica", "grupo", "cod_inst", "periodo", "categoria"],
                               na_position="first").reset_index(drop=True)


def verificar_mix7(mix: pd.DataFrame, cartera_saldo: pd.DataFrame | None = None) -> list[str]:
    """Σ peso = 1 en cada banco, grupo y panel con saldo; Σ saldo de banco = cartera_saldo de bk_panel (si se pasa);
    dirigido_peso en [0, 1]; 2024-T4 ausente."""
    errores = []
    k = ["nivel", "optica", "grupo", "cod_inst", "periodo"]
    r = mix.groupby(k, dropna=False).agg(peso=("peso", "sum"), total=("total", "first"), saldo=("saldo", "sum")).reset_index()
    r = r[r["total"] > 0]
    malos = r[(r["peso"] - 1).abs() > 1e-9]
    if len(malos):
        errores.append(f"{len(malos)} filas con Σ peso ≠ 1 en bk_cartera_mix7; ej.:\n{malos.head(5).to_string(index=False)}")
    if cartera_saldo is not None:
        b = r[r["nivel"] == "banco"].merge(cartera_saldo, on=["cod_inst", "periodo"], how="inner")
        dif = (b["saldo"] / b["valor"] - 1).abs()
        dif = dif[b["valor"] > 0]
        if (dif > 1e-6).any():
            errores.append(f"{(dif > 1e-6).sum()} bancos con Σ saldo mix7 ≠ cartera_saldo de bk_panel")
    d = mix["dirigido_peso"].dropna()
    if ((d < 0) | (d > 1)).any():
        errores.append("dirigido_peso fuera de [0, 1] en bk_cartera_mix7")
    if (mix["periodo"] == "202412").any():
        errores.append("bk_cartera_mix7 tiene 2024-T4 y debía quedar vacío")
    return errores


def verificar(cartera: pd.DataFrame, tot: pd.DataFrame) -> list[str]:
    """Σ modalidades por banco = total publicado − exterior (tolerancia de cre_*); 2024-T4 ausente; npl en [0, 1]."""
    errores = []
    s = cartera.groupby(["periodo", "cod_inst", "tipo"])["saldo"].sum(min_count=1).rename("suma").reset_index()
    m = s.merge(tot, on=["periodo", "cod_inst", "tipo"], how="inner")
    m = m[m["brasil"].abs() > 0]
    dif = (m["suma"] / m["brasil"] - 1).abs()
    malos = m[dif > C.TOLERANCIA_TOTAL]
    if len(malos):
        errores.append(f"{len(malos)} combinaciones banco×tipo×trimestre con Σ modalidades ≠ total Brasil "
                       f"(> {C.TOLERANCIA_TOTAL:.1%}); ej.:\n{malos.head(8).to_string(index=False)}")
    if (cartera["periodo"] == "202412").any():
        errores.append("2024-T4 tiene filas y debía quedar vacío")
    fuera = cartera["npl15"].dropna()
    if ((fuera < 0) | (fuera > 1)).any():
        errores.append(f"npl15 fuera de [0, 1] en {((fuera < 0) | (fuera > 1)).sum()} filas")
    return errores


def _bytes(df: pd.DataFrame) -> bytes:
    b = io.BytesIO()
    df.to_parquet(b, index=False)
    return b.getvalue()


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    solo = "--solo-mix7" in argv
    if solo:
        # Reusa la salida ya verificada de bk_cartera (no reconstruye desde el crudo).
        cartera = pd.read_parquet(BANKS / "bk_cartera.parquet")
        tot = pd.read_parquet(BANKS / "bk_cartera_totales.parquet")
        ruptura = None
    else:
        cartera, tot, ruptura = construir()
    errores = verificar(cartera, tot)
    mix = mix7(cartera)
    panel = pd.read_parquet(BANKS / "bk_panel.parquet")
    saldo_panel = panel.loc[panel["metrica"] == "cartera_saldo", ["cod_inst", "periodo", "valor"]]
    errores += verificar_mix7(mix, saldo_panel)

    tablas = []
    if not solo:
        tablas += [
            ("bk_cartera.parquet", cartera, ["bcb_ifdata/valores", "bcb_ifdata/cadastro"]),
            ("bk_cartera_totales.parquet", tot, ["bcb_ifdata/valores", "bcb_ifdata/cadastro"]),
        ]
    tablas += [
        ("bk_cartera_grupo.parquet", cartera_grupo(cartera), ["bcb_ifdata/valores", "bcb_ifdata/cadastro",
                                                              "bcb_sgs/bancos_sistema"]),
        (f"{TABLA_MIX7}.parquet", mix, ["bcb_ifdata/valores", "bcb_ifdata/cadastro"]),
    ]
    if not solo:
        # cre_panorama y cre_calidad (preparar_credito_paginas_powerbi.py) ya traen los aportes al crecimiento y la
        # calidad por grupo con muestra constante: se copian tal cual a la capa gold, sin recalcular nada.
        # Única transformación: ±inf (crecimientos con base cero en cre_panorama) → vacío, porque JSON no admite inf.
        tablas += [
            ("bk_cre_panorama.parquet", pd.read_parquet(RAIZ / "datos" / "intermedio" / "cre_panorama.parquet").replace([np.inf, -np.inf], np.nan),
             ["datos/intermedio/cre_panorama.parquet"]),
            ("bk_cre_calidad.parquet", pd.read_parquet(RAIZ / "datos" / "intermedio" / "cre_calidad.parquet"), ["datos/intermedio/cre_calidad.parquet"]),
            ("bk_cre_contexto.parquet", pd.read_parquet(RAIZ / "datos" / "intermedio" / "cre_contexto.parquet"), ["datos/intermedio/cre_contexto.parquet"]),
        ]
    for nombre, df, desde in tablas:
        datos = _bytes(df)
        A.guardar_derivado(FUENTE, DATASET, nombre, datos, desde=desde, como=COMANDO)
        A.escribir_atomico(BANKS / nombre, datos)
        print(f"{nombre}: {len(df):,} filas, {df['periodo'].min()}–{df['periodo'].max()}")
    if ruptura is not None:
        print(f"bancos con ruptura de cobertura en 2025: {ruptura}")
    for e in errores:
        print(f"[ERROR] {e}")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
