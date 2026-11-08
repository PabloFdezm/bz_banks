# -*- coding: utf-8 -*-
"""Prepara la capa de métricas del dashboard de bancos (proyecto independiente).

Consume los parquets curados (datos/gold/) y produce una tabla limpia de métricas
en formato largo (una fila por banco × período × métrica) para consumo directo
por la capa visual (HTML/Plotly hoy, Power BI DAX mañana).

Reglas de diseño (fórmulas y códigos en definiciones/metricas_bancos.json, vía registro_metricas.py):
- Solo escopo prudencial.
- Códigos COSIF por era: cosif_2025 (140xxx/141xxx) y cosif_pre2025 (78xxx).
- 'credito_total' = (e)+(f)+(g)+(h) en era nueva; (d)+(e)+(f) en era vieja
  (menos comparable: 'outros créditos' incluye partidas extra).
- Flujos DRE des-acumulados por trimestre (bank_resultados).
- TTM = suma de los 4 trimestres consecutivos que terminan en t (NaN si falta uno).
- ROE/ROA TTM con promedio de patrimônio/ativo entre t-4 y t (2 puntos).
- Cuotas de mercado dentro del panel presente en cada trimestre.
Salidas:
- datos/intermedio/metricas_bancos.parquet  (largo: banco × trimestre × métrica)
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import almacen as A
import periodos as PER
import registro_metricas as R



def _cargar_hechos() -> pd.DataFrame:
    df = pd.read_parquet(A.GOLD / "bank_hechos.parquet")
    df = df[df.escopo == "prudencial"].copy()
    # stocks: solo informes 2 (ativo) y 3 (passivo); el informe 4 trae memos con
    # códigos repetidos (p. ej. 140220) que contaminarían el pivote
    informes = df["num_informe"].isin([2, 3])
    df = df[informes].drop_duplicates(["cod_inst", "periodo", "cod_cuenta"], keep="first")
    df["valor_publicado"] = pd.to_numeric(df["valor_publicado"], errors="coerce")
    return df


def _pivotar_stocks(hechos: pd.DataFrame) -> pd.DataFrame:
    """Convierte los códigos COSIF por era en columnas de métricas."""
    filas = []
    for (cod, periodo), grupo in hechos.groupby(["cod_inst", "periodo"], sort=False):
        era = grupo["era"].iloc[0]
        codigos = R.CODIGOS_COSIF[era]
        serie = grupo.set_index("cod_cuenta")["valor_publicado"]
        fila = {"cod_inst": cod, "periodo": periodo, "era": era}
        for nombre, codigo in codigos.items():
            fila[nombre] = serie.get(codigo, np.nan)
        filas.append(fila)
    return pd.DataFrame(filas)


def _ttm(tabla: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas *_ttm: suma de 4 trimestres consecutivos (NaN si falta alguno)."""
    tabla = tabla.sort_values(["cod_inst", "periodo"]).reset_index(drop=True)
    serie_periodo = tabla.set_index(["cod_inst", "periodo"])
    for titulo in R.TITULOS_TTM:
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
                p = PER.previo(p)
            valores.append(acumulado if ok else np.nan)
        tabla[destino] = valores
    return tabla


def _razones(tabla: pd.DataFrame) -> pd.DataFrame:
    """Métricas derivadas (razones, TTM, crecimientos y cuotas)."""
    tabla = tabla.sort_values(["cod_inst", "periodo"]).reset_index(drop=True)

    def _prev_valor(columna: str, cod: str, periodo: str, pasos: int) -> float:
        p = PER.previo(periodo, pasos)
        mascara = (tabla["cod_inst"] == cod) & (tabla["periodo"] == p)
        fila = tabla[mascara]
        return fila[columna].iloc[0] if len(fila) else np.nan

    nueva = tabla["era"] == "cosif_2025"
    tabla["credito_total"] = np.where(
        nueva,
        tabla[["credito_liquido", "arrendamento", "outras_concessao", "pagos_receber"]].sum(axis=1, min_count=2),
        tabla[["credito_liquido", "arrendamento", "outras_concessao"]].sum(axis=1, min_count=2),
    )

    # Medio de 12 meses: (t + t−4) / 2, con los dos extremos; si falta uno, vacío.
    for nivel, medio in (("patrimonio_liquido", "pl_medio_ttm"), ("ativo_total", "ativo_medio_ttm")):
        previo = [_prev_valor(nivel, cod, periodo, 4) for cod, periodo in zip(tabla["cod_inst"], tabla["periodo"])]
        tabla[medio] = (tabla[nivel] + np.asarray(previo, dtype=float)) / 2

    for metrica, r in R.RAZONES.items():   # las que se calculan con lo que hay en la tabla
        if all(c in tabla.columns for c in r["num"] + r["den"]):
            tabla[metrica] = R.valor_banco(tabla, metrica)

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

    for destino, origen in R.CRECIMIENTOS.items():
        tabla[destino] = [
            _crecimiento(origen, cod, periodo, v)
            for cod, periodo, v in zip(tabla["cod_inst"], tabla["periodo"], tabla[origen])
        ]
        if destino in R.VACIAS_EN_QUIEBRE_2025:   # el saldo cambia de definición en 2025-T1 (spec/08 punto 6)
            tabla.loc[PER.cruza_quiebre(tabla["periodo"], 4).to_numpy(), destino] = np.nan

    for origen, destino in [("ativo_total", "share_ativo"), ("depositos", "share_depositos"),
                            ("credito_total", "share_credito")]:
        totales = tabla.groupby("periodo")[origen].transform(lambda s: s[s > 0].sum())
        tabla[destino] = np.where(totales > 0, tabla[origen] / totales, np.nan)
    return tabla


def _principal() -> pd.DataFrame:
    hechos = _cargar_hechos()
    resultados = pd.read_parquet(A.GOLD / "bank_resultados.parquet")
    instituciones = pd.read_parquet(A.GOLD / "bank_instituciones.parquet")

    tabla = _pivotar_stocks(hechos)
    flujos = resultados[["cod_inst", "periodo", *R.FLUJOS.values()]].copy()
    flujos = flujos.rename(columns={v: k for k, v in R.FLUJOS.items()})
    tabla = tabla.merge(flujos, on=["cod_inst", "periodo"], how="left")

    tabla = _ttm(tabla)
    tabla = _razones(tabla)

    dim = instituciones[["cod_inst", "nombre_corto", "categoria", "tcb", "segmento", "situacion"]]
    tabla = tabla.merge(dim, on="cod_inst", how="left")

    tabla.insert(1, "fecha", PER.fin_de_mes(tabla["periodo"]))
    return tabla


def _salidas(tabla: pd.DataFrame) -> None:
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
    A.escribir_parquet(largo, A.INTERMEDIO / "metricas_bancos.parquet")
    print(f"metricas_bancos.parquet: {len(largo):,} filas, {largo.metrica.nunique()} métricas, "
          f"{largo.cod_inst.nunique()} bancos, {largo.periodo.nunique()} períodos")


def main(argv: list[str] | None = None) -> int:
    _salidas(_principal())
    return 0


if __name__ == "__main__":
    sys.exit(main())
