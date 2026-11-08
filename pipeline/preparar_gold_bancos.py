# -*- coding: utf-8 -*-
"""Capa gold base del dashboard de bancos: tablas bk_* que leen el sitio, y el puente IF.Data ↔ publicado.

POR QUÉ EXISTE
--------------
El sitio de bancos no calcula nada («Python calcula, el navegador dibuja»,
docs/SPEC_DATOS_BANCOS_v0.1.md §1.3). Las fórmulas viven aquí, una sola vez, y el
sitio lee tablas ya listas. Este subcomando (``base``) no baja nada de la red: reordena lo que ya
existe —el panel de métricas por banco y trimestre (``datos/intermedio/metricas_bancos.parquet``), las
dimensiones de los bancos (``bancos.py``), las métricas (``registro_metricas.py``) y el cruce IF.Data ↔
publicado (``definiciones/validacion_bancos.json``)— y lo entrega en cinco tablas: ``bk_banco``, ``bk_metrica``
(definición de cada métrica), ``bk_panel`` (banco × trimestre × métrica, con rezagos, percentiles del grupo y
rankings), ``bk_grupo`` (óptica × grupo × trimestre × métrica, con muestra constante) y ``bk_puente``.

Reglas que no se tocan: no se recalculan TTM, ROE, ROA, cuotas ni crédito total (salen de
preparar_metricas_bancos.py). Los agregados de grupo son sumas o cocientes de sumas, nunca promedios de ratios.
Lo que no tiene definición segura queda en null.

Uso:

    python -X utf8 pipeline/preparar_gold_bancos.py base

El subcomando ``rentabilidad`` (encargo 64) añade ``bk_roe_arbol`` (árbol del ROE por banco y
por grupo) y ``bk_sensibilidad`` (beta del NIM contra el CDI); no reescribe las tablas de base.

    python -X utf8 pipeline/preparar_gold_bancos.py rentabilidad
"""
from __future__ import annotations

import argparse
import math
import sys

import numpy as np
import pandas as pd

import almacen as A
import bancos as B
import periodos as PER
import registro_metricas as R
import reglas_gold as RG
import sgs as SG

ENTRADA_METRICAS = A.INTERMEDIO / "metricas_bancos.parquet"
ENTRADA_INSTITUCIONES = A.GOLD / "bank_instituciones.parquet"
ENTRADA_SISTEMA_Q = A.GOLD / "bk_sistema_q.parquet"
ENTRADA_CARTERA = A.GOLD / "bk_cartera.parquet"
ENTRADA_MIX7 = A.GOLD / "bk_cartera_mix7.parquet"

DATASET_DERIVADO = "bancos_gold"

def _fecha(periodos: pd.Series) -> pd.Series:
    return PER.fin_de_mes(periodos).dt.date


# valor_tt y credito_real_aa necesitan trimestre anterior, quiebre 2025 y el IPCA de bk_sistema_q.
SERIE_IPCA_12M = "ipca_12m"        # fracción, valor del último mes del trimestre


def _real_desde_nominal(nominal, ipca):
    """Crecimiento real: (1 + nominal) / (1 + IPCA 12 meses) − 1, ambos en fracción."""
    return (1 + nominal) / (1 + ipca) - 1


def _ipca_12m_trimestral() -> pd.Series:
    """IPCA acumulado 12 meses por periodo AAAAMM (mes final del trimestre), fracción, desde bk_sistema_q.

    No se aproxima con el año calendario ni con otra serie: sin ipca_12m, la corrida falla.
    """
    if not ENTRADA_SISTEMA_Q.exists():
        raise FileNotFoundError("falta bk_sistema_q.parquet: correr antes «actualizar.py --desde sistema» (preparar_gold_bancos_sistema.py)")
    s = pd.read_parquet(ENTRADA_SISTEMA_Q, columns=["fecha", "serie_id", "valor"])
    s = s[s["serie_id"].eq(SERIE_IPCA_12M)]
    if s.empty:
        raise ValueError("bk_sistema_q no tiene la serie ipca_12m")
    fecha = pd.to_datetime(s["fecha"])
    s = s[fecha.dt.month.isin([3, 6, 9, 12]).to_numpy()]
    periodo = pd.to_datetime(s["fecha"]).dt.strftime("%Y%m").to_numpy()
    return pd.Series(s["valor"].to_numpy(float), index=periodo).groupby(level=0).last().sort_index()


def _bk_banco() -> pd.DataFrame:
    inst = pd.read_parquet(ENTRADA_INSTITUCIONES)
    inst["cod_inst"] = inst["cod_inst"].astype(str)
    universo = B.universo()
    bal = pd.DataFrame(universo)
    bal = bal[["cod_inst", "modelo_negocio", "nota"]].rename(columns={"modelo_negocio": "modelo"})
    dash = pd.DataFrame(A.leer_definicion(B.DEF_DASHBOARD)["bancos"])
    if "nota" not in dash:
        dash["nota"] = None
    dash = dash[["cod_inst", "slug", "cotizado", "ticker", "ticker_estado", "ficha", "color", "nota"]]
    dash = dash.rename(columns={"nota": "nota_dashboard"})
    t = (inst[["cod_inst", "nombre_corto", "institucion_bcb_ultima", "sr", "tc",
               "primer_periodo", "ultimo_periodo"]]
         .merge(bal, on="cod_inst", how="left", validate="1:1")
         .merge(dash, on="cod_inst", how="left", validate="1:1"))
    if len(t) != len(universo):
        raise ValueError(f"bk_banco: se esperaban {len(universo)} bancos y hay {len(t)}")
    if t["modelo"].isna().any() or t["slug"].isna().any():
        raise ValueError("bk_banco: falta modelo_negocio o slug para algún banco")
    sr = t["sr"].fillna("").astype(str).str.strip()
    t["segmento_reg"] = sr.mask(sr == "", "Sin segmento")
    t["propiedad"] = t["tc"].astype(str).str.strip().map(B.PROPIEDAD)
    if t["propiedad"].isna().any():
        raise ValueError("bk_banco: tc fuera de 1, 2, 3")
    t["fintech"] = B.fintech(t["modelo"])
    t["segmento_ref"] = np.select(
        [t["propiedad"].eq("Público"), t["modelo"].isin(B.MODELOS_FINTECH), t["segmento_reg"].eq("S1")],
        ["Públicos", "Digitales", "S1 privados"], default="Demás")
    # La nota del dashboard (lectura para el usuario) se suma a la de balances (identidad del conglomerado).
    t["nota"] = [" ".join(x for x in (a, b) if isinstance(x, str) and x) or None
                 for a, b in zip(t["nota"], t["nota_dashboard"])]
    t = t.rename(columns={"institucion_bcb_ultima": "institucion_bcb"})
    cols = ["cod_inst", "slug", "nombre_corto", "institucion_bcb", "modelo", "segmento_reg",
            "propiedad", "fintech", "segmento_ref", "cotizado", "ticker", "ticker_estado",
            "ficha", "color", "nota", "primer_periodo", "ultimo_periodo"]
    return t[cols].sort_values("nombre_corto").reset_index(drop=True)


