# -*- coding: utf-8 -*-
"""Portada mensual, secciones 02 (precio del crédito) y 03 (NPL): series SGS por segmento y su tabla (frente 9).

La sección 01 (concesiones e impulso) ya está en gold: bk_concesiones y bk_concesiones_tablas
(preparar_gold_bancos_concesiones.py, parte A1). Este preparador cubre lo demás que el canvas de la Portada calculaba
con los datos incrustados en las hojas (Seccion02/03.dc.html).

TABLAS (datos/gold/)
--------------------
- bk_portada_m (larga): seccion («02» o «03»), indicador, segmento, fecha (último día del mes), valor.
  Clave: indicador, segmento, fecha.
  * Indicadores: ``tasa`` (tasa media de las operaciones nuevas), ``icc`` (costo del stock), ``spread``, ``mora90``
    (inadimplência > 90 días), ``atraso15_90`` y ``selic_meta`` (SGS 432, a fin de mes; segmento «tot»). Todos en
    fracción (el % o los p.p. del SGS / 100). Derivadas: ``tasa_menos_icc`` (tot) y ``d_aa`` de mora y atraso (Δ a/a,
    fracción) para tot, pf y pj.
  * Segmentos: tot, pf, pj, li, di, pfli, pfdi, pjli, pjdi. El spread dirigido de personas (pfdi) no lo publica el
    BCB (tareas/borradores/portada_sgs_barrido.md): no hay fila, y la hoja lo dice.
- bk_portada_m_tablas: seccion, indicador, orden, fila, segmento, ultimo, d1, d3, d12, dventana, corte, z120, p25, p50,
  p75, minimo, maximo. Clave: indicador, segmento.

REGLAS
------
- Cambios: m/m y a/a punta contra punta; 3m/3m y 12m/12m promedio de la ventana contra la anterior; en pp (tabla
  estándar, tabla_estandar.variaciones_tasa con escala 100).
- Z 10 años: (último − promedio de los 120 meses que terminan en el último) / desvío muestral (ddof = 1) de esos
  meses. Con menos de 120 meses, vacío.
- Historia (caja): percentiles 25, 50 y 75, mínimo y máximo desde ene-14; en los Δ a/a de mora y atraso, desde mar-12.
- Res. CMN 4.966 (ene-25): las moras y atrasos cambian de definición; la serie no se empalma (banda en la hoja).
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import almacen as A
import sgs as SG
import tabla_estandar as T

DATASET = "bancos_gold_portada_m"
DESDE = "2011-03"            # el Δ a/a de mora y atraso necesita 12 meses antes de mar-12
DESDE_CAJA = "2014-01"
DESDE_CAJA_DAA = "2012-03"
VENTANA_Z = 120
SEGMENTOS = ["tot", "pf", "pj", "li", "di", "pfli", "pfdi", "pjli", "pjdi"]
ROTULO = {"tot": "Total", "pf": "Personas", "pj": "Empresas", "li": "Libre", "di": "Dirigido",
          "pfli": "Personas libre", "pfdi": "Personas dirigido", "pjli": "Empresas libre", "pjdi": "Empresas dirigido"}
# indicador → segmento → clave de sgs.CODIGOS (códigos en portada_sgs_barrido.md)
CLAVES = {
    "tasa": {"tot": "tasa_creditos_nuevos", "pf": "tasa_pf_total", "pj": "tasa_pj_total", "li": "tasa_libre",
             "di": "tasa_direccionado", "pfli": "tasa_pf_libre", "pfdi": "tasa_pf_direccionado",
             "pjli": "tasa_pj_libre", "pjdi": "tasa_pj_direccionado"},
    "icc": {"tot": "icc", "pf": "icc_pf", "pj": "icc_pj", "li": "icc_libre", "di": "icc_direccionado",
            "pfli": "icc_pf_libre", "pfdi": "icc_pf_direccionado", "pjli": "icc_pj_libre",
            "pjdi": "icc_pj_direccionado"},
    "spread": {"tot": "spread_total", "pf": "spread_pf", "pj": "spread_pj", "li": "spread_livre",
               "di": "spread_direccionado", "pfli": "spread_pf_libre", "pjli": "spread_pj_libre",
               "pjdi": "spread_pj_direccionado"},
    "mora90": {"tot": "mora90_total", "pf": "mora90_pf", "pj": "mora90_pj", "li": "mora90_libre",
               "di": "mora90_direccionado", "pfli": "mora90_pf_livre", "pfdi": "mora90_pf_direccionado",
               "pjli": "mora90_pj_livre", "pjdi": "mora90_pj_direccionado"},
    "atraso15_90": {"tot": "atraso15_90_total", "pf": "atraso15_90_pf", "pj": "atraso15_90_pj",
                    "li": "atraso15_90_libre", "di": "atraso15_90_direccionado", "pfli": "atraso15_90_pf_libre",
                    "pfdi": "atraso15_90_pf_direccionado", "pjli": "atraso15_90_pj_libre",
                    "pjdi": "atraso15_90_pj_direccionado"},
}
SECCION = {"tasa": "02", "icc": "02", "spread": "02", "selic_meta": "02", "tasa_menos_icc": "02",
           "mora90": "03", "atraso15_90": "03", "mora90_d_aa": "03", "atraso15_90_d_aa": "03"}
CON_DAA = ["tot", "pf", "pj"]
COLUMNAS_TABLA = ["seccion", "indicador", "orden", "fila", "segmento", "ultimo", "d1", "d3", "d12", "dventana",
                  "corte", "z120", "p25", "p50", "p75", "minimo", "maximo"]


def zscore(x: pd.Series, ventana: int = VENTANA_Z) -> float:
    x = x.dropna()
    if len(x) < ventana:
        return np.nan
    w = x.iloc[-ventana:]
    return float((w.iloc[-1] - w.mean()) / w.std(ddof=1))


def caja(x: pd.Series, desde: str) -> dict:
    h = x.dropna().loc[pd.Period(desde, "M"):]
    if h.empty:
        return dict(p25=np.nan, p50=np.nan, p75=np.nan, minimo=np.nan, maximo=np.nan)
    return dict(p25=h.quantile(0.25), p50=h.quantile(0.5), p75=h.quantile(0.75), minimo=h.min(), maximo=h.max())


def construir(series: dict[str, dict[str, pd.Series]], selic: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """``series``: indicador → segmento → serie mensual (PeriodIndex) en % o p.p. del SGS; ``selic``: meta, % a.a."""
    largas, tablas = [], []

    def agregar(indicador, segmento, s):
        s = (s / 100).dropna()
        largas.append(pd.DataFrame({"seccion": SECCION[indicador], "indicador": indicador, "segmento": segmento,
                                    "fecha": T.fecha_fin(s.index), "valor": s.to_numpy(dtype=float)}))
        return s

    def fila(indicador, orden, segmento, s, desde_caja):
        v = T.variaciones_tasa(s, escala=100)
        v.update(caja(s, desde_caja))
        tablas.append({"seccion": SECCION[indicador], "indicador": indicador, "orden": orden,
                       "fila": ROTULO[segmento], "segmento": segmento, **v, "z120": zscore(s)})

    for indicador, segs in series.items():
        for orden, seg in enumerate(SEGMENTOS):
            if seg not in segs:
                continue
            s = agregar(indicador, seg, segs[seg].loc[pd.Period(DESDE, "M"):])
            fila(indicador, orden, seg, s, DESDE_CAJA)
            if indicador in ("mora90", "atraso15_90") and seg in CON_DAA:
                daa = agregar(f"{indicador}_d_aa", seg, (segs[seg] - segs[seg].shift(12)).loc[pd.Period(DESDE, "M"):])
                fila(f"{indicador}_d_aa", orden, seg, daa, DESDE_CAJA_DAA)
    gap = agregar("tasa_menos_icc", "tot", (series["tasa"]["tot"] - series["icc"]["tot"]).loc[pd.Period(DESDE, "M"):])
    fila("tasa_menos_icc", 0, "tot", gap, DESDE_CAJA)
    # Selic meta a fin de mes, hasta el último mes de las tasas (la serie diaria sigue después).
    fin = pd.Period(max(pd.concat(largas)["fecha"]), "M")
    sm = selic.loc[pd.Period(DESDE, "M"):fin]
    agregar("selic_meta", "tot", sm)
    larga = pd.concat(largas, ignore_index=True)
    return larga, pd.DataFrame(tablas)[COLUMNAS_TABLA]


def leer() -> tuple[dict[str, dict[str, pd.Series]], pd.Series]:
    series = {ind: {seg: SG.serie_mensual(SG.CODIGOS[k]) for seg, k in segs.items()} for ind, segs in CLAVES.items()}
    return series, SG.serie_mensual(SG.CODIGOS["selic_meta"])


def main(argv: list[str] | None = None) -> int:
    series, selic = leer()
    larga, tablas = construir(series, selic)
    for nombre, df in (("bk_portada_m", larga), ("bk_portada_m_tablas", tablas)):
        A.publicar_gold(nombre, df, fuente="bcb_sgs", dataset=DATASET, desde=[f"crudo/{SG.FUENTE}"],
                        nota="Portada mensual, secciones 02 y 03 (frente 9)")
        print(f"{nombre}: {len(df):,} filas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
