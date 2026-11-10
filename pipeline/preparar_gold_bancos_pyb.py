# -*- coding: utf-8 -*-
"""Hoja «P&L y balance por banco» (frente 15): estado de resultados, balance y capital por banco y trimestre.

Lleva a gold lo que el canvas calculaba con el borrador ``extraer_pyb.py``. El mapa de cuentas por época del plan
contable (antes y desde 1T25, Res. CMN 4.966) está en ``definiciones/pyb_lineas.json``, no en el código.

FUENTES
-------
- bank_hechos (IF.Data, conglomerado prudencial, informes 2 activo, 3 pasivo y 4 resultados). ``valor`` del informe 4
  es el flujo del trimestre (ya desacumulado del semestre).
- bk_panel: crédito bruto y pérdida esperada acumulada (balance), activo y patrimonio medio 12m (denominadores),
  ROE y modelo de negocio (grupo de la mediana).
- bk_capital y bk_capital_grupo (informe 5): sección P7 Capital.
- bk_producto_pf_m (referencia/selic): Selic efectiva del mes, para el costo de fondeo relativo.

TABLAS (datos/gold/)
--------------------
- bk_pyb: cod_inst, periodo (AAAAMM), trimestre («2T26»), seccion, linea, medida, valor.
  Clave: cod_inst, periodo, linea, medida.
  * seccion ``pyl``: medidas ``rs_trim`` (R$ del trimestre), ``rs_12m`` (R$, suma de cuatro trimestres
    consecutivos; si falta uno, no hay fila) y ``pct_activo_medio_12m`` (rs_12m / ativo_medio_ttm de bk_panel,
    en fracción).
  * secciones ``activo`` y ``pasivo``: ``rs`` (saldo a fin de trimestre, R$) y ``pct_activo`` (rs / activo total,
    fracción). El pasivo se divide por el activo total (= pasivo total).
  * seccion ``indicador``: ``roe`` (roe_ttm de bk_panel), medida ``fraccion``.
  * seccion ``capital``: índices del informe 5 (``fraccion``) y variaciones del capital principal (``rs``); ver
    CAPITAL_FRACCION y CAPITAL_RS.
  * seccion ``sensibilidad`` (``fraccion``): ``mfb_qa`` = margen financiero antes de pérdida esperada del trimestre
    × 4 / activo medio del trimestre (promedio de dos cierres consecutivos); ``cf_qa`` = −gasto de captación × 4 /
    fondeo medio (líneas ``fondeo`` de la definición); ``cf_pct`` = cf_qa / Selic efectiva media del trimestre.
- bk_pyb_grupo: grupo, periodo, trimestre, seccion, linea, medida, valor, n_bancos.
  Clave: grupo, periodo, linea, medida.
  * ``grupo`` = modelo de negocio de bk_panel: mediana de los bancos del grupo con dato (n_bancos = cuántos).
  * ``grupo`` = «Panel»: razón de sumas de los bancos con numerador y denominador (no promedio de razones):
    Σ rs_12m / Σ ativo_medio_ttm, Σ rs / Σ activo total, ROE = Σ utilidad 12m / Σ pl_medio_ttm. Capital: los
    índices cp, bas, dens, hol y req_cp se toman de bk_capital_grupo («Total panel», sus n_bancos) y apalancamiento
    y crecimientos son razón de sumas de los bancos de bk_pyb (decisión pendiente: unificar en 31 o 34 bancos).
    Sensibilidad: Σ(mfb × 4) / Σ activo medio, Σ(−captación × 4) / Σ fondeo medio y su cociente con la Selic.
  * ``grupo`` = «Referencia»: linea ``selic`` (seccion sensibilidad), promedio de los meses del trimestre de la
    Selic efectiva anualizada (bk_producto_pf_m, referencia/selic, SGS 4189), en fracción.

REGLAS
------
- La época de cada banco-trimestre sale de la columna ``era`` de bank_hechos, no de si la cuenta existe.
- Las cuentas se buscan por (informe, cuenta_base): 'ativo total' está en los informes 2 y 4 e 'instrumentos
  derivativos' en el 2 y el 3. Una cuenta usada que aparezca dos veces en el mismo informe hace fallar el paso.
- Los trimestres se ordenan por (año, trimestre); el 12m y los a/a se calculan sobre una grilla completa de
  trimestres, así un hueco deja vacío el 12m en vez de sumar trimestres no consecutivos.
- Las líneas residuales cierran contra la cuenta publicada (resultado de intermediación, resultado antes de
  impuestos, utilidad, activo total y pasivo total): las sumas cuadran por construcción y los tests lo vigilan.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import almacen as A

DATASET = "bancos_gold_pyb"
DEF_LINEAS = "pyb_lineas"
INFORMES = (2, 3, 4)
PANEL = "Panel"
REFERENCIA = "Referencia"
SECCIONES_PYL = {"pyl"}
SECCIONES_BALANCE = {"activo", "pasivo"}
METRICAS_PANEL = ["credito_bruto", "ecl_saldo", "ativo_medio_ttm", "pl_medio_ttm", "roe_ttm"]

# Capital (bk_capital): línea → columna (índices en fracción) y R$.
CAPITAL_FRACCION = {"cp": "indice_cp", "bas": "basilea", "n1": "indice_nivel1", "req_cp": "requerimiento_cp",
                    "req_pr": "requerimiento_pr", "hol": "holgura_cp_pp", "apal": "razon_apalancamiento",
                    "dens": "densidad_rwa"}
CAPITAL_RS = {"var_cp": "var_cp_4t", "luc": "lucro_ttm", "otr": "otros_var_cp_4t"}
CAPITAL_MEDIANA = ["cp", "bas", "hol", "apal", "dens", "rwa_aa", "cred_aa", "req_cp"]
CAPITAL_DE_GRUPO = {"cp": "indice_cp", "bas": "basilea", "dens": "densidad_rwa", "hol": "holgura_cp_pp",
                    "req_cp": "requerimiento_cp"}      # panel tomado de bk_capital_grupo («Total panel»)
COLUMNAS = ["cod_inst", "periodo", "trimestre", "seccion", "linea", "medida", "valor"]
COLUMNAS_GRUPO = ["grupo", "periodo", "trimestre", "seccion", "linea", "medida", "valor", "n_bancos"]


# ================================================== utilidades =====================================================

def etiqueta(periodo: str) -> str:
    """'202606' → '2T26'."""
    return f"{(int(periodo[4:]) - 1) // 3 + 1}T{periodo[2:4]}"


def n_trimestre(periodo: pd.Series) -> pd.Series:
    """Número correlativo de trimestre (año·4 + trimestre − 1): consecutivos difieren en 1."""
    p = periodo.astype(str)
    return p.str[:4].astype(int) * 4 + (p.str[4:].astype(int) - 1) // 3


def periodo_de_n(n: pd.Index) -> list[str]:
    return [f"{k // 4}{(k % 4 + 1) * 3:02d}" for k in n]


def en_grilla(ancho: pd.DataFrame) -> pd.DataFrame:
    """Ancho (cod_inst, periodo) × columnas → misma tabla sobre la grilla completa de trimestres de cada banco."""
    partes = []
    for cod, g in ancho.groupby(level=0, sort=False):
        n = n_trimestre(pd.Series(g.index.get_level_values(1)))
        x = g.droplevel(0).set_axis(n.to_numpy())
        x = x.reindex(pd.RangeIndex(int(n.min()), int(n.max()) + 1))
        x.index = pd.MultiIndex.from_product([[cod], periodo_de_n(x.index)], names=["cod_inst", "periodo"])
        partes.append(x)
    return pd.concat(partes)


def suma_12m(ancho: pd.DataFrame) -> pd.DataFrame:
    """Suma de cuatro trimestres consecutivos por banco; vacío si falta alguno. Devuelve el índice original."""
    g = en_grilla(ancho)
    r = g.groupby(level=0, group_keys=False).apply(lambda x: x.rolling(4, min_periods=4).sum())
    return r.reindex(ancho.index)


def var_aa(ancho: pd.DataFrame) -> pd.DataFrame:
    """x_t / x_{t−4} − 1 por banco, con t−4 el mismo trimestre del año anterior (no la cuarta fila)."""
    g = en_grilla(ancho)
    r = g.groupby(level=0, group_keys=False).apply(lambda x: x / x.shift(4) - 1)
    return r.replace([np.inf, -np.inf], np.nan).reindex(ancho.index)


# ================================================== líneas ==========================================================

def definiciones() -> dict:
    return A.leer_definicion(DEF_LINEAS)


def cuentas_usadas(defn: dict) -> set[tuple[int, str]]:
    out = set()
    for l in defn["lineas"]:
        for ep in l.get("epocas", {}).values():
            out |= {(ep["informe"], c["cuenta"]) for c in ep["cuentas"]}
    return out


def pivotar_hechos(hechos: pd.DataFrame, defn: dict) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Ancho (cod_inst, periodo) × (informe, cuenta_base), la época de cada fila y qué informes tiene."""
    h = hechos[hechos["num_informe"].isin(INFORMES)]
    usadas = cuentas_usadas(defn)
    clave = list(zip(h["num_informe"], h["cuenta_base"]))
    hu = h[[k in usadas for k in clave]]
    rep = hu.groupby(["cod_inst", "periodo", "num_informe", "cuenta_base"]).size()
    if (rep > 1).any():
        raise ValueError(f"cuentas repetidas en un mismo informe: {rep[rep > 1].head().to_dict()}")
    w = hu.pivot_table(index=["cod_inst", "periodo"], columns=["num_informe", "cuenta_base"], values="valor",
                       aggfunc="first")
    eras = h.groupby(["cod_inst", "periodo"])["era"].agg(lambda s: s.unique().tolist())
    if (eras.map(len) > 1).any():
        raise ValueError("un banco-trimestre con dos épocas del plan contable")
    era = eras.map(lambda s: s[0])
    # Un informe «está» si trae algún valor: hay filas con todas las cuentas vacías (BRB 3T22–4T22 y 4T25–2T26,
    # XP 2015–16, Agibank 2014–15, primer trimestre de los bancos nuevos en el informe 4, que no se desacumula).
    # Ahí todas las líneas quedan vacías, no en cero.
    tiene = h.groupby(["cod_inst", "periodo", "num_informe"])["valor"].count().unstack().fillna(0) > 0
    idx = era.index
    return w.reindex(idx), era, tiene.reindex(idx).fillna(False)