def _cargar_ancho(cods: list[str]) -> tuple[pd.DataFrame, pd.MultiIndex]:
    m = pd.read_parquet(ENTRADA_METRICAS)
    m["cod_inst"] = m["cod_inst"].astype(str)
    m["periodo"] = m["periodo"].astype(str)
    if set(m["cod_inst"]) != set(cods):
        raise ValueError("metricas_bancos.parquet tiene bancos distintos de bk_banco")
    if m.duplicated(["cod_inst", "periodo", "metrica"]).any():
        raise ValueError("metricas_bancos.parquet tiene filas duplicadas")
    periodos = sorted(m["periodo"].unique())
    qis = [PER.qi(p) for p in periodos]
    if qis != list(range(qis[0], qis[0] + len(qis))):
        raise ValueError("los trimestres de metricas_bancos no son contiguos")
    grilla = pd.MultiIndex.from_product([sorted(cods), periodos], names=["cod_inst", "periodo"])
    w = (m.set_index(["cod_inst", "periodo", "metrica"])["valor"]
         .unstack("metrica").reindex(grilla))
    w.columns.name = "metrica"
    # Cartera por modalidad (bk_cartera, informes 11 y 13): NPL total y peso de personas.
    if not ENTRADA_CARTERA.exists():
        raise FileNotFoundError("falta bk_cartera.parquet: correr antes «actualizar.py --desde cartera» (preparar_gold_bancos_cartera.py)")
    c = pd.read_parquet(ENTRADA_CARTERA)
    agg = c.groupby(["cod_inst", "periodo"]).agg(cartera_saldo=("saldo", "sum"),
                                                  cartera_vencido15=("vencido15", "sum"))
    agg["cartera_saldo_pf"] = c[c["tipo"] == "PF"].groupby(["cod_inst", "periodo"])["saldo"].sum()
    agg = agg.reindex(grilla)
    for col in agg.columns:
        w[col] = agg[col]
    for m in R.RAZONES:   # las razones que necesitan la cartera
        if m not in w.columns:
            w[m] = R.valor_banco(w, m)
    # Numerador y denominador de eficiencia_ttm (el gasto en positivo: las despesas vienen en negativo).
    w["gasto_total_ttm"] = R.numerador(w, "eficiencia_ttm")
    w["ingreso_total_ttm"] = R.denominador(w, "eficiencia_ttm")
    # Encargo 78a §2: crecimiento real a/a del crédito con el IPCA 12 meses del trimestre.
    ipca = _ipca_12m_trimestral().reindex(w.index.get_level_values("periodo")).to_numpy()
    w["credito_real_aa"] = _real_desde_nominal(w["credito_aa"].to_numpy(float), ipca)
    return w, grilla


def _serie(df: pd.DataFrame, col: str) -> pd.Series:
    idx = pd.MultiIndex.from_arrays([df["cod_inst"].to_numpy(), df["periodo"].to_numpy(),
                                     df["metrica"].to_numpy()],
                                    names=["cod_inst", "periodo", "metrica"])
    return pd.Series(df[col].to_numpy(), index=idx)


def _rezago(serie: pd.Series, k: int, grilla: pd.MultiIndex) -> pd.Series:
    """Valor de hace k trimestres para cada (banco, periodo, métrica); vacío si el trimestre no existe."""
    ancho = serie.unstack("metrica").reindex(grilla)
    return ancho.groupby(level="cod_inst").shift(k).stack(future_stack=True)


def _tomar(serie: pd.Series, df: pd.DataFrame) -> np.ndarray:
    idx = pd.MultiIndex.from_arrays([df["cod_inst"].to_numpy(), df["periodo"].to_numpy(),
                                     df["metrica"].to_numpy()],
                                    names=["cod_inst", "periodo", "metrica"])
    return serie.reindex(idx).to_numpy()


def _variacion(valor: pd.Series, previo: pd.Series, unidad: pd.Series):
    """ratio → diferencia en pp; brl → variación en fracción; indice → diferencia absoluta."""
    dif = valor - previo
    base = previo.abs().where(previo.abs() > 0)
    pct = dif / base
    es = [(unidad == "ratio").to_numpy(), (unidad == "brl").to_numpy(), (unidad == "indice").to_numpy()]
    d = np.select(es, [dif.to_numpy() * 100, pct.to_numpy(), dif.to_numpy()], default=np.nan)
    ud = np.select(es, ["pp", "fraccion", "abs"], default="")
    return d, np.where(ud == "", None, ud)


