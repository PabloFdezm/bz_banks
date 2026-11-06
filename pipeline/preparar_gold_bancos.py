# -*- coding: utf-8 -*-
"""Capa gold base del dashboard de bancos: tablas bk_* que leen el sitio, y el puente IF.Data ↔ publicado.

POR QUÉ EXISTE
--------------
El sitio de bancos no calcula nada («Python calcula, el navegador dibuja»,
docs/dashboard_bancos/SPEC_DATOS_BANCOS_v0.1.md §1.3). Las fórmulas viven aquí, una sola vez, y el
sitio lee tablas ya listas. Este subcomando (``base``) no baja nada de la red: reordena lo que ya
existe en el repo —el panel de métricas por banco y trimestre, con TTM, ROE, ROA, cuotas y crédito
total (``datos/intermedio/metricas_bancos.parquet``); las dimensiones de los bancos
(``datos/gold/bank_instituciones.parquet`` y ``definiciones/bcb_ifdata__bancos_balances.json``); los
cotizados y tickers (``definiciones/bancos__dashboard.json``); las ópticas de grupo que ya usa
``cre_*`` (``datos/intermedio/cre_institucion.parquet``) y el cruce IF.Data ↔ publicado
(``definiciones/validacion_bancos.json``)— y lo entrega en seis tablas: ``bk_banco`` (34 bancos),
``bk_metrica`` (definición de cada métrica), ``bk_panel`` (banco × trimestre × métrica, con rezagos,
percentiles del grupo y rankings), ``bk_grupo`` (óptica × grupo × trimestre × métrica, con muestra
constante a/a), ``bk_puente`` y ``bk_manifiesto`` (filas, rangos, sha256 y último corte de cada
universo).

Reglas que no se tocan (SPEC §1.5 y cabeceras de ``preparar_metricas_bancos.py`` y
``preparar_credito_paginas_powerbi.py``): no se recalculan TTM, ROE, ROA, cuotas ni crédito total.
Los agregados de grupo son sumas o cocientes de sumas, nunca promedios de ratios. Lo que no tiene
definición segura queda en null y se lista en el resultado del encargo.

Salidas: ``datos/derivado/bcb_ifdata/bancos_gold/`` (con ``almacen.guardar_derivado``, que deja en el
manifiesto de qué entradas salió cada tabla y con qué comando) y una copia en ``datos/gold/``, donde
las leen el exportador y el sitio.

Uso:

    python -X utf8 preparar_gold_bancos.py base

El subcomando ``rentabilidad`` (encargo 64) añade ``bk_roe_arbol`` (árbol del ROE por banco y
por grupo) y ``bk_sensibilidad`` (beta del NIM contra el CDI); no reescribe las tablas de base.

    python -X utf8 preparar_gold_bancos.py rentabilidad
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import almacen as A
import preparar_metricas_bancos as PM

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_BANKS = RAIZ / "datos" / "gold"
ENTRADA_METRICAS = RAIZ / "datos" / "intermedio" / "metricas_bancos.parquet"
ENTRADA_INSTITUCIONES = CARPETA_BANKS / "bank_instituciones.parquet"
ENTRADA_CRE_INSTITUCION = RAIZ / "datos" / "intermedio" / "cre_institucion.parquet"
ENTRADA_BALANCES = RAIZ / "definiciones" / "bcb_ifdata__bancos_balances.json"
ENTRADA_DASHBOARD = RAIZ / "definiciones" / "bancos__dashboard.json"
ENTRADA_VALIDACION = RAIZ / "definiciones" / "validacion_bancos.json"
ENTRADA_SISTEMA_M = CARPETA_BANKS / "bk_sistema_m.parquet"
ENTRADA_CONTEXTO = RAIZ / "datos" / "intermedio" / "cre_contexto.parquet"
ENTRADA_CARTERA = CARPETA_BANKS / "bk_cartera.parquet"

FUENTE_DERIVADA = "bcb_ifdata"
DATASET_DERIVADO = "bancos_gold"
COMANDO = "python -X utf8 preparar_gold_bancos.py base"
N_BANCOS = 34
MIN_GRUPO_PERCENTIL = 3

PROPIEDAD = {"1": "Público", "2": "Privado nacional", "3": "Privado extranjero"}
MODELOS_FINTECH = ("Digitales", "Pagos")

# --- Metadatos de las métricas ------------------------------------------------
NOMBRES = {
    "antes_tributacao_q": "Resultado antes de tributación (trimestre)",
    "antes_tributacao_ttm": "Resultado antes de tributación (12 meses)",
    "aplic_interfinanceiras": "Aplicaciones interfinancieras",
    "apalancamiento": "Apalancamiento (activo / patrimonio)",
    "arrendamento": "Arrendamiento financiero",
    "ativo_aa": "Crecimiento a/a del activo",
    "ativo_medio_ttm": "Activo medio (12 meses)",
    "ativo_permanente": "Activo permanente",
    "ativo_total": "Activo total",
    "cobertura_ecl": "Cobertura de pérdida esperada",
    "costo_riesgo_ttm": "Costo del riesgo (12 meses)",
    "credito_aa": "Crecimiento a/a de la cartera",
    "credito_bruto": "Cartera bruta",
    "credito_depositos": "Crédito / depósitos",
    "credito_liquido": "Cartera neta de provisiones",
    "credito_total": "Crédito total",
    "depositos": "Depósitos",
    "depositos_aa": "Crecimiento a/a de depósitos",
    "depositos_interfinanceiros": "Depósitos interfinancieros",
    "derivativos_ativo": "Derivativos (activo)",
    "derivativos_passivo": "Derivativos (pasivo)",
    "despesas_administrativas_q": "Gastos administrativos (trimestre)",
    "despesas_administrativas_ttm": "Gastos administrativos (12 meses)",
    "despesas_pessoal_q": "Gastos de personal (trimestre)",
    "despesas_pessoal_ttm": "Gastos de personal (12 meses)",
    "despesas_tributarias_q": "Gastos tributarios (trimestre)",
    "disponibilidades": "Disponibilidades",
    "ecl_saldo": "Saldo de pérdida esperada",
    "eficiencia_ttm": "Eficiencia (gasto / ingreso, 12 meses)",
    "gasto_total_ttm": "Gasto de personal y administrativo (12 meses)",
    "ingreso_total_ttm": "Ingreso operacional (12 meses)",
    "credito_real_aa": "Crecimiento real de la cartera a/a",
    "emprestimos_repasses": "Préstamos y repasses",
    "hhi_ativo": "Concentración HHI del activo",
    "hhi_credito": "Concentración HHI del crédito",
    "hhi_depositos": "Concentración HHI de depósitos",
    "instrumentos_elegiveis": "Instrumentos elegibles",
    "lucro_liquido_q": "Lucro líquido (trimestre)",
    "lucro_liquido_ttm": "Lucro líquido (12 meses)",
    "lucro_ttm_aa": "Crecimiento a/a del lucro (12 meses)",
    "margem_intermediacao_ttm": "Margen de intermediación (12 meses / activo medio)",
    "oblig_compromissadas": "Obligaciones en operaciones compromissadas",
    "outras_concessao": "Otros créditos",
    "outras_obrigacoes": "Otras obligaciones",
    "outras_receitas_despesas_q": "Otros ingresos y gastos (trimestre)",
    "outros_ativos": "Otros activos",
    "outros_instrumentos_divida": "Otros instrumentos de deuda",
    "pagos_receber": "Pagos a recibir",
    "passivo_exigivel": "Pasivo exigible",
    "patrimonio_liquido": "Patrimonio líquido",
    "pl_medio_ttm": "Patrimonio líquido medio (12 meses)",
    "provisoes_credito_q": "Provisiones de crédito (trimestre)",
    "provisoes_credito_ttm": "Provisiones de crédito (12 meses)",
    "rendas_servicos_q": "Ingresos por servicios (trimestre)",
    "rendas_servicos_ttm": "Ingresos por servicios (12 meses)",
    "rendas_tarifas_q": "Ingresos por tarifas (trimestre)",
    "rendas_tarifas_ttm": "Ingresos por tarifas (12 meses)",
    "resultado_intermediacao_financeira_q": "Resultado de intermediación financiera (trimestre)",
    "resultado_intermediacao_financeira_ttm": "Resultado de intermediación financiera (12 meses)",
    "resultado_nao_operacional_q": "Resultado no operacional (trimestre)",
    "resultado_transacoes_pagamento_q": "Resultado de transacciones de pago (trimestre)",
    "resultado_transacoes_pagamento_ttm": "Resultado de transacciones de pago (12 meses)",
    "roa_ttm": "ROA (12 meses)",
    "roe_ttm": "ROE (12 meses)",
    "share_ativo": "Cuota de activo",
    "share_credito": "Cuota de crédito",
    "share_depositos": "Cuota de depósitos",
    "npl15_total": "NPL ≥ 15 días (cartera total)",
    "pf_share": "Peso de personas en la cartera",
    "tarifas_ativo_ttm": "Tarifas y servicios / activo medio (12 meses)",
    "cartera_saldo": "Cartera activa en Brasil (informes 11 y 13)",
    "cartera_vencido15": "Cartera vencida ≥ 15 días",
    "cartera_saldo_pf": "Cartera activa de personas",
    "fondeo_depositos": "Fondeo: depósitos",
    "fondeo_depositos_interfinanceiros": "Fondeo: depósitos interfinancieros",
    "fondeo_oblig_compromissadas": "Fondeo: operaciones compromisadas",
    "fondeo_outros_instrumentos_divida": "Fondeo: otros instrumentos de deuda",
    "fondeo_emprestimos_repasses": "Fondeo: préstamos y repases",
    "fondeo_outras_obrigacoes": "Fondeo: otras obligaciones",
    "fondeo_patrimonio_liquido": "Fondeo: patrimonio",
    "top5_credito": "Cuota de las 5 mayores (crédito)",
    "top5_depositos": "Cuota de las 5 mayores (depósitos)",
    "tvm": "Títulos y valores mobiliarios",
    "tvm_mas_derivativos": "Títulos y valores mobiliarios más derivativos",
}

FAMILIA_ORDEN = ["tamaño", "crédito", "calidad", "fondeo", "rentabilidad", "capital", "conducta"]
FAMILIA_CAPITAL = {"patrimonio_liquido", "pl_medio_ttm", "apalancamiento"}
FAMILIA_CREDITO = {"credito_total", "credito_bruto", "credito_liquido", "credito_aa",
                   "arrendamento", "outras_concessao", "pagos_receber", "pf_share", "cartera_saldo",
                   "cartera_saldo_pf", "credito_real_aa"}
FAMILIA_CALIDAD = {"npl15_total", "cartera_vencido15", "costo_riesgo_ttm", "cobertura_ecl", "provisoes_credito_q",
                   "provisoes_credito_ttm", "ecl_saldo"}
FAMILIA_FONDEO = {"depositos", "depositos_aa", "depositos_interfinanceiros", "oblig_compromissadas",
                  "outros_instrumentos_divida", "emprestimos_repasses", "derivativos_passivo",
                  "outras_obrigacoes", "passivo_exigivel", "instrumentos_elegiveis", "credito_depositos",
                  *["fondeo_" + c for c in ['depositos', 'depositos_interfinanceiros', 'oblig_compromissadas', 'outros_instrumentos_divida', 'emprestimos_repasses', 'outras_obrigacoes', 'patrimonio_liquido']], }
PREFIJOS_RENTABILIDAD = ("roe_", "roa_", "margem_", "eficiencia_", "lucro_", "resultado_", "rendas_",
                         "despesas_", "antes_tributacao_", "outras_receitas_despesas_",
                         "gasto_total_", "ingreso_total_")

# Unidad: ratio (pp en la variación), brl (variación en fracción), indice (diferencia absoluta).
UNIDAD_RATIO = {"roe_ttm", "roa_ttm", "margem_intermediacao_ttm", "costo_riesgo_ttm", "cobertura_ecl",
                "eficiencia_ttm", "credito_aa", "depositos_aa", "ativo_aa", "lucro_ttm_aa",
                "credito_depositos", "npl15_total", "pf_share", "tarifas_ativo_ttm", "credito_real_aa",
                *["fondeo_" + c for c in ['depositos', 'depositos_interfinanceiros', 'oblig_compromissadas', 'outros_instrumentos_divida', 'emprestimos_repasses', 'outras_obrigacoes', 'patrimonio_liquido']], }
UNIDAD_INDICE = {"apalancamiento", "hhi_credito", "hhi_depositos", "hhi_ativo"}

# Signo (ESQUELETO §0.8). Lo que no está literal se marca como deducido o sin definir.
SIGNO_ESQUELETO = {m: "mejora_sube" for m in ["roe_ttm", "roa_ttm", "margem_intermediacao_ttm",
                                              "cobertura_ecl", "share_ativo", "share_depositos",
                                              "share_credito"]}
SIGNO_ESQUELETO.update({"costo_riesgo_ttm": "mejora_baja", "eficiencia_ttm": "mejora_baja",
                        "credito_aa": "neutro", "npl15_total": "mejora_baja"})
SIGNO_DEDUCIDO = {m: "mejora_sube" for m in [
    "lucro_liquido_q", "lucro_liquido_ttm", "lucro_ttm_aa", "antes_tributacao_q",
    "antes_tributacao_ttm", "resultado_intermediacao_financeira_q",
    "resultado_intermediacao_financeira_ttm", "resultado_transacoes_pagamento_q",
    "resultado_transacoes_pagamento_ttm", "rendas_tarifas_q", "rendas_tarifas_ttm",
    "rendas_servicos_q", "rendas_servicos_ttm", "patrimonio_liquido", "pl_medio_ttm"]}
SIGNO_DEDUCIDO.update({m: "mejora_baja" for m in [
    "provisoes_credito_q", "provisoes_credito_ttm", "despesas_pessoal_q", "despesas_pessoal_ttm",
    "despesas_administrativas_q", "despesas_administrativas_ttm", "despesas_tributarias_q"]})
SIGNO_SIN_DEFINIR = {"apalancamiento", "credito_depositos"}

EN_FICHA = {"credito_aa", "costo_riesgo_ttm", "cobertura_ecl", "margem_intermediacao_ttm",
            "eficiencia_ttm", "roa_ttm", "roe_ttm", "apalancamiento", "credito_depositos",
            "npl15_total", "pf_share", "tarifas_ativo_ttm"}
RANKEABLE = {"ativo_total", "credito_total", "depositos", "patrimonio_liquido"}
CRECIMIENTO_BASE = {"credito_aa": "credito_total", "depositos_aa": "depositos",
                    "ativo_aa": "ativo_total", "lucro_ttm_aa": "lucro_liquido_ttm"}
METRICAS_SOLO_GRUPO = ["hhi_credito", "hhi_depositos", "hhi_ativo", "top5_credito", "top5_depositos"]

DEFINICION_EXPLICITA = {
    "credito_total": "Saldo al cierre: credito_liquido + arrendamento + outras_concessao + pagos_receber "
                     "(era 2025); credito_liquido + arrendamento + outras_concessao (era vieja).",
    "ativo_medio_ttm": "(ativo_total de t + ativo_total de t−4) / 2; vacío si falta t−4.",
    "pl_medio_ttm": "(patrimonio_liquido de t + patrimonio_liquido de t−4) / 2; vacío si falta t−4.",
    "roe_ttm": "lucro_liquido_ttm / pl_medio_ttm.",
    "roa_ttm": "lucro_liquido_ttm / ativo_medio_ttm.",
    "margem_intermediacao_ttm": "(resultado_intermediacao_financeira_ttm + resultado_transacoes_pagamento_ttm) / ativo_medio_ttm.",
    "costo_riesgo_ttm": "−provisoes_credito_ttm / credito_total, si credito_total > 0.",
    "cobertura_ecl": "−ecl_saldo / credito_bruto, si credito_bruto > 0.",
    "eficiencia_ttm": "−(despesas_pessoal_ttm + despesas_administrativas_ttm) / (rendas_tarifas_ttm + "
                      "rendas_servicos_ttm + resultado_intermediacao_financeira_ttm + "
                      "resultado_transacoes_pagamento_ttm), si el denominador > 0.",
    "credito_aa": "credito_total de t / credito_total de t−4 − 1.",
    "depositos_aa": "depositos de t / depositos de t−4 − 1.",
    "ativo_aa": "ativo_total de t / ativo_total de t−4 − 1.",
    "lucro_ttm_aa": "lucro_liquido_ttm de t / lucro_liquido_ttm de t−4 − 1.",
    "share_ativo": "ativo_total del banco / suma de ativo_total del panel con dato en el trimestre (solo valores > 0).",
    "share_depositos": "depositos del banco / suma de depositos del panel con dato en el trimestre (solo valores > 0).",
    "share_credito": "credito_total del banco / suma de credito_total del panel con dato en el trimestre (solo valores > 0).",
    "credito_depositos": "credito_total / depositos, si depositos > 0 (SPEC §4.2).",
    "apalancamiento": "ativo_medio_ttm / pl_medio_ttm, si pl_medio_ttm > 0 (SPEC §4.2).",
    "npl15_total": "cartera_vencido15 / cartera_saldo (informes 11 y 13, Σ de las 16 modalidades; bk_cartera).",
    "pf_share": "cartera_saldo_pf / cartera_saldo (bk_cartera).",
    "cartera_saldo": "Σ saldo de las 16 modalidades de los informes 11 y 13 (cartera activa en Brasil; bk_cartera).",
    "cartera_vencido15": "Σ vencido ≥ 15 días de las 16 modalidades (bk_cartera).",
    "cartera_saldo_pf": "Σ saldo de las 7 modalidades de personas (bk_cartera).",
    "tarifas_ativo_ttm": "(rendas_tarifas_ttm + rendas_servicos_ttm) / ativo_medio_ttm.",
    "credito_real_aa": "(1 + credito_aa) / (1 + ipca_12m) − 1, con ipca_12m el IPCA acumulado 12 meses del "
                       "último mes del trimestre (bk_sistema_q, fracción). Vacía mientras no exista la serie ipca_12m.",
    "gasto_total_ttm": "−(despesas_pessoal_ttm + despesas_administrativas_ttm): numerador de eficiencia_ttm, en BRL "
                       "positivo (gasto operativo de 4 trimestres).",
    "ingreso_total_ttm": "rendas_tarifas_ttm + rendas_servicos_ttm + resultado_intermediacao_financeira_ttm + "
                         "resultado_transacoes_pagamento_ttm: denominador de eficiencia_ttm, en BRL.",
    **{"fondeo_" + c: f"{c} / Σ (" + ", ".join(['depositos', 'depositos_interfinanceiros', 'oblig_compromissadas', 'outros_instrumentos_divida', 'emprestimos_repasses', 'outras_obrigacoes', 'patrimonio_liquido']) + ")" for c in ['depositos', 'depositos_interfinanceiros', 'oblig_compromissadas', 'outros_instrumentos_divida', 'emprestimos_repasses', 'outras_obrigacoes', 'patrimonio_liquido']},
    "hhi_credito": "Σ (share_credito × 100)² sobre los bancos del panel con dato en el trimestre.",
    "hhi_depositos": "Σ (share_depositos × 100)² sobre los bancos del panel con dato en el trimestre.",
    "hhi_ativo": "Σ (share_ativo × 100)² sobre los bancos del panel con dato en el trimestre.",
    "top5_credito": "Suma de las 5 mayores share_credito del panel en el trimestre.",
    "top5_depositos": "Suma de las 5 mayores share_depositos del panel en el trimestre.",
}
FUENTE_DIRECTA = "BCB IF.Data (prudencial)"
FUENTE_DERIVADA_TXT = "Derivado de BCB IF.Data (prudencial), preparar_metricas_bancos.py"

# --- Agregados de grupo: numerador y denominador (como en preparar_metricas_bancos.py) ---
def _suma(d, nombres, suf=""):
    return d[[n + suf for n in nombres]].sum(axis=1, min_count=1)


RATIO_SPECS = {
    "roe_ttm": (lambda d, s: d["lucro_liquido_ttm" + s], lambda d, s: d["pl_medio_ttm" + s]),
    "roa_ttm": (lambda d, s: d["lucro_liquido_ttm" + s], lambda d, s: d["ativo_medio_ttm" + s]),
    "margem_intermediacao_ttm": (
        lambda d, s: _suma(d, ["resultado_intermediacao_financeira_ttm", "resultado_transacoes_pagamento_ttm"], s),
        lambda d, s: d["ativo_medio_ttm" + s]),
    "costo_riesgo_ttm": (lambda d, s: -d["provisoes_credito_ttm" + s], lambda d, s: d["credito_total" + s]),
    "cobertura_ecl": (lambda d, s: -d["ecl_saldo" + s], lambda d, s: d["credito_bruto" + s]),
    "eficiencia_ttm": (
        lambda d, s: -_suma(d, ["despesas_pessoal_ttm", "despesas_administrativas_ttm"], s),
        lambda d, s: _suma(d, ["rendas_tarifas_ttm", "rendas_servicos_ttm",
                               "resultado_intermediacao_financeira_ttm",
                               "resultado_transacoes_pagamento_ttm"], s)),
    "credito_depositos": (lambda d, s: d["credito_total" + s], lambda d, s: d["depositos" + s]),
    "apalancamiento": (lambda d, s: d["ativo_medio_ttm" + s], lambda d, s: d["pl_medio_ttm" + s]),
    "npl15_total": (lambda d, s: d["cartera_vencido15" + s], lambda d, s: d["cartera_saldo" + s]),
    "pf_share": (lambda d, s: d["cartera_saldo_pf" + s], lambda d, s: d["cartera_saldo" + s]),
    "tarifas_ativo_ttm": (lambda d, s: _suma(d, ["rendas_tarifas_ttm", "rendas_servicos_ttm"], s),
                          lambda d, s: d["ativo_medio_ttm" + s]),
    **{"fondeo_" + c: ((lambda c: lambda d, s: d[c + s])(c),
                       lambda d, s: _suma(d, ['depositos', 'depositos_interfinanceiros', 'oblig_compromissadas', 'outros_instrumentos_divida', 'emprestimos_repasses', 'outras_obrigacoes', 'patrimonio_liquido'], s)) for c in ['depositos', 'depositos_interfinanceiros', 'oblig_compromissadas', 'outros_instrumentos_divida', 'emprestimos_repasses', 'outras_obrigacoes', 'patrimonio_liquido']},
}


# --- Utilidades de periodo ----------------------------------------------------
def _qi(periodo: str) -> int:
    """Índice trimestral consecutivo de un periodo AAAAMM."""
    return int(periodo[:4]) * 4 + int(periodo[4:]) // 3 - 1


def _periodo_de_qi(qi: int) -> str:
    return f"{qi // 4}{(qi % 4 + 1) * 3:02d}"


def _trimestre(periodo: str) -> str:
    return f"{int(periodo[4:]) // 3}T{periodo[2:4]}"


def _fecha(periodos: pd.Series) -> pd.Series:
    return (pd.to_datetime(periodos, format="%Y%m") + pd.offsets.MonthEnd(0)).dt.date


def _div(a: pd.Series, b: pd.Series) -> pd.Series:
    return a / b.where(b != 0)


def _unidad_aa(unidad: str | None) -> str | None:
    return {"ratio": "pp", "brl": "fraccion", "indice": "abs"}.get(unidad)


# --- Variaciones trimestrales, IPCA y crédito real (encargo 78a) --------------------------
# POR QUÉ: valor_tt y credito_real_aa necesitan trimestre anterior, quiebre 2025 y el IPCA de
# bk_sistema_q. Se escriben aquí, una sola vez, igual que valor_aa.
PERIODO_2024T4 = "202412"          # regla 6 del spec: 2024-T4 vacío; ninguna variación que lo toque
ENTRADA_SISTEMA_Q = CARPETA_BANKS / "bk_sistema_q.parquet"
SERIE_IPCA_12M = "ipca_12m"        # la agrega el encargo 78c: fracción, valor del último mes del trimestre


def _periodo_previo(periodo: str, k: int = 1) -> str:
    return _periodo_de_qi(_qi(periodo) - k)


def _periodo_previo_serie(periodos: pd.Series, k: int = 1) -> pd.Series:
    mapa = {p: _periodo_previo(p, k) for p in periodos.unique()}
    return periodos.map(mapa)


def _mascara_endpoints(periodo: pd.Series, k: int) -> pd.Series:
    """True si la variación de k trimestres no toca 2024-T4 ni como punto final ni como punto de partida."""
    previo = _periodo_previo_serie(periodo, k)
    return ~(periodo.eq(PERIODO_2024T4) | previo.eq(PERIODO_2024T4))


def _mascara_tt(periodo: pd.Series, cod_inst: pd.Series, quiebre: set[str]) -> pd.Series:
    """True donde valor_tt es válido: sin 2024-T4 y sin los bancos con quiebre 2025 en 2025-T1.

    POR QUÉ el quiebre solo en 2025-T1: el spec excluye de las variaciones que cruzan 2025-T1 a los bancos
    con cambio de cobertura (quiebre_2025 = true en bk_cartera).
    """
    ok = _mascara_endpoints(periodo, 1)
    ok = ok & ~(periodo.eq(PERIODO_QUIEBRE_2025) & cod_inst.isin(quiebre))
    return ok.astype(bool)


def _real_desde_nominal(nominal, ipca):
    """Crecimiento real: (1 + nominal) / (1 + IPCA 12 meses) − 1, ambos en fracción."""
    return (1 + nominal) / (1 + ipca) - 1


def _ipca_12m_trimestral() -> pd.Series:
    """IPCA acumulado 12 meses por periodo AAAAMM (mes final del trimestre), fracción, desde bk_sistema_q.

    POR QUÉ vacía si falta la serie: ipca_12m la agrega el encargo 78c. Mientras no exista, credito_real_aa
    queda nulo; no se aproxima con el año calendario ni con otra serie.
    """
    if not ENTRADA_SISTEMA_Q.exists():
        print("[aviso] bk_sistema_q.parquet no existe: credito_real_aa queda vacía")
        return pd.Series(dtype=float)
    s = pd.read_parquet(ENTRADA_SISTEMA_Q, columns=["fecha", "serie_id", "valor"])
    s = s[s["serie_id"].eq(SERIE_IPCA_12M)]
    if s.empty:
        print("[aviso] bk_sistema_q sin serie ipca_12m: credito_real_aa queda vacía (falta encargo 78c)")
        return pd.Series(dtype=float)
    fecha = pd.to_datetime(s["fecha"])
    s = s[fecha.dt.month.isin([3, 6, 9, 12]).to_numpy()]
    periodo = pd.to_datetime(s["fecha"]).dt.strftime("%Y%m").to_numpy()
    return pd.Series(s["valor"].to_numpy(float), index=periodo).groupby(level=0).last().sort_index()


# --- bk_banco -----------------------------------------------------------------
def _bk_banco() -> pd.DataFrame:
    inst = pd.read_parquet(ENTRADA_INSTITUCIONES)
    inst["cod_inst"] = inst["cod_inst"].astype(str)
    bal = pd.DataFrame(json.loads(ENTRADA_BALANCES.read_text(encoding="utf-8"))["bancos"])
    bal = bal[["cod_inst", "modelo_negocio", "nota"]].rename(columns={"modelo_negocio": "modelo"})
    dash = pd.DataFrame(json.loads(ENTRADA_DASHBOARD.read_text(encoding="utf-8"))["bancos"])
    if "nota" not in dash:
        dash["nota"] = None
    dash = dash[["cod_inst", "slug", "cotizado", "ticker", "ticker_estado", "ficha", "color", "nota"]]
    dash = dash.rename(columns={"nota": "nota_dashboard"})
    t = (inst[["cod_inst", "nombre_corto", "institucion_bcb_ultima", "sr", "tc",
               "primer_periodo", "ultimo_periodo"]]
         .merge(bal, on="cod_inst", how="left", validate="1:1")
         .merge(dash, on="cod_inst", how="left", validate="1:1"))
    if len(t) != N_BANCOS:
        raise ValueError(f"bk_banco: se esperaban {N_BANCOS} bancos y hay {len(t)}")
    if t["modelo"].isna().any() or t["slug"].isna().any():
        raise ValueError("bk_banco: falta modelo_negocio o slug para algún banco")
    sr = t["sr"].fillna("").astype(str).str.strip()
    t["segmento_reg"] = sr.mask(sr == "", "Sin segmento")
    t["propiedad"] = t["tc"].astype(str).str.strip().map(PROPIEDAD)
    if t["propiedad"].isna().any():
        raise ValueError("bk_banco: tc fuera de 1, 2, 3")
    t["fintech"] = np.where(t["modelo"].isin(MODELOS_FINTECH), "Fintech", "Tradicional")
    t["segmento_ref"] = np.select(
        [t["propiedad"].eq("Público"), t["modelo"].isin(MODELOS_FINTECH), t["segmento_reg"].eq("S1")],
        ["Públicos", "Digitales", "S1 privados"], default="Demás")
    # La nota del dashboard (lectura para el usuario) se suma a la de balances (identidad del conglomerado).
    t["nota"] = [" ".join(x for x in (a, b) if isinstance(x, str) and x) or None
                 for a, b in zip(t["nota"], t["nota_dashboard"])]
    t = t.rename(columns={"institucion_bcb_ultima": "institucion_bcb"})
    cols = ["cod_inst", "slug", "nombre_corto", "institucion_bcb", "modelo", "segmento_reg",
            "propiedad", "fintech", "segmento_ref", "cotizado", "ticker", "ticker_estado",
            "ficha", "color", "nota", "primer_periodo", "ultimo_periodo"]
    return t[cols].sort_values("nombre_corto").reset_index(drop=True)


# --- Panel ancho (banco × trimestre × métrica) --------------------------------
def _cargar_ancho(cods: list[str]) -> tuple[pd.DataFrame, pd.MultiIndex]:
    m = pd.read_parquet(ENTRADA_METRICAS)
    m["cod_inst"] = m["cod_inst"].astype(str)
    m["periodo"] = m["periodo"].astype(str)
    if set(m["cod_inst"]) != set(cods):
        raise ValueError("metricas_bancos.parquet tiene bancos distintos de bk_banco")
    if m.duplicated(["cod_inst", "periodo", "metrica"]).any():
        raise ValueError("metricas_bancos.parquet tiene filas duplicadas")
    periodos = sorted(m["periodo"].unique())
    qis = [_qi(p) for p in periodos]
    if qis != list(range(qis[0], qis[0] + len(qis))):
        raise ValueError("los trimestres de metricas_bancos no son contiguos")
    grilla = pd.MultiIndex.from_product([sorted(cods), periodos], names=["cod_inst", "periodo"])
    w = (m.set_index(["cod_inst", "periodo", "metrica"])["valor"]
         .unstack("metrica").reindex(grilla))
    w.columns.name = "metrica"
    # Métricas de SPEC §4.2 que sí se pueden calcular hoy (las de cartera y capital son de la ola 2).
    w["credito_depositos"] = w["credito_total"] / w["depositos"].where(w["depositos"] > 0)
    w["apalancamiento"] = w["ativo_medio_ttm"] / w["pl_medio_ttm"].where(w["pl_medio_ttm"] > 0)
    # Tarifas sobre activo y mix de fondeo (decisión del arquitecto, revisión de la Ficha 2026-11-03).
    w["tarifas_ativo_ttm"] = (w[["rendas_tarifas_ttm", "rendas_servicos_ttm"]].sum(axis=1, min_count=1)
                              / w["ativo_medio_ttm"].where(w["ativo_medio_ttm"] > 0))
    fon = ['depositos', 'depositos_interfinanceiros', 'oblig_compromissadas', 'outros_instrumentos_divida', 'emprestimos_repasses', 'outras_obrigacoes', 'patrimonio_liquido']
    tot_fon = w[fon].sum(axis=1, min_count=1)
    for c in fon:
        w["fondeo_" + c] = w[c] / tot_fon.where(tot_fon > 0)
    # Cartera por modalidad (bk_cartera, informes 11 y 13): NPL total y peso de personas. Si la tabla
    # todavía no existe, las columnas quedan vacías y se avisa.
    ruta_c = CARPETA_BANKS / "bk_cartera.parquet"
    if ruta_c.exists():
        c = pd.read_parquet(ruta_c)
        agg = c.groupby(["cod_inst", "periodo"]).agg(cartera_saldo=("saldo", "sum"),
                                                      cartera_vencido15=("vencido15", "sum"))
        agg["cartera_saldo_pf"] = c[c["tipo"] == "PF"].groupby(["cod_inst", "periodo"])["saldo"].sum()
        agg = agg.reindex(grilla)
        for col in agg.columns:
            w[col] = agg[col]
        w["npl15_total"] = w["cartera_vencido15"] / w["cartera_saldo"].where(w["cartera_saldo"] > 0)
        w["pf_share"] = w["cartera_saldo_pf"].fillna(0).where(w["cartera_saldo"] > 0) / w["cartera_saldo"]
    else:
        print("[aviso] bk_cartera.parquet no existe: npl15_total y pf_share quedan vacías (correr «cartera» antes)")
    # Encargo 78a §3: numerador y denominador de eficiencia_ttm, con las mismas sumas que RATIO_SPECS
    # (un término nulo no tumba la suma). El gasto va en positivo: las despesas vienen en negativo.
    w["gasto_total_ttm"] = -_suma(w, ["despesas_pessoal_ttm", "despesas_administrativas_ttm"])
    w["ingreso_total_ttm"] = _suma(w, ["rendas_tarifas_ttm", "rendas_servicos_ttm",
                                       "resultado_intermediacao_financeira_ttm",
                                       "resultado_transacoes_pagamento_ttm"])
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


# --- Familia, signo, definición -----------------------------------------------
def _familia(m: str) -> str:
    if m in FAMILIA_CAPITAL:
        return "capital"
    if m in FAMILIA_CREDITO:
        return "crédito"
    if m in FAMILIA_CALIDAD:
        return "calidad"
    if m in FAMILIA_FONDEO:
        return "fondeo"
    if m.startswith(PREFIJOS_RENTABILIDAD):
        return "rentabilidad"
    return "tamaño"


def _signo(m: str) -> tuple[str | None, str]:
    if m in SIGNO_ESQUELETO:
        return SIGNO_ESQUELETO[m], "esqueleto_0.8"
    if m in SIGNO_DEDUCIDO:
        # Corrección 58b: provisiones y gastos vienen en negativo en los datos, así que una
        # dirección deducida pintaría al revés. El signo solo aplica a los ratios de §0.8.
        return "neutro", "arquitecto_montos"
    if m in SIGNO_SIN_DEFINIR:
        # neutro = sin juicio de color en el sitio; el origen queda en signo_fuente.
        return "neutro", "arquitecto"
    return "neutro", "neutro_por_defecto"


def _definicion(m: str) -> str:
    if m in DEFINICION_EXPLICITA:
        return DEFINICION_EXPLICITA[m]
    if m in PM.CODIGOS_2025 or m in PM.CODIGOS_PRE2025:
        c25, cpre = PM.CODIGOS_2025.get(m), PM.CODIGOS_PRE2025.get(m)
        partes = [f"COSIF {c25} (desde 2025)" if c25 else "sin código COSIF desde 2025",
                  f"COSIF {cpre} (hasta 2024)" if cpre else "sin código COSIF hasta 2024"]
        extra = " Antes de 2025 no es del todo comparable (incluye partidas extra)." if m == "outras_concessao" else ""
        return "Saldo al cierre, conglomerado prudencial: " + "; ".join(partes) + "." + extra
    if m in PM.FLUJOS.keys():
        return f"Flujo del trimestre, des-acumulado de bank_resultados (campo «{PM.FLUJOS[m]}»)."
    if m.endswith("_ttm") and f"{m[:-4]}_q" in PM.FLUJOS.keys():
        return f"Suma de los 4 trimestres consecutivos que terminan en t de {m[:-4]}_q; vacío si falta uno."
    raise KeyError(f"sin definición para la métrica {m}")


def _es_directa(m: str) -> bool:
    return (m in PM.CODIGOS_2025 or m in PM.CODIGOS_PRE2025 or m in PM.FLUJOS.keys()) and m not in DEFINICION_EXPLICITA


def _bk_metrica(metricas: list[str]) -> pd.DataFrame:
    filas = []
    for m in metricas:
        if m in UNIDAD_INDICE:
            unidad = "indice"
        elif m in UNIDAD_RATIO or m.startswith(("share_", "top5_")):
            unidad = "ratio"
        else:
            unidad = "brl"
        if m == "apalancamiento":
            formato = "x1"
        elif unidad == "ratio":
            formato = "pct1"
        elif unidad == "brl":
            formato = "brl_mm"
        else:
            formato = None
        signo, signo_fuente = _signo(m)
        filas.append({
            "metrica": m,
            "nombre": NOMBRES[m],
            "nombre_corto": NOMBRES[m],
            "familia": _familia(m),
            "unidad": unidad,
            "formato": formato,
            "signo": signo,
            "signo_fuente": signo_fuente,
            "universo": "panel",
            "fuente": FUENTE_DIRECTA if _es_directa(m) else FUENTE_DERIVADA_TXT,
            "definicion": _definicion(m),
            "en_comparador": pd.NA,
            "en_ficha": m in EN_FICHA,
        })
    df = pd.DataFrame(filas)
    df["_f"] = df["familia"].map({f: i for i, f in enumerate(FAMILIA_ORDEN)})
    df = df.sort_values(["_f", "metrica"]).drop(columns="_f").reset_index(drop=True)
    df.insert(len(df.columns), "orden", np.arange(1, len(df) + 1))
    df["en_comparador"] = df["en_comparador"].astype("boolean")
    df["en_ficha"] = df["en_ficha"].astype(bool)
    return df


# --- bk_panel -----------------------------------------------------------------
def _bk_panel(w: pd.DataFrame, banco: pd.DataFrame, meta: pd.DataFrame, grilla: pd.MultiIndex) -> pd.DataFrame:
    # explícito: pandas 2 descartaba los NaN en stack() y pandas 3 no (spec/08, pendiente 3b)
    L = w.stack(future_stack=True).dropna().rename("valor").reset_index()
    L["modelo"] = L["cod_inst"].map(dict(zip(banco["cod_inst"], banco["modelo"])))
    L["unidad"] = L["metrica"].map(meta["unidad"])
    L["fecha"] = _fecha(L["periodo"])
    L["trimestre"] = L["periodo"].map(_trimestre)

    s = _serie(L, "valor")
    L["valor_t1"] = _tomar(_rezago(s, 1, grilla), L)
    L["valor_t4"] = _tomar(_rezago(s, 4, grilla), L)
    L["d_tt"], L["unidad_d"] = _variacion(L["valor"], L["valor_t1"], L["unidad"])
    L["d_aa"], _ = _variacion(L["valor"], L["valor_t4"], L["unidad"])
    # Encargo 78a §1: valor_tt es la misma variación que d_tt, pero vacía si cruza 2024-T4 o si el banco
    # tiene quiebre 2025 en 2025-T1. d_tt se deja como estaba (lo leen las páginas).
    L["valor_tt"] = L["d_tt"].where(_mascara_tt(L["periodo"], L["cod_inst"], _bancos_con_quiebre_2025()))

    clave = ["metrica", "periodo", "modelo"]
    g = L.groupby(clave)["valor"]
    est = pd.DataFrame({"n_grupo": g.count(), "p10_grupo": g.quantile(0.10),
                        "p50_grupo": g.quantile(0.50), "p90_grupo": g.quantile(0.90)}).reset_index()
    L = L.merge(est, on=clave, how="left")
    chico = L["n_grupo"] < MIN_GRUPO_PERCENTIL
    for c in ["p10_grupo", "p50_grupo", "p90_grupo"]:
        L.loc[chico, c] = np.nan
    L["pct_grupo"] = L.groupby(clave)["valor"].rank(pct=True)
    L.loc[chico, "pct_grupo"] = np.nan
    L["pct_panel"] = L.groupby(["metrica", "periodo"])["valor"].rank(pct=True)

    ranq = L["metrica"].isin(RANKEABLE) | L["metrica"].str.startswith("share_")
    L["rank_panel"] = np.nan
    L.loc[ranq, "rank_panel"] = (L.loc[ranq].groupby(["metrica", "periodo"])["valor"]
                                 .rank(ascending=False, method="min"))
    L["rank_panel_t4"] = _tomar(_rezago(_serie(L, "rank_panel"), 4, grilla), L)

    cols = ["cod_inst", "periodo", "fecha", "trimestre", "metrica", "valor", "valor_t1", "valor_t4",
            "d_tt", "d_aa", "valor_tt", "unidad_d", "p10_grupo", "p50_grupo", "p90_grupo", "pct_grupo", "pct_panel",
            "rank_panel", "rank_panel_t4", "modelo", "n_grupo"]
    return L[cols].sort_values(["cod_inst", "periodo", "metrica"]).reset_index(drop=True)


# --- bk_grupo -----------------------------------------------------------------
def _membresia(cre: pd.DataFrame, banco: pd.DataFrame) -> pd.DataFrame:
    """Qué bancos entran en cada grupo de cada óptica, con los textos de cre_institucion."""
    filas = []
    for f in cre.itertuples(index=False):
        clave = f.inst_key
        if clave.endswith("|todos"):
            cods = banco["cod_inst"].tolist()
        else:
            campo, valor = clave.split("|", 1)
            col, etiqueta = {
                "segmento": ("segmento_reg", "Sin segmento" if valor == "sin" else valor),
                "propiedad": ("propiedad", PROPIEDAD.get(valor)),
                "modelo": ("modelo", valor),
                "fintech": ("fintech", valor),
            }[campo]
            cods = banco.loc[banco[col] == etiqueta, "cod_inst"].tolist()
        if not cods:
            raise ValueError(f"grupo vacío en cre_institucion: {clave}")
        filas.append(pd.DataFrame({"inst_key": clave, "cod_inst": cods}))
    mb = pd.concat(filas, ignore_index=True)
    mb = mb.merge(cre[["inst_key", "optica", "grupo", "orden_optica", "orden_grupo"]],
                  on="inst_key", how="left", validate="m:1")
    for optica, sub in mb[~mb["inst_key"].str.endswith("|todos")].groupby("optica"):
        if sub["cod_inst"].nunique() != len(banco) or len(sub) != len(banco):
            raise ValueError(f"la óptica {optica} no parte el panel en grupos disjuntos")
    return mb


def _estadisticas(fb: pd.DataFrame, m: str) -> pd.DataFrame:
    """Bancos con dato, mediana y cuartiles por grupo y trimestre (sin cambios frente a la versión anterior)."""
    bl = fb[["inst_key", "periodo", m]].dropna(subset=[m]).groupby(["inst_key", "periodo"])[m]
    return pd.concat([bl.count().rename("n_bancos"), bl.median().rename("mediana"),
                      bl.quantile(0.25).rename("p25"), bl.quantile(0.75).rename("p75")], axis=1)


def _agregar(fb: pd.DataFrame, m: str, tipo: str, unidad: str, ok_tt: pd.Series | None = None) -> pd.DataFrame:
    """Agregado de grupo por trimestre: valor, valor_aa (a/a) y valor_tt (contra t−1).

    Las dos variaciones usan muestra constante: solo cuentan los bancos con dato en ambos lados.
    valor_tt además exige ok_tt (ver _mascara_tt: 2024-T4 y quiebre 2025).
    """
    clave = [fb["inst_key"], fb["periodo"]]
    if ok_tt is None:
        ok_tt = pd.Series(True, index=fb.index)

    def suma(serie: pd.Series, msk: pd.Series) -> pd.Series:
        return serie.where(msk).groupby(clave).sum(min_count=1)

    if tipo == "crec":
        base = CRECIMIENTO_BASE[m]
        n, d = fb[base], fb[base + "__4"]
        msk = n.notna() & d.notna() & (d != 0)
        valor = _div(suma(n, msk), suma(d, msk)) - 1
        valor_aa = pd.Series(np.nan, index=valor.index)
        valor_tt = pd.Series(np.nan, index=valor.index)
    elif tipo == "ratio":
        f_n, f_d = RATIO_SPECS[m]
        n, d = f_n(fb, ""), f_d(fb, "")
        n4, d4 = f_n(fb, "__4"), f_d(fb, "__4")
        msk = n.notna() & d.notna() & (d > 0)
        valor = _div(suma(n, msk), suma(d, msk))
        msk_s = msk & n4.notna() & d4.notna() & (d4 > 0)
        r_t = _div(suma(n, msk_s), suma(d, msk_s))
        r_4 = _div(suma(n4, msk_s), suma(d4, msk_s))
        valor_aa = (r_t - r_4) * (100 if unidad == "ratio" else 1)
        n1, d1 = f_n(fb, "__1"), f_d(fb, "__1")
        msk_t = msk & n1.notna() & d1.notna() & (d1 > 0) & ok_tt
        r_t1 = _div(suma(n, msk_t), suma(d, msk_t))
        r_1 = _div(suma(n1, msk_t), suma(d1, msk_t))
        valor_tt = (r_t1 - r_1) * (100 if unidad == "ratio" else 1)
    else:  # monto, incluidas las cuotas (suma de cuotas = cuota del grupo)
        x, x4, x1 = fb[m], fb[m + "__4"], fb[m + "__1"]
        valor = suma(x, x.notna())
        msk_s = x.notna() & x4.notna()
        a_t, a_4 = suma(x, msk_s), suma(x4, msk_s)
        valor_aa = (a_t - a_4) * 100 if unidad == "ratio" else _div(a_t, a_4) - 1
        msk_t = x.notna() & x1.notna() & ok_tt
        b_t, b_1 = suma(x, msk_t), suma(x1, msk_t)
        valor_tt = (b_t - b_1) * 100 if unidad == "ratio" else _div(b_t, b_1) - 1

    est = _estadisticas(fb, m)
    res = pd.concat([valor.rename("valor"), valor_aa.rename("valor_aa"), valor_tt.rename("valor_tt"), est], axis=1)
    res = res.dropna(subset=["valor"]).reset_index()
    res["metrica"] = m
    res["unidad_aa"] = None if tipo == "crec" else _unidad_aa(unidad)
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
                                          _periodo_previo_serie(per, k).to_numpy()])
        return pd.Series(valor.reindex(prev).to_numpy(), index=base.index)

    valor_aa = ((valor - desfasado(4)) * 100).where(_mascara_endpoints(per, 4))
    valor_tt = ((valor - desfasado(1)) * 100).where(_mascara_endpoints(per, 1))
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
            "inst_key": "panel|todos", "periodo": valor.index, "metrica": nombre,
            "valor": valor.to_numpy(), "valor_aa": np.nan, "unidad_aa": None,
            "n_bancos": n.reindex(valor.index).to_numpy(), "mediana": np.nan,
            "p25": np.nan, "p75": np.nan}))
    return pd.concat(filas, ignore_index=True)


def _bk_grupo(w: pd.DataFrame, banco: pd.DataFrame, cre: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    w4 = w.groupby(level="cod_inst").shift(4)
    w1 = w.groupby(level="cod_inst").shift(1)
    mb = _membresia(cre, banco)
    fb = mb.merge(pd.concat([w, w4.add_suffix("__4"), w1.add_suffix("__1")], axis=1).reset_index(), on="cod_inst")
    ok_tt = _mascara_tt(fb["periodo"], fb["cod_inst"], _bancos_con_quiebre_2025())
    partes = []
    pieza_credito = None
    for m in w.columns:
        if m == "credito_real_aa":
            continue  # se deriva del crecimiento nominal del grupo, más abajo
        # Cuotas de grupo: suma de las cuotas de sus bancos (verificar.py la exceptúa del rango).
        tipo = "crec" if m in CRECIMIENTO_BASE else ("ratio" if m in RATIO_SPECS else "monto")
        res = _agregar(fb, m, tipo, meta.loc[m, "unidad"], ok_tt)
        if m == "credito_aa":
            pieza_credito = res
        partes.append(res)
    partes.append(_agregar_real(fb, pieza_credito, _ipca_12m_trimestral()))
    partes.append(_hhi_top5(w))
    out = pd.concat(partes, ignore_index=True)
    grupos = cre[["inst_key", "optica", "grupo", "orden_optica", "orden_grupo"]]
    out = out.merge(grupos, on="inst_key", how="left", validate="m:1")
    out["fecha"] = _fecha(out["periodo"])
    out["trimestre"] = out["periodo"].map(_trimestre)
    out["n_bancos"] = out["n_bancos"].astype("Int64")
    cols = ["optica", "grupo", "periodo", "fecha", "trimestre", "metrica", "valor", "valor_aa",
            "unidad_aa", "valor_tt", "unidad_tt", "mediana", "p25", "p75", "n_bancos",
            "orden_optica", "orden_grupo"]
    return out[cols].sort_values(["orden_optica", "orden_grupo", "metrica", "periodo"]).reset_index(drop=True)


# --- bk_puente ----------------------------------------------------------------
def _bk_puente(banco: pd.DataFrame) -> pd.DataFrame:
    val = pd.DataFrame(json.loads(ENTRADA_VALIDACION.read_text(encoding="utf-8")))
    cod = dict(zip(banco["nombre_corto"], banco["cod_inst"]))
    val["cod_inst"] = val["banco"].map(cod)
    if val["cod_inst"].isna().any():
        raise ValueError("validacion.json: banco sin cod_inst: " + ", ".join(val.loc[val.cod_inst.isna(), "banco"].unique()))
    val["periodo"] = val["periodo"].astype(str)
    val["dif_pct"] = (val["ifdata"] - val["gaap"]) / val["gaap"].where(val["gaap"] != 0)
    return val[["banco", "cod_inst", "linea", "periodo", "gaap", "ifdata", "dif_pct", "nota"]].reset_index(drop=True)


# --- bk_manifiesto ------------------------------------------------------------
def _corte_sistema() -> tuple[str | None, str | None]:
    if not ENTRADA_SISTEMA_M.exists():
        return None, "bk_sistema_m.parquet todavía no existe"
    s = pd.read_parquet(ENTRADA_SISTEMA_M)
    if "periodo" in s.columns:
        return str(s["periodo"].max()), None
    if "fecha" in s.columns:
        return str(pd.to_datetime(s["fecha"]).max().date()), None
    return None, "bk_sistema_m.parquet sin columna de fecha"


def _parquet_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    return buf.getvalue()


def _rango(df: pd.DataFrame, col: str) -> str:
    return f"{df[col].min()}–{df[col].max()}"


def _principal_base() -> None:
    banco = _bk_banco()
    cods = banco["cod_inst"].tolist()
    w, grilla = _cargar_ancho(cods)
    metricas = list(w.columns) + METRICAS_SOLO_GRUPO
    metrica_df = _bk_metrica(metricas)
    meta = metrica_df.set_index("metrica")
    panel = _bk_panel(w, banco, meta, grilla)
    cre = pd.read_parquet(ENTRADA_CRE_INSTITUCION)
    grupo = _bk_grupo(w, banco, cre, meta)
    puente = _bk_puente(banco)

    entradas = {
        "bk_banco.parquet": (banco, f"{len(banco)} bancos", [
            "datos/gold/bank_instituciones.parquet", "definiciones/bcb_ifdata__bancos_balances.json",
            "definiciones/bancos__dashboard.json"]),
        "bk_metrica.parquet": (metrica_df, f"{len(metrica_df)} métricas", [
            "datos/intermedio/metricas_bancos.parquet"]),
        "bk_panel.parquet": (panel, f"{panel['periodo'].min()}–{panel['periodo'].max()}", [
            "datos/intermedio/metricas_bancos.parquet", "datos/gold/bank_instituciones.parquet"]),
        "bk_grupo.parquet": (grupo, f"{grupo['periodo'].min()}–{grupo['periodo'].max()}", [
            "datos/intermedio/metricas_bancos.parquet", "datos/intermedio/cre_institucion.parquet",
            "datos/gold/bank_instituciones.parquet"]),
        "bk_puente.parquet": (puente, f"{puente['periodo'].min()}–{puente['periodo'].max()}", [
            "definiciones/validacion_bancos.json"]),
    }

    filas_man = []
    for nombre, (df, rango, desde) in entradas.items():
        datos = _parquet_bytes(df)
        A.guardar_derivado(FUENTE_DERIVADA, DATASET_DERIVADO, nombre, datos, desde=desde, como=COMANDO)
        A.escribir_atomico(CARPETA_BANKS / nombre, datos)
        filas_man.append({"tipo": "tabla", "tabla": nombre.replace(".parquet", ""), "archivo": nombre,
                          "filas": len(df), "columnas": df.shape[1], "rango": rango,
                          "sha256": hashlib.sha256(datos).hexdigest(), "bytes": len(datos),
                          "producido_por": COMANDO, "universo": None, "ultimo_corte": None, "nota": None})
        print(f"{nombre}: {len(df):,} filas, {df.shape[1]} columnas, rango {rango}")

    # Tablas bk_* que ya existían en datos/gold y no produce este script (p. ej. bk_sistema_m/q):
    # el manifiesto las declara con su sha256 real para que la portada las vea.
    for ruta in sorted(CARPETA_BANKS.glob("bk_*.parquet")):
        if ruta.name in entradas or ruta.name == "bk_manifiesto.parquet":
            continue
        datos_o = ruta.read_bytes()
        otra = pd.read_parquet(ruta)
        producido = {"bk_sistema_m.parquet": "preparar_gold_bancos_sistema.py (encargo 61)",
                     "bk_sistema_q.parquet": "preparar_gold_bancos_sistema.py (encargo 61)",
                     "bk_roe_arbol.parquet": COMANDO_RENTABILIDAD,
                     "bk_sensibilidad.parquet": COMANDO_RENTABILIDAD,
                     "bk_cartera.parquet": "preparar_gold_bancos_cartera.py",
                     "bk_cartera_totales.parquet": "preparar_gold_bancos_cartera.py",
                     "bk_exposicion.parquet": "preparar_gold_bancos_exposicion.py",
                     "bk_scr.parquet": "preparar_gold_bancos_scr.py (encargo 67)",
                     "bk_cartera_mix7.parquet": "preparar_gold_bancos_cartera.py (encargo 78b)",
                     "bk_cartera_grupo.parquet": "preparar_gold_bancos_cartera.py",
                     "bk_qcambio.parquet": "preparar_gold_bancos_qcambio.py (encargo 78d; correr después de base)",
                     "bk_scr_tablas.parquet": "preparar_gold_bancos_scr_productos.py (páginas Personas y Mora, 6-nov)",
                     "bk_scr_series.parquet": "preparar_gold_bancos_scr_productos.py (páginas Personas y Mora, 6-nov)",
                     }.get(ruta.name, "fuera de preparar_gold_bancos.py base")
        filas_man.append({"tipo": "tabla", "tabla": ruta.stem, "archivo": ruta.name,
                          "filas": len(otra), "columnas": otra.shape[1],
                          "rango": _rango(otra, "fecha") if "fecha" in otra.columns else None,
                          "sha256": hashlib.sha256(datos_o).hexdigest(), "bytes": len(datos_o),
                          "producido_por": producido, "universo": None, "ultimo_corte": None, "nota": None})

    # Universos con tabla en esta ola. SCR, Publicado y REF no tienen tabla gold todavía: se
    # añaden cuando existan, sin corte inventado.
    corte_sis, nota_sis = _corte_sistema()
    universos = [("Panel", str(panel["fecha"].max()), "IF.Data prudencial, trimestral")]
    if corte_sis is not None:
        universos.append(("Sistema", corte_sis, "SGS, mensual (bk_sistema_m, encargo 61)"))
    ruta_scr = CARPETA_BANKS / "bk_scr.parquet"
    if ruta_scr.exists():
        corte_scr = str(pd.read_parquet(ruta_scr, columns=["fecha"])["fecha"].max())
        universos.append(("SCR", corte_scr, "SCR.data, mensual, por segmento de institución (bk_scr, encargo 67)"))
    elif nota_sis:
        print("aviso:", nota_sis)
    for nombre, corte, nota in universos:
        filas_man.append({"tipo": "universo", "tabla": None, "archivo": None, "filas": None,
                          "columnas": None, "rango": None, "sha256": None, "bytes": None,
                          "producido_por": None, "universo": nombre, "ultimo_corte": corte, "nota": nota})
    manifiesto = pd.DataFrame(filas_man)
    datos = _parquet_bytes(manifiesto)
    nombre = "bk_manifiesto.parquet"
    A.guardar_derivado(FUENTE_DERIVADA, DATASET_DERIVADO, nombre, datos,
                       desde=[f"datos/gold/{k}" for k in entradas], como=COMANDO)
    A.escribir_atomico(CARPETA_BANKS / nombre, datos)
    print(f"{nombre}: {len(manifiesto)} filas")


# --- Rentabilidad: árbol del ROE y sensibilidad a la Selic (encargo 64) ---------------
# POR QUÉ: el sitio muestra de dónde sale el ROE (margen, provisiones, costos, impuestos y
# apalancamiento) y cuánto se mueve el margen de intermediación con la Selic. Las dos tablas
# salen de aquí para que el sitio solo dibuje (ESQUELETO B6-02, B6-04, B8-04; SPEC §3.7 y §3.8).
COMANDO_RENTABILIDAD = "python -X utf8 preparar_gold_bancos.py rentabilidad"
LINEAS_ARBOL = ["margen_antes_provisiones", "provisiones", "tarifas_servicios", "transacciones_pago",
                "personal", "administrativos", "tributarios", "no_operacional", "otros",
                "impuesto_participaciones"]
LINEAS_EXPORTABLES = LINEAS_ARBOL + ["roa", "apalancamiento", "roe"]
ORDEN_LINEA = {linea: i for i, linea in enumerate(LINEAS_EXPORTABLES, start=1)}
LINEAS_EN_VECES = {"apalancamiento"}     # activo medio / patrimonio medio; el resto es fracción
TOL_ROA_ARBOL = 1e-6          # Σ líneas 1–9 = ROA = roa_ttm (SPEC §3.7)
TOL_ROE_ARBOL = 0.001         # ROA × apalancamiento = roe_ttm (0,1 pp)
PERIODO_QUIEBRE_2025 = "202503"  # ruptura de cobertura de 2025: solo bancos con quiebre_2025 = true
PERIODO_INICIO_BETA = "201603"
PERIODO_EXCLUIDO_BETA = "202412"
REZAGOS_NEWEY_WEST = 4
MIN_TRIMESTRES_BETA = 16      # SPEC §3.8: si n < 16, todo null
MIN_BANCOS_MEDIANA = 3        # igual que los percentiles de bk_panel
NUCLEO_ARBOL = ["A", "PL", "lucro", "antes", "rif", "prov", "tarifas", "servicios", "personal",
                "administrativos", "tributarios", "roa_m", "roe_m"]


def _ttm_desde_q(serie_q: pd.Series) -> pd.Series:
    """TTM = suma de los 4 trimestres consecutivos que terminan en t; vacío si falta uno.

    POR QUÉ: despesas_tributarias_ttm no está en metricas_bancos (SPEC §3.7). Se suma sobre la
    cuadrícula de trimestres y no sobre las filas que existen: un trimestre sin dato tumba el
    TTM, igual que en el resto del panel, en vez de saltarse en silencio.
    """
    ancho = serie_q.unstack("periodo")
    suma = ancho
    for k in range(1, 4):
        suma = suma + ancho.shift(k, axis=1)
    return suma.stack(future_stack=True)


def _control_ttm(calculado: pd.Series, existente: pd.Series) -> tuple[int, int]:
    """El TTM propio tiene que reproducir el de metricas_bancos donde ambos existen (personal)."""
    ambos = calculado.notna() & existente.notna()
    dif = (calculado - existente).abs() / existente.abs().where(ambos)
    maximo = float(dif.where(ambos).max()) if ambos.any() else 0.0
    if not maximo <= 1e-9:
        raise ValueError(f"el TTM calculado no reproduce el de metricas_bancos (diferencia relativa {maximo})")
    return int(ambos.sum()), int((calculado.notna() != existente.notna()).sum())


def _insumos_arbol(w: pd.DataFrame, trib_ttm: pd.Series, noop_ttm: pd.Series) -> pd.DataFrame:
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
        "tributarios": trib_ttm.reindex(w.index), "no_op": noop_ttm.reindex(w.index),
        "roa_m": w["roa_ttm"], "roe_m": w["roe_ttm"],
    }, index=w.index)
    d["apto"] = d[NUCLEO_ARBOL].notna().all(axis=1) & (d["A"] > 0) & (d["PL"] > 0)
    return d


def _lineas_banco(d: pd.DataFrame) -> pd.DataFrame:
    """Líneas 1–9, ROA, apalancamiento y ROE por banco y trimestre (fracción del activo medio).

    POR QUÉ las provisiones se restan así: resultado_intermediacao_financeira ya viene neto de
    provisiones (COSIF), así que el margen antes de provisiones es RIF − provisiones, y la línea 2
    lleva las provisiones con su signo negativo. «Otros» es el residuo que cierra con el antes de
    tributación, y por eso absorbe lo que una línea no separa (p. ej. pagos antes de 2025).
    """
    ap = d["apto"]
    a = d["A"].where(ap)
    L = pd.DataFrame(index=d.index)
    L["margen_antes_provisiones"] = (d["rif"] - d["prov"]).where(ap) / a
    L["provisiones"] = d["prov"].where(ap) / a
    L["tarifas_servicios"] = (d["tarifas"] + d["servicios"]).where(ap) / a
    L["transacciones_pago"] = d["transacciones"].where(ap) / a
    L["personal"] = d["personal"].where(ap) / a
    L["administrativos"] = d["administrativos"].where(ap) / a
    L["tributarios"] = d["tributarios"].where(ap) / a
    L["no_operacional"] = d["no_op"].where(ap) / a
    resto = (L[["margen_antes_provisiones", "provisiones", "tarifas_servicios", "personal",
                "administrativos", "tributarios"]].sum(axis=1, min_count=1)
             + L["transacciones_pago"].fillna(0) + L["no_operacional"].fillna(0))
    L["otros"] = d["antes"].where(ap) / a - resto
    L["impuesto_participaciones"] = (d["lucro"] - d["antes"]).where(ap) / a
    L["roa"] = d["lucro"].where(ap) / a
    L["apalancamiento"] = a / d["PL"].where(ap)
    L["roe"] = L["roa"] * L["apalancamiento"]
    L.columns.name = "linea"
    return L[LINEAS_EXPORTABLES]


def _lineas_grupo(d: pd.DataFrame, mb: pd.DataFrame) -> pd.DataFrame:
    """Las mismas líneas por grupo: Σ numerador / Σ activo medio, con los bancos aptos del grupo.

    POR QUÉ: un grupo no es el promedio de los ratios de sus bancos (SPEC §1.5). Solo cuentan los
    bancos aptos en ese trimestre, para que todas las líneas del grupo usen el mismo conjunto
    de bancos y el árbol cierre también a nivel de grupo.
    """
    cols = ["A", "PL", "lucro", "antes", "rif", "prov", "tarifas", "servicios", "transacciones",
            "personal", "administrativos", "tributarios", "no_op"]
    x = d[cols].where(d["apto"], axis=0).reset_index()
    x = x.merge(mb[["cod_inst", "entidad"]], on="cod_inst", how="inner")
    S = x.groupby(["entidad", "periodo"])[cols].sum(min_count=1)
    a, pl = S["A"], S["PL"]
    G = pd.DataFrame(index=S.index)
    G["margen_antes_provisiones"] = (S["rif"] - S["prov"]) / a
    G["provisiones"] = S["prov"] / a
    G["tarifas_servicios"] = (S["tarifas"] + S["servicios"]) / a
    G["transacciones_pago"] = S["transacciones"] / a
    G["personal"] = S["personal"] / a
    G["administrativos"] = S["administrativos"] / a
    G["tributarios"] = S["tributarios"] / a
    G["no_operacional"] = S["no_op"] / a
    resto = (G[["margen_antes_provisiones", "provisiones", "tarifas_servicios", "personal",
                "administrativos", "tributarios"]].sum(axis=1, min_count=1)
             + G["transacciones_pago"].fillna(0) + G["no_operacional"].fillna(0))
    G["otros"] = S["antes"] / a - resto
    G["impuesto_participaciones"] = (S["lucro"] - S["antes"]) / a
    G["roa"] = S["lucro"] / a
    G["apalancamiento"] = a / pl
    G["roe"] = G["roa"] * G["apalancamiento"]
    G.columns.name = "linea"
    return G[LINEAS_EXPORTABLES]


def _medianas(largo: pd.DataFrame, pertenencia: pd.DataFrame) -> pd.DataFrame:
    """Mediana de cada línea entre los bancos de cada grupo; vacío si el grupo tiene menos de 3 con dato."""
    j = largo.dropna(subset=["valor"]).merge(pertenencia, on="cod_inst")
    g = j.groupby(["entidad", "periodo", "linea"])["valor"]
    med = pd.DataFrame({"mediana": g.median(), "n": g.count()}).reset_index()
    med.loc[med["n"] < MIN_BANCOS_MEDIANA, "mediana"] = np.nan
    return med[["entidad", "periodo", "linea", "mediana"]]


# --- Sensibilidad a la Selic --------------------------------------------------------
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


def _cdi_trimestral() -> pd.Series:
    """CDI medio del trimestre (tasa anual en fracción) desde datos/intermedio/cre_contexto.parquet, panel|todos.

    Unidad confirmada: 0,1413 = 14,13 % anual (Selic 14,25 % en 2016-T1). Se comprueba además que
    la media de 4 trimestres de esta serie reproduce «CDI (media 4T)» de la misma tabla.
    """
    ctx = pd.read_parquet(ENTRADA_CONTEXTO)
    base = ctx[ctx["inst_key"] == "panel|todos"]
    cdi = base[base["serie"] == "CDI"].assign(periodo=lambda t: t["periodo"].astype(str))
    cdi = cdi.set_index("periodo")["valor"].astype(float).sort_index()
    if cdi.empty or cdi.isna().any() or not ((cdi > 0) & (cdi < 1)).all():
        raise ValueError("CDI de cre_contexto fuera de la unidad esperada (fracción anual)")
    media = base[base["serie"] == "CDI (media 4T)"].assign(periodo=lambda t: t["periodo"].astype(str))
    media = media.set_index("periodo")["valor"].astype(float).sort_index()
    grilla = [p for p in media.index if p in cdi.index]
    rolling = cdi.reindex(sorted(set(cdi.index) | set(media.index))).rolling(4, min_periods=4).mean()
    dif = float((rolling.reindex(grilla) - media.reindex(grilla)).abs().max())
    if not dif <= 1e-9:
        raise ValueError(f"la media de 4 trimestres del CDI no reproduce «CDI (media 4T)» (dif {dif})")
    return cdi


def _bancos_con_quiebre_2025() -> set[str]:
    """Bancos con ruptura de cobertura en 2025 según bk_cartera (columna quiebre_2025)."""
    c = pd.read_parquet(ENTRADA_CARTERA, columns=["cod_inst", "quiebre_2025"])
    return set(c.loc[c["quiebre_2025"].astype(bool), "cod_inst"].astype(str))


def _bk_sensibilidad(w: pd.DataFrame, banco: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Beta del NIM trimestral anualizado contra el CDI, por banco (SPEC §3.8; encargo 64b).

    NIM_t = 4 × (RIF_q − provisiones_q) / ((activo_{t−1} + activo_t) / 2). Excluidos: 202412 en todos
    los bancos, y 202503 solo en los bancos con ruptura de cobertura en 2025 (quiebre_2025 = true en
    bk_cartera). El crecimiento orgánico no se excluye. El intervalo de 90 % usa el cuantil t con
    n − 2 grados de libertad y el error de Newey-West.
    """
    cdi = _cdi_trimestral()
    ativo = w["ativo_total"]
    ativo_prev = ativo.groupby(level="cod_inst").shift(1)
    medio = (ativo + ativo_prev) / 2.0
    nim = 4.0 * (w["resultado_intermediacao_financeira_q"] - w["provisoes_credito_q"]) / medio.where(medio > 0)
    quiebre = _bancos_con_quiebre_2025()

    periodos = sorted(w.index.get_level_values("periodo").unique())
    en_ventana = pd.Series([p >= PERIODO_INICIO_BETA for p in periodos], index=periodos)
    fijo = pd.Series([p == PERIODO_EXCLUIDO_BETA for p in periodos], index=periodos)
    cdi_g = cdi.reindex(periodos)

    filas = []
    for cod in banco["cod_inst"]:
        y_all = nim.xs(cod, level="cod_inst").reindex(periodos)
        por_quiebre = pd.Series([cod in quiebre and p == PERIODO_QUIEBRE_2025 for p in periodos], index=periodos)
        excluido = en_ventana & (fijo | por_quiebre)
        usa = en_ventana & ~excluido & y_all.notna() & cdi_g.notna()
        lista_excl = [p for p in periodos if excluido[p] and pd.notna(y_all[p])]
        n = int(usa.sum())
        beta = ic_inf = ic_sup = r2 = np.nan
        if n >= MIN_TRIMESTRES_BETA and float(np.ptp(cdi_g[usa].to_numpy())) > 0:
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
    cierra = (((suma - L["roa"]).abs() <= TOL_ROA_ARBOL)
              & ((L["roa"] - d["roa_m"]).abs() <= TOL_ROA_ARBOL)
              & ((L["roe"] - d["roe_m"]).abs() <= TOL_ROE_ARBOL))
    return (cierra | ~d["apto"]).astype(bool)