def calcular_lineas(hechos: pd.DataFrame, panel: pd.DataFrame, defn: dict) -> pd.DataFrame:
    """Ancho (cod_inst, periodo) × línea, en R$ (flujos del trimestre para el P&L, saldos para el balance)."""
    w, era, tiene = pivotar_hechos(hechos, defn)
    pv = panel[panel["metrica"].isin(METRICAS_PANEL)].pivot_table(
        index=["cod_inst", "periodo"], columns="metrica", values="valor", aggfunc="first").reindex(w.index)
    out = {}
    lineas = defn["lineas"]
    for l in lineas:
        if l["tipo"] in ("cuentas", "total"):
            s = pd.Series(np.nan, index=w.index)
            for nombre_era, ep in l["epocas"].items():
                m = (era == nombre_era) & tiene.get(ep["informe"], False)
                if not ep["cuentas"]:
                    v = pd.Series(0.0, index=w.index)
                else:
                    partes = []
                    for c in ep["cuentas"]:
                        col = (ep["informe"], c["cuenta"])
                        x = w[col] if col in w.columns else pd.Series(np.nan, index=w.index)
                        partes.append(c["signo"] * (x if l["tipo"] == "total" else x.fillna(0)))
                    v = sum(partes[1:], partes[0])
                s = s.where(~m, v)
            out[l["linea"]] = s
        elif l["tipo"] == "panel":
            out[l["linea"]] = l["signo"] * pv[l["metrica"]] if l["metrica"] in pv else pd.Series(np.nan, index=w.index)
    for l in lineas:
        if l["tipo"] == "subtotal":
            out[l["linea"]] = sum(t["signo"] * out[t["linea"]] for t in l["suma"])
    for l in lineas:
        if l["tipo"] == "residual":
            out[l["linea"]] = out[l["total"]] - sum(out[k].fillna(0) for k in l["resta"])
    return pd.DataFrame(out, index=w.index)