def _bk_panel(w: pd.DataFrame, banco: pd.DataFrame, meta: pd.DataFrame, grilla: pd.MultiIndex,
              quiebre: set[str]) -> pd.DataFrame:
    # explícito: pandas 2 descartaba los NaN en stack() y pandas 3 no (spec/08, pendiente 3b)
    L = w.stack(future_stack=True).dropna().rename("valor").reset_index()
    L["modelo"] = L["cod_inst"].map(dict(zip(banco["cod_inst"], banco["modelo"])))
    L["unidad"] = L["metrica"].map(meta["unidad"])
    L["fecha"] = _fecha(L["periodo"])
    L["trimestre"] = L["periodo"].map(PER.etiqueta_trimestre)

    s = _serie(L, "valor")
    L["valor_t1"] = _tomar(_rezago(s, 1, grilla), L)
    L["valor_t4"] = _tomar(_rezago(s, 4, grilla), L)
    L["d_tt"], L["unidad_d"] = _variacion(L["valor"], L["valor_t1"], L["unidad"])
    L["d_aa"], _ = _variacion(L["valor"], L["valor_t4"], L["unidad"])
    # Encargo 78a §1: valor_tt es la misma variación que d_tt, pero vacía si cruza 2024-T4 o si el banco
    # tiene quiebre 2025 en 2025-T1. d_tt se deja como estaba (lo leen las páginas).
    L["valor_tt"] = L["d_tt"].where(PER.variacion_valida(L["periodo"], 1, L["cod_inst"].isin(quiebre)))

    clave = ["metrica", "periodo", "modelo"]
    g = L.groupby(clave)["valor"]
    est = pd.DataFrame({"n_grupo": g.count(), "p10_grupo": g.quantile(0.10),
                        "p50_grupo": g.quantile(0.50), "p90_grupo": g.quantile(0.90)}).reset_index()
    L = L.merge(est, on=clave, how="left")
    chico = L["n_grupo"] < RG.MIN_GRUPO_PERCENTIL
    for c in ["p10_grupo", "p50_grupo", "p90_grupo"]:
        L.loc[chico, c] = np.nan
    L["pct_grupo"] = L.groupby(clave)["valor"].rank(pct=True)
    L.loc[chico, "pct_grupo"] = np.nan
    L["pct_panel"] = L.groupby(["metrica", "periodo"])["valor"].rank(pct=True)

    ranq = L["metrica"].isin(R.RANKEABLES)
    L["rank_panel"] = np.nan
    L.loc[ranq, "rank_panel"] = (L.loc[ranq].groupby(["metrica", "periodo"])["valor"]
                                 .rank(ascending=False, method="min"))
    L["rank_panel_t4"] = _tomar(_rezago(_serie(L, "rank_panel"), 4, grilla), L)

    cols = ["cod_inst", "periodo", "fecha", "trimestre", "metrica", "valor", "valor_t1", "valor_t4",
            "d_tt", "d_aa", "valor_tt", "unidad_d", "p10_grupo", "p50_grupo", "p90_grupo", "pct_grupo", "pct_panel",
            "rank_panel", "rank_panel_t4", "modelo", "n_grupo"]
    return L[cols].sort_values(["cod_inst", "periodo", "metrica"]).reset_index(drop=True)


def _membresia(banco: pd.DataFrame) -> pd.DataFrame:
    """Grupo × banco de cada óptica (bancos.pertenencia), con los bancos en el orden de bk_banco."""
    attrs = B.atributos().set_index("cod_inst").loc[banco["cod_inst"]].reset_index()
    return B.pertenencia(attrs)[["inst_key", "cod_inst", "optica", "grupo", "orden_optica", "orden_grupo"]]


def _estadisticas(fb: pd.DataFrame, m: str) -> pd.DataFrame:
    """Bancos con dato, mediana y cuartiles por grupo y trimestre (sin cambios frente a la versión anterior)."""
    bl = fb[["inst_key", "periodo", m]].dropna(subset=[m]).groupby(["inst_key", "periodo"])[m]
    return pd.concat([bl.count().rename("n_bancos"), bl.median().rename("mediana"),
                      bl.quantile(0.25).rename("p25"), bl.quantile(0.75).rename("p75")], axis=1)


def agregar_grupo(fb: pd.DataFrame, m: str, tipo: str, unidad: str, ok_tt: pd.Series | None = None) -> pd.DataFrame:
    """Agregado de grupo por trimestre: valor, valor_aa (a/a) y valor_tt (contra t−1).

    Las dos variaciones usan muestra constante: solo cuentan los bancos con dato en ambos lados.
    valor_tt además exige ok_tt (periodos.variacion_valida: trimestres anómalos y quiebre 2025).
    """
    clave = [fb["inst_key"], fb["periodo"]]
    if ok_tt is None:
        ok_tt = pd.Series(True, index=fb.index)

    def suma(serie: pd.Series, msk: pd.Series) -> pd.Series:
        return serie.where(msk).groupby(clave).sum(min_count=1)

    if tipo == "crec":
        base = R.CRECIMIENTOS[m]
        n, d = fb[base], fb[base + "__4"]
        msk = n.notna() & d.notna() & (d != 0)
        if m in R.VACIAS_EN_QUIEBRE_2025:   # mismo vacío que por banco (preparar_metricas_bancos)
            msk &= ~PER.cruza_quiebre(fb["periodo"], 4)
        valor = RG.div(suma(n, msk), suma(d, msk)) - 1
        valor_aa = pd.Series(np.nan, index=valor.index)
        valor_tt = pd.Series(np.nan, index=valor.index)
    elif tipo == "ratio":
        def f_n(d, s):
            return R.numerador(d, m, s)

        def f_d(d, s):
            return R.denominador(d, m, s)

        n, d = f_n(fb, ""), f_d(fb, "")
        n4, d4 = f_n(fb, "__4"), f_d(fb, "__4")
        msk = n.notna() & d.notna() & (d > 0)
        valor = RG.div(suma(n, msk), suma(d, msk))
        msk_s = msk & n4.notna() & d4.notna() & (d4 > 0)
        r_t = RG.div(suma(n, msk_s), suma(d, msk_s))
        r_4 = RG.div(suma(n4, msk_s), suma(d4, msk_s))
        valor_aa = (r_t - r_4) * (100 if unidad == "ratio" else 1)
        n1, d1 = f_n(fb, "__1"), f_d(fb, "__1")
        msk_t = msk & n1.notna() & d1.notna() & (d1 > 0) & ok_tt
        r_t1 = RG.div(suma(n, msk_t), suma(d, msk_t))
        r_1 = RG.div(suma(n1, msk_t), suma(d1, msk_t))
        valor_tt = (r_t1 - r_1) * (100 if unidad == "ratio" else 1)
    else:  # monto, incluidas las cuotas (suma de cuotas = cuota del grupo)
        x, x4, x1 = fb[m], fb[m + "__4"], fb[m + "__1"]
        valor = suma(x, x.notna())
        msk_s = x.notna() & x4.notna()
        a_t, a_4 = suma(x, msk_s), suma(x4, msk_s)
        valor_aa = (a_t - a_4) * 100 if unidad == "ratio" else RG.div(a_t, a_4) - 1
        msk_t = x.notna() & x1.notna() & ok_tt
        b_t, b_1 = suma(x, msk_t), suma(x1, msk_t)
        valor_tt = (b_t - b_1) * 100 if unidad == "ratio" else RG.div(b_t, b_1) - 1

    est = _estadisticas(fb, m)
    res = pd.concat([valor.rename("valor"), valor_aa.rename("valor_aa"), valor_tt.rename("valor_tt"), est], axis=1)
    res = res.dropna(subset=["valor"]).reset_index()
    res["metrica"] = m
    res["unidad_aa"] = None if tipo == "crec" else R.unidad_variacion(unidad)
    res["unidad_tt"] = res["unidad_aa"]
    return res


