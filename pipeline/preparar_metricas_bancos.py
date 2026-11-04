# -*- coding: utf-8 -*-
"""Prepara la capa de métricas del dashboard de bancos (proyecto independiente).

Consume los parquets curados (datos/gold/) y produce una tabla limpia de métricas
en formato largo (una fila por banco × período × métrica) para consumo directo
por la capa visual (HTML/Plotly hoy, Power BI DAX mañana).

Reglas de diseño (ver docs/validacion_multibanco.md):
- Solo escopo prudencial.
- Códigos COSIF por era: cosif_2025 (140xxx/141xxx) y cosif_pre2025 (78xxx).
- 'credito_total' = (e)+(f)+(g)+(h) en era nueva; (d)+(e)+(f) en era vieja
  (menos comparable: 'outros créditos' incluye partidas extra).
- Flujos DRE des-acumulados por trimestre (bank_resultados).
- TTM = suma de los 4 trimestres consecutivos que terminan en t (NaN si falta uno).
- ROE/ROA TTM con promedio de patrimônio/ativo entre t-4 y t (2 puntos).
- Cuotas de mercado dentro del panel presente en cada trimestre.
Salidas:
- datos/intermedio/metricas_bancos.parquet  (largo, consumo visual)
- datos/intermedio/panel_bancos_wide.csv    (ancha, inspección)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_BANCOS = RAIZ / "datos" / "gold"
CARPETA_SALIDA = RAIZ / "datos" / "intermedio"

# --- Códigos COSIF por era (informe 2 = ativo, informe 3 = passivo) ------------
CODIGOS_2025 = {
    "disponibilidades": "140198",
    "aplic_interfinanceiras": "140199",
    "tvm": "140200",
    "derivativos_ativo": "141612",
    "credito_bruto": "140201",
    "ecl_saldo": "140202",
    "credito_liquido": "140205",
    "arrendamento": "140210",
    "outras_concessao": "140216",
    "pagos_receber": "145833",
    "outros_ativos": "140218",
    "ativo_permanente": "140219",
    "ativo_total": "140220",
    "depositos": "140228",
    "depositos_interfinanceiros": "140224",
    "oblig_compromissadas": "140230",
    "outros_instrumentos_divida": "140236",
    "emprestimos_repasses": "140238",
    "derivativos_passivo": "140241",
    "outras_obrigacoes": "140242",
    "instrumentos_elegiveis": "140243",
    "passivo_exigivel": "140244",
    "patrimonio_liquido": "140246",
}
CODIGOS_PRE2025 = {
    "disponibilidades": "78188",
    "aplic_interfinanceiras": "78189",
    "tvm_mas_derivativos": "78190",
    "credito_bruto": "78191",
    "ecl_saldo": "78192",
    "credito_liquido": "78193",
    "arrendamento": "78198",
    "outras_concessao": "78199",  # 'outros créditos (f)' — menos comparable
    "outros_ativos": "78200",
    "ativo_permanente": "78201",
    "ativo_total": "78202",
    "depositos": "78287",
    "depositos_interfinanceiros": "78284",
    "oblig_compromissadas": "78288",
    "outros_instrumentos_divida": "78294",
    "emprestimos_repasses": "78295",
    "derivativos_passivo": "78296",
    "outras_obrigacoes": "78297",
    "passivo_exigivel": "78298",
    "patrimonio_liquido": "78186",
}

FLUJOS = {  # columnas de bank_resultados (des-acumulado por trimestre)
    "lucro_liquido_q": "lucro_liquido",
    "resultado_intermediacao_financeira_q": "resultado_intermediacao_financeira",
    "resultado_transacoes_pagamento_q": "resultado_transacoes_pagamento",
    "provisoes_credito_q": "provisoes_credito",
    "rendas_tarifas_q": "rendas_tarifas_bancarias",
    "rendas_servicos_q": "rendas_prestacao_servicos",
    "despesas_pessoal_q": "despesas_pessoal",
    "despesas_administrativas_q": "despesas_administrativas",
    "despesas_tributarias_q": "despesas_tributarias",
    "antes_tributacao_q": "resultado_antes_tributacao_participacoes",
    "outras_receitas_despesas_q": "outras_receitas_despesas",
    "resultado_nao_operacional_q": "resultado_nao_operacional",
}

TITULOS_TTM = [  # flujos que se acumulan a TTM
    "lucro_liquido_q",
    "resultado_intermediacao_financeira_q",
    "resultado_transacoes_pagamento_q",
    "provisoes_credito_q",
    "rendas_tarifas_q",
    "rendas_servicos_q",
    "despesas_pessoal_q",
    "despesas_administrativas_q",
    "antes_tributacao_q",
]


def _periodo_prev(periodo: str) -> str | None:
    """Devuelve el label del trimestre anterior (YYYYMM) o None."""
    anio, mes = int(periodo[:4]), int(periodo[4:])
    mes -= 3
    if mes == 0:
        return f"{anio - 1}12"
    return f"{anio}{mes:02d}"


def _cargar_hechos() -> pd.DataFrame:
    df = pd.read_parquet(CARPETA_BANCOS / "bank_hechos.parquet")
    df = df[df.escopo == "prudencial"].copy()
    # stocks: solo informes 2 (ativo) y 3 (passivo); el informe 4 trae memos con
    # códigos repetidos (p. ej. 140220) que contaminarían el pivote
    informes = df["cuenta_id"].str.slice(0, 2).isin(["r2", "r3"])
    df = df[informes].drop_duplicates(["cod_inst", "periodo", "cod_cuenta"], keep="first")
    df["valor_publicado"] = pd.to_numeric(df["valor_publicado"], errors="coerce")
    return df


def _pivotar_stocks(hechos: pd.DataFrame) -> pd.DataFrame:
    """Convierte los códigos COSIF por era en columnas de métricas."""
    filas = []
    for (cod, periodo), grupo in hechos.groupby(["cod_inst", "periodo"], sort=False):
        era = grupo["era"].iloc[0]
        codigos = CODIGOS_2025 if era == "cosif_2025" else CODIGOS_PRE2025
        serie = grupo.set_index("cod_cuenta")["valor_publicado"]
        fila = {"cod_inst": cod, "periodo": periodo, "era": era}
        for nombre, codigo in codigos.items():
            # en era vieja puede haber códigos duplicados (sub-rubros): tomar el mayor
            fila[nombre] = serie.get(codigo, np.nan)
        filas.append(fila)
    return pd.DataFrame(filas)


def _ttm(tabla: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas *_ttm: suma de 4 trimestres consecutivos (NaN si falta alguno)."""
    tabla = tabla.sort_values(["cod_inst", "periodo"]).reset_index(drop=True)
    serie_periodo = tabla.set_index(["cod_inst", "periodo"])
    for titulo in TITULOS_TTM:
        destino = titulo.removesuffix("_q") + "_ttm"
        serie = serie_periodo[titulo]
        valores: list[float] = []
        for cod, periodo in zip(tabla["cod_inst"], tabla["periodo"]):
            acumulado = 0.0
            ok = True
            p = periodo
            for _ in range(4):
                v = serie.get((cod, p))
                if v is None or pd.isna(v):
                    ok = False
                    break
                acumulado += float(v)
                prev = _periodo_prev(p)
                if prev is None:
                    ok = False
                    break
                p = prev
            valores.append(acumulado if ok else np.nan)
        tabla[destino] = valores
    return tabla