def _largo(ancho: pd.DataFrame, seccion: dict[str, str], medida: str) -> pd.DataFrame:
    x = ancho.rename_axis(columns="linea").stack().rename("valor").reset_index()
    x = x[np.isfinite(x["valor"])]
    x["seccion"] = x["linea"].map(seccion)
    x["medida"] = medida
    return x


SENSIBILIDAD = ["mfb_qa", "cf_qa", "cf_pct"]


def promedio_2(ancho: pd.DataFrame) -> pd.DataFrame:
    """(x_t + x_{t−1}) / 2 por banco, con t−1 el trimestre anterior (no la fila anterior)."""
    g = en_grilla(ancho)
    r = g.groupby(level=0, group_keys=False).apply(lambda x: (x + x.shift(1)) / 2)
    return r.reindex(ancho.index)


def selic_trimestral(selic_m: pd.DataFrame) -> pd.Series:
    """Selic efectiva media del trimestre (fracción), indexada por periodo AAAAMM del cierre del trimestre."""
    f = pd.to_datetime(selic_m["fecha"])
    per = (f.dt.year * 100 + ((f.dt.month - 1) // 3 + 1) * 3).astype(str)
    return selic_m["valor"].groupby(per.to_numpy()).mean()


def sensibilidad(L: pd.DataFrame, fondeo: list[str], selic: pd.Series) -> pd.DataFrame:
    medios = promedio_2(pd.DataFrame({"activo": L["activo"], "fondeo": L[fondeo].sum(axis=1, min_count=1)}))
    out = pd.DataFrame(index=L.index)
    out["mfb_qa"] = L["mfb"] * 4 / medios["activo"]
    out["cf_qa"] = -L["capt"] * 4 / medios["fondeo"]
    out["cf_pct"] = out["cf_qa"] / selic.reindex(L.index.get_level_values(1)).to_numpy()
    return out.replace([np.inf, -np.inf], np.nan)


def construir(hechos: pd.DataFrame, panel: pd.DataFrame, capital: pd.DataFrame, defn: dict,
              selic: pd.Series | None = None) -> pd.DataFrame:
    """bk_pyb (largo)."""
    hechos = hechos.assign(periodo=hechos["periodo"].astype(str))
    panel = panel.assign(periodo=panel["periodo"].astype(str))
    L = calcular_lineas(hechos, panel, defn)
    seccion = {l["linea"]: l["seccion"] for l in defn["lineas"]}
    pyl = [l["linea"] for l in defn["lineas"] if l["seccion"] in SECCIONES_PYL]
    bal = [l["linea"] for l in defn["lineas"] if l["seccion"] in SECCIONES_BALANCE]
    pv = panel[panel["metrica"].isin(METRICAS_PANEL)].pivot_table(
        index=["cod_inst", "periodo"], columns="metrica", values="valor", aggfunc="first").reindex(L.index)
    q = L[pyl]
    t = suma_12m(q)
    partes = [_largo(q, seccion, "rs_trim"), _largo(t, seccion, "rs_12m"),
              _largo(t.div(pv["ativo_medio_ttm"], axis=0), seccion, "pct_activo_medio_12m"),
              _largo(L[bal], seccion, "rs"), _largo(L[bal].div(L["activo"], axis=0), seccion, "pct_activo"),
              _largo(pv[["roe_ttm"]].rename(columns={"roe_ttm": "roe"}), {"roe": "indicador"}, "fraccion")]
    partes += construir_capital(capital, panel, L.index)
    if selic is not None:
        partes.append(_largo(sensibilidad(L, defn["fondeo"], selic), {k: "sensibilidad" for k in SENSIBILIDAD},
                             "fraccion"))
    df = pd.concat(partes, ignore_index=True)
    df["trimestre"] = df["periodo"].map(etiqueta)
    df = df[COLUMNAS].sort_values(["cod_inst", "periodo", "seccion", "linea", "medida"]).reset_index(drop=True)
    return df


def construir_capital(capital: pd.DataFrame, panel: pd.DataFrame, indice: pd.MultiIndex) -> list[pd.DataFrame]:
    c = capital.assign(periodo=capital["periodo"].astype(str)).set_index(["cod_inst", "periodo"]).sort_index()
    c = c[c.index.isin(indice)]
    fr = pd.DataFrame({k: c[v] for k, v in CAPITAL_FRACCION.items()})
    fr["rwa_c"] = c["rwa_credito"] / c["rwa_total"]
    fr["rwa_m"] = c["rwa_mercado"] / c["rwa_total"]
    fr["rwa_o"] = c["rwa_operacional"] / c["rwa_total"]
    fr["rwa_aa"] = var_aa(c[["rwa_total"]])["rwa_total"]
    cb = panel[panel["metrica"] == "credito_bruto"].set_index(["cod_inst", "periodo"])[["valor"]].sort_index()
    fr = fr.join(var_aa(cb)["valor"].rename("cred_aa"), how="outer")
    fr = fr[fr.index.isin(indice)]
    rs = pd.DataFrame({k: c[v] for k, v in CAPITAL_RS.items()})
    sec = {k: "capital" for k in list(fr.columns) + list(rs.columns)}
    return [_largo(fr.replace([np.inf, -np.inf], np.nan), sec, "fraccion"), _largo(rs, sec, "rs")]


# ================================================== grupo y panel ===================================================

def modelos(panel: pd.DataFrame) -> pd.Series:
    """cod_inst → modelo de negocio (el último informado en bk_panel)."""
    p = panel.dropna(subset=["modelo"]).sort_values("periodo")
    return p.groupby("cod_inst")["modelo"].last()


def construir_grupo(pyb: pd.DataFrame, panel: pd.DataFrame, capital: pd.DataFrame,
                    capital_grupo: pd.DataFrame, defn: dict, selic: pd.Series | None = None) -> pd.DataFrame:
    """bk_pyb_grupo: mediana por modelo de negocio y panel como razón de sumas."""
    panel = panel.assign(periodo=panel["periodo"].astype(str))
    mod = modelos(panel)
    ratios = pyb[pyb["medida"].isin(["pct_activo_medio_12m", "pct_activo"])
                 | ((pyb["seccion"] == "indicador") & (pyb["medida"] == "fraccion"))
                 | ((pyb["seccion"] == "capital") & pyb["linea"].isin(CAPITAL_MEDIANA))
                 | (pyb["seccion"] == "sensibilidad")]
    r = ratios.assign(grupo=ratios["cod_inst"].map(mod)).dropna(subset=["grupo"])
    med = (r.groupby(["grupo", "periodo", "seccion", "linea", "medida"])["valor"]
           .agg(valor="median", n_bancos="count").reset_index())

    # Panel: Σ numerador / Σ denominador sobre los bancos con ambos.
    pv = panel[panel["metrica"].isin(["ativo_medio_ttm", "pl_medio_ttm", "credito_bruto"])].pivot_table(
        index=["cod_inst", "periodo"], columns="metrica", values="valor", aggfunc="first")
    filas = []

    def razon(num: pd.DataFrame, den: pd.Series, medida: str, seccion_de: pd.Series):
        """num: largo (cod_inst, periodo, linea, valor); den: Series (cod_inst, periodo)."""
        x = num.join(den.rename("den"), on=["cod_inst", "periodo"]).dropna(subset=["valor", "den"])
        g = x.groupby(["periodo", "linea"]).agg(num=("valor", "sum"), den=("den", "sum"), n_bancos=("valor", "count"))
        g = g.reset_index()
        g["valor"] = g["num"] / g["den"]
        g["medida"] = medida
        g["seccion"] = g["linea"].map(seccion_de)
        filas.append(g[["periodo", "seccion", "linea", "medida", "valor", "n_bancos"]])

    sec = pyb.drop_duplicates("linea").set_index("linea")["seccion"]
    r12 = pyb[pyb["medida"] == "rs_12m"]
    razon(r12, pv["ativo_medio_ttm"], "pct_activo_medio_12m", sec)
    rs = pyb[pyb["medida"] == "rs"]
    act = rs[rs["linea"] == "activo"].set_index(["cod_inst", "periodo"])["valor"]
    razon(rs, act, "pct_activo", sec)
    luc = r12[r12["linea"] == "lucro"].assign(linea="roe")
    razon(luc, pv["pl_medio_ttm"], "fraccion", pd.Series({"roe": "indicador"}))
    filas.append(panel_capital(pyb, capital, capital_grupo, pv))
    if selic is not None:
        filas.append(panel_sensibilidad(pyb, defn["fondeo"], selic))
    pan = pd.concat(filas, ignore_index=True).assign(grupo=PANEL)
    ref = []
    if selic is not None:
        s = selic[selic.index.isin(set(pyb["periodo"]))]
        ref.append(pd.DataFrame({"grupo": REFERENCIA, "periodo": s.index, "seccion": "sensibilidad", "linea": "selic",
                                 "medida": "fraccion", "valor": s.to_numpy(), "n_bancos": 0}))
    df = pd.concat([med, pan, *ref], ignore_index=True)
    df = df[np.isfinite(df["valor"])]
    df["trimestre"] = df["periodo"].map(etiqueta)
    df["n_bancos"] = df["n_bancos"].astype(int)
    return df[COLUMNAS_GRUPO].sort_values(["grupo", "periodo", "seccion", "linea", "medida"]).reset_index(drop=True)


def panel_capital(pyb: pd.DataFrame, capital: pd.DataFrame, capital_grupo: pd.DataFrame,
                  pv: pd.DataFrame) -> pd.DataFrame:
    bancos = set(pyb["cod_inst"])
    c = capital.assign(periodo=capital["periodo"].astype(str))
    c = c[c["cod_inst"].isin(bancos)]
    s = c.groupby("periodo")
    serie = lambda col: s[col].sum(min_count=1)
    n = s["cod_inst"].count()
    out = {}
    apal = c.dropna(subset=["nivel1", "exposicion_total"]).groupby("periodo")
    out["apal"] = (apal["nivel1"].sum() / apal["exposicion_total"].sum(), apal["cod_inst"].count())

    def aa(x: pd.Series) -> pd.Series:
        x = x.copy()
        x.index = n_trimestre(pd.Series(x.index)).to_numpy()
        x = x.reindex(pd.RangeIndex(x.index.min(), x.index.max() + 1))
        r = x / x.shift(4) - 1
        r.index = periodo_de_n(r.index)
        return r

    # Crecimientos: razón de sumas de los bancos presentes en t (pueden entrar bancos nuevos entre t−4 y t).
    out["rwa_aa"] = (aa(serie("rwa_total")), n)
    cb = pv["credito_bruto"].dropna()
    cb = cb[cb.index.get_level_values(0).isin(bancos)]
    out["cred_aa"] = (aa(cb.groupby(level=1).sum()), cb.groupby(level=1).count())
    tp = capital_grupo[capital_grupo["optica"] == "Total panel"].assign(periodo=lambda d: d["periodo"].astype(str))
    tp = tp.set_index("periodo")
    for k, col in CAPITAL_DE_GRUPO.items():
        out[k] = (tp[col], tp["n_bancos"])
    filas = []
    for k, (v, nb) in out.items():
        x = pd.DataFrame({"valor": v, "n_bancos": nb.reindex(v.index)}).dropna(subset=["valor"])
        x = x.rename_axis("periodo").reset_index().assign(seccion="capital", linea=k, medida="fraccion")
        filas.append(x)
    df = pd.concat(filas, ignore_index=True)
    df = df[df["periodo"].isin(set(pyb["periodo"]))]
    df["n_bancos"] = df["n_bancos"].fillna(0)
    return df[["periodo", "seccion", "linea", "medida", "valor", "n_bancos"]]


def panel_sensibilidad(pyb: pd.DataFrame, fondeo: list[str], selic: pd.Series) -> pd.DataFrame:
    """Σ(mfb × 4) / Σ activo medio y Σ(−captación × 4) / Σ fondeo medio, sobre los bancos con ambos."""
    q = pyb[(pyb["medida"] == "rs_trim") & pyb["linea"].isin(["mfb", "capt"])].pivot_table(
        index=["cod_inst", "periodo"], columns="linea", values="valor", aggfunc="first")
    b = pyb[(pyb["medida"] == "rs") & pyb["linea"].isin(["activo", *fondeo])].pivot_table(
        index=["cod_inst", "periodo"], columns="linea", values="valor", aggfunc="first")
    medios = promedio_2(pd.DataFrame({"activo": b["activo"], "fondeo": b[fondeo].sum(axis=1, min_count=1)}))
    x = q.join(medios, how="inner")
    filas = []
    for linea, num, den in (("mfb_qa", x["mfb"] * 4, x["activo"]), ("cf_qa", -x["capt"] * 4, x["fondeo"])):
        d = pd.DataFrame({"num": num, "den": den}).dropna()
        g = d.groupby(level=1).agg(num=("num", "sum"), den=("den", "sum"), n_bancos=("num", "count"))
        g["valor"] = g["num"] / g["den"]
        filas.append(g.assign(linea=linea))
        if linea == "cf_qa":
            filas.append(g.assign(linea="cf_pct", valor=g["valor"] / selic.reindex(g.index)))
    df = pd.concat(filas).rename_axis("periodo").reset_index()
    return df.assign(seccion="sensibilidad", medida="fraccion")[["periodo", "seccion", "linea", "medida", "valor",
                                                                   "n_bancos"]]


# ================================================== main ============================================================

def leer_fuentes() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series]:
    hechos = pd.read_parquet(A.GOLD / "bank_hechos.parquet",
                             columns=["cod_inst", "periodo", "num_informe", "era", "cuenta_base", "valor"])
    panel = pd.read_parquet(A.GOLD / "bk_panel.parquet", columns=["cod_inst", "periodo", "metrica", "valor", "modelo"])
    capital = pd.read_parquet(A.GOLD / "bk_capital.parquet")
    capital_grupo = pd.read_parquet(A.GOLD / "bk_capital_grupo.parquet")
    m = pd.read_parquet(A.GOLD / "bk_producto_pf_m.parquet")
    selic = selic_trimestral(m[(m["producto"] == "referencia") & (m["sub"] == "selic") & (m["medida"] == "tasa")])
    return hechos, panel, capital, capital_grupo, selic


def main(argv: list[str] | None = None) -> int:
    defn = definiciones()
    hechos, panel, capital, capital_grupo, selic = leer_fuentes()
    pyb = construir(hechos, panel, capital, defn, selic)
    grupo = construir_grupo(pyb, panel, capital, capital_grupo, defn, selic)
    desde = ["gold/bank_hechos", "gold/bk_panel", "gold/bk_capital", "gold/bk_capital_grupo", "gold/bk_producto_pf_m",
             f"definiciones/{DEF_LINEAS}.json"]
    for nombre, df in (("bk_pyb", pyb), ("bk_pyb_grupo", grupo)):
        A.publicar_gold(nombre, df, fuente="bcb_ifdata", dataset=DATASET, desde=desde,
                        nota="Hoja «P&L y balance por banco» (frente 15)")
        print(f"{nombre}: {len(df):,} filas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