def _agregar_real(fb: pd.DataFrame, pieza_credito: pd.DataFrame, ipca: pd.Series) -> pd.DataFrame:
    """credito_real_aa por grupo: (1 + crédito a/a del grupo) / (1 + IPCA 12 meses) − 1 (encargo 78a §2).

    POR QUÉ desde el crecimiento del grupo: el real del grupo sale del mismo cociente de sumas que
    credito_aa, no de un promedio de reales de los bancos. Las medianas y cuartiles sí son de los bancos.
    valor_aa y valor_tt en pp; las variaciones que tocan 2024-T4 quedan vacías. El quiebre 2025 no se
    aplica aquí porque el crecimiento del grupo ya viene de su muestra de bancos.
    """
    base = pieza_credito.set_index(["inst_key", "periodo"])["valor"]
    per = pd.Series(base.index.get_level_values("periodo"), index=base.index)
    valor = _real_desde_nominal(base, ipca.reindex(per).to_numpy())

    def desfasado(k: int) -> pd.Series:
        prev = pd.MultiIndex.from_arrays([base.index.get_level_values("inst_key"),
                                          PER.previo_serie(per, k).to_numpy()])
        return pd.Series(valor.reindex(prev).to_numpy(), index=base.index)

    valor_aa = ((valor - desfasado(4)) * 100).where(PER.variacion_valida(per, 4))
    valor_tt = ((valor - desfasado(1)) * 100).where(PER.variacion_valida(per, 1))
    out = pd.concat([valor.rename("valor"), valor_aa.rename("valor_aa"), valor_tt.rename("valor_tt"),
                     _estadisticas(fb, "credito_real_aa")], axis=1)
    out = out.dropna(subset=["valor"]).reset_index()
    out["metrica"] = "credito_real_aa"
    out["unidad_aa"] = "pp"
    out["unidad_tt"] = "pp"
    return out


def _hhi_top5(w: pd.DataFrame) -> pd.DataFrame:
    """HHI y top5 sobre el panel completo: solo existen en la óptica «Total panel»."""
    filas = []
    for nombre, base, tipo in [("hhi_credito", "share_credito", "hhi"),
                               ("hhi_depositos", "share_depositos", "hhi"),
                               ("hhi_ativo", "share_ativo", "hhi"),
                               ("top5_credito", "share_credito", "top5"),
                               ("top5_depositos", "share_depositos", "top5")]:
        s = w[base]
        if tipo == "hhi":
            valor = (s * 100).pow(2).groupby(level="periodo").sum(min_count=1)
        else:
            valor = s.groupby(level="periodo").apply(
                lambda x: x.dropna().nlargest(5).sum() if x.notna().any() else np.nan)
        n = s.notna().groupby(level="periodo").sum()
        filas.append(pd.DataFrame({
            "inst_key": B.CLAVE_PANEL, "periodo": valor.index, "metrica": nombre,
            "valor": valor.to_numpy(), "valor_aa": np.nan, "unidad_aa": None,
            "n_bancos": n.reindex(valor.index).to_numpy(), "mediana": np.nan,
            "p25": np.nan, "p75": np.nan}))
    return pd.concat(filas, ignore_index=True)


def _bk_grupo(w: pd.DataFrame, banco: pd.DataFrame, meta: pd.DataFrame, quiebre: set[str]) -> pd.DataFrame:
    w4 = w.groupby(level="cod_inst").shift(4)
    w1 = w.groupby(level="cod_inst").shift(1)
    mb = _membresia(banco)
    fb = mb.merge(pd.concat([w, w4.add_suffix("__4"), w1.add_suffix("__1")], axis=1).reset_index(), on="cod_inst")
    ok_tt = PER.variacion_valida(fb["periodo"], 1, fb["cod_inst"].isin(quiebre))
    partes = []
    pieza_credito = None
    for m in w.columns:
        if m == "credito_real_aa":
            continue  # se deriva del crecimiento nominal del grupo, más abajo
        tipo = "crec" if m in R.CRECIMIENTOS else ("ratio" if m in R.RAZONES else "monto")
        res = agregar_grupo(fb, m, tipo, meta.loc[m, "unidad"], ok_tt)
        if m == "credito_aa":
            pieza_credito = res
        partes.append(res)
    partes.append(_agregar_real(fb, pieza_credito, _ipca_12m_trimestral()))
    partes.append(_hhi_top5(w))
    out = pd.concat(partes, ignore_index=True)
    grupos = mb.drop(columns="cod_inst").drop_duplicates("inst_key")
    out = out.merge(grupos, on="inst_key", how="left", validate="m:1")
    out["fecha"] = _fecha(out["periodo"])
    out["trimestre"] = out["periodo"].map(PER.etiqueta_trimestre)
    out["n_bancos"] = out["n_bancos"].astype("Int64")
    cols = ["optica", "grupo", "periodo", "fecha", "trimestre", "metrica", "valor", "valor_aa",
            "unidad_aa", "valor_tt", "unidad_tt", "mediana", "p25", "p75", "n_bancos",
            "orden_optica", "orden_grupo"]
    return out[cols].sort_values(["orden_optica", "orden_grupo", "metrica", "periodo"]).reset_index(drop=True)