def _razones(tabla: pd.DataFrame) -> pd.DataFrame:
    """Métricas derivadas (razones, TTM, crecimientos y cuotas)."""
    tabla = tabla.sort_values(["cod_inst", "periodo"]).reset_index(drop=True)

    def _prev_valor(columna: str, cod: str, periodo: str, pasos: int) -> float:
        p = periodo
        for _ in range(pasos):
            p = _periodo_prev(p)
            if p is None:
                return np.nan
        mascara = (tabla["cod_inst"] == cod) & (tabla["periodo"] == p)
        fila = tabla[mascara]
        return fila[columna].iloc[0] if len(fila) else np.nan

    # crédito total por era
    nueva = tabla["era"] == "cosif_2025"
    tabla["credito_total"] = np.where(
        nueva,
        tabla[["credito_liquido", "arrendamento", "outras_concessao", "pagos_receber"]].sum(axis=1, min_count=2),
        tabla[["credito_liquido", "arrendamento", "outras_concessao"]].sum(axis=1, min_count=2),
    )

    # PL / ativo medios (t-4 y t)
    tabla["pl_medio_ttm"] = np.nan
    tabla["ativo_medio_ttm"] = np.nan
    for i, fila in tabla.iterrows():
        cod, periodo = fila["cod_inst"], fila["periodo"]
        pl_prev = _prev_valor("patrimonio_liquido", cod, periodo, 4)
        at_prev = _prev_valor("ativo_total", cod, periodo, 4)
        tabla.at[i, "pl_medio_ttm"] = np.nanmean([fila["patrimonio_liquido"], pl_prev]) if pd.notna(pl_prev) else np.nan
        tabla.at[i, "ativo_medio_ttm"] = np.nanmean([fila["ativo_total"], at_prev]) if pd.notna(at_prev) else np.nan

    tabla["roe_ttm"] = tabla["lucro_liquido_ttm"] / tabla["pl_medio_ttm"]
    tabla["roa_ttm"] = tabla["lucro_liquido_ttm"] / tabla["ativo_medio_ttm"]
    tabla["margem_intermediacao_ttm"] = (
        tabla[["resultado_intermediacao_financeira_ttm", "resultado_transacoes_pagamento_ttm"]].sum(axis=1)
        / tabla["ativo_medio_ttm"]
    )
    # costo del riesgo: ECL TTM sobre cartera total (era nueva); si no, cartera líquida
    tabla["costo_riesgo_ttm"] = (
        -tabla["provisoes_credito_ttm"] / tabla["credito_total"].where(tabla["credito_total"] > 0)
    )
    tabla["cobertura_ecl"] = -tabla["ecl_saldo"] / tabla["credito_bruto"].where(tabla["credito_bruto"] > 0)
    receitas = (
        tabla[["rendas_tarifas_ttm", "rendas_servicos_ttm", "resultado_intermediacao_financeira_ttm",
               "resultado_transacoes_pagamento_ttm"]].sum(axis=1)
    )
    despesas = tabla[["despesas_pessoal_ttm", "despesas_administrativas_ttm"]].sum(axis=1)
    tabla["eficiencia_ttm"] = np.where(receitas > 0, -despesas / receitas, np.nan)

    # crecimientos a/a (vs mismo trimestre año anterior).
    # Si la base es cero el crecimiento no existe: NaN, nunca inf. Un inf
    # rompe el JSON de la API y no es un dato financiero válido.
    def _crecimiento(origen: str, cod: str, periodo: str, valor: float) -> float:
        if pd.isna(valor):
            return np.nan
        previo = _prev_valor(origen, cod, periodo, 4)
        if pd.isna(previo) or previo == 0:
            return np.nan
        return float(valor) / float(previo) - 1

    for origen, destino in [
        ("ativo_total", "ativo_aa"),
        ("depositos", "depositos_aa"),
        ("credito_total", "credito_aa"),
        ("lucro_liquido_ttm", "lucro_ttm_aa"),
    ]:
        tabla[destino] = [
            _crecimiento(origen, cod, periodo, v)
            for cod, periodo, v in zip(tabla["cod_inst"], tabla["periodo"], tabla[origen])
        ]

    # cuotas de mercado dentro del panel presente en el trimestre
    for origen, destino in [("ativo_total", "share_ativo"), ("depositos", "share_depositos"),
                            ("credito_total", "share_credito")]:
        totales = tabla.groupby("periodo")[origen].transform(lambda s: s[s > 0].sum())
        tabla[destino] = np.where(totales > 0, tabla[origen] / totales, np.nan)
    return tabla


