#!/usr/bin/env python3
"""Series del Sistema financiero (SGS + tablas del macro) para el dashboard de bancos.

POR QUÉ EXISTE
--------------
El spec de datos del dashboard de bancos (``docs/dashboard_bancos/SPEC_DATOS_BANCOS_v0.1.md``
§3.9) pide las series del Sistema —mora 90, atrasos 15-90, crédito real, crédito dirigido,
spread, ICC, deuda de hogares— en formato largo mensual y trimestral con bandas. Esas series
viven mitad en el SGS y mitad en tablas que el dashboard macro ya construyó en ``pb/``;
reunirlas en cada página del sitio produciría cifras divergentes. Este módulo es el único
lugar donde se transforman, y escribe ``datos/gold/bk_sistema_m.parquet`` y
``datos/gold/bk_sistema_q.parquet``.

Es un archivo aparte de ``preparar_gold_bancos.py`` a propósito: ese lo escribe otro worker
en la misma ola del plan 57 y el arquitecto integra ambos como subcomandos.

Decisiones del encargo 61 y su corrección 61b (02-11-2026, «Decisiones del arquitecto»
en ``docs/dashboard_bancos/PENDIENTES.md``), registradas aquí para el que relea:

- Los 38 códigos del encargo respondieron con JSON y fechas recientes (paso 1, tabla en
  ``docs/orquestacion/61_resultado_sgs_sistema_2026-11-02.md``). Ninguno se reemplazó.
- ``impulso_credito`` no existe como tabla en ``pb/`` (se revisó el inventario; solo aparece
  en un docstring), así que se recalcula con SGS 20539 + 4382. Se publica en pp del PIB
  como ``impulso_credito_pp``.
- 61b · Unidades: TODA la tabla va en fracción (0,05 = 5 %): mora, atrasos, spread, icc,
  credito_pib, crecimientos reales y las series que ya venían en fracción de pb. Solo el
  impulso y el hiato del BIS quedan en pp, marcados con sufijo ``_pp`` y columna ``unidad``
  (fraccion | pp).
- 61b · mora90 por modalidad: TODAS salen del SGS (21119, 21121, 21127, 21151 incluidas);
  ``hogares_modalidades`` queda fuera de esta tabla (solo B4-02). ``mora90_personal`` =
  21114 (incluye consignado). Equivalencia «Tarjeta de crédito» = 21129 (total); 21127 y
  21128 son detalle.
- 61b · Nombres sin la expansión mecánica del shorthand de §3.9:
  ``dirigido_{rural,imob,bndes}_real_aa``, ``credito_grande_real_aa`` (27702),
  ``mora90_grande`` (27704).
- ``comprometimento`` (29034) y ``endividamento`` (29037) se leen de ``datos/intermedio/fh_deuda.parquet``;
  ``desocupación`` de ``datos/intermedio/tasas_pnad.parquet`` (t6381|v4099); ``selic_real_exante`` de
  ``datos/intermedio/tasa_real_exante.parquet`` (media mensual de la serie diaria; 23 trimestres es
  excepción aceptada). Nada de eso se re-baja.
- ``bis_hiato_credito_pib_pp`` se lee del crudo local ``datos/crudo/bis/credit_gap`` tal
  cual, en pp (solo trimestral). ``pix_share`` queda fuera: encargo propio en la ola 2.

78c (encargo 78, ola 4): ipca_12m (acumulado 12 meses desde SGS 433), ipca_esperado_12m
(mediana Focus a 12 meses, último envío de cada mes), icc_real_exante (ex ante),
mora90_pf_livre_adel3m (mora 90 de t+3 en la fecha t) y d_1m / d_3m en bk_sistema_m.
En _q, ipca_12m toma el último mes del trimestre; el resto, promedio como siempre.

Receta:

    python -X utf8 preparar_gold_bancos_sistema.py             # baja lo que falta y deriva
    python -X utf8 preparar_gold_bancos_sistema.py --descargar  # fuerza re-descarga del SGS
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

import almacen as A

BASE = Path(__file__).resolve().parents[1]
FUENTE_SGS = "bcb_sgs"
DATASET_SGS = "bancos_sistema"       # dataset propio, como cada hoja del macro
DESDE_SGS = "01/01/2000"
PB = BASE / "datos" / "intermedio"
CARPETA_GOLD = PB / "Banks"

# Series en nivel: el valor del SGS (que las sirve en %) pasado a fracción (61b).
NIVELES = {
    "credito_pib": 20622,
    "mora90_total": 21082,
    "mora90_pf_livre": 21112,
    "mora90_pj_livre": 21086,
    "atraso15_90_pf": 21005,
    "atraso15_90_pj": 21004,
    "mora90_personal": 21114,             # incluye consignado (decisión 61b)
    "mora90_consignado_privado": 21116,
    "mora90_consignado_publico": 21117,
    "mora90_consignado_inss": 21118,
    "mora90_consignado_total": 21119,     # del SGS desde 61b, no de hogares_modalidades
    "mora90_vehiculos": 21121,
    "mora90_rotativo": 21127,
    "mora90_parcelado": 21128,
    "mora90_cartao_total": 21129,
    "mora90_inmobiliario_mercado": 21149,
    "mora90_inmobiliario_dirigido": 21150,
    "mora90_inmobiliario_total": 21151,
    "mora90_mpme": 27703,
    "mora90_grande": 27704,
    "spread_livre": 20786,
    "icc": 25351,
}

# Saldos que se deflactan con el IPCA y se publican como variación real a/a (fracción).
# Las dirigidas suman PJ + PF en nominal antes de deflactar.
REAL_AA = {
    "credito_total_real_aa": [20539],
    "credito_total_real_aa_pf": [20541],
    "credito_total_real_aa_pj": [20540],
    "credito_mpme_real_aa": [27701],
    "credito_grande_real_aa": [27702],
    "dirigido_rural_real_aa": [20597, 20609],
    "dirigido_imob_real_aa": [20600, 20612],
    "dirigido_bndes_real_aa": [20604, 20616],
}

# Concesiones PF livre SA: deflactar y 3m/3m anualizado.
REAL_M3M3A = {"conc_pf_livre_sa": 24444}

IPCA, PIB_12M, SALDO_TOTAL = 433, 4382, 20539

PNAD_DESOCUPACION = "t6381|v4099"   # Taxa de desocupação, la misma que cita §3.9
FOCUS_PARQUET = PB / "expectativas_focus.parquet"   # 78c: expectativas IPCA 12 meses

# Únicas series en puntos porcentuales; todo lo demás va en fracción (61b).
SERIES_EN_PP = frozenset({"impulso_credito_pp", "bis_hiato_credito_pib_pp"})

VENTANA_M, MINIMO_M = 120, 60       # bandas mensuales: 120 meses, mínimo 60
VENTANA_Q, MINIMO_Q = 40, 20        # bandas trimestrales: 40 trimestres, mínimo 20


# --- SGS: descarga y lectura (mismo patrón que preparar_finanzas_hogares_powerbi) -------- #

def sgs(codigo: int, descargar: bool) -> pd.Series:
    """Serie SGS desde el crudo ``bcb_sgs/bancos_sistema`` (la baja si falta o si se pide).

    Usa ``bcb_api.descargar_serie`` (nunca requests directo) y guarda por ``almacen``.
    El JSON se guarda con la clave ``data`` para seguir el formato del resto del crudo SGS.
    """
    ruta = A.ruta_cruda(FUENTE_SGS, DATASET_SGS) / f"serie_{codigo}.json"
    if descargar or not ruta.exists():
        import certificados  # noqa: F401  CA corporativa; antes de requests

        import bcb_api

        print(f"[~] bajando SGS {codigo}...", file=sys.stderr)
        filas = [{"data": f["fecha"], "valor": f["valor"]}
                 for f in bcb_api.descargar_serie(codigo, desde=DESDE_SGS)]
        if not filas:
            raise ValueError(f"SGS {codigo}: la API no devolvió observaciones")
        url = (f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
               f"?formato=json&dataInicial={DESDE_SGS}")
        A.guardar_crudo(FUENTE_SGS, DATASET_SGS, ruta.name,
                        json.dumps(filas, ensure_ascii=False).encode("utf-8"), url)
    d = pd.DataFrame(json.loads(ruta.read_text(encoding="utf-8")))
    s = pd.Series(pd.to_numeric(d["valor"], errors="coerce").to_numpy(),
                  index=pd.to_datetime(d["data"], format="%d/%m/%Y"))
    if s.index.duplicated().any():
        raise ValueError(f"SGS {codigo}: meses repetidos")
    return s.sort_index().rename(str(codigo))


def mensual(s: pd.Series) -> pd.Series:
    """Índice a PeriodIndex mensual continuo, para que ``shift(12)`` sean 12 meses de verdad."""
    p = s.copy()
    p.index = pd.PeriodIndex(pd.to_datetime(p.index), freq="M")
    p = p[~p.index.duplicated(keep="last")].sort_index()
    if len(p) > 1:
        p = p.reindex(pd.period_range(p.index[0], p.index[-1], freq="M"))
    return p.astype(float)


# --- transformaciones de §3.9 ------------------------------------------------------------ #

def deflactor(ipca: pd.Series) -> pd.Series:
    """Índice IPCA encadenando la variación mensual (SGS 433), base 1,0 = último mes."""
    if ipca.isna().any():
        raise ValueError("SGS 433 trae meses sin valor: no se puede encadenar el índice")
    indice = (1.0 + ipca / 100.0).cumprod()
    return indice / indice.iloc[-1]


def real_aa(nominal: pd.Series, indice: pd.Series) -> pd.Series:
    """Deflacta y devuelve la variación a/a en fracción (61b: 0,05 = 5 %).

    Misma base en t y t-12: el ancla del índice se cancela en el cociente.
    """
    real = nominal / indice.reindex(nominal.index)
    return real / real.shift(12) - 1.0


def real_m3m3a(nominal: pd.Series, indice: pd.Series) -> pd.Series:
    """Deflacta y anualiza 3m/3m: (media3_t / media3_{t-3})^4 - 1, en fracción."""
    real = nominal / indice.reindex(nominal.index)
    m3, previa = real.rolling(3).mean(), real.shift(3).rolling(3).mean()
    return (m3 / previa) ** 4 - 1.0


def impulso_credito(saldo: pd.Series, pib: pd.Series) -> pd.Series:
    """(flujo12_t - flujo12_{t-12}) / PIB nominal 12m × 100, en pp del PIB (61b: única
    unidad que no es fracción, por eso el sufijo _pp del serie_id)."""
    flujo12 = saldo - saldo.shift(12)
    return (flujo12 - flujo12.shift(12)) / pib * 100.0


def ipca_12m(ipca_mensual_pct: pd.Series) -> pd.Series:
    """IPCA acumulado 12 meses en fracción, encadenando la variación mensual (SGS 433, en %).

    Exige los doce meses con dato: si falta uno, el valor queda vacío.
    """
    factor = 1.0 + ipca_mensual_pct / 100.0
    return (factor.rolling(12).apply(np.prod, raw=True) - 1.0).rename("ipca_12m")


def adelantar(serie: pd.Series, meses: int = 3) -> pd.Series:
    """Valor de t+meses en la fecha t (shift hacia atrás). Quita los últimos meses vacíos."""
    return serie.shift(-meses).dropna()


def leer_focus_ipca_12m() -> pd.Series:
    """Mediana Focus del IPCA a 12 meses adelante, último envío de cada mes, en fracción.

    La mediana ya viene en fracción (es_porcentaje = True: 0,046 = 4,6 %). Solo el horizonte
    «12 meses» de tipo_horizonte; nunca el año calendario, que no es 12 meses adelante.
    """
    d = pd.read_parquet(FOCUS_PARQUET)
    d = d[(d["indicador"] == "IPCA") & (d["tipo_horizonte"] == "12 meses")].copy()
    if d.empty:
        raise ValueError("expectativas_focus: no hay IPCA con horizonte 12 meses")
    d["fecha_encuesta"] = pd.to_datetime(d["fecha_encuesta"])
    d["mes"] = d["fecha_encuesta"].dt.to_period("M").dt.to_timestamp()
    d = d.sort_values("fecha_encuesta").drop_duplicates("mes", keep="last")
    s = pd.Series(d["mediana"].to_numpy(dtype=float), index=pd.DatetimeIndex(d["mes"]))
    return mensual(s).rename("ipca_esperado_12m")


def ultimo_mes_trimestral(s: pd.Series) -> pd.Series:
    """Valor del último mes de cada trimestre (marzo, junio, septiembre, diciembre), a fin de
    trimestre. Para saldos acumulados como el IPCA de 12 meses, donde el promedio no sirve."""
    s = s[s.index.month % 3 == 0].dropna()
    return pd.Series(s.to_numpy(dtype=float),
                     index=s.index.to_timestamp(how="end").normalize())


def deltas_mensuales(m: pd.DataFrame) -> pd.DataFrame:
    """d_1m y d_3m por serie, con la convención de d_tt / d_aa de la tabla trimestral: la
    diferencia va en la misma unidad que la serie (fracción o pp)."""
    m = m.sort_values(["serie_id", "fecha"]).copy()
    m["d_1m"] = m.groupby("serie_id")["valor"].diff(1)
    m["d_3m"] = m.groupby("serie_id")["valor"].diff(3)
    return m.sort_values(["fecha", "serie_id"]).reset_index(drop=True)


# --- lectura de pb/ (no se re-baja nada) -------------------------------------------------- #

def leer_fh_deuda() -> dict[str, pd.Series]:
    d = pd.read_parquet(PB / "fh_deuda.parquet")
    idx = pd.to_datetime(d["fecha"])
    return {
        "endividamento": mensual(pd.Series(d["deuda_ingreso"].to_numpy(), index=idx)),
        "comprometimento": mensual(pd.Series(d["servicio"].to_numpy(), index=idx)),
    }


def leer_desocupacion() -> pd.Series:
    d = pd.read_parquet(PB / "tasas_pnad.parquet")
    d = d[d["serie_id"] == PNAD_DESOCUPACION]
    if d.empty:
        raise ValueError(f"tasas_pnad: no está la serie {PNAD_DESOCUPACION}")
    return mensual(pd.Series(d["tasa"].to_numpy(), index=pd.to_datetime(d["fecha"]))) \
        .rename("desocupacion")


def leer_selic_real_exante() -> pd.Series:
    d = pd.read_parquet(PB / "tasa_real_exante.parquet")
    s = pd.Series(d["tasa_real_exante"].to_numpy(), index=pd.to_datetime(d["fecha"]))
    return s.groupby(pd.PeriodIndex(s.index, freq="M")).mean().rename("selic_real_exante")


def leer_bis() -> pd.Series:
    """Brecha crédito/PIB del BIS desde el crudo local, trimestral tal cual, en pp (§3.9/61b)."""
    ruta = A.ruta_cruda("bis", "credit_gap") / "brecha_credito_brasil.csv"
    d = pd.read_csv(ruta)
    q = pd.PeriodIndex(d["TIME_PERIOD"], freq="Q")
    s = pd.Series(d["OBS_VALUE"].astype(float).to_numpy(),
                  index=q.to_timestamp(how="end").normalize())
    return s.rename("bis_hiato_credito_pib_pp")


# --- armado de las dos tablas ------------------------------------------------------------ #

def construir_series(descargar: bool) -> tuple[dict[str, pd.Series], dict[str, pd.Series]]:
    """Devuelve (series mensuales, serie BIS trimestral). Queda separado para que el
    arquitecto lo integre como subcomando sin tocar las transformaciones."""
    cache: dict[int, pd.Series] = {}

    def s(cod: int) -> pd.Series:
        if cod not in cache:
            cache[cod] = mensual(sgs(cod, descargar))
        return cache[cod]

    indice = deflactor(s(IPCA))
    m: dict[str, pd.Series] = {}

    for serie_id, cod in NIVELES.items():
        m[serie_id] = s(cod) / 100.0            # el SGS las sirve en %; la tabla va en fracción
    for serie_id, codigos in REAL_AA.items():
        nominal = s(codigos[0])
        for c in codigos[1:]:                       # dirigidas: PJ + PF en nominal
            nominal = nominal + s(c)               # alinea meses; si falta uno, NaN
        m[serie_id] = real_aa(nominal, indice)
    for serie_id, cod in REAL_M3M3A.items():
        m[serie_id] = real_m3m3a(s(cod), indice)

    m["impulso_credito_pp"] = impulso_credito(s(SALDO_TOTAL), s(PIB_12M))

    # 78c · IPCA 12m, expectativa Focus y derivadas ex ante (fracción).
    m["ipca_12m"] = ipca_12m(s(IPCA))
    m["ipca_esperado_12m"] = leer_focus_ipca_12m()
    m["icc_real_exante"] = ((1.0 + m["icc"]) / (1.0 + m["ipca_esperado_12m"]) - 1.0) \
        .rename("icc_real_exante")
    m["mora90_pf_livre_adel3m"] = adelantar(m["mora90_pf_livre"], 3) \
        .rename("mora90_pf_livre_adel3m")

    m.update(leer_fh_deuda())
    m["desocupacion"] = leer_desocupacion()
    m["selic_real_exante"] = leer_selic_real_exante()

    for serie_id, serie in m.items():
        if serie.dropna().empty:
            raise ValueError(f"{serie_id}: quedó vacía tras la transformación")
    return m, {"bis_hiato_credito_pib_pp": leer_bis()}


def tabla_larga(series: dict[str, pd.Series], ventana: int, minimo: int) -> pd.DataFrame:
    """Formato largo con bandas p10/p50/p90 (rolling, nulas con menos de ``minimo``) y es_ultimo."""
    partes = []
    for serie_id, serie in series.items():
        fechas = serie.index.to_timestamp() if isinstance(serie.index, pd.PeriodIndex) \
            else serie.index
        partes.append(pd.DataFrame({"fecha": fechas, "serie_id": serie_id,
                                    "unidad": "pp" if serie_id in SERIES_EN_PP else "fraccion",
                                    "valor": serie.to_numpy(dtype=float)}))
    t = pd.concat(partes, ignore_index=True)
    for col, q in (("p10", 0.10), ("p50", 0.50), ("p90", 0.90)):
        t[col] = float("nan")
    for _, g in t.groupby("serie_id", sort=False):
        v = pd.Series(g["valor"].to_numpy())
        for col, q in (("p10", 0.10), ("p50", 0.50), ("p90", 0.90)):
            t.loc[g.index, col] = v.rolling(ventana, min_periods=minimo).quantile(q).to_numpy()
    t["es_ultimo"] = False
    t.loc[t.groupby("serie_id")["fecha"].idxmax(), "es_ultimo"] = True
    return t.sort_values(["fecha", "serie_id"]).reset_index(drop=True)


def promedio_trimestral(s: pd.Series) -> pd.Series:
    """Promedio de los tres meses, fecha a fin de trimestre; solo trimestres completos.

    §3.9/encargo 61: tasas, ratios y mora van por promedio; en esta tabla no entra ningún
    saldo en nivel (todos los niveles son tasas o índices), así que no hay caso "último mes".
    """
    grupos = s.groupby(s.index.asfreq("Q"))
    valores = grupos.mean()
    valores = valores[grupos.count() == 3]        # exige los tres meses con dato
    return pd.Series(valores.to_numpy(),
                     index=valores.index.to_timestamp(how="end").normalize())


def construir_trimestral(mensuales: dict[str, pd.Series],
                         trimestrales: dict[str, pd.Series]) -> pd.DataFrame:
    series = {serie_id: promedio_trimestral(s) for serie_id, s in mensuales.items()}
    series["ipca_12m"] = ultimo_mes_trimestral(mensuales["ipca_12m"])   # 78c: saldo, no promedio
    series.update(trimestrales)                   # el BIS ya es trimestral, tal cual
    series = {k: v for k, v in series.items() if not v.dropna().empty}
    q = tabla_larga(series, VENTANA_Q, MINIMO_Q)
    # Δ contra el trimestre anterior y contra el mismo trimestre de un año antes (decisión 74/B0: las
    # diferencias se calculan aquí, nunca en el navegador). Misma unidad que la serie: en fracción, la
    # diferencia también es fracción (0,01 = 1 pp); en pp, pp.
    q = q.sort_values(["serie_id", "fecha"])
    q["d_tt"] = q.groupby("serie_id")["valor"].diff(1)
    q["d_aa"] = q.groupby("serie_id")["valor"].diff(4)
    return q.reset_index(drop=True)


def escribir_parquet_atomico(tabla: pd.DataFrame, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporal = tempfile.mkstemp(dir=destino.parent, suffix=".parquet.tmp")
    os.close(descriptor)
    try:
        tabla.to_parquet(temporal, index=False)
        os.replace(temporal, destino)
    except BaseException:
        Path(temporal).unlink(missing_ok=True)
        raise


# --- verificación (define «terminado» en los encargos 61 y 61b) -------------------------- #

def verificar(m: pd.DataFrame, q: pd.DataFrame, crudo: dict[int, pd.Series]) -> int:
    problemas = []
    hoy = pd.Timestamp.now().normalize()

    for nombre, t in (("bk_sistema_m", m), ("bk_sistema_q", q)):
        if (t["fecha"] > hoy).any():
            problemas.append(f"{nombre}: hay fechas futuras")
        n = t.groupby("serie_id").size()
        cortas = n[n < 24]
        for serie_id, k in cortas.items():
            ultima = t.loc[t["serie_id"] == serie_id, "fecha"].max().date()
            print(f"[i] {nombre} · {serie_id}: {k} observaciones (hasta {ultima})")

    # tres series contra el SGS crudo: una de saldo/ratio, una de mora, una de tasa.
    # La tabla va en fracción: tabla × 100 debe reproducir el crudo exactamente.
    print("\núltimos 3 valores: tabla (fracción) vs SGS crudo (%)")
    for serie_id, codigo in (("credito_pib", 20622), ("mora90_total", 21082),
                             ("spread_livre", 20786)):
        t = m.loc[m["serie_id"] == serie_id, ["fecha", "valor"]].dropna().tail(3)
        c = crudo[codigo].dropna().tail(3)
        fechas_c = c.index.to_timestamp() if isinstance(c.index, pd.PeriodIndex) else c.index
        print(f"  {serie_id} (SGS {codigo}):")
        print("    tabla:", "  ".join(f"{f.date()} {v:.4f}" for f, v in t.itertuples(index=False)))
        print("    crudo:", "  ".join(f"{f.date()} {v:.2f}" for f, v in zip(fechas_c, c.to_numpy())))
        tabla_v = t["valor"].to_numpy()
        crudo_v = c.to_numpy()
        if len(tabla_v) != len(crudo_v) or not (abs(tabla_v * 100.0 - crudo_v) < 1e-9).all():
            problemas.append(f"{serie_id}: la tabla no reproduce el SGS crudo")

    ult = m.loc[m["serie_id"] == "impulso_credito_pp", ["fecha", "valor"]].dropna().tail(1)
    valor = float(ult["valor"].iloc[0]) if not ult.empty else float("nan")
    print(f"\n  impulso_credito_pp (último): {ult['fecha'].iloc[0].date() if not ult.empty else '-'} "
          f"{valor:.3f} pp del PIB")
    if not (-20 < valor < 20):
        problemas.append(f"impulso_credito_pp fuera de rango plausible: {valor}")

    for sid, (lo, hi) in {"ipca_12m": (-0.05, 0.5), "ipca_esperado_12m": (0.0, 0.3)}.items():
        v = m.loc[m["serie_id"] == sid, "valor"].dropna()
        if v.empty or not v.between(lo, hi).all():
            problemas.append(f"{sid} fuera de rango plausible ({lo}, {hi}): revisar unidad")

    atraso = m.loc[m["serie_id"].isin(["atraso15_90_pf", "atraso15_90_pj"]), "valor"].dropna()
    if not atraso.empty and not atraso.between(0, 1).all():
        problemas.append("atrasos 15-90 fuera de 0-1: revisar la unidad de la familia 21003+")

    print("\nserie_id | unidad (bk_sistema_q, superconjunto de _m)")
    for serie_id, unidad in q[["serie_id", "unidad"]].drop_duplicates() \
            .sort_values("serie_id").itertuples(index=False):
        print(f"  {serie_id} | {unidad}")

    for p in problemas:
        print(f"[!] {p}", file=sys.stderr)
    return 1 if problemas else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--descargar", action="store_true",
                    help="re-baja las series del SGS aunque el crudo exista")
    args = ap.parse_args(argv)

    mensuales, trimestrales_bis = construir_series(args.descargar)
    m = deltas_mensuales(tabla_larga(mensuales, VENTANA_M, MINIMO_M))   # 78c: d_1m, d_3m
    q = construir_trimestral(mensuales, trimestrales_bis)

    escribir_parquet_atomico(m, CARPETA_GOLD / "bk_sistema_m.parquet")
    escribir_parquet_atomico(q, CARPETA_GOLD / "bk_sistema_q.parquet")
    print(f"[+] bk_sistema_m: {len(m)} filas, {m['serie_id'].nunique()} series, "
          f"{m['fecha'].min().date()} a {m['fecha'].max().date()}")
    print(f"[+] bk_sistema_q: {len(q)} filas, {q['serie_id'].nunique()} series, "
          f"{q['fecha'].min().date()} a {q['fecha'].max().date()}")

    crudo = {cod: mensual(sgs(cod, False)) for cod in (20622, 21082, 20786)}
    return verificar(m, q, crudo)


if __name__ == "__main__":
    sys.exit(main())