def _bk_puente(banco: pd.DataFrame) -> pd.DataFrame:
    val = pd.DataFrame(A.leer_definicion("validacion_bancos"))
    cod = dict(zip(banco["nombre_corto"], banco["cod_inst"]))
    val["cod_inst"] = val["banco"].map(cod)
    if val["cod_inst"].isna().any():
        raise ValueError("validacion.json: banco sin cod_inst: " + ", ".join(val.loc[val.cod_inst.isna(), "banco"].unique()))
    val["periodo"] = val["periodo"].astype(str)
    val["dif_pct"] = (val["ifdata"] - val["gaap"]) / val["gaap"].where(val["gaap"] != 0)
    return val[["banco", "cod_inst", "linea", "periodo", "gaap", "ifdata", "dif_pct", "nota"]].reset_index(drop=True)


def _comprobar_mix7(panel: pd.DataFrame) -> None:
    """Σ saldo de bk_cartera_mix7 por banco = cartera_saldo de bk_panel (mix7 lo publica cartera, antes que base)."""
    mix = pd.read_parquet(ENTRADA_MIX7)
    saldo_panel = panel.loc[panel["metrica"] == "cartera_saldo", ["cod_inst", "periodo", "valor"]]
    errores = RG.verificar_mix7(mix, saldo_panel)
    if errores:
        raise ValueError("bk_cartera_mix7 no cuadra con bk_panel:\n" + "\n".join(errores))


def _principal_base() -> None:
    banco = _bk_banco()
    cods = banco["cod_inst"].tolist()
    w, grilla = _cargar_ancho(cods)
    metricas = list(w.columns) + R.SOLO_GRUPO
    metrica_df = R.tabla_metricas(metricas)
    meta = metrica_df.set_index("metrica")
    quiebre = B.con_quiebre_2025()
    panel = _bk_panel(w, banco, meta, grilla, quiebre)
    _comprobar_mix7(panel)
    grupo = _bk_grupo(w, banco, meta, quiebre)
    puente = _bk_puente(banco)

    def rel(*rutas):
        return [str(r.relative_to(A.RAIZ)) for r in rutas]

    defs_bancos = (A.DEFINICIONES / f"{B.DEF_BALANCES}.json", A.DEFINICIONES / f"{B.DEF_DASHBOARD}.json")
    panel_desde = rel(ENTRADA_METRICAS, ENTRADA_INSTITUCIONES, ENTRADA_CARTERA, ENTRADA_SISTEMA_Q, *defs_bancos,
                      A.DEFINICIONES / "metricas_bancos.json")
    entradas = {
        "bk_banco": (banco, rel(ENTRADA_INSTITUCIONES, *defs_bancos)),
        "bk_metrica": (metrica_df, rel(A.DEFINICIONES / "metricas_bancos.json")),
        "bk_panel": (panel, panel_desde),
        "bk_grupo": (grupo, panel_desde),
        "bk_puente": (puente, rel(A.DEFINICIONES / "validacion_bancos.json", ENTRADA_INSTITUCIONES)),
    }
    for nombre, (df, desde) in entradas.items():
        A.publicar_gold(nombre, df, dataset=DATASET_DERIVADO, desde=desde)
        print(f"{nombre}: {len(df):,} filas, {df.shape[1]} columnas")


# Rentabilidad: árbol del ROE y sensibilidad a la Selic (encargo 64). El sitio muestra de dónde sale el ROE (margen, provisiones, costos, impuestos y
# apalancamiento) y cuánto se mueve el margen de intermediación con la Selic. Las dos tablas
# salen de aquí para que el sitio solo dibuje (ESQUELETO B6-02, B6-04, B8-04; SPEC §3.7 y §3.8).
# Línea del árbol → rótulo que muestra el sitio (columna «nombre»), en el orden de la cascada.
NOMBRE_LINEA = {
    "margen_antes_provisiones": "Margen antes de provisiones",
    "provisiones": "Provisiones",
    "tarifas_servicios": "Tarifas y servicios",
    "transacciones_pago": "Transacciones de pago",
    "personal": "Personal",
    "administrativos": "Administrativos",
    "tributarios": "Tributarios",
    "no_operacional": "No operacional",
    "otros": "Otros",
    "impuesto_participaciones": "Impuesto y participaciones",
    "roa": "ROA",
    "apalancamiento": "Apalancamiento",
    "roe": "ROE",
}
LINEAS_EXPORTABLES = list(NOMBRE_LINEA)
LINEAS_ARBOL = LINEAS_EXPORTABLES[:10]   # las que suman el ROA
ORDEN_LINEA = {linea: i for i, linea in enumerate(LINEAS_EXPORTABLES, start=1)}
LINEAS_EN_VECES = {"apalancamiento"}     # activo medio / patrimonio medio; el resto es fracción
PERIODO_INICIO_BETA = "201603"
REZAGOS_NEWEY_WEST = 4
NUCLEO_ARBOL = ["A", "PL", "lucro", "antes", "rif", "prov", "tarifas", "servicios", "personal",
                "administrativos", "tributarios", "roa_m", "roe_m"]