def _principal() -> pd.DataFrame:
    hechos = _cargar_hechos()
    resultados = pd.read_parquet(CARPETA_BANCOS / "bank_resultados.parquet")
    instituciones = pd.read_parquet(CARPETA_BANCOS / "bank_instituciones.parquet")

    tabla = _pivotar_stocks(hechos)
    flujos = resultados[list({FLUJOS[k] for k in FLUJOS} | {"cod_inst", "periodo"})].copy()
    flujos = flujos.rename(columns={v: k for k, v in FLUJOS.items()})
    tabla = tabla.merge(flujos, on=["cod_inst", "periodo"], how="left")

    tabla = _ttm(tabla)
    tabla = _razones(tabla)

    dim = instituciones[["cod_inst", "nombre_corto", "categoria", "tcb", "segmento", "situacion"]]
    tabla = tabla.merge(dim, on="cod_inst", how="left")

    fecha = pd.to_datetime(tabla["periodo"], format="%Y%m") + pd.offsets.MonthEnd(0)
    tabla.insert(1, "fecha", fecha)
    return tabla


def _salidas(tabla: pd.DataFrame) -> None:
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    largas: list[pd.DataFrame] = []
    for columna in tabla.columns:
        if columna in {"cod_inst", "periodo", "fecha", "era", "nombre_corto", "categoria",
                       "tcb", "segmento", "situacion"}:
            continue
        parcial = tabla[["periodo", "fecha", "cod_inst", "nombre_corto", "categoria", columna]].copy()
        parcial.columns = ["periodo", "fecha", "cod_inst", "nombre_corto", "categoria", "valor"]
        parcial["metrica"] = columna
        largas.append(parcial.dropna(subset=["valor"]))
    largo = pd.concat(largas, ignore_index=True)
    largo = largo[["periodo", "fecha", "cod_inst", "nombre_corto", "categoria", "metrica", "valor"]]
    largo.to_parquet(CARPETA_SALIDA / "metricas_bancos.parquet", index=False)
    tabla.to_csv(CARPETA_SALIDA / "panel_bancos_wide.csv", index=False, encoding="utf-8-sig")
    print(f"metricas_bancos.parquet: {len(largo):,} filas, {largo.metrica.nunique()} métricas, "
          f"{largo.cod_inst.nunique()} bancos, {largo.periodo.nunique()} períodos")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    panel = _principal()
    _salidas(panel)