def _bk_roe_arbol(w: pd.DataFrame, banco: pd.DataFrame, mb: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Árbol del ROE por banco y por grupo de cada óptica (SPEC §3.7). Una fila que no cierra no se exporta."""
    trib = _ttm_desde_q(w["despesas_tributarias_q"]).reindex(w.index)
    control = _control_ttm(_ttm_desde_q(w["despesas_pessoal_q"]).reindex(w.index), w["despesas_pessoal_ttm"])
    noop = _ttm_desde_q(w["resultado_nao_operacional_q"]).reindex(w.index)
    d = _insumos_arbol(w, trib, noop)

    L = _lineas_banco(d)
    cuadra_b = _cuadra_arbol(L, d)
    Lb = L.rename_axis(columns="linea").stack(future_stack=True).rename("valor").reset_index()
    Lb = Lb.merge(cuadra_b.rename("cuadra").reset_index(), on=["cod_inst", "periodo"])
    fallas_b = sorted(set(Lb.loc[~Lb["cuadra"], ["cod_inst", "periodo"]].itertuples(index=False, name=None)))
    Lb_ok = Lb[Lb["cuadra"]][["cod_inst", "periodo", "linea", "valor"]]

    G = _lineas_grupo(d, mb)
    suma_g = G[LINEAS_ARBOL].sum(axis=1, min_count=1)
    cuadra_g = (((suma_g - G["roa"]).abs() <= TOL_ROA_ARBOL) | G["roa"].isna())
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
    out["unidad"] = np.where(out["linea"].isin(LINEAS_EN_VECES), "veces", "fraccion")
    out["fecha"] = _fecha(out["periodo"])
    out["trimestre"] = out["periodo"].map(_trimestre)
    # Encargo 78a §4: brecha = valor − mediana_grupo, en la misma unidad que valor (solo una resta).
    out["brecha"] = out["valor"] - out["mediana_grupo"]
    out = out.sort_values(["entidad", "periodo", "orden"]).reset_index(drop=True)
    cols_fin = ["entidad", "periodo", "fecha", "trimestre", "linea", "orden", "unidad", "valor",
                "mediana_grupo", "brecha"]
    return out[cols_fin], {"control_ttm": control, "fallas_bancos": fallas_b, "fallas_grupos": fallas_g,
                           "d": d, "L": L, "G": G}


def _registrar_en_manifiesto(filas: list[dict]) -> None:
    """Pone las filas de las tablas nuevas en bk_manifiesto: verificar.py exige una fila por tabla presente.

    Reemplaza solo las filas de estas tablas; las demás quedan como las dejó base.
    """
    ruta = CARPETA_BANKS / "bk_manifiesto.parquet"
    man = pd.read_parquet(ruta)
    columnas = list(man.columns)
    nombres = {f["tabla"] for f in filas}
    man = man[~man["tabla"].isin(nombres)]
    man = pd.concat([man, pd.DataFrame(filas)], ignore_index=True)[columnas]
    datos = _parquet_bytes(man)
    desde = [f"datos/gold/{n}.parquet" for n in sorted(nombres)] + ["datos/gold/bk_manifiesto.parquet"]
    A.guardar_derivado(FUENTE_DERIVADA, DATASET_DERIVADO, "bk_manifiesto.parquet", datos,
                       desde=desde, como=f"{COMANDO} + {COMANDO_RENTABILIDAD}")
    A.escribir_atomico(ruta, datos)


def _principal_rentabilidad() -> None:
    banco = _bk_banco()
    cods = banco["cod_inst"].tolist()
    w, _grilla = _cargar_ancho(cods)
    cre = pd.read_parquet(ENTRADA_CRE_INSTITUCION)
    mb = _membresia(cre, banco)
    mb["entidad"] = mb["optica"] + "|" + mb["grupo"]

    arbol, rep = _bk_roe_arbol(w, banco, mb)
    sens, rep_s = _bk_sensibilidad(w, banco)
    print(f"bk_roe_arbol: {len(arbol):,} filas, {arbol['entidad'].nunique()} entidades; "
          f"TTM personal reproducido en {rep['control_ttm'][0]:,} celdas")
    print(f"  no exportadas por no cuadrar: {len(rep['fallas_bancos'])} bancos-trimestres, "
          f"{len(rep['fallas_grupos'])} grupos-trimestres")
    print(f"bk_sensibilidad: {len(sens)} bancos, {int(sens['beta_nim_cdi'].notna().sum())} con beta")

    tablas = [
        ("bk_roe_arbol.parquet", arbol, f"{arbol['periodo'].min()}–{arbol['periodo'].max()}",
         ["datos/intermedio/metricas_bancos.parquet", "datos/gold/bank_instituciones.parquet",
          "datos/intermedio/cre_institucion.parquet"], "bk_roe_arbol"),
        ("bk_sensibilidad.parquet", sens, f"{PERIODO_INICIO_BETA}–{rep_s['periodos'][-1]}",
         ["datos/intermedio/metricas_bancos.parquet", "datos/intermedio/cre_contexto.parquet",
          "datos/gold/bank_instituciones.parquet"], "bk_sensibilidad"),
    ]
    filas_man = []
    for nombre, df, rango, desde, tabla in tablas:
        datos = _parquet_bytes(df)
        A.guardar_derivado(FUENTE_DERIVADA, DATASET_DERIVADO, nombre, datos, desde=desde,
                           como=COMANDO_RENTABILIDAD)
        A.escribir_atomico(CARPETA_BANKS / nombre, datos)
        filas_man.append({"tipo": "tabla", "tabla": tabla, "archivo": nombre, "filas": len(df),
                          "columnas": df.shape[1], "rango": rango,
                          "sha256": hashlib.sha256(datos).hexdigest(), "bytes": len(datos),
                          "producido_por": COMANDO_RENTABILIDAD, "universo": None,
                          "ultimo_corte": None, "nota": None})
        print(f"{nombre}: {len(df):,} filas, {df.shape[1]} columnas, rango {rango}")
    _registrar_en_manifiesto(filas_man)
    print("bk_manifiesto.parquet: filas de bk_roe_arbol y bk_sensibilidad actualizadas")



def main() -> None:
    """Un comando por tabla y `todo` para el refresco completo.

    `sistema`, `cartera` y `exposicion` viven en módulos aparte (preparar_gold_bancos_sistema.py,
    _cartera.py, _exposicion.py) porque se escribieron en paralelo con este archivo; aquí solo se
    enchufan. `todo` respeta las dependencias: sistema → cartera → base (usa bk_cartera para npl15_total y pf_share) → rentabilidad (usa el
    quiebre 2025 de bk_cartera) → exposicion (usa bk_cartera y bk_sistema_q) → base otra vez, para que
    bk_manifiesto registre todas las tablas con su sha256 final.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="orden", required=True)
    sub.add_parser("base", help="construye bk_banco, bk_metrica, bk_panel, bk_grupo, bk_puente y bk_manifiesto, sin red")
    sub.add_parser("rentabilidad", help="construye bk_roe_arbol y bk_sensibilidad (encargo 64), sin red")
    p_sis = sub.add_parser("sistema", help="construye bk_sistema_m y bk_sistema_q (SGS; baja lo que falte)")
    p_sis.add_argument("--descargar", action="store_true", help="re-baja las series del SGS aunque el crudo exista")
    sub.add_parser("cartera", help="construye bk_cartera y bk_cartera_totales desde los informes 11 y 13, sin red")
    sub.add_parser("exposicion", help="construye bk_exposicion (mora implícita del mix), sin red")
    p_todo = sub.add_parser("todo", help="corre todo en orden de dependencias")
    p_todo.add_argument("--descargar", action="store_true", help="pasa --descargar a sistema")
    args = parser.parse_args()

    def _sistema(descargar: bool) -> None:
        import preparar_gold_bancos_sistema as S
        if S.main(["--descargar"] if descargar else []):
            raise SystemExit("sistema: la verificación de bk_sistema falló")

    def _cartera() -> None:
        import preparar_gold_bancos_cartera as Ca
        if Ca.main():
            raise SystemExit("cartera: la verificación de bk_cartera falló")

    def _exposicion() -> None:
        import preparar_gold_bancos_exposicion as E
        E.main()

    if args.orden == "base":
        _principal_base()
    elif args.orden == "rentabilidad":
        _principal_rentabilidad()
    elif args.orden == "sistema":
        _sistema(args.descargar)
    elif args.orden == "cartera":
        _cartera()
    elif args.orden == "exposicion":
        _exposicion()
    elif args.orden == "todo":
        _sistema(args.descargar)
        _cartera()
        _principal_base()
        _principal_rentabilidad()
        _exposicion()
        _principal_base()


if __name__ == "__main__":
    main()