def _insumos_arbol(w: pd.DataFrame) -> pd.DataFrame:
    """Insumos TTM en BRL por banco y trimestre, y si el banco tiene todo lo que el árbol necesita.

    «apto» exige el núcleo completo y activo y patrimonio medios positivos. La transacción de
    pagos no entra en el núcleo: antes de 2025 no existe en metricas_bancos y su línea queda null.
    """
    d = pd.DataFrame({
        "A": w["ativo_medio_ttm"], "PL": w["pl_medio_ttm"], "lucro": w["lucro_liquido_ttm"],
        "antes": w["antes_tributacao_ttm"], "rif": w["resultado_intermediacao_financeira_ttm"],
        "prov": w["provisoes_credito_ttm"], "tarifas": w["rendas_tarifas_ttm"],
        "servicios": w["rendas_servicos_ttm"], "transacciones": w["resultado_transacoes_pagamento_ttm"],
        "personal": w["despesas_pessoal_ttm"], "administrativos": w["despesas_administrativas_ttm"],
        "tributarios": w["despesas_tributarias_ttm"], "no_op": w["resultado_nao_operacional_ttm"],
        "roa_m": w["roa_ttm"], "roe_m": w["roe_ttm"],
    }, index=w.index)
    d["apto"] = d[NUCLEO_ARBOL].notna().all(axis=1) & (d["A"] > 0) & (d["PL"] > 0)
    return d


INSUMOS_ARBOL = ["A", "PL", "lucro", "antes", "rif", "prov", "tarifas", "servicios", "transacciones",
                 "personal", "administrativos", "tributarios", "no_op"]


def _lineas(x: pd.DataFrame) -> pd.DataFrame:
    """Líneas 1–9, ROA, apalancamiento y ROE (fracción del activo medio) desde los insumos TTM en BRL.

    POR QUÉ las provisiones se restan así: resultado_intermediacao_financeira ya viene neto de
    provisiones (COSIF), así que el margen antes de provisiones es RIF − provisiones, y la línea 2
    lleva las provisiones con su signo negativo. «Otros» es el residuo que cierra con el antes de
    tributación, y por eso absorbe lo que una línea no separa (p. ej. pagos antes de 2025).
    """
    a = x["A"]
    L = pd.DataFrame(index=x.index)
    L["margen_antes_provisiones"] = (x["rif"] - x["prov"]) / a
    L["provisiones"] = x["prov"] / a
    L["tarifas_servicios"] = (x["tarifas"] + x["servicios"]) / a
    L["transacciones_pago"] = x["transacciones"] / a
    L["personal"] = x["personal"] / a
    L["administrativos"] = x["administrativos"] / a
    L["tributarios"] = x["tributarios"] / a
    L["no_operacional"] = x["no_op"] / a
    resto = (L[["margen_antes_provisiones", "provisiones", "tarifas_servicios", "personal",
                "administrativos", "tributarios"]].sum(axis=1, min_count=1)
             + L["transacciones_pago"].fillna(0) + L["no_operacional"].fillna(0))
    L["otros"] = x["antes"] / a - resto
    L["impuesto_participaciones"] = (x["lucro"] - x["antes"]) / a
    L["roa"] = x["lucro"] / a
    L["apalancamiento"] = a / x["PL"]
    L["roe"] = L["roa"] * L["apalancamiento"]
    L.columns.name = "linea"
    return L[LINEAS_EXPORTABLES]


def _lineas_banco(d: pd.DataFrame) -> pd.DataFrame:
    """Las líneas por banco y trimestre; vacías donde el banco no es apto."""
    return _lineas(d[INSUMOS_ARBOL].where(d["apto"], axis=0))


def _lineas_grupo(d: pd.DataFrame, mb: pd.DataFrame) -> pd.DataFrame:
    """Las mismas líneas por grupo: Σ numerador / Σ activo medio, con los bancos aptos del grupo.

    POR QUÉ: un grupo no es el promedio de los ratios de sus bancos (SPEC §1.5). Solo cuentan los
    bancos aptos en ese trimestre, para que todas las líneas del grupo usen el mismo conjunto
    de bancos y el árbol cierre también a nivel de grupo.
    """
    x = d[INSUMOS_ARBOL].where(d["apto"], axis=0).reset_index()
    x = x.merge(mb[["cod_inst", "entidad"]], on="cod_inst", how="inner")
    return _lineas(x.groupby(["entidad", "periodo"])[INSUMOS_ARBOL].sum(min_count=1))


def _medianas(largo: pd.DataFrame, pertenencia: pd.DataFrame) -> pd.DataFrame:
    """Mediana de cada línea entre los bancos de cada grupo; vacío si el grupo tiene menos de 3 con dato."""
    j = largo.dropna(subset=["valor"]).merge(pertenencia, on="cod_inst")
    g = j.groupby(["entidad", "periodo", "linea"])["valor"]
    med = pd.DataFrame({"mediana": g.median(), "n": g.count()}).reset_index()
    med.loc[med["n"] < RG.MIN_GRUPO_PERCENTIL, "mediana"] = np.nan
    return med[["entidad", "periodo", "linea", "mediana"]]


def _fraccion_continua_beta(a: float, b: float, x: float) -> float:
    """Fracción continua de la beta incompleta (método de Lentz, Numerical Recipes)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 301):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        de = d * c
        h *= de
        if abs(de - 1.0) < 3e-14:
            break
    return h


def _beta_incompleta(a: float, b: float, x: float) -> float:
    """Beta incompleta regularizada I_x(a, b). Sin scipy en esta máquina; ver Numerical Recipes §6.4."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_frente = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                 + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(ln_frente) * _fraccion_continua_beta(a, b, x) / a
    return 1.0 - math.exp(ln_frente) * _fraccion_continua_beta(b, a, 1.0 - x) / b


