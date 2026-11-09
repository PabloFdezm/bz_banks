#!/usr/bin/env python3
"""Series del Sistema financiero (SGS + tablas del macro) para el dashboard de bancos.

POR QUÉ EXISTE
--------------
El spec de datos del dashboard de bancos (``docs/SPEC_DATOS_BANCOS_v0.1.md``
§3.9) pide las series del Sistema —mora 90, atrasos 15-90, crédito real, crédito dirigido,
spread, ICC, deuda de hogares— en formato largo mensual y trimestral con bandas. Esas series
vienen del SGS, de la encuesta Focus (``focus.py``) y del BIS;
reunirlas en cada página del sitio produciría cifras divergentes. Este módulo es el único
lugar donde se transforman, y escribe ``datos/gold/bk_sistema_m.parquet`` y
``datos/gold/bk_sistema_q.parquet``.

Decisiones del encargo 61 y su corrección 61b (02-11-2026, «Decisiones del arquitecto»
en ``docs/PENDIENTES.md``), registradas aquí para el que relea:

- Los 38 códigos del encargo respondieron con JSON y fechas recientes (2-nov-2026). Ninguno se reemplazó.
- ``impulso_credito`` no existe como tabla en ``pb/`` (se revisó el inventario; solo aparece
  en un docstring), así que se recalcula con SGS 20539 + 4382. Se publica en pp del PIB
  como ``impulso_credito_pp``.
- 61b · Unidades: TODA la tabla va en fracción (0,05 = 5 %): mora, atrasos, spread, icc,
  credito_pib, crecimientos reales y las series que ya venían en fracción de pb. Solo el
  impulso y el hiato del BIS quedan en pp, marcados con sufijo ``_pp`` y columna ``unidad``
  (fraccion | pp).
- 61b · mora90 por modalidad: TODAS salen del SGS (21119, 21121, 21127, 21151 incluidas);
  ``hogares_modalidades`` queda fuera de esta tabla (solo B4-02). ``mora90_personal`` =
  21114 (personal NO consignado, nombre oficial del SGS). Equivalencia «Tarjeta de crédito» = 21129 (total); 21127 y
  21128 son detalle.
- 61b · Nombres sin la expansión mecánica del shorthand de §3.9:
  ``dirigido_{rural,imob,bndes}_real_aa``, ``credito_grande_real_aa`` (27702),
  ``mora90_grande`` (27704).
- ``comprometimento`` (29034), ``endividamento`` (29037) y ``desocupación`` (24369, PNADC = IBGE
  t6381|v4099) se leen del SGS desde el 6-nov-2026 (tarea 1.3; antes venían congeladas de
  ``datos/intermedio/``). Desde el 8-nov-2026 tampoco quedan entradas congeladas: ``ipca_esperado_12m`` sale
  de Focus (``focus.py``) y ``selic_real_exante`` = (1 + meta Selic SGS 432) / (1 + Focus IPCA 12m) − 1 por día
  de encuesta, media mensual (23 trimestres es excepción aceptada). Reproduce al decimal la entrada congelada
  ``datos/intermedio/tasa_real_exante.parquet`` que dejó el dashboard macro.
- ``bis_hiato_credito_pib_pp`` se lee del crudo local ``datos/crudo/bis/credit_gap`` tal
  cual, en pp (solo trimestral). ``pix_share`` queda fuera: encargo propio en la ola 2.

78c (encargo 78, ola 4): ipca_12m (acumulado 12 meses desde SGS 433), ipca_esperado_12m
(mediana Focus a 12 meses, último envío de cada mes), icc_real_exante (ex ante),
mora90_pf_livre_adel3m (mora 90 de t+3 en la fecha t) y d_1m / d_3m en bk_sistema_m.
En _q, ipca_12m toma el último mes del trimestre; el resto, promedio como siempre.

Receta:

    python -X utf8 pipeline/preparar_gold_bancos_sistema.py   # deriva; una serie que falte en el crudo se baja
                                                     # (el refresco de todas: paso «sgs» de actualizar.py)
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

import almacen as A
import focus as FO
import sgs as SG


# Series en nivel: el valor del SGS (que las sirve en %) pasado a fracción (61b).
# Series en nivel: el valor del SGS (que las sirve en %) pasado a fracción (61b). Códigos en sgs.CODIGOS.
NIVELES = ["credito_pib", "mora90_total", "mora90_libre", "mora90_direccionado", "mora90_pf", "mora90_pj",
           "mora90_pf_livre", "mora90_pj_livre", "atraso15_90_pf", "atraso15_90_pj", "mora90_personal",
           "mora90_consignado_privado", "mora90_consignado_publico", "mora90_consignado_inss",
           "mora90_consignado_total", "mora90_vehiculos", "mora90_rotativo", "mora90_parcelado",
           "mora90_cartao_total", "mora90_inmobiliario_mercado", "mora90_inmobiliario_dirigido",
           "mora90_inmobiliario_total", "mora90_mpme", "mora90_grande", "spread_livre", "icc"]

# Saldos que se deflactan con el IPCA y se publican como variación real a/a (fracción).
# Las dirigidas suman PJ + PF en nominal antes de deflactar.
REAL_AA = {
    "credito_total_real_aa": ["credito_total"],
    "credito_total_real_aa_pf": ["credito_pf"],
    "credito_total_real_aa_pj": ["credito_pj"],
    "credito_mpme_real_aa": ["credito_mpme"],
    "credito_grande_real_aa": ["credito_grande"],
    "dirigido_rural_real_aa": ["credito_pj_rural", "credito_pf_rural"],
    "dirigido_imob_real_aa": ["credito_pj_inmobiliario", "credito_pf_inmobiliario"],
    "dirigido_bndes_real_aa": ["credito_pj_bndes", "credito_pf_bndes"],
}

# Concesiones PF livre SA: deflactar y 3m/3m anualizado.
REAL_M3M3A = ["conc_pf_livre_sa"]

# Hogares y empleo directo del SGS (tarea 1.3), en % → fracción.
HOGARES_SGS = ["endividamento", "comprometimento", "desocupacion"]

# Únicas series en puntos porcentuales; todo lo demás va en fracción (61b).
SERIES_EN_PP = frozenset({"impulso_credito_pp", "bis_hiato_credito_pib_pp"})

VENTANA_M, MINIMO_M = 120, 60       # bandas mensuales: 120 meses, mínimo 60
VENTANA_Q, MINIMO_Q = 40, 20        # bandas trimestrales: 40 trimestres, mínimo 20


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
    d = FO.ipca_12m()
    if d.empty:
        raise ValueError("Focus: no hay IPCA con horizonte 12 meses")
    s = d.groupby(d.index.to_period("M")).last()
    s.index = s.index.to_timestamp()
    return SG.mensual(s).rename("ipca_esperado_12m")


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


def leer_selic_real_exante() -> pd.Series:
    """Selic real ex ante: (1 + meta Selic) / (1 + Focus IPCA 12m) − 1 en cada día de encuesta, media mensual.

    La meta (SGS 432) viene publicada hasta la próxima reunión del Copom; solo cuentan los días con encuesta."""
    esperado = FO.ipca_12m()
    meta = (SG.serie(SG.CODIGOS["selic_meta"]) / 100).reindex(esperado.index)
    if meta.isna().any():
        raise ValueError("SGS 432: faltan días de meta Selic en fechas con encuesta Focus")
    s = (1.0 + meta) / (1.0 + esperado) - 1.0
    return s.groupby(pd.PeriodIndex(s.index, freq="M")).mean().rename("selic_real_exante")


def leer_bis() -> pd.Series:
    """Brecha crédito/PIB del BIS desde el crudo local, trimestral tal cual, en pp (§3.9/61b)."""
    ruta = A.ruta_cruda("bis", "credit_gap") / "brecha_credito_brasil.csv"
    d = pd.read_csv(ruta)
    q = pd.PeriodIndex(d["TIME_PERIOD"], freq="Q")
    s = pd.Series(d["OBS_VALUE"].astype(float).to_numpy(),
                  index=q.to_timestamp(how="end").normalize())
    return s.rename("bis_hiato_credito_pib_pp")


def construir_series() -> tuple[dict[str, pd.Series], dict[str, pd.Series]]:
    """Devuelve (series mensuales, serie BIS trimestral)."""
    cache: dict[int, pd.Series] = {}

    def s(nombre: str) -> pd.Series:
        if nombre not in cache:
            cache[nombre] = SG.mensual(SG.serie(SG.CODIGOS[nombre]))
        return cache[nombre]

    indice = SG.deflactor(s("ipca"))
    m: dict[str, pd.Series] = {}

    for serie_id in NIVELES:
        m[serie_id] = s(serie_id) / 100.0       # el SGS las sirve en %; la tabla va en fracción
    for serie_id, codigos in REAL_AA.items():
        nominal = s(codigos[0])
        for c in codigos[1:]:                       # dirigidas: PJ + PF en nominal
            nominal = nominal + s(c)               # si falta un mes en una, NaN
        m[serie_id] = real_aa(nominal, indice)
    for serie_id in REAL_M3M3A:
        m[serie_id] = real_m3m3a(s(serie_id), indice)

    m["impulso_credito_pp"] = impulso_credito(s("credito_total"), s("pib_12m"))

    m["ipca_12m"] = ipca_12m(s("ipca"))
    m["ipca_esperado_12m"] = leer_focus_ipca_12m()
    m["icc_real_exante"] = ((1.0 + m["icc"]) / (1.0 + m["ipca_esperado_12m"]) - 1.0) \
        .rename("icc_real_exante")
    m["mora90_pf_livre_adel3m"] = adelantar(m["mora90_pf_livre"], 3) \
        .rename("mora90_pf_livre_adel3m")

    for serie_id in HOGARES_SGS:
        m[serie_id] = (s(serie_id) / 100.0).rename(serie_id)
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
    valores = valores[grupos.count() == 3]
    return pd.Series(valores.to_numpy(),
                     index=valores.index.to_timestamp(how="end").normalize())


def construir_trimestral(mensuales: dict[str, pd.Series],
                         trimestrales: dict[str, pd.Series]) -> pd.DataFrame:
    series = {serie_id: promedio_trimestral(s) for serie_id, s in mensuales.items()}
    series["ipca_12m"] = ultimo_mes_trimestral(mensuales["ipca_12m"])   # acumulado: último mes, no promedio
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


def verificar(m: pd.DataFrame, q: pd.DataFrame) -> int:
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
    for serie_id in ("credito_pib", "mora90_total", "spread_livre"):
        codigo = SG.CODIGOS[serie_id]
        t = m.loc[m["serie_id"] == serie_id, ["fecha", "valor"]].dropna().tail(3)
        c = SG.mensual(SG.serie(codigo)).dropna().tail(3)
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
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    mensuales, trimestrales_bis = construir_series()
    m = deltas_mensuales(tabla_larga(mensuales, VENTANA_M, MINIMO_M))
    q = construir_trimestral(mensuales, trimestrales_bis)
    if verificar(m, q):
        print("[!] bk_sistema no se publica: la verificación falló", file=sys.stderr)
        return 1

    desde = [f"crudo/{SG.FUENTE}/{SG.DATASET}", "crudo/bis/credit_gap", f"crudo/{FO.FUENTE}/{FO.DATASET}"]
    for nombre, tabla in (("bk_sistema_m", m), ("bk_sistema_q", q)):
        A.publicar_gold(nombre, tabla, fuente=SG.FUENTE, dataset="bancos_gold_sistema", desde=desde)
    print(f"[+] bk_sistema_m: {len(m)} filas, {m['serie_id'].nunique()} series, "
          f"{m['fecha'].min().date()} a {m['fecha'].max().date()}")
    print(f"[+] bk_sistema_q: {len(q)} filas, {q['serie_id'].nunique()} series, "
          f"{q['fecha'].min().date()} a {q['fecha'].max().date()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
