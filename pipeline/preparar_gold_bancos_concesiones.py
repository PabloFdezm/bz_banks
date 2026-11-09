# -*- coding: utf-8 -*-
"""Concesiones libre / dirigido por segmento y el índice de concesiones reales frente a la actividad.

Es la base de la sección 01 de la Portada (canvas, láminas 06–08): libre = SGS 20634 (total), 20635 (empresas) y
20662 (personas); dirigido = total − libre. El índice compara el crédito concedido real con la actividad (IBC-Br).

TABLAS (datos/gold/)
------------------
- bk_concesiones (larga, una fila por segmento y mes): segmento, fecha (último día del mes),
  concesiones (R$ millones, flujo del mes), conc_12m (suma móvil de 12 meses, R$ millones), conc_12m_aa (a/a de esa suma, fracción),
  conc_real_12m (suma móvil de 12 meses deflactada, R$ millones a precios del último mes), ibc_12m (promedio móvil de
  12 meses del IBC-Br desestacionalizado), indice (concesiones reales 12m / IBC-Br 12m, base promedio 2014 = 100),
  indice_aa (a/a del índice, fracción) e indice_z120 (z-score del índice en 120 meses).
  Clave: segmento, fecha. Segmentos: tot, pf, pj, li, di, pfli, pfdi, pjli, pjdi.
- bk_concesiones_tablas: tabla estándar (bloque, orden, fila, grupo, ultimo, d1, d3, d12, dventana, corte, unidades,
  share, z120). Bloques: «mes» (concesiones del mes, R$ mil millones), «12m» (suma móvil, R$ mil millones) e «indice»
  (índice de concesiones reales frente a la actividad, puntos con base 2014 = 100). Clave: bloque, orden.
  La fila Total del bloque «mes» es «Concesiones totales» de bk_cred_tablas: mismas cifras (control en las pruebas).

REGLAS
------
- Segmentos: total = SGS 20631; personas = 20633; empresas = 20632; libre = 20634; libre empresas = 20635;
  libre personas = 20662. Dirigido = total − libre del mismo grupo: di = 20631 − 20634, pfdi = 20633 − 20662,
  pjdi = 20632 − 20635. Así li + di = total exacto y pf/pj se reconstruyen con sus libres y dirigidos.
  Identidades de la fuente: 20631 = 20632 + 20633 y 20634 = 20635 + 20662. Las series están en millones enteros, así
  que cada identidad puede fallar en ±1 R$ millón por redondeo (pruebas de integración).
- Deflactación: índice de precios a partir de la variación mensual del IPCA (SGS 433), encadenado
  (producto acumulado de 1 + var/100) y normalizado al último mes (sgs.deflactor). Cada concesión mensual se divide
  por el índice de su mes (precios del último mes). La normalización a 2014 = 100 del índice final elimina esa
  escala y no cambia la forma de la serie.
- Índice: concesiones reales 12m / IBC-Br desestacionalizado promedio 12m (SGS 24364), dividido por su promedio de los
  meses de 2014 y multiplicado por 100. El IBC-Br publica con dos meses de atraso: el índice llega al último mes del
  IBC-Br; el último mes de concesiones queda sin índice (no se rellena).
- Tabla estándar. En «mes» (flujo): m/m y a/a son el mes contra el anterior y contra el mismo mes del año anterior;
  3m/3m es el promedio de tres meses contra los tres anteriores; 12m/12m es la suma de doce meses contra la de los
  doce anteriores. En «12m» e «indice» (saldos): las ventanas son promedios de valores. Share: segmento contra total
  en el mismo mes («mes» y «12m»); vacío en el índice.
- Z-score del índice: (índice_t − media) / desviación típica muestral (ddof = 1) de los 120 meses que terminan en t.
  Solo con los 120 meses completos; antes queda vacío.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import almacen as A
import sgs as SG
import tabla_estandar as T

DATASET = "bancos_gold_concesiones"
BASE_ANIO = 2014          # el índice vale 100 en el promedio de los meses de este año
VENTANA_Z = 120           # meses del z-score del índice

# (clave, rótulo, grupo) en el orden de las filas de la tabla estándar.
SEGMENTOS = [
    ("tot", "Total", "Total"),
    ("pf", "Personas", "Personas"),
    ("pj", "Empresas", "Empresas"),
    ("li", "Libre", "Total"),
    ("di", "Dirigido", "Total"),
    ("pfli", "Personas · libre", "Personas"),
    ("pfdi", "Personas · dirigido", "Personas"),
    ("pjli", "Empresas · libre", "Empresas"),
    ("pjdi", "Empresas · dirigido", "Empresas"),
]

# Claves de sgs.CODIGOS que lee el paso, y el nombre con que llegan a construir().
SERIES = {
    "concesiones_total": "total", "concesiones_pf": "pf", "concesiones_pj": "pj",
    "concesiones_libre": "li", "concesiones_pj_libre": "pjli", "concesiones_pf_libre": "pfli",
    "ibc_br": "ibc",
}


def segmentos(s: dict[str, pd.Series]) -> dict[str, pd.Series]:
    """Concesiones mensuales por segmento (R$ millones). ``s`` trae total, pf, pj, li, pjli, pfli (SGS)."""
    tot, pf, pj = s["total"], s["pf"], s["pj"]
    li, pjli, pfli = s["li"], s["pjli"], s["pfli"]
    return {"tot": tot, "pf": pf, "pj": pj, "li": li, "di": tot - li,
            "pfli": pfli, "pfdi": pf - pfli, "pjli": pjli, "pjdi": pj - pjli}


def deflactar(nominal: pd.Series, deflactor: pd.Series) -> pd.Series:
    """Serie nominal mensual a precios del último mes: cada mes entre el índice IPCA de ese mes (SG.deflactor)."""
    return nominal / deflactor.reindex(nominal.index)


def suma_movil(x: pd.Series, ventana: int = 12) -> pd.Series:
    """Suma de los últimos ``ventana`` meses; vacía si falta alguno (la serie es mensual continua)."""
    return x.rolling(ventana).sum()


def promedio_movil(x: pd.Series, ventana: int = 12) -> pd.Series:
    return x.rolling(ventana).mean()


def indice_real(conc_real_12m: pd.Series, ibc_12m: pd.Series, anio: int = BASE_ANIO) -> pd.Series:
    """(concesiones reales 12m / IBC-Br 12m) × 100 / promedio de ese cociente en los meses de ``anio``.

    Falla si el año base no tiene sus doce meses con dato: un índice sin base no se publica.
    """
    cociente = conc_real_12m / ibc_12m
    base = cociente[cociente.index.year == anio].dropna()
    if len(base) != 12:
        raise ValueError(f"el índice necesita los 12 meses de {anio} con dato; hay {len(base)}")
    return 100 * cociente / base.mean()


def zscore(x: pd.Series, ventana: int = VENTANA_Z) -> pd.Series:
    """(x − media) / desviación típica muestral de los ``ventana`` meses que terminan en cada mes."""
    return (x - x.rolling(ventana).mean()) / x.rolling(ventana).std(ddof=1)


def construir(s: dict[str, pd.Series], deflactor: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(bk_concesiones, bk_concesiones_tablas). ``s``: series mensuales (PeriodIndex) en R$ millones, claves
    total, pf, pj, li, pjli, pfli y el IBC-Br en ibc; ``deflactor`` es el índice IPCA de SG.deflactor."""
    seg = segmentos(s)
    ibc12 = promedio_movil(s["ibc"])
    filas, tablas = [], []
    tot_mes = seg["tot"]
    tot_12 = suma_movil(tot_mes)
    for orden, (clave, rotulo, grupo) in enumerate(SEGMENTOS):
        mes = seg[clave]
        n12 = suma_movil(mes)
        real12 = suma_movil(deflactar(mes, deflactor))
        idx = indice_real(real12, ibc12)
        z = zscore(idx)
        filas.append(pd.DataFrame({
            "segmento": clave,
            "fecha": T.fecha_fin(mes.index),
            "concesiones": mes.to_numpy(),
            "conc_12m": n12.to_numpy(),
            "conc_12m_aa": (n12 / n12.shift(12) - 1).to_numpy(),
            "conc_real_12m": real12.to_numpy(),
            "ibc_12m": ibc12.reindex(mes.index).to_numpy(),
            "indice": idx.reindex(mes.index).to_numpy(),
            "indice_aa": (idx / idx.shift(12) - 1).reindex(mes.index).to_numpy(),
            "indice_z120": z.reindex(mes.index).to_numpy(),
        }, index=mes.index))

        # Bloque «mes»: concesiones del mes (flujo: 12m/12m = suma de doce meses contra la anterior).
        m = mes.dropna()
        v = T.variaciones_saldo(m, flujo=True)
        v["ultimo"] = m.iloc[-1] / 1e3
        v["share"] = m.iloc[-1] / tot_mes[m.index[-1]]
        tablas.append(T.fila(v, bloque="mes", orden=orden, fila=rotulo, grupo=grupo,
                             unidad_ultimo="brl_mm", unidad_cambio="pct", trimestral=False, z120=np.nan))

        # Bloque «12m»: suma móvil de doce meses (saldo: promedio de doce sumas contra las doce anteriores).
        s12 = n12.dropna()
        v = T.variaciones_saldo(s12)
        v["ultimo"] = s12.iloc[-1] / 1e3
        v["share"] = s12.iloc[-1] / tot_12[s12.index[-1]]
        tablas.append(T.fila(v, bloque="12m", orden=orden, fila=rotulo, grupo=grupo,
                             unidad_ultimo="brl_mm", unidad_cambio="pct", trimestral=False, z120=np.nan))

        # Bloque «indice»: concesiones reales 12m / IBC-Br 12m, base 2014 = 100. Sin share.
        i = idx.dropna()
        v = T.variaciones_saldo(i)
        v["ultimo"] = i.iloc[-1]
        v["share"] = np.nan
        zs = z.dropna()
        v["z120"] = zs.iloc[-1] if len(zs) else np.nan
        tablas.append(T.fila(v, bloque="indice", orden=orden, fila=rotulo, grupo=grupo,
                             unidad_ultimo="num", unidad_cambio="pct", trimestral=False))
    return pd.concat(filas, ignore_index=True), pd.DataFrame(tablas)


def main(argv: list[str] | None = None) -> int:
    s = {nombre: SG.serie_mensual(SG.CODIGOS[clave]) for clave, nombre in SERIES.items()}
    deflactor = SG.deflactor(SG.serie_mensual(SG.CODIGOS["ipca"]))
    larga, tablas = construir(s, deflactor)
    for nombre, df in (("bk_concesiones", larga), ("bk_concesiones_tablas", tablas)):
        A.publicar_gold(nombre, df, fuente="bcb_sgs", dataset=DATASET, desde=[f"crudo/{SG.FUENTE}"],
                        nota="Concesiones libre/dirigido e índice frente al IBC-Br (sección 01)")
        print(f"{nombre}: {len(df):,} filas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