def _cuantil_t(p: float, gl: int) -> float:
    """Cuantil p de la t de Student con gl grados de libertad, por bisección sobre la cola."""
    objetivo = 1.0 - p

    def cola_superior(t: float) -> float:
        mitad = 0.5 * _beta_incompleta(gl / 2.0, 0.5, gl / (gl + t * t))
        return mitad if t >= 0 else 1.0 - mitad

    lo, hi = 0.0, 50.0
    for _ in range(200):
        medio = (lo + hi) / 2.0
        if cola_superior(medio) > objetivo:
            lo = medio
        else:
            hi = medio
    return (lo + hi) / 2.0


def _regresion_nw(y: np.ndarray, x: np.ndarray, rezagos: int = REZAGOS_NEWEY_WEST):
    """MCO de y = a + b·x con errores Newey-West (núcleo de Bartlett, `rezagos` rezagos).

    Con h_t = x_t·u_t, x_t = (1, x_t): Var(b) = (X'X)⁻¹ Ω (X'X)⁻¹, con
    Ω = Σ_t h_t h_tᵀ + Σ_{l=1..L} (1 − l/(L+1)) · Σ_{t>l} (h_t h_{t−l}ᵀ + h_{t−l} h_tᵀ).
    Los rezagos se cuentan por posición en la muestra: los trimestres excluidos (202412, saltos
    de perímetro) no se tratan como huecos de tiempo. Devuelve (b, error estándar de b, R²).
    """
    n = len(y)
    X = np.column_stack([np.ones(n), x])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = y - X @ beta
    H = X * u[:, None]
    omega = H.T @ H
    for lag in range(1, rezagos + 1):
        G = H[lag:].T @ H[:-lag]
        omega = omega + (1.0 - lag / (rezagos + 1.0)) * (G + G.T)
    V = XtX_inv @ omega @ XtX_inv
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(u @ u) / sst if sst > 0 else np.nan
    return float(beta[1]), float(np.sqrt(V[1, 1])), r2


