"""Series del SGS del BCB: el único lector y descargador del pipeline.

Cada serie vive en ``datos/crudo/bcb_sgs/<dataset>/actual/serie_<codigo>.json`` con la forma
``[{"data": "DD/MM/AAAA", "valor": "..."}]``. Si falta, se baja con ``bcb_api.descargar_serie`` (que sabe
que una serie inexistente llega como HTML y no como 404) y se guarda por ``almacen`` con su URL.

Siempre se pide con ``dataInicial``: sin fechas el SGS llegó a servir series atrasadas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

import almacen as A
import red

FUENTE = "bcb_sgs"
DATASET = "bancos_sistema"
DESDE = "01/01/2000"

# Catálogo de las series del SGS que usa el pipeline: nombre → código. Los nombres de las modalidades se
# identificaron cuadrando montos (pendiente: validarlos contra el catálogo del SGS). Concesiones validadas el 8-nov
# cuadrando contra la API: 20631 = 20632 (PJ) + 20633 (PF) es el total; las libres son 20634 = 20635 (PJ) + 20662 (PF).
CODIGOS = {
    # saldos de crédito (R$ millones)
    "credito_total": 20539, "credito_libre": 20542, "credito_direccionado": 20593,
    "credito_pf": 20541, "credito_pj": 20540, "credito_mpme": 27701, "credito_grande": 27702,
    "credito_pf_tarjeta": 20590, "credito_pf_consignado_a": 20576, "credito_pf_consignado_b": 20577,
    "credito_pf_consignado_c": 20578, "credito_pf_personal": 20574, "credito_pf_vehiculos": 20581,
    "credito_pf_inmobiliario": 20612, "credito_pf_rural": 20609, "credito_pf_bndes": 20616,
    "credito_pj_libre": 20543, "credito_pj_bndes": 20604, "credito_pj_rural": 20597, "credito_pj_inmobiliario": 20600,
    # concesiones (flujo mensual)
    "concesiones_total": 20631, "concesiones_pf": 20633, "concesiones_pj": 20632, "conc_pf_livre_sa": 24444,
    # mora > 90 días y atrasos 15-90 (en %)
    "mora90_total": 21082, "mora90_libre": 21085, "mora90_direccionado": 21132, "mora90_pf": 21084,
    "mora90_pj": 21083, "mora90_pf_livre": 21112, "mora90_pj_livre": 21086,
    "atraso15_90_pf": 21005, "atraso15_90_pj": 21004,
    "mora90_personal": 21114,             # incluye consignado
    "mora90_consignado_privado": 21116, "mora90_consignado_publico": 21117, "mora90_consignado_inss": 21118,
    "mora90_consignado_total": 21119, "mora90_vehiculos": 21121, "mora90_rotativo": 21127,
    "mora90_parcelado": 21128, "mora90_cartao_total": 21129,   # tarjeta = 21129 (total); 21127 y 21128 son detalle
    "mora90_inmobiliario_mercado": 21149, "mora90_inmobiliario_dirigido": 21150, "mora90_inmobiliario_total": 21151,
    "mora90_mpme": 27703, "mora90_grande": 27704,
    # tasas, precios, actividad, hogares
    "spread_livre": 20786, "icc": 25351, "tasa_creditos_nuevos": 20714, "cdi": 4389, "ipca": 433,
    "credito_pib": 20622, "pib_12m": 4382,
    "endividamento": 29037, "comprometimento": 29034,
    "desocupacion": 24369,                # PNADC (IBGE t6381|v4099)
}


def ruta(codigo: int, dataset: str = DATASET) -> Path:
    return A.ruta_cruda(FUENTE, dataset) / f"serie_{codigo}.json"


def bajar(codigo: int, dataset: str = DATASET, desde: str = DESDE) -> Path:
    """Baja la serie completa desde ``desde`` y la guarda en el crudo con su procedencia."""
    red.exigir_red(f"la serie SGS {codigo}")
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests

    import bcb_api

    print(f"[~] bajando SGS {codigo}...", file=sys.stderr)
    filas = [{"data": f["data"], "valor": f["valor"]} for f in bcb_api.descargar_serie(codigo, desde=desde)]
    if not filas:
        raise ValueError(f"SGS {codigo}: la API no devolvió observaciones")
    url = bcb_api.url_serie(codigo, desde)
    return A.guardar_crudo(FUENTE, dataset, f"serie_{codigo}.json",
                           json.dumps(filas, ensure_ascii=False).encode("utf-8"), url)


def serie(codigo: int, descargar: bool = False, *, dataset: str = DATASET, desde: str = DESDE) -> pd.Series:
    """Serie del crudo (la baja si falta o si ``descargar``), indexada por fecha y ordenada."""
    p = ruta(codigo, dataset)
    if descargar or not p.exists():
        bajar(codigo, dataset, desde)
    d = pd.DataFrame(json.loads(p.read_text(encoding="utf-8")))
    s = pd.Series(pd.to_numeric(d["valor"], errors="coerce").to_numpy(),
                  index=pd.to_datetime(d["data"], format="%d/%m/%Y"))
    if s.index.duplicated().any():
        raise ValueError(f"SGS {codigo}: fechas repetidas")
    return s.sort_index().rename(str(codigo))


def serie_mensual(codigo: int) -> pd.Series:
    """Serie del crudo con índice mensual continuo (la baja si falta)."""
    return mensual(serie(codigo))


def mensual(s: pd.Series) -> pd.Series:
    """Índice a PeriodIndex mensual continuo, para que ``shift(12)`` sean 12 meses de verdad."""
    p = s.copy()
    p.index = pd.PeriodIndex(pd.to_datetime(p.index), freq="M")
    p = p[~p.index.duplicated(keep="last")].sort_index()
    if len(p) > 1:
        p = p.reindex(pd.period_range(p.index[0], p.index[-1], freq="M"))
    return p.astype(float)


def deflactor(ipca: pd.Series) -> pd.Series:
    """Índice IPCA encadenando la variación mensual (SGS 433, en %), base 1,0 = último mes."""
    if ipca.isna().any():
        raise ValueError("SGS 433 trae meses sin valor: no se puede encadenar el índice")
    indice = (1.0 + ipca / 100.0).cumprod()
    return indice / indice.iloc[-1]


CDI = CODIGOS["cdi"]   # diario, % a.a.


def cdi_mensual() -> pd.Series:
    """CDI promedio de cada mes (fracción anual), índice Period mensual continuo (un mes sin dato queda vacío)."""
    s = serie(CDI)
    return pd.Series(s.to_numpy() / 100, index=s.index.to_period("M")).groupby(level=0).mean().asfreq("M")


def _a_fin_de_trimestre(m: pd.Series) -> pd.Series:
    m = m[m.index.month % 3 == 0]
    return pd.Series(m.to_numpy(), index=[f"{p.year}{p.month:02d}" for p in m.index])


def cdi_trimestral() -> pd.Series:
    """CDI promedio del trimestre (media de sus 3 meses), índice AAAAMM del mes final."""
    return _a_fin_de_trimestre(cdi_mensual().rolling(3, min_periods=3).mean())


def cdi_12m() -> pd.Series:
    """CDI promedio de los 12 meses que terminan en el trimestre (el horizonte del ROE y del NIM de 12 meses)."""
    return _a_fin_de_trimestre(cdi_mensual().rolling(12, min_periods=12).mean())


def menos_cdi(tasa: pd.Series) -> pd.Series:
    """Tasa de 12 meses (índice AAAAMM, fracción) menos el CDI de esos mismos 12 meses: ROE − CDI."""
    return tasa - cdi_12m().reindex(tasa.index).to_numpy()


def refrescar(argv: list[str] | None = None) -> int:
    """Vuelve a bajar todas las series del catálogo (el paso SGS de actualizar.py)."""
    for nombre, codigo in CODIGOS.items():
        print(f"{nombre} ({codigo})", file=sys.stderr)
        bajar(codigo)
    return 0


if __name__ == "__main__":
    sys.exit(refrescar())
