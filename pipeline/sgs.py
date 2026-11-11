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
# Nombre, unidad y periodicidad oficiales de cada código: definiciones/bcb_sgs__catalogo.json
# (herramientas/validar_sgs.py). Un código nuevo sin entrada allí hace fallar tests/test_sgs_catalogo.py.
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
    "concesiones_libre": 20634, "concesiones_pj_libre": 20635, "concesiones_pf_libre": 20662,   # libres: 20634 = 20635 + 20662
    # actividad (índice): IBC-Br desestacionalizado, base del índice de concesiones reales (pag_credito y concesiones)
    "ibc_br": 24364,
    # mora > 90 días y atrasos 15-90 (en %)
    "mora90_total": 21082, "mora90_libre": 21085, "mora90_direccionado": 21132, "mora90_pf": 21084,
    "mora90_pj": 21083, "mora90_pf_livre": 21112, "mora90_pj_livre": 21086,
    "atraso15_90_pf": 21005, "atraso15_90_pj": 21004,
    "mora90_personal": 21114,             # personal NO consignado (nombre oficial; ver bcb_sgs__catalogo.json)
    "mora90_consignado_privado": 21116, "mora90_consignado_publico": 21117, "mora90_consignado_inss": 21118,
    "mora90_consignado_total": 21119, "mora90_vehiculos": 21121, "mora90_rotativo": 21127,
    "mora90_parcelado": 21128, "mora90_cartao_total": 21129,   # tarjeta = 21129 (total); 21127 y 21128 son detalle
    "mora90_inmobiliario_mercado": 21149, "mora90_inmobiliario_dirigido": 21150, "mora90_inmobiliario_total": 21151,
    "mora90_mpme": 27703, "mora90_grande": 27704,
    # tasas, precios, actividad, hogares
    "spread_livre": 20786, "icc": 25351, "tasa_creditos_nuevos": 20714, "cdi": 4389, "ipca": 433, "selic_meta": 432,
    "credito_pib": 20622, "pib_12m": 4382,
    # Crédito/PIB por segmento (Portada 01, validado con validar_sgs el 11-nov-2026).
    "credito_pib_pj": 20623, "credito_pib_pf": 20624, "credito_pib_livre": 20625, "credito_pib_direcionado": 20628,
    "endividamento": 29037, "comprometimento": 29034,
    "desocupacion": 24369,                # PNADC (IBGE t6381|v4099)
    # personas por producto (frente 12, hojas Tarjeta, Personal, Descuento por planilla y Vehículos; validado 10-nov).
    # Ojo: el «não consignado total» (20574, 20666, 20742, 21114) YA incluye la renegociación «vinculado à composição
    # de dívidas» (20575, 20667, 20743, 21115): 20580 = 20574 + 20579. No sumarlas.
    # 22024 (tarjeta total) incluye la tarjeta al contado a tasa 0 y no se reconstruye con 22022/22023 (A.4).
    "credito_pf_tarjeta_rotativo": 20587, "credito_pf_tarjeta_parcelado": 20588, "credito_pf_tarjeta_vista": 20589,
    "credito_pf_cheque_especial": 20573, "credito_pf_personal_renegociacion": 20575,
    "credito_pf_consignado_total": 20579,                 # = 20576 + 20577 + 20578
    "conc_pf_tarjeta_total": 20682, "conc_pf_tarjeta_rotativo": 20679, "conc_pf_tarjeta_parcelado": 20680,
    "conc_pf_tarjeta_vista": 20681, "conc_pf_cheque_especial": 20665, "conc_pf_personal": 20666,
    "conc_pf_personal_renegociacion": 20667, "conc_pf_consignado_privado": 20668,
    "conc_pf_consignado_publico": 20669, "conc_pf_consignado_inss": 20670, "conc_pf_consignado_total": 20671,
    "conc_pf_vehiculos": 20673,
    "tasa_pf_total": 20716, "tasa_pf_cheque_especial": 20741, "tasa_pf_personal": 20742,
    "tasa_pf_personal_renegociacion": 20743, "tasa_pf_consignado_privado": 20744,
    "tasa_pf_consignado_publico": 20745, "tasa_pf_consignado_inss": 20746, "tasa_pf_consignado_total": 20747,
    "tasa_pf_vehiculos": 20749, "tasa_pf_tarjeta_rotativo": 22022, "tasa_pf_tarjeta_parcelado": 22023,
    "tasa_pf_tarjeta_total": 22024,
    "mora90_cheque_especial": 21113, "mora90_personal_renegociacion": 21115,
    "salario_minimo": 1619,               # R$ (u.m.c.), para el ticket en meses de renta (P8)
    "selic_efectiva_mes": 4189,           # Selic acumulada en el mes, anualizada (base 252): la referencia de las hojas
    # inmobiliario PF (frente 16; validado 10-nov): 20610 + 20611 = 20612 y 20702 + 20703 = 20704. «Regulada» = SFH y
    # programas con tasa tope; ojo: 21150 se llama «mora90_inmobiliario_dirigido» pero es la de tasas reguladas.
    "credito_pf_inmobiliario_mercado": 20610, "credito_pf_inmobiliario_regulada": 20611,
    "conc_pf_inmobiliario_mercado": 20702, "conc_pf_inmobiliario_regulada": 20703, "conc_pf_inmobiliario_total": 20704,
    "tasa_pf_inmobiliario_mercado": 20772, "tasa_pf_inmobiliario_regulada": 20773, "tasa_pf_inmobiliario_total": 20774,
    # empresas (frente 13, hojas MPME y Grandes; validado 10-nov). 27706/27707 están desactivadas (terminan en dic-24).
    "tasa_pj_total": 20715, "tasa_pj_libre": 20718, "spread_pj": 20784, "icc_pj": 25352,
    "riesgo_eh_mpme": 27706, "riesgo_eh_grande": 27707,
    # sucesoras de 27705–27707 desde ene-25: % del saldo de mayor riesgo (Res. CMN 4.966); no empalman con E–H
    "riesgo_4966_pj": 29581, "riesgo_4966_mpme": 29582, "riesgo_4966_grande": 29583,
    # empresas por modalidad (frente 13, parte A; nombres validados contra el SGS el 10-nov). Libres: saldo,
    # concesiones del mes, tasa (% a.a.) y mora > 90 (%). Direccionados: rural, inmobiliario y BNDES (saldos arriba).
    "credito_pj_giro": 20550, "conc_pj_giro": 20642, "tasa_pj_giro": 20725, "mora90_pj_giro": 21093,
    "credito_pj_duplicatas": 20544, "conc_pj_duplicatas": 20636, "tasa_pj_duplicatas": 20719,
    "mora90_pj_duplicatas": 21087,        # «desconto de duplicatas e recebíveis»
    "credito_pj_antecipacao_cartao": 20546, "conc_pj_antecipacao_cartao": 20638,
    "tasa_pj_antecipacao_cartao": 20721, "mora90_pj_antecipacao_cartao": 21089,
    "credito_pj_conta_garantida": 20551, "conc_pj_conta_garantida": 20643, "tasa_pj_conta_garantida": 20726,
    "mora90_pj_conta_garantida": 21094,
    "credito_pj_cheque_especial": 20552, "conc_pj_cheque_especial": 20644, "tasa_pj_cheque_especial": 20727,
    "mora90_pj_cheque_especial": 21095,
    "credito_pj_tarjeta": 20564, "conc_pj_tarjeta": 20656, "tasa_pj_tarjeta": 22021, "mora90_pj_tarjeta": 21106,
    "credito_pj_acc": 20565, "conc_pj_acc": 20657, "tasa_pj_acc": 20736, "mora90_pj_acc": 21107,
    "credito_pj_export": 20567, "conc_pj_export": 20659, "tasa_pj_export": 20738, "mora90_pj_export": 21109,
    "credito_pj_import": 20566, "conc_pj_import": 20658, "tasa_pj_import": 20737, "mora90_pj_import": 21108,
    "credito_pj_repasse_externo": 20568, "conc_pj_repasse_externo": 20660, "tasa_pj_repasse_externo": 20739,
    "mora90_pj_repasse_externo": 21110,
    "credito_pj_bienes": 20555, "conc_pj_bienes": 20647, "tasa_pj_bienes": 20730, "mora90_pj_bienes": 21098,
    "credito_pj_otros_libres": 20569, "conc_pj_otros_libres": 20661, "mora90_pj_otros_libres": 21111,
    "credito_pj_direccionado": 20594, "conc_pj_direccionado": 20686, "tasa_pj_direccionado": 20757,
    "mora90_pj_direccionado": 21133,
    "credito_pj_bndes_inversion": 20602, "conc_pj_bndes_inversion": 20694, "tasa_pj_bndes_inversion": 20765,
    "mora90_pj_bndes_inversion": 21141,
    "conc_pj_bndes": 20696, "tasa_pj_bndes": 20767, "mora90_pj_bndes": 21143,
    "conc_pj_rural": 20689, "tasa_pj_rural": 20760, "mora90_pj_rural": 21136,
    "conc_pj_inmobiliario": 20692, "tasa_pj_inmobiliario": 20763, "mora90_pj_inmobiliario": 21139,
    "credito_pj_programas_mpme": 29966, "conc_pj_programas_mpme": 29969, "tasa_pj_programas_mpme": 29975,
    "mora90_pj_programas_mpme": 29993,    # Pronampe, PEAC y similares (serie nueva)
    # agregados monetarios, metodología nueva, saldo a fin de período en R$ mil (frente 14, hoja Fondeo; validado 10-nov)
    "mp_moneda": 27789, "mp_depositos_vista": 27790, "mp_m1": 27791, "mp_depositos_plazo": 27805,
    "mp_letras_financieras": 27806, "mp_letras_credito": 27807,           # 27807 = letras de crédito (LCI/LCA), no de cambio
    "mp_otros_titulos_privados": 27808, "mp_titulos_privados": 27809, "mp_m2": 27810,
    "mp_fondos_monetarios": 27811, "mp_compromisadas_privados": 27812, "mp_m3": 27813,
    "mp_titulos_federales": 27814, "mp_m4": 27815, "mp_ahorro": 1835,
    # inmobiliario (frente 16, decisión de Pablo del 11-nov): valor de las garantías (índice, mensual) y captación
    # líquida de poupança SBPE (R$ mil, DIARIA: se suma por mes, no se toma el último dato).
    "ivg_r": 21340, "captacion_sbpe_diaria": 240,
    # Portada mensual (frente 9, barrido del 11-nov en tareas/borradores/portada_sgs_barrido.md): los nueve segmentos
    # de tasa, ICC, spread, mora y atraso. El spread dirigido de personas no se publica.
    "tasa_libre": 20717, "tasa_pf_libre": 20740, "tasa_direccionado": 20756,
    "tasa_pf_direccionado": 20768, "spread_total": 20783, "spread_pf": 20785,
    "spread_pj_libre": 20787, "spread_pf_libre": 20809, "spread_direccionado": 20825,
    "spread_pj_direccionado": 20826, "atraso15_90_total": 21003, "atraso15_90_libre": 21006,
    "atraso15_90_pj_libre": 21007, "atraso15_90_pf_libre": 21033, "atraso15_90_direccionado": 21053,
    "atraso15_90_pj_direccionado": 21054, "atraso15_90_pf_direccionado": 21066, "mora90_pf_direccionado": 21145,
    "icc_pf": 25353, "icc_libre": 25354, "icc_pj_libre": 25355,
    "icc_pf_libre": 25356, "icc_direccionado": 25357, "icc_pj_direccionado": 25358,
    "icc_pf_direccionado": 25359,
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