def _bk_sensibilidad(w: pd.DataFrame, banco: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Beta del NIM trimestral anualizado contra el CDI, por banco (SPEC §3.8; encargo 64b).

    NIM_t = 4 × (RIF_q − provisiones_q) / ((activo_{t−1} + activo_t) / 2). Excluidos: los trimestres anómalos
    en todos los bancos, y 2025-T1 solo en los bancos con ruptura de cobertura en 2025 (quiebre_2025 = true en
    bk_cartera). El crecimiento orgánico no se excluye. El intervalo de 90 % usa el cuantil t con
    n − 2 grados de libertad y el error de Newey-West.
    """
    cdi = SG.cdi_trimestral()
    if cdi.empty or not ((cdi.dropna() > 0) & (cdi.dropna() < 1)).all():
        raise ValueError("CDI fuera de la unidad esperada (fracción anual)")
    ativo = w["ativo_total"]
    ativo_prev = ativo.groupby(level="cod_inst").shift(1)
    medio = (ativo + ativo_prev) / 2.0
    # NIM trimestral anualizado, antes de provisiones (≠ margem_intermediacao_ttm, que es de 12 meses y neto).
    nim_trimestral = 4.0 * (w["resultado_intermediacao_financeira_q"] - w["provisoes_credito_q"]) / medio.where(medio > 0)
    quiebre = B.con_quiebre_2025()

    periodos = sorted(w.index.get_level_values("periodo").unique())
    en_ventana = pd.Series([p >= PERIODO_INICIO_BETA for p in periodos], index=periodos)
    fijo = pd.Series([p in PER.ANOMALOS for p in periodos], index=periodos)
    cdi_g = cdi.reindex(periodos)

    filas = []
    for cod in banco["cod_inst"]:
        y_all = nim_trimestral.xs(cod, level="cod_inst").reindex(periodos)
        por_quiebre = pd.Series([cod in quiebre and p == PER.QUIEBRE_2025 for p in periodos], index=periodos)
        excluido = en_ventana & (fijo | por_quiebre)
        usa = en_ventana & ~excluido & y_all.notna() & cdi_g.notna()
        lista_excl = [p for p in periodos if excluido[p] and pd.notna(y_all[p])]
        n = int(usa.sum())
        beta = ic_inf = ic_sup = r2 = np.nan
        if n >= RG.MIN_TRIMESTRES_BETA and float(np.ptp(cdi_g[usa].to_numpy())) > 0:
            b, se, r2 = _regresion_nw(y_all[usa].to_numpy(float), cdi_g[usa].to_numpy(float))
            tc = _cuantil_t(0.95, n - 2)
            beta, ic_inf, ic_sup = b, b - tc * se, b + tc * se
        filas.append({"cod_inst": cod, "beta_nim_cdi": beta, "ic_inf": ic_inf, "ic_sup": ic_sup,
                      "r2": r2, "n_trimestres": n, "excluidos": ";".join(lista_excl)})
    sens = pd.DataFrame(filas)
    sens = sens.merge(banco[["cod_inst", "modelo"]], on="cod_inst", how="left")
    sens["n_trimestres"] = sens["n_trimestres"].astype("Int64")
    cols = ["cod_inst", "modelo", "beta_nim_cdi", "ic_inf", "ic_sup", "r2", "n_trimestres", "excluidos"]
    return sens[cols], {"quiebre": sorted(quiebre), "periodos": periodos}


def _cuadra_arbol(L: pd.DataFrame, d: pd.DataFrame) -> pd.Series:
    """True si la fila cierra: Σ líneas 1–9 = ROA = roa_ttm y ROE = roe_ttm. Las no aptas no se juzgan."""
    suma = L[LINEAS_ARBOL].sum(axis=1, min_count=1)
    cierra = (((suma - L["roa"]).abs() <= RG.TOL_ROA_ARBOL)
              & ((L["roa"] - d["roa_m"]).abs() <= RG.TOL_ROA_ARBOL)
              & ((L["roe"] - d["roe_m"]).abs() <= RG.TOL_ROE_ARBOL))
    return (cierra | ~d["apto"]).astype(bool)


def _bk_roe_arbol(w: pd.DataFrame, banco: pd.DataFrame, mb: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Árbol del ROE por banco y por grupo de cada óptica (SPEC §3.7). Una fila que no cierra no se exporta."""
    d = _insumos_arbol(w)

    L = _lineas_banco(d)
    cuadra_b = _cuadra_arbol(L, d)
    Lb = L.rename_axis(columns="linea").stack(future_stack=True).rename("valor").reset_index()
    Lb = Lb.merge(cuadra_b.rename("cuadra").reset_index(), on=["cod_inst", "periodo"])
    fallas_b = sorted(set(Lb.loc[~Lb["cuadra"], ["cod_inst", "periodo"]].itertuples(index=False, name=None)))
    Lb_ok = Lb[Lb["cuadra"]][["cod_inst", "periodo", "linea", "valor"]]

    G = _lineas_grupo(d, mb)
    suma_g = G[LINEAS_ARBOL].sum(axis=1, min_count=1)
    cuadra_g = (((suma_g - G["roa"]).abs() <= RG.TOL_ROA_ARBOL) | G["roa"].isna())
    Lg = G.rename_axis(columns="linea").stack(future_stack=True).rename("valor").reset_index()
    Lg = Lg.merge(cuadra_g.rename("cuadra").reset_index(), on=["entidad", "periodo"])
    fallas_g = sorted(set(Lg.loc[~Lg["cuadra"], ["entidad", "periodo"]].itertuples(index=False, name=None)))
    Lg_ok = Lg[Lg["cuadra"]][["entidad", "periodo", "linea", "valor"]]

    med = _medianas(Lb_ok, mb[["entidad", "cod_inst"]])
    modelo = dict(zip(banco["cod_inst"], banco["modelo"]))
    b_out = Lb_ok.assign(entidad_mediana=Lb_ok["cod_inst"].map(modelo).map("Modelo de negocio|{}".format))
    b_out = b_out.merge(med.rename(columns={"entidad": "entidad_mediana", "mediana": "mediana_grupo"}),
                        on=["entidad_mediana", "periodo", "linea"], how="left")
    b_out = b_out.rename(columns={"cod_inst": "entidad"})
    g_out = Lg_ok.merge(med.rename(columns={"mediana": "mediana_grupo"}), on=["entidad", "periodo", "linea"], how="left")
    cols = ["entidad", "periodo", "linea", "valor", "mediana_grupo"]
    out = pd.concat([b_out[cols], g_out[cols]], ignore_index=True)
    out["orden"] = out["linea"].map(ORDEN_LINEA).astype(int)
    out["nombre"] = out["linea"].map(NOMBRE_LINEA)
    out["es_resumen"] = ~out["linea"].isin(LINEAS_ARBOL)   # ROA, apalancamiento y ROE: no son pasos de la cascada
    out["unidad"] = np.where(out["linea"].isin(LINEAS_EN_VECES), "veces", "fraccion")
    out["fecha"] = _fecha(out["periodo"])
    out["trimestre"] = out["periodo"].map(PER.etiqueta_trimestre)
    # Encargo 78a §4: brecha = valor − mediana_grupo, en la misma unidad que valor (solo una resta).
    out["brecha"] = out["valor"] - out["mediana_grupo"]
    out = out.sort_values(["entidad", "periodo", "orden"]).reset_index(drop=True)
    cols_fin = ["entidad", "periodo", "fecha", "trimestre", "linea", "nombre", "orden", "es_resumen", "unidad", "valor",
                "mediana_grupo", "brecha"]
    return out[cols_fin], {"fallas_bancos": fallas_b, "fallas_grupos": fallas_g,
                           "d": d, "L": L, "G": G}


def _principal_rentabilidad() -> None:
    banco = _bk_banco()
    cods = banco["cod_inst"].tolist()
    w, _grilla = _cargar_ancho(cods)
    mb = _membresia(banco)
    mb["entidad"] = mb["optica"] + "|" + mb["grupo"]

    arbol, rep = _bk_roe_arbol(w, banco, mb)
    sens, rep_s = _bk_sensibilidad(w, banco)
    print(f"bk_roe_arbol: {len(arbol):,} filas, {arbol['entidad'].nunique()} entidades")
    print(f"  no exportadas por no cuadrar: {len(rep['fallas_bancos'])} bancos-trimestres, "
          f"{len(rep['fallas_grupos'])} grupos-trimestres")
    print(f"bk_sensibilidad: {len(sens)} bancos, {int(sens['beta_nim_cdi'].notna().sum())} con beta")

    tablas = [
        ("bk_roe_arbol", arbol, ["intermedio/metricas_bancos.parquet", "gold/bank_instituciones.parquet",
                                 "definiciones/bcb_ifdata__bancos_balances.json"]),
        ("bk_sensibilidad", sens, ["intermedio/metricas_bancos.parquet", str(SG.ruta(SG.CDI).relative_to(A.DATOS)),
                                   "gold/bank_instituciones.parquet", "gold/bk_cartera.parquet"]),
    ]
    for nombre, df, desde in tablas:
        A.publicar_gold(nombre, df, dataset=DATASET_DERIVADO, desde=desde)
        print(f"{nombre}: {len(df):,} filas, {df.shape[1]} columnas")


def main(argv: list[str] | None = None) -> int:
    """`base` (bk_banco, bk_metrica, bk_panel, bk_grupo, bk_puente) y `rentabilidad` (bk_roe_arbol,
    bk_sensibilidad). El orden con los demás pasos y el manifiesto los lleva actualizar.py."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="orden", required=True)
    sub.add_parser("base", help="bk_banco, bk_metrica, bk_panel, bk_grupo y bk_puente; necesita bk_cartera y bk_sistema_q")
    sub.add_parser("rentabilidad", help="bk_roe_arbol y bk_sensibilidad (encargo 64)")
    args = parser.parse_args(argv)
    if args.orden == "base":
        _principal_base()
    else:
        _principal_rentabilidad()
    return 0


if __name__ == "__main__":
    sys.exit(main())
