# -*- coding: utf-8 -*-
# Generado por Muse Spark (muse-spark), asistente de IA — 2026-10-20.
"""Verificador de solo lectura del pipeline del dashboard de bancos.

POR QUÉ EXISTE
--------------
El dashboard no calcula finanzas: consume parquets ya preparados. Un error en
`metricas_bancos.parquet` o en los derivados de crédito se ve como un gráfico
raro, no como una excepción. Este script pone las comprobaciones estructurales
antes de promover un trimestre nuevo y sirve como *dry run*: no escribe nada.

Comprueba:
- `metricas_bancos.parquet`: columnas, nulos, duplicados, fechas, períodos
  trimestrales continuos, cobertura mínima, cuotas de mercado y la identidad
  de crédito total (si está disponible `panel_bancos_wide.csv`).
- `cre_panorama.parquet` y `cre_calidad.parquet`: contrato que consume la API,
  duplicados y períodos.
- `validacion.json`: claves, números y `dif_pct` calculado.
- Opcionalmente, compara un candidato de staging contra el parquet actual.

No audita PDFs ni reemplaza `tests/auditoria/auditar_fuentes.py`; con
`--auditoria` lo ejecuta como una puerta más. Los PDFs son otra fuente, con
estados explícitos (`verificado`, `aproximado_press_release`, etc.).

Uso desde la raíz del repo:

    python herramientas/verificar_gold.py
    python herramientas/verificar_gold.py --json
    python herramientas/verificar_gold.py --comparar bancos_web/staging/202609/metricas.parquet
    python herramientas/verificar_gold.py --estricto --auditoria
    python herramientas/verificar_gold.py --gold

Código de salida: 0 si no hay errores (o advertencias con `--estricto`), 1 si
hay algún error. Las advertencias no bloquean por defecto: los saltos de un
banco que sale del panel son datos reales y requieren revisión humana, no un
`assert` ciego.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
METRICAS = RAIZ / "datos" / "intermedio" / "metricas_bancos.parquet"
ANCHO = RAIZ / "datos" / "intermedio" / "panel_bancos_wide.csv"
PANORAMA = RAIZ / "datos" / "intermedio" / "cre_panorama.parquet"
CALIDAD = RAIZ / "datos" / "intermedio" / "cre_calidad.parquet"
VALIDACION = RAIZ / "definiciones" / "validacion_bancos.json"
AUDITORIA = RAIZ / "tests" / "auditoria" / "auditar_fuentes.py"

COLUMNAS_METRICAS = [
    "periodo", "fecha", "cod_inst", "nombre_corto", "categoria", "metrica", "valor",
]
METRICAS_NUCLEO = [
    "ativo_total", "credito_total", "depositos", "credito_bruto", "credito_liquido",
]
METRICAS_CUOTA = ["share_ativo", "share_depositos", "share_credito"]
PATRON_PERIODO = re.compile(r"^\d{4}(03|06|09|12)$")
MIN_BANCOS = 10
MIN_BANCOS_ULTIMO = 20
TOLERANCIA_CUOTA = 1e-6
TOLERANCIA_RELATIVA = 1e-9
TOLERANCIA_ABSOLUTA = 1.0  # R$ 1: absorbe el redondeo binario de valores en R$

TIPOS_CREDITO = {"total", "PF", "PJ"}
COLUMNAS_PANORAMA = [
    "inst_key", "tipo_key", "apilar", "medida", "periodo", "serie",
    "nivel", "participacion", "n_bancos",
]
COLUMNAS_CALIDAD = [
    "inst_key", "tipo_key", "ver", "medida_cal", "periodo", "serie", "valor",
]
CLAVES_PANORAMA = ["inst_key", "tipo_key", "apilar", "medida", "periodo", "serie"]
CLAVES_CALIDAD = ["inst_key", "tipo_key", "ver", "medida_cal", "periodo", "serie"]
CAMPOS_VALIDACION = ("banco", "linea", "periodo", "gaap", "ifdata")


@dataclass
class Resultado:
    """Hallazgos de una verificación; vacío = OK."""

    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    resumen: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errores


def _corto(seq: list[str], n: int = 8) -> str:
    """Formatea una lista sin volcar cientos de elementos en el log."""
    if len(seq) <= n:
        return ", ".join(seq)
    return ", ".join(seq[:n]) + f"… (+{len(seq) - n})"


def _leer_parquet(ruta: Path, etiqueta: str, resultado: Resultado) -> pd.DataFrame | None:
    if not ruta.exists():
        resultado.errores.append(f"{etiqueta}: no existe {ruta}")
        return None
    try:
        return pd.read_parquet(ruta)
    except Exception as exc:  # noqa: BLE001 - el mensaje debe llegar al operador
        resultado.errores.append(f"{etiqueta}: no se pudo leer {ruta}: {exc}")
        return None


def _leer_csv(ruta: Path, etiqueta: str, resultado: Resultado) -> pd.DataFrame | None:
    if not ruta.exists():
        resultado.errores.append(f"{etiqueta}: no existe {ruta}")
        return None
    try:
        return pd.read_csv(ruta)
    except Exception as exc:  # noqa: BLE001
        resultado.errores.append(f"{etiqueta}: no se pudo leer {ruta}: {exc}")
        return None


def _leer_json(ruta: Path, etiqueta: str, resultado: Resultado) -> Any | None:
    if not ruta.exists():
        resultado.errores.append(f"{etiqueta}: no existe {ruta}")
        return None
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        resultado.errores.append(f"{etiqueta}: JSON inválido ({exc})")
        return None


def _columnas(df: pd.DataFrame, requeridas: list[str], etiqueta: str,
              resultado: Resultado) -> bool:
    faltan = [c for c in requeridas if c not in df.columns]
    if faltan:
        resultado.errores.append(f"{etiqueta}: faltan columnas {faltan}")
        return False
    return True


def _trimestres(desde: str, hasta: str) -> list[str]:
    """Lista de etiquetas AAAAMM entre dos trimestres, ambos inclusive."""
    inicio = pd.Period(year=int(desde[:4]), quarter=int(desde[4:]) // 3, freq="Q")
    fin = pd.Period(year=int(hasta[:4]), quarter=int(hasta[4:]) // 3, freq="Q")
    return [f"{p.year}{p.quarter * 3:02d}" for p in pd.period_range(inicio, fin, freq="Q")]


def _periodos_validos(serie: pd.Series, etiqueta: str, resultado: Resultado) -> list[str]:
    """Devuelve solo etiquetas válidas; las inválidas se reportan y no se usan
    para calcular el calendario (evita un ValueError en el medio del chequeo)."""
    valores = serie.astype(str)
    validos = {v for v in valores if PATRON_PERIODO.match(v)}
    malos = sorted(set(valores) - validos)
    if malos:
        resultado.errores.append(f"{etiqueta}: períodos inválidos {_corto(malos)}")
    return sorted(validos)


def _verificar_periodos(periodos: list[str], etiqueta: str,
                        resultado: Resultado) -> None:
    if not periodos:
        resultado.errores.append(f"{etiqueta}: no hay períodos")
        return
    esperados = _trimestres(periodos[0], periodos[-1])
    faltan = [p for p in esperados if p not in set(periodos)]
    if faltan:
        resultado.errores.append(
            f"{etiqueta}: faltan trimestres en el calendario: {_corto(faltan)}"
        )


def verificar_metricas(df: pd.DataFrame, ancho: pd.DataFrame | None = None,
                       etiqueta: str = "metricas") -> Resultado:
    """Comprueba la tabla larga que consume la API del dashboard."""
    r = Resultado()
    if not _columnas(df, COLUMNAS_METRICAS, etiqueta, r):
        return r

    df = df.copy()
    df["periodo"] = df["periodo"].astype(str)
    for columna in COLUMNAS_METRICAS:
        nulos = int(df[columna].isna().sum())
        if nulos:
            r.errores.append(f"{etiqueta}: {nulos} nulos en {columna}")

    periodos = _periodos_validos(df["periodo"], etiqueta, r)
    _verificar_periodos(periodos, etiqueta, r)

    fechas = pd.to_datetime(df["fecha"], errors="coerce")
    malas = fechas.isna() | (fechas.dt.strftime("%Y%m") != df["periodo"]) | ~fechas.dt.is_quarter_end
    if malas.any():
        ejemplos = df.loc[malas, ["periodo", "fecha"]].head(3).to_dict("records")
        r.errores.append(f"{etiqueta}: {int(malas.sum())} fechas no son fin de trimestre: {ejemplos}")

    dup = df.duplicated(["periodo", "cod_inst", "metrica"], keep=False)
    if dup.any():
        ejemplos = df.loc[dup, ["periodo", "cod_inst", "metrica"]].head(3).to_dict("records")
        r.errores.append(f"{etiqueta}: {int(dup.sum())} filas duplicadas: {ejemplos}")

    try:
        valores = pd.to_numeric(df["valor"], errors="coerce")
        malos = ~np.isfinite(valores)
        if malos.any():
            r.errores.append(f"{etiqueta}: {int(malos.sum())} valores no finitos")
    except Exception as exc:  # noqa: BLE001
        r.errores.append(f"{etiqueta}: valor no numérico ({exc})")

    bancos = int(df["cod_inst"].nunique())
    if bancos < MIN_BANCOS:
        r.errores.append(f"{etiqueta}: solo {bancos} bancos (mínimo {MIN_BANCOS})")
    if periodos:
        ultimo = periodos[-1]
        n_ultimo = int(df.loc[df["periodo"] == ultimo, "cod_inst"].nunique())
        if n_ultimo < MIN_BANCOS_ULTIMO:
            r.errores.append(
                f"{etiqueta}: el último período {ultimo} tiene {n_ultimo} bancos "
                f"(mínimo {MIN_BANCOS_ULTIMO})"
            )

        # Un banco puede entrar o salir del panel (adquisición, cambio de
        # perímetro). Eso no es un error estructural, pero sí una alerta que
        # un humano debe mirar antes de promover: un hueco interior o una
        # salida sin explicación puede ser una extracción incompleta.
        ativo = df[df["metrica"] == "ativo_total"]
        for cod, grupo in ativo.groupby("cod_inst"):
            propios = sorted(grupo["periodo"].unique())
            if not propios:
                continue
            huecos = [
                p for p in _trimestres(propios[0], propios[-1]) if p not in set(propios)
            ]
            if huecos:
                r.advertencias.append(
                    f"{etiqueta}: {cod} tiene huecos internos: {_corto(huecos)}"
                )
            if propios[-1] != ultimo:
                r.advertencias.append(
                    f"{etiqueta}: {cod} no reporta el último período {ultimo} "
                    f"(último: {propios[-1]}); confirmar salida del panel"
                )

    nombres = df.groupby("cod_inst")["nombre_corto"].nunique()
    multiple = sorted(nombres[nombres > 1].index.tolist())
    if multiple:
        r.errores.append(f"{etiqueta}: bancos con más de un nombre: {_corto(multiple)}")

    base = set(map(tuple, df.loc[df["metrica"] == "ativo_total",
                                 ["periodo", "cod_inst"]].itertuples(index=False, name=None)))
    if not base:
        r.errores.append(f"{etiqueta}: no hay filas de ativo_total")
    for metrica in METRICAS_NUCLEO:
        claves = set(map(tuple, df.loc[df["metrica"] == metrica,
                                      ["periodo", "cod_inst"]].itertuples(index=False, name=None)))
        faltan = sorted(base - claves)
        if faltan:
            r.errores.append(
                f"{etiqueta}: {len(faltan)} combinaciones sin {metrica}: {_corto([str(x) for x in faltan])}"
            )

    for metrica in METRICAS_CUOTA:
        cuota = df[df["metrica"] == metrica]
        if cuota.empty:
            r.errores.append(f"{etiqueta}: no hay {metrica}")
            continue
        totales = cuota.groupby("periodo")["valor"].sum()
        malos = (totales - 1).abs() > TOLERANCIA_CUOTA
        if malos.any():
            r.errores.append(
                f"{etiqueta}: {int(malos.sum())} períodos con {metrica} que no suma 1: "
                f"{totales[malos].head(3).to_dict()}"
            )

    if ancho is not None:
        r.errores.extend(_verificar_identidad_credito(ancho, etiqueta))

    r.resumen.update({
        "filas": int(len(df)),
        "bancos": bancos,
        "periodos": len(periodos),
        "primer_periodo": periodos[0] if periodos else None,
        "ultimo_periodo": periodos[-1] if periodos else None,
        "metricas": int(df["metrica"].nunique()),
    })
    return r


def _verificar_identidad_credito(ancho: pd.DataFrame,
                                 etiqueta: str = "metricas") -> list[str]:
    """Crédito total = cartera líquida + arrendamiento + otras concesiones (+ pagos)."""
    errores: list[str] = []
    requeridas = [
        "era", "credito_total", "credito_liquido", "arrendamento",
        "outras_concessao", "pagos_receber",
    ]
    faltan = [c for c in requeridas if c not in ancho.columns]
    if faltan:
        errores.append(f"{etiqueta}/ancho: faltan columnas {faltan}")
        return errores
    if ancho["era"].isna().any():
        errores.append(f"{etiqueta}/ancho: hay filas sin era")
        return errores

    nuevo = ancho["era"].eq("cosif_2025")
    calculado = ancho[["credito_liquido", "arrendamento", "outras_concessao"]].sum(
        axis=1, min_count=2
    )
    calculado = calculado.where(
        ~nuevo,
        ancho[["credito_liquido", "arrendamento", "outras_concessao", "pagos_receber"]].sum(
            axis=1, min_count=2
        ),
    )
    total = pd.to_numeric(ancho["credito_total"], errors="coerce")
    calculado = pd.to_numeric(calculado, errors="coerce")
    comparables = total.notna() & calculado.notna()
    residual = (total - calculado).abs()
    tolerancia = TOLERANCIA_ABSOLUTA + calculado.abs() * TOLERANCIA_RELATIVA
    malos = comparables & (residual > tolerancia)
    if malos.any():
        errores.append(
            f"{etiqueta}/ancho: {int(malos.sum())} filas no cumplen "
            f"crédito total = componentes (residuo máx. {residual[malos].max():.4f})"
        )
    return errores


def verificar_credito(panorama: pd.DataFrame, calidad: pd.DataFrame,
                      ultimo_metricas: str | None = None) -> Resultado:
    """Comprueba los dos parquets que alimentan la página Crédito."""
    r = Resultado()
    if not _columnas(panorama, COLUMNAS_PANORAMA, "cre_panorama", r) or not _columnas(
        calidad, COLUMNAS_CALIDAD, "cre_calidad", r
    ):
        return r

    for etiqueta, df, claves, metrica in (
        ("cre_panorama", panorama, CLAVES_PANORAMA, "nivel"),
        ("cre_calidad", calidad, CLAVES_CALIDAD, "valor"),
    ):
        df = df.copy()
        df["periodo"] = df["periodo"].astype(str)
        periodos = _periodos_validos(df["periodo"], etiqueta, r)
        _verificar_periodos(periodos, etiqueta, r)
        dup = df.duplicated(claves, keep=False)
        if dup.any():
            r.errores.append(f"{etiqueta}: {int(dup.sum())} filas duplicadas")
        if "tipo_key" in df and not set(df["tipo_key"].unique()) <= TIPOS_CREDITO:
            r.errores.append(f"{etiqueta}: tipo_key fuera de {sorted(TIPOS_CREDITO)}")
        columnas_obligatorias = [
            "inst_key", "tipo_key", "ver", "medida_cal", "periodo", "serie",
            "valor", "npl_def",
        ] if etiqueta == "cre_calidad" else [
            "inst_key", "tipo_key", "apilar", "medida", "periodo", "serie",
            "nivel", "n_bancos",
        ]
        for columna in columnas_obligatorias:
            if columna in df and df[columna].isna().any():
                r.errores.append(f"{etiqueta}: nulos en {columna}")
        if "n_bancos" in df and (df["n_bancos"] <= 0).any():
            r.errores.append(f"{etiqueta}: n_bancos debe ser positivo")
        if metrica in df:
            try:
                valores = pd.to_numeric(df[metrica], errors="coerce")
                if (~np.isfinite(valores)).any():
                    r.errores.append(f"{etiqueta}: valores no finitos en {metrica}")
            except Exception as exc:  # noqa: BLE001
                r.errores.append(f"{etiqueta}: {metrica} no numérico ({exc})")

    p_pan = set(panorama["periodo"].astype(str))
    p_cal = set(calidad["periodo"].astype(str))
    if p_pan != p_cal:
        r.errores.append(
            "crédito: panorama y calidad no cubren los mismos períodos "
            f"(solo panorama: {_corto(sorted(p_pan - p_cal))}; "
            f"solo calidad: {_corto(sorted(p_cal - p_pan))})"
        )
    ultimo_credito = max(p_pan | p_cal) if (p_pan or p_cal) else None
    if ultimo_metricas and ultimo_credito and ultimo_credito != ultimo_metricas:
        r.advertencias.append(
            f"crédito: último período {ultimo_credito} != métricas {ultimo_metricas}; "
            "puede ser un desfase normal de la fuente"
        )
    r.resumen.update({
        "panorama_filas": int(len(panorama)),
        "calidad_filas": int(len(calidad)),
        "panorama_periodos": len(p_pan),
        "calidad_periodos": len(p_cal),
        "credito_ultimo": ultimo_credito,
    })
    return r


def verificar_validacion(datos: Any) -> Resultado:
    """Comprueba el contrato de la tabla del puente auditado."""
    r = Resultado()
    if not isinstance(datos, list) or not datos:
        r.errores.append("validacion: debe ser una lista no vacía")
        return r
    claves: set[tuple[str, str, str]] = set()
    for n, fila in enumerate(datos, start=1):
        if not isinstance(fila, dict):
            r.errores.append(f"validacion fila {n}: no es un objeto")
            continue
        faltan = [c for c in CAMPOS_VALIDACION if c not in fila]
        if faltan:
            r.errores.append(f"validacion fila {n}: faltan {faltan}")
            continue
        clave = (str(fila["banco"]), str(fila["linea"]), str(fila["periodo"]))
        if clave in claves:
            r.errores.append(f"validacion fila {n}: clave duplicada {clave}")
        claves.add(clave)
        if not PATRON_PERIODO.match(str(fila["periodo"])):
            r.errores.append(f"validacion fila {n}: período inválido {fila['periodo']}")
        try:
            gaap, ifdata = float(fila["gaap"]), float(fila["ifdata"])
        except (TypeError, ValueError):
            r.errores.append(f"validacion fila {n}: gaap/ifdata no numéricos")
            continue
        if not np.isfinite(gaap) or not np.isfinite(ifdata):
            r.errores.append(f"validacion fila {n}: gaap/ifdata no finitos")
        if gaap == 0:
            r.errores.append(f"validacion fila {n}: gaap no puede ser cero")
            continue
        calculada = round(100 * (ifdata - gaap) / gaap, 2)
        if "dif_pct" in fila and abs(float(fila["dif_pct"]) - calculada) > 0.02:
            r.errores.append(
                f"validacion fila {n}: dif_pct={fila['dif_pct']} vs {calculada}"
            )
    r.resumen["validacion_filas"] = len(datos)
    return r


def comparar_metricas(actual: pd.DataFrame, candidato: pd.DataFrame,
                      etiqueta: str = "candidato") -> Resultado:
    """Compara un candidato de staging con el parquet vigente (sin escribirlo)."""
    r = Resultado()
    if not _columnas(actual, COLUMNAS_METRICAS, "actual", r) or not _columnas(
        candidato, COLUMNAS_METRICAS, etiqueta, r
    ):
        return r
    a = actual.copy()
    c = candidato.copy()
    a["periodo"] = a["periodo"].astype(str)
    c["periodo"] = c["periodo"].astype(str)

    p_actual = set(a["periodo"])
    p_cand = set(c["periodo"])
    perdidos = sorted(p_actual - p_cand)
    nuevos = sorted(p_cand - p_actual)
    if perdidos:
        r.errores.append(f"{etiqueta}: pierde períodos del actual: {_corto(perdidos)}")
    if nuevos:
        r.advertencias.append(f"{etiqueta}: agrega períodos: {_corto(nuevos)}")
    if p_cand and p_actual and max(p_cand) < max(p_actual):
        r.errores.append(
            f"{etiqueta}: su último período {max(p_cand)} es anterior al actual {max(p_actual)}"
        )

    b_actual = set(a["cod_inst"])
    b_cand = set(c["cod_inst"])
    faltan = sorted(b_actual - b_cand)
    agregados = sorted(b_cand - b_actual)
    if faltan:
        r.errores.append(f"{etiqueta}: pierde bancos del actual: {_corto(faltan)}")
    if agregados:
        r.advertencias.append(f"{etiqueta}: agrega bancos: {_corto(agregados)}")

    r.resumen.update({
        "candidato_filas": int(len(c)),
        "candidato_bancos": len(b_cand),
        "candidato_periodos": len(p_cand),
        "candidato_ultimo": max(p_cand) if p_cand else None,
    })
    return r


def _ejecutar_auditoria(script: Path) -> Resultado:
    r = Resultado()
    if not script.exists():
        r.errores.append(f"auditoría: no existe {script}")
        return r
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(RAIZ),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    salida = (proc.stdout or "").strip().splitlines()
    if proc.returncode != 0:
        detalle = " | ".join(salida[-3:]) if salida else "sin salida"
        r.errores.append(f"auditoría: falló (código {proc.returncode}): {detalle}")
    r.resumen["auditoria"] = "OK" if proc.returncode == 0 else "falló"
    return r


def verificar_todo(
    metricas: Path = METRICAS,
    ancho: Path = ANCHO,
    panorama: Path = PANORAMA,
    calidad: Path = CALIDAD,
    validacion: Path = VALIDACION,
    comparar: Path | None = None,
    con_auditoria: bool = False,
) -> Resultado:
    """Ejecuta todas las puertas y devuelve un resultado agregado."""
    r = Resultado()
    df_metricas = _leer_parquet(metricas, "metricas", r)
    df_ancho = _leer_csv(ancho, "ancho", r) if ancho.exists() else None
    if not ancho.exists():
        r.advertencias.append(f"ancho: no existe {ancho}; se omite la identidad de crédito")
    if df_metricas is not None:
        parcial = verificar_metricas(df_metricas, df_ancho)
        r.errores.extend(parcial.errores)
        r.advertencias.extend(parcial.advertencias)
        r.resumen.update(parcial.resumen)

    df_pan = _leer_parquet(panorama, "cre_panorama", r)
    df_cal = _leer_parquet(calidad, "cre_calidad", r)
    if df_pan is not None and df_cal is not None:
        ultimo = r.resumen.get("ultimo_periodo")
        parcial = verificar_credito(df_pan, df_cal, ultimo_metricas=ultimo)
        r.errores.extend(parcial.errores)
        r.advertencias.extend(parcial.advertencias)
        r.resumen.update(parcial.resumen)

    datos_validacion = _leer_json(validacion, "validacion", r)
    if datos_validacion is not None:
        parcial = verificar_validacion(datos_validacion)
        r.errores.extend(parcial.errores)
        r.advertencias.extend(parcial.advertencias)
        r.resumen.update(parcial.resumen)

    if comparar is not None:
        df_candidato = _leer_parquet(comparar, "candidato", r)
        if df_metricas is not None and df_candidato is not None:
            # El candidato debe cumplir el mismo contrato que el actual; no
            # alcanza con comparar conjuntos de bancos/períodos.
            parcial = verificar_metricas(df_candidato, None, etiqueta="candidato")
            r.errores.extend(parcial.errores)
            r.advertencias.extend(parcial.advertencias)
            r.resumen.update(parcial.resumen)
            parcial = comparar_metricas(df_metricas, df_candidato)
            r.errores.extend(parcial.errores)
            r.advertencias.extend(parcial.advertencias)
            r.resumen.update(parcial.resumen)

    if con_auditoria:
        parcial = _ejecutar_auditoria(AUDITORIA)
        r.errores.extend(parcial.errores)
        r.advertencias.extend(parcial.advertencias)
        r.resumen.update(parcial.resumen)
    return r


# ---------------------------------------------------------------------------
# Capa gold: tablas bk_* del dashboard de bancos (encargo 59).
#
# POR QUÉ ESTÁ AQUÍ
# -----------------
# Las tablas gold las escriben workers baratos contra el contrato del spec
# (SPEC_DATOS_BANCOS §3), no contra la salida de otro worker. Un error plausible
# (un período corrido, un ratio de grupo con el denominador equivocado, grupos
# que no suman el panel) no hace ruido al escribirse: aparece como un gráfico
# raro en la portada. Estas comprobaciones son la red que lo hace ruidoso antes
# de promover. Siguen siendo de solo lectura: no escriben ni corrigen nada.
#
# Una tabla que todavía no existe es un aviso, no un error: la capa se arma por
# olas. Con --estricto los avisos también fallan, como en el resto.
#
# Supuestos sobre nombres que el spec no fija. Si el preparador usa otros, la
# comprobación falla y hay que decidir cuál cambiar:
#   - bk_manifiesto: columnas tabla, universo y ultimo_corte.
#   - bk_scr: el corte por segmento son las filas con modalidad, porte y uf vacíos.
#   - bk_cartera_totales.parquet (auxiliar; contrato en COLUMNAS_GOLD): cod_inst, periodo,
#     tipo, publicado y exterior, con los totales de los informes 11 + 13.
#   - bk_conducta: columnas mínimas tomadas del texto del spec §3.14 (encargo 71);
#     confirmar cuando el worker de conducta escriba la tabla.
# ---------------------------------------------------------------------------

GOLD = RAIZ / "datos" / "gold"
TABLAS_GOLD = [
    "bk_banco", "bk_metrica", "bk_panel", "bk_grupo", "bk_puente", "bk_manifiesto",
    "bk_roe_arbol", "bk_cartera", "bk_sistema_m", "bk_sistema_q", "bk_scr",
    "bk_exposicion", "bk_sensibilidad", "bk_conducta",
]
COLUMNAS_GOLD = {
    "bk_banco": [
        "cod_inst", "slug", "nombre_corto", "institucion_bcb", "modelo", "segmento_reg",
        "propiedad", "fintech", "segmento_ref", "cotizado", "ticker", "ficha", "color",
        "nota", "primer_periodo", "ultimo_periodo",
    ],
    "bk_metrica": [
        "metrica", "nombre", "nombre_corto", "familia", "unidad", "formato", "signo",
        "universo", "fuente", "definicion", "en_comparador", "en_ficha", "orden",
    ],
    "bk_panel": [
        "cod_inst", "periodo", "fecha", "trimestre", "metrica", "valor", "valor_t1",
        "valor_t4", "d_tt", "d_aa", "p10_grupo", "p50_grupo", "p90_grupo", "pct_grupo",
        "pct_panel", "rank_panel", "rank_panel_t4",
    ],
    "bk_grupo": [
        "optica", "grupo", "periodo", "fecha", "trimestre", "metrica", "valor",
        "mediana", "p25", "p75", "n_bancos", "valor_aa",
    ],
    "bk_cartera": [
        "cod_inst", "periodo", "fecha", "trimestre", "tipo", "modalidad", "saldo",
        "vencido15", "npl15", "peso_banco", "cuota_modalidad", "d_cuota_aa",
    ],
    "bk_roe_arbol": ["entidad", "periodo", "linea", "orden", "valor", "mediana_grupo"],
    "bk_sistema_m": ["fecha", "serie_id", "unidad", "valor", "p10", "p50", "p90", "es_ultimo"],
    "bk_sistema_q": ["fecha", "serie_id", "unidad", "valor", "p10", "p50", "p90", "es_ultimo"],
    "bk_scr": [
        "fecha", "segmento_inst", "cliente", "modalidad", "porte", "uf", "carteira_ativa",
        "vencido_15_90", "vencido_90", "inadimplencia_brl", "ativo_problematico",
        "tasa_inad", "tasa_ap",
    ],
    "bk_manifiesto": [
        "tabla", "filas", "columnas", "rango", "sha256", "producido_por", "universo",
        "ultimo_corte",
    ],
    "bk_puente": ["banco", "linea", "periodo", "gaap", "ifdata", "dif_pct"],
    "bk_exposicion": [
        "cod_inst", "periodo", "fecha", "trimestre", "cobertura", "mora_implicita",
        "npl_observado", "brecha_pp", "efecto_mix_pp", "efecto_mora_pp",
        "d_mora_implicita_aa_pp", "quiebre_2025",
    ],
    "bk_sensibilidad": [
        "cod_inst", "modelo", "beta_nim_cdi", "ic_inf", "ic_sup", "r2", "n_trimestres",
        "excluidos",
    ],
    "bk_cartera_totales": ["cod_inst", "periodo", "tipo", "publicado", "exterior", "brasil"],
    "bk_conducta": ["cod_inst", "periodo", "trimestre", "reclamos_por_millon", "clientes"],
}
CLAVES_GOLD = {
    "bk_banco": ["cod_inst"],
    "bk_metrica": ["metrica"],
    "bk_panel": ["cod_inst", "periodo", "metrica"],
    "bk_grupo": ["optica", "grupo", "periodo", "metrica"],
    "bk_cartera": ["cod_inst", "periodo", "tipo", "modalidad"],
    "bk_roe_arbol": ["entidad", "periodo", "linea"],
    "bk_sistema_m": ["fecha", "serie_id"],
    "bk_sistema_q": ["fecha", "serie_id"],
    "bk_scr": ["fecha", "segmento_inst", "cliente", "modalidad", "porte", "uf"],
    "bk_manifiesto": ["tabla", "universo"],
    "bk_puente": ["banco", "linea", "periodo"],
    "bk_exposicion": ["cod_inst", "periodo"],
    "bk_sensibilidad": ["cod_inst"],
    "bk_cartera_totales": ["cod_inst", "periodo", "tipo"],
    "bk_conducta": ["cod_inst", "periodo"],
}
# Fragmentos de nombre de columna que delatan datos con licencia (Bloomberg, consenso...).
PROHIBIDAS_LICENCIA = ("px_", "pbv", "pe_", "bbg", "bloomberg", "consenso", "target")
N_BANCOS_GOLD = 34
MODELOS_GOLD = frozenset({"Grandes", "Digitales", "Medianos y nicho", "Pagos", "Desarrollo"})
SIGNOS_GOLD = frozenset({"mejora_sube", "mejora_baja", "neutro"})
UNIDADES_SISTEMA = frozenset({"fraccion", "pp"})
MIN_BANCOS_GRUPO = 3          # percentiles de grupo solo con n >= 3 (spec §3.3)
MUESTRA_T4 = 50               # filas al azar para contrastar valor_t4
SEMILLA_MUESTRA = 0           # la muestra es reproducible
TOL_SUMA_ROA = 1e-6           # Σ líneas 1–9 del árbol = ROA
TOL_ROE = 1e-3                # ROA × apalancamiento = ROE (0,1 pp)
TOL_RANGO = 1e-9              # holgura numérica para ratios dentro de [mín, máx]
TOL_TOTAL_CARTERA = 0.005     # = TOLERANCIA_TOTAL de preparar_credito_paginas_powerbi.py
COBERTURA_MIN_GOLD = 0.5      # bk_exposicion: bajo esto la mora implícita queda nula (SPEC §3.6; A3)
MIN_TRIMESTRES_BETA = 16      # bk_sensibilidad: con n < 16, beta, IC y R² quedan nulos (SPEC §3.8)
TOL_EFECTOS = 1e-9            # efecto mix + efecto mora = Δ mora implícita a/a (pp)
PERIODO_SIN_CARTERA = "202412"  # regla 6: 2024-T4 no tiene cartera por modalidad
MIN_OBS_SERIE = 24
# Series con menos observaciones que MIN_OBS_SERIE, aceptadas por el arquitecto
# (encargo 59). El valor es el mínimo que sí debe cumplir.
EXCEPCIONES_OBS = {"bk_sistema_q": {"selic_real_exante": 23,
                                    # Focus empieza en 2021-01 (encargo 78c): 23 trimestres a 2026-T3
                                    "ipca_esperado_12m": 20, "icc_real_exante": 20}}
# Tasa de inadimplencia SCR de jun-2026 por segmento, en unidad del modelo (encargo 59).
# Referencia jun-2026 sobre el crudo bajado el 2026-10-23. La de agosto (Financeira 12,31 %, Fintech 16,42 %)
# quedó obsoleta: el BCB reclasificó segmentos (apareció «Instituição de pagamento») y sirve el dato revisado.
# Banco y Cooperativa no cambiaron. Decisión del arquitecto, revisión del encargo 67 (2026-11-03).
TASA_JUN26 = {"Banco": 0.0442, "Financeira": 0.1223, "Fintech": 0.1774, "Cooperativa": 0.0520}
TOL_TASA = 1e-4               # ±0,01 pp
TOTAL_PANEL = "Total panel"
# Dentro de cada óptica hay una fila «Todos los grupos» (el total de la óptica).
TODOS_LOS_GRUPOS = "Todos los grupos"
# Variaciones a/a de un flujo con signo: Σ(t) / Σ(t−4) − 1 no es un promedio ponderado
# de las variaciones de los bancos, así que el rango mín.–máx. no aplica.
METRICAS_SIN_RANGO = frozenset({"lucro_ttm_aa"})
# Cuotas (aditivas: suman 1 por óptica), HHI y top5 (sumas sobre el panel, no promedios):
# el rango mín.–máx. de los bancos no les aplica.
PREFIJOS_SIN_RANGO = ("share_", "hhi_", "top5_")
ETIQUETA_PROPIEDAD = {
    "1": "Público", "2": "Privado nacional", "3": "Privado extranjero",
    "Público": "Público", "Privado nacional": "Privado nacional",
    "Privado extranjero": "Privado extranjero",
}
ETIQUETA_FINTECH = {"Fintech": "Fintechs", "Tradicional": "Tradicionales"}


def _faltan(df: pd.DataFrame, requeridas: list[str]) -> bool:
    """Silencioso: el error de contrato lo reporta la comprobación general."""
    return any(c not in df.columns for c in requeridas)


def _acumular(destino: Resultado, parcial: Resultado) -> None:
    destino.errores.extend(parcial.errores)
    destino.advertencias.extend(parcial.advertencias)
    destino.resumen.update(parcial.resumen)


def _texto(valor: Any) -> str | None:
    """Texto de una celda de categoría: 1.0 y 1 cuentan como «1»; nulo, como None."""
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float, np.integer, np.floating)) and float(valor).is_integer():
        return str(int(valor))
    return str(valor)


def _fin_de_trimestre(periodo: str) -> pd.Timestamp:
    p = pd.Period(year=int(periodo[:4]), quarter=int(periodo[4:]) // 3, freq="Q")
    return pd.Timestamp(p.end_time.date())


def _restar_trimestres(periodo: str, n: int) -> str:
    p = pd.Period(year=int(periodo[:4]), quarter=int(periodo[4:]) // 3, freq="Q") - n
    return f"{p.year}{p.quarter * 3:02d}"


def _iguales(a: Any, b: Any) -> bool:
    if pd.isna(a) or pd.isna(b):
        return bool(pd.isna(a)) and bool(pd.isna(b))
    return bool(np.isclose(float(a), float(b), rtol=1e-9, atol=1e-12))


def _sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _panel_numerico(panel: pd.DataFrame) -> pd.DataFrame:
    return panel.assign(
        periodo=panel["periodo"].astype(str),
        metrica=panel["metrica"].astype(str),
        valor=pd.to_numeric(panel["valor"], errors="coerce"),
    )


def _grupos_por_banco(banco: pd.DataFrame) -> dict[str, pd.Series]:
    """Grupo de cada banco (indexado por cod_inst) en las ópticas que conocemos.

    Los textos de grupo son los de datos/intermedio/cre_institucion.parquet; la columna de bk_banco
    que los produce es la inferencia documentada en el encabezado de este bloque.
    """
    idx = banco.drop_duplicates("cod_inst").set_index("cod_inst")
    return {
        "Modelo de negocio": idx["modelo"].map(_texto),
        "Propiedad": idx["propiedad"].map(lambda v: ETIQUETA_PROPIEDAD.get(_texto(v) or "")),
        "Segmento regulatorio": idx["segmento_reg"].map(lambda v: _texto(v) or "Sin segmento"),
        "Tradicional vs Fintech": idx["fintech"].map(lambda v: ETIQUETA_FINTECH.get(_texto(v) or "")),
    }


def _chequear_rango(filas: pd.DataFrame, optica: str, etiqueta: str, r: Resultado) -> None:
    """Un ratio de grupo es un promedio ponderado de sus bancos: cae entre su mín. y máx."""
    valor = filas["valor"]
    sin_bancos = filas["min"].isna() & valor.notna()
    if sin_bancos.any():
        r.errores.append(
            f"{etiqueta}: {int(sin_bancos.sum())} ratios de «{optica}» con valor y sin bancos con dato en bk_panel"
        )
    fuera = filas["min"].notna() & (
        (valor < filas["min"] - TOL_RANGO) | (valor > filas["max"] + TOL_RANGO)
    )
    if fuera.any():
        r.errores.append(
            f"{etiqueta}: {int(fuera.sum())} ratios de «{optica}» fuera del rango mínimo–máximo de sus bancos"
        )


def _comprobar_gold_general(nombre: str, df: pd.DataFrame, hoy: pd.Timestamp) -> Resultado:
    """Lo que vale para toda tabla bk_*: contrato, claves, infinitos, fechas y licencias."""
    r = Resultado()
    if nombre in COLUMNAS_GOLD:
        _columnas(df, COLUMNAS_GOLD[nombre], nombre, r)
    else:
        r.advertencias.append(
            f"{nombre}: sin contrato de columnas en verificar.py; solo comprobaciones generales"
        )
    claves = [c for c in CLAVES_GOLD.get(nombre, []) if c in df.columns]
    if claves:
        dup = df.duplicated(claves, keep=False)
        if dup.any():
            r.errores.append(f"{nombre}: {int(dup.sum())} filas repetidas en la clave {claves}")
    numericas = df.select_dtypes(include="number")
    infinitas = [c for c in numericas.columns if np.isinf(numericas[c].to_numpy(dtype=float)).any()]
    if infinitas:
        r.errores.append(f"{nombre}: valores infinitos en {infinitas}")
    if "fecha" in df.columns:
        fecha = pd.to_datetime(df["fecha"], errors="coerce")
        if (fecha.isna() & df["fecha"].notna()).any():
            r.errores.append(f"{nombre}: fechas que no se pueden leer")
        posteriores = int((fecha.dt.normalize() > hoy).sum())
        if posteriores:
            r.errores.append(f"{nombre}: {posteriores} fechas posteriores a hoy ({hoy.date()})")
    for columna in ("periodo", "primer_periodo", "ultimo_periodo"):
        if columna not in df.columns:
            continue
        valores = df[columna].dropna().astype(str).unique()
        formato = [v for v in valores if not PATRON_PERIODO.match(v)]
        if formato:
            r.errores.append(f"{nombre}: {columna} con formato inválido: {_corto(sorted(formato))}")
        futuros = [v for v in valores if PATRON_PERIODO.match(v) and _fin_de_trimestre(v) > hoy]
        if futuros:
            r.errores.append(f"{nombre}: {columna} posterior a hoy: {_corto(sorted(futuros))}")
    licencia = [str(c) for c in df.columns if any(p in str(c).lower() for p in PROHIBIDAS_LICENCIA)]
    if licencia:
        r.errores.append(f"{nombre}: columnas con datos de licencia (no se publican): {licencia}")
    return r


def verificar_gold_banco(banco: pd.DataFrame, etiqueta: str = "bk_banco") -> Resultado:
    """Dimensión de bancos: 34 filas, modelo dentro de los cinco válidos, slug único."""
    r = Resultado()
    if _faltan(banco, COLUMNAS_GOLD["bk_banco"]):
        return r
    if len(banco) != N_BANCOS_GOLD:
        r.errores.append(f"{etiqueta}: {len(banco)} filas (se esperaban {N_BANCOS_GOLD})")
    nulos = int(banco["modelo"].isna().sum())
    if nulos:
        r.errores.append(f"{etiqueta}: {nulos} bancos sin modelo")
    fuera = sorted(set(banco["modelo"].dropna().astype(str)) - MODELOS_GOLD)
    if fuera:
        r.errores.append(f"{etiqueta}: modelo fuera de {sorted(MODELOS_GOLD)}: {_corto(fuera)}")
    slug = banco["slug"].dropna().astype(str)
    repetidos = sorted(set(slug[slug.duplicated(keep=False)]))
    if repetidos:
        r.errores.append(f"{etiqueta}: slug repetido: {_corto(repetidos)}")
    return r


def verificar_gold_metrica(metrica: pd.DataFrame, panel: pd.DataFrame | None = None,
                           etiqueta: str = "bk_metrica") -> Resultado:
    """Diccionario de métricas: signo válido y toda métrica de bk_panel definida."""
    r = Resultado()
    if _faltan(metrica, COLUMNAS_GOLD["bk_metrica"]):
        return r
    signos = metrica["signo"]
    fuera = sorted(set(signos[~signos.isin(SIGNOS_GOLD)].astype(str)))
    if fuera:
        r.errores.append(f"{etiqueta}: signo fuera de {sorted(SIGNOS_GOLD)}: {_corto(fuera)}")
    if panel is not None and not _faltan(panel, ["metrica"]):
        usadas = set(panel["metrica"].dropna().astype(str))
        definidas = set(metrica["metrica"].dropna().astype(str))
        faltan = sorted(usadas - definidas)
        if faltan:
            r.errores.append(f"{etiqueta}: métricas de bk_panel sin fila: {_corto(faltan)}")
    return r


def verificar_gold_panel(panel: pd.DataFrame, banco: pd.DataFrame | None = None,
                         etiqueta: str = "bk_panel") -> Resultado:
    """Hechos banco × trimestre × métrica: percentiles con n >= 3, pct en [0, 1] y valor_t4."""
    r = Resultado()
    if _faltan(panel, COLUMNAS_GOLD["bk_panel"]):
        return r
    panel = panel.reset_index(drop=True)
    for columna in ("pct_grupo", "pct_panel"):
        pct = pd.to_numeric(panel[columna], errors="coerce")
        n = int(((pct < 0) | (pct > 1)).sum())
        if n:
            r.errores.append(f"{etiqueta}: {n} valores de {columna} fuera de [0, 1]")

    periodo = panel["periodo"].astype(str)
    valor = pd.to_numeric(panel["valor"], errors="coerce")
    if banco is None:
        r.advertencias.append(
            f"{etiqueta}: sin bk_banco no se comprueba que los percentiles de grupo tengan n >= {MIN_BANCOS_GRUPO}"
        )
    else:
        mapa = banco.drop_duplicates("cod_inst").set_index("cod_inst")["modelo"]
        modelo = panel["cod_inst"].map(mapa)
        n_grupo = (
            pd.DataFrame({"p": periodo, "m": panel["metrica"].astype(str), "g": modelo,
                          "c": valor.notna()})
            .groupby(["p", "m", "g"], dropna=False)["c"].transform("sum")
        )
        for columna in ("p10_grupo", "p50_grupo", "p90_grupo"):
            con_pct = pd.to_numeric(panel[columna], errors="coerce").notna()
            n = int((con_pct & (n_grupo < MIN_BANCOS_GRUPO)).sum())
            if n:
                r.errores.append(
                    f"{etiqueta}: {n} filas con {columna} aunque el grupo tiene menos de "
                    f"{MIN_BANCOS_GRUPO} bancos con dato"
                )

    base = pd.DataFrame({"cod": panel["cod_inst"], "p": periodo,
                         "m": panel["metrica"].astype(str), "v": valor})
    base = base.drop_duplicates(["cod", "p", "m"])
    ref = {(a, b, c): d for a, b, c, d in base.itertuples(index=False, name=None)}
    muestra = panel.assign(periodo=periodo, valor=valor).sample(
        n=min(MUESTRA_T4, len(panel)), random_state=SEMILLA_MUESTRA
    )
    t4 = pd.to_numeric(muestra["valor_t4"], errors="coerce")
    malos, ejemplo = 0, None
    for cod, per, met, real in muestra[["cod_inst", "periodo", "metrica"]].assign(t4=t4).itertuples(
        index=False, name=None
    ):
        esperado = ref.get((cod, _restar_trimestres(per, 4), str(met)), np.nan)
        if not _iguales(esperado, real):
            malos += 1
            ejemplo = ejemplo or (cod, per, str(met))
    if malos:
        r.errores.append(
            f"{etiqueta}: valor_t4 no coincide con el valor de t−4 en {malos} de {len(muestra)} "
            f"filas de la muestra (p. ej. {ejemplo})"
        )
    return r


def verificar_gold_grupo(grupo: pd.DataFrame, panel: pd.DataFrame | None = None,
                         banco: pd.DataFrame | None = None, metrica: pd.DataFrame | None = None,
                         etiqueta: str = "bk_grupo") -> Resultado:
    """Agregados por óptica: Total panel = Σ bancos, ópticas que suman el total, ratios en rango."""
    r = Resultado()
    if _faltan(grupo, COLUMNAS_GOLD["bk_grupo"]):
        return r
    g = grupo.reset_index(drop=True).assign(
        periodo=grupo["periodo"].astype(str),
        metrica=grupo["metrica"].astype(str),
        valor=pd.to_numeric(grupo["valor"], errors="coerce"),
    )
    if not (g["optica"] == TOTAL_PANEL).any():
        r.errores.append(f"{etiqueta}: no hay filas de la óptica «{TOTAL_PANEL}»")
        return r
    if metrica is None:
        r.advertencias.append(
            f"{etiqueta}: sin bk_metrica no se distinguen montos de ratios; se omiten sumas y rangos"
        )
        return r
    # Montos (brl) y cuotas (share_*) son aditivas: el total del panel es Σ de los bancos
    # (la cuota del panel vale 1). Se comparan como sumas, no como cocientes.
    brl = set(metrica.loc[metrica["unidad"] == "brl", "metrica"].astype(str))
    montos = brl | set(METRICAS_CUOTA)
    en_monto = g["metrica"].isin(montos)

    # 1. Total panel = Σ de los bancos del panel, en montos.
    total = (
        g[en_monto & (g["optica"] == TOTAL_PANEL)]
        .groupby(["periodo", "metrica"])["valor"].sum(min_count=1).rename("total")
    )
    if panel is None:
        r.advertencias.append(
            f"{etiqueta}: sin bk_panel no se comprueba que «{TOTAL_PANEL}» sea la suma de los bancos"
        )
    else:
        p = _panel_numerico(panel)
        bancos = (
            p[p["metrica"].isin(montos) & p["valor"].notna()]
            .groupby(["periodo", "metrica"])["valor"].sum().rename("bancos").reset_index()
        )
        cmp = total.reset_index().merge(bancos, on=["periodo", "metrica"], how="left")
        malos = cmp["bancos"].isna().to_numpy() | ~np.isclose(
            cmp["total"], cmp["bancos"], rtol=1e-9,
            atol=np.where(cmp["metrica"].isin(brl), 1.0, 1e-9),
        )
        if malos.any():
            r.errores.append(
                f"{etiqueta}: «{TOTAL_PANEL}» no es igual a la suma de los bancos en "
                f"{int(malos.sum())} casos (p. ej. {cmp.loc[malos, ['periodo', 'metrica']].head(3).to_dict('records')})"
            )

    # 2. Los grupos de cada óptica suman el Total panel, en montos.
    partes = (
        g[en_monto & (g["optica"] != TOTAL_PANEL) & (g["grupo"] != TODOS_LOS_GRUPOS)]
        .groupby(["optica", "periodo", "metrica"])["valor"].sum(min_count=1)
        .rename("suma").reset_index()
        .merge(total.reset_index(), on=["periodo", "metrica"], how="left")
    )
    malos = partes["total"].isna().to_numpy() | ~np.isclose(
        partes["suma"], partes["total"], rtol=1e-9,
        atol=np.where(partes["metrica"].isin(brl), 1.0, 1e-9),
    )
    for optica in sorted(set(partes.loc[malos, "optica"])):
        n = int((malos & (partes["optica"] == optica).to_numpy()).sum())
        r.errores.append(f"{etiqueta}: los grupos de «{optica}» no suman «{TOTAL_PANEL}» en {n} casos")

    # 2b. El «Todos los grupos» de cada óptica también debe ser el Total panel.
    tod = (
        g[en_monto & (g["optica"] != TOTAL_PANEL) & (g["grupo"] == TODOS_LOS_GRUPOS)]
        .groupby(["optica", "periodo", "metrica"])["valor"].sum(min_count=1)
        .rename("suma").reset_index()
        .merge(total.reset_index(), on=["periodo", "metrica"], how="left")
    )
    malos_t = tod["total"].isna().to_numpy() | ~np.isclose(
        tod["suma"], tod["total"], rtol=1e-9,
        atol=np.where(tod["metrica"].isin(brl), 1.0, 1e-9),
    )
    for optica in sorted(set(tod.loc[malos_t, "optica"])):
        n = int((malos_t & (tod["optica"] == optica).to_numpy()).sum())
        r.errores.append(
            f"{etiqueta}: «{TODOS_LOS_GRUPOS}» de «{optica}» no es igual a «{TOTAL_PANEL}» en {n} casos"
        )

    # 2c. Las cuotas (share_*) de los grupos de cada óptica suman 1 en cada período.
    cuotas = g[g["metrica"].isin(METRICAS_CUOTA) & (g["optica"] != TOTAL_PANEL)
               & (g["grupo"] != TODOS_LOS_GRUPOS)]
    suma_cuotas = cuotas.groupby(["optica", "periodo", "metrica"])["valor"].sum(min_count=1)
    malos_c = (suma_cuotas.isna() | ~np.isclose(suma_cuotas, 1.0, rtol=0, atol=1e-9)).to_numpy()
    for optica in sorted(set(suma_cuotas.index.get_level_values("optica")[malos_c])):
        n = int((malos_c & (suma_cuotas.index.get_level_values("optica") == optica)).sum())
        r.errores.append(f"{etiqueta}: las cuotas de los grupos de «{optica}» no suman 1 en {n} casos")

    # 3. Los ratios de cada grupo caen entre el mínimo y el máximo de sus bancos.
    if panel is None or banco is None:
        r.advertencias.append(
            f"{etiqueta}: sin bk_panel y bk_banco no se comprueba que los ratios de grupo "
            "caigan entre el mínimo y el máximo de sus bancos"
        )
        return r
    p = _panel_numerico(panel)
    ratios = {m for m in set(p["metrica"]) - montos - METRICAS_SIN_RANGO
              if not m.startswith(PREFIJOS_SIN_RANGO)}
    sin_rango = sorted(METRICAS_SIN_RANGO & set(p["metrica"]))
    if sin_rango:
        r.advertencias.append(
            f"{etiqueta}: el rango mín.–máx. no se comprueba en {_corto(sin_rango)} "
            "(variación a/a de un flujo con signo)"
        )
    bp = p[p["metrica"].isin(ratios) & p["valor"].notna()]
    gr = g[g["metrica"].isin(ratios)]
    rango_panel = bp.groupby(["periodo", "metrica"])["valor"].agg(["min", "max"]).reset_index()
    _chequear_rango(
        gr[gr["optica"] == TOTAL_PANEL].merge(rango_panel, on=["periodo", "metrica"], how="left"),
        TOTAL_PANEL, etiqueta, r,
    )
    for optica, mapa in _grupos_por_banco(banco).items():
        filas = gr[gr["optica"] == optica]
        if filas.empty:
            continue
        # El «Todos los grupos» de la óptica se contrasta contra todos los bancos.
        _chequear_rango(
            filas[filas["grupo"] == TODOS_LOS_GRUPOS].merge(rango_panel, on=["periodo", "metrica"], how="left"),
            optica, etiqueta, r,
        )
        por_grupo = bp.assign(grupo=bp["cod_inst"].map(mapa))
        rango = por_grupo.groupby(["grupo", "periodo", "metrica"])["valor"].agg(["min", "max"]).reset_index()
        _chequear_rango(
            filas[filas["grupo"] != TODOS_LOS_GRUPOS].merge(rango, on=["grupo", "periodo", "metrica"], how="left"),
            optica, etiqueta, r,
        )
    return r


def verificar_gold_roe_arbol(roe: pd.DataFrame, etiqueta: str = "bk_roe_arbol") -> Resultado:
    """Árbol del ROE: Σ líneas 1–9 = ROA y ROA × apalancamiento = ROE, por entidad y trimestre."""
    r = Resultado()
    if _faltan(roe, COLUMNAS_GOLD["bk_roe_arbol"]):
        return r
    filas = roe.reset_index(drop=True).assign(
        valor=pd.to_numeric(roe["valor"], errors="coerce"),
        linea=roe["linea"].astype(str),
    )
    clave = ["entidad", "periodo"]
    arbol = (
        filas.drop_duplicates(clave + ["linea"])
        .pivot(index=clave, columns="linea", values="valor")
        .reindex(columns=["roa", "roe", "apalancamiento"])
    )
    orden_roa = filas.loc[filas["linea"] == "roa", "orden"].min()
    suma = filas[filas["orden"] < orden_roa].groupby(clave)["valor"].sum(min_count=1)
    suma = suma.reindex(arbol.index)
    roa, roe_v, apal = arbol["roa"], arbol["roe"], arbol["apalancamiento"]

    hay_roa, hay_suma = roa.notna(), suma.notna()
    malo = (hay_roa != hay_suma).to_numpy() | (
        hay_roa & ((suma - roa).abs() > TOL_SUMA_ROA)
    ).to_numpy()
    if malo.any():
        r.errores.append(
            f"{etiqueta}: en {int(malo.sum())} entidades-trimestres, Σ líneas 1–{int(orden_roa) - 1} no es igual al ROA "
            f"(tolerancia {TOL_SUMA_ROA})"
        )

    completo = (roa.notna() & apal.notna()).to_numpy()
    malo2 = (roe_v.notna().to_numpy() != completo) | (
        completo & ((roa * apal - roe_v).abs() > TOL_ROE).to_numpy()
    )
    if malo2.any():
        r.errores.append(
            f"{etiqueta}: en {int(malo2.sum())} entidades-trimestres, ROA × apalancamiento no es igual "
            f"al ROE (tolerancia {TOL_ROE})"
        )
    return r


def verificar_gold_cartera(cartera: pd.DataFrame, totales: pd.DataFrame | None = None,
                           etiqueta: str = "bk_cartera") -> Resultado:
    """Cartera por modalidad: sin 2024-T4, npl15 en [0, 1] y Σ modalidades contra el total publicado."""
    r = Resultado()
    if _faltan(cartera, COLUMNAS_GOLD["bk_cartera"]):
        return r
    cartera = cartera.reset_index(drop=True)
    periodo = cartera["periodo"].astype(str)
    n = int((periodo == PERIODO_SIN_CARTERA).sum())
    if n:
        r.errores.append(f"{etiqueta}: {n} filas de 2024-T4 (el período debe quedar vacío)")
    npl = pd.to_numeric(cartera["npl15"], errors="coerce")
    n = int(((npl < 0) | (npl > 1)).sum())
    if n:
        r.errores.append(f"{etiqueta}: {n} valores de npl15 fuera de [0, 1]")
    if totales is None:
        r.advertencias.append(
            f"{etiqueta}: no hay totales publicados (informes 11 + 13); "
            "Σ modalidades contra el total del BCB no se comprueba"
        )
        return r
    if _faltan(totales, ["cod_inst", "periodo", "tipo", "publicado", "exterior"]):
        r.errores.append(
            f"{etiqueta}: los totales no traen cod_inst, periodo, tipo, publicado y exterior"
        )
        return r
    tot = totales.assign(
        periodo=totales["periodo"].astype(str),
        publicado=pd.to_numeric(totales["publicado"], errors="coerce"),
        exterior=pd.to_numeric(totales["exterior"], errors="coerce").fillna(0.0),
    )
    tot = tot[tot["periodo"] != PERIODO_SIN_CARTERA].set_index(["cod_inst", "periodo", "tipo"])
    tmp = cartera.assign(periodo=periodo, saldo=pd.to_numeric(cartera["saldo"], errors="coerce"))
    suma = tmp.groupby(["cod_inst", "periodo", "tipo"])["saldo"].sum(min_count=1).rename("suma")
    comp = tot.join(suma, how="left")
    comp = comp[comp["publicado"].abs() > 1e6]
    desvio = ((comp["suma"] + comp["exterior"]) / comp["publicado"] - 1).abs()
    malos = desvio.isna().to_numpy() | (desvio > TOL_TOTAL_CARTERA).to_numpy()
    if malos.any():
        r.errores.append(
            f"{etiqueta}: Σ modalidades + exterior no cuadra con el total publicado en "
            f"{int(malos.sum())} casos (tolerancia {TOL_TOTAL_CARTERA})"
        )
    return r


def verificar_gold_sistema(sist: pd.DataFrame, nombre: str, hoy: pd.Timestamp,
                           excepciones: dict[str, int] | None = None) -> Resultado:
    """Series de contexto: ≥ 24 observaciones, sin constantes, último dato no futuro y unidades coherentes."""
    r = Resultado()
    if _faltan(sist, COLUMNAS_GOLD[nombre]):
        return r
    excepciones = excepciones or {}
    tabla = sist.reset_index(drop=True).assign(
        serie_id=sist["serie_id"].astype(str),
        valor=pd.to_numeric(sist["valor"], errors="coerce"),
        fecha=pd.to_datetime(sist["fecha"], errors="coerce"),
    )
    con_dato = tabla[tabla["valor"].notna()]
    conteo = con_dato.groupby("serie_id").size()
    for serie in sorted(tabla["serie_id"].dropna().unique()):
        n = int(conteo.get(serie, 0))
        minimo = excepciones.get(serie, MIN_OBS_SERIE)
        if n < minimo:
            r.errores.append(f"{nombre}: {serie} tiene {n} observaciones (mínimo {minimo})")
        if n and con_dato.loc[con_dato["serie_id"] == serie, "valor"].nunique() <= 1:
            r.errores.append(f"{nombre}: {serie} es constante")
    ultimos = con_dato.groupby("serie_id")["fecha"].max()
    posteriores = sorted(ultimos[ultimos > hoy].index)
    if posteriores:
        r.errores.append(f"{nombre}: último dato posterior a hoy en {_corto(posteriores)}")
    unidades = sorted(set(sist["unidad"].dropna().astype(str)) - UNIDADES_SISTEMA)
    if unidades:
        r.errores.append(f"{nombre}: unidades fuera de {sorted(UNIDADES_SISTEMA)}: {unidades}")
    fraccion = con_dato[(con_dato["unidad"] == "fraccion") & (con_dato["valor"].abs() > 1)]
    if not fraccion.empty:
        r.errores.append(
            f"{nombre}: {len(fraccion)} observaciones con unidad fraccion y |valor| > 1 en "
            f"{_corto(sorted(fraccion['serie_id'].unique()))}"
        )
    return r


def verificar_gold_scr(scr: pd.DataFrame, etiqueta: str = "bk_scr") -> Resultado:
    """Inadimplencia SCR de jun-2026 por segmento, recalculada contra la tasa publicada."""
    r = Resultado()
    if _faltan(scr, COLUMNAS_GOLD["bk_scr"]):
        return r
    fecha = pd.to_datetime(scr["fecha"], errors="coerce")
    jun = scr[fecha.dt.to_period("M") == pd.Period("2026-06", freq="M")]
    for segmento, esperada in TASA_JUN26.items():
        corte = jun[
            (jun["segmento_inst"].astype(str) == segmento)
            & jun["modalidad"].isna() & jun["porte"].isna() & jun["uf"].isna()
        ]
        if corte["cliente"].notna().any():
            corte = corte[corte["cliente"].notna()]
        if corte.empty:
            r.errores.append(f"{etiqueta}: no hay corte de {segmento} en jun-2026 (modalidad, porte y uf vacíos)")
            continue
        activa = pd.to_numeric(corte["carteira_ativa"], errors="coerce").sum()
        inadimplente = pd.to_numeric(corte["inadimplencia_brl"], errors="coerce").sum()
        tasa = inadimplente / activa if activa else np.nan
        if not np.isfinite(tasa) or abs(tasa - esperada) > TOL_TASA:
            r.errores.append(
                f"{etiqueta}: tasa de {segmento} en jun-2026 = {tasa * 100:.2f} % "
                f"(esperada {esperada * 100:.2f} %)"
            )
    return r


def _fecha_de_corte(valor: Any) -> pd.Timestamp | None:
    """Último corte del manifiesto: AAAAMM de trimestre, fecha ISO o None si no se puede leer."""
    texto = str(valor).strip()
    if PATRON_PERIODO.match(texto):
        return _fin_de_trimestre(texto)
    fecha = pd.to_datetime(texto, errors="coerce")
    return None if pd.isna(fecha) else fecha.normalize()


def verificar_gold_manifiesto(man: pd.DataFrame, presentes: dict[str, Path], hoy: pd.Timestamp,
                              etiqueta: str = "bk_manifiesto") -> Resultado:
    """Manifiesto: cada tabla presente tiene fila con su sha256 y cada universo tiene corte no futuro."""
    r = Resultado()
    if _faltan(man, COLUMNAS_GOLD["bk_manifiesto"]):
        return r
    man = man.reset_index(drop=True)
    de_tabla = man[man["universo"].isna()].copy()
    de_tabla["tabla"] = de_tabla["tabla"].astype(str).str.replace(".parquet", "", regex=False)
    for nombre, ruta in sorted(presentes.items()):
        if nombre == "bk_manifiesto":
            continue
        filas = de_tabla[de_tabla["tabla"] == nombre]
        if filas.empty:
            r.errores.append(f"{etiqueta}: {nombre} no tiene fila")
            continue
        declarado = str(filas["sha256"].iloc[0]).strip().lower()
        if declarado != _sha256(ruta):
            r.errores.append(f"{etiqueta}: sha256 de {nombre} no coincide con el archivo")
    # Un universo sin corte todavía (sin tabla en esta ola) es un aviso; un corte que
    # no se lee o que cae en el futuro es un error.
    universos = man[man["universo"].notna()]
    if universos.empty:
        r.advertencias.append(f"{etiqueta}: no hay filas de universo con último corte")
    sin_corte, ilegibles, futuros = 0, [], []
    for universo, valor in zip(universos["universo"], universos["ultimo_corte"]):
        if pd.isna(valor):
            sin_corte += 1
            continue
        fecha = _fecha_de_corte(valor)
        if fecha is None:
            ilegibles.append(f"{universo}={valor}")
        elif fecha > hoy:
            futuros.append(f"{universo}={valor}")
    if sin_corte:
        r.advertencias.append(f"{etiqueta}: {sin_corte} universos sin último corte (sin tabla todavía)")
    if ilegibles:
        r.errores.append(f"{etiqueta}: último corte que no se puede leer: {_corto(ilegibles)}")
    if futuros:
        r.errores.append(f"{etiqueta}: último corte posterior a hoy: {_corto(futuros)}")
    return r


def _numero(serie: pd.Series) -> pd.Series:
    """Serie como float64: los Int64 con nulos y los textos no numéricos pasan a NaN."""
    return pd.to_numeric(serie, errors="coerce").astype("float64")


def verificar_gold_exposicion(exp: pd.DataFrame, etiqueta: str = "bk_exposicion") -> Resultado:
    """Exposición a la mora del sistema (SPEC §3.6): cobertura en [0, 1]; con cobertura < 0,5 la mora
    implícita, la brecha y los efectos quedan nulos; efecto mix + efecto mora = Δ mora implícita a/a."""
    r = Resultado()
    if _faltan(exp, COLUMNAS_GOLD["bk_exposicion"]):
        return r
    cobertura = _numero(exp["cobertura"])
    # holgura TOL_RANGO: Σ de pesos normalizados puede dar 1 + 2e-16
    n = int((cobertura.notna() & ((cobertura < -TOL_RANGO) | (cobertura > 1 + TOL_RANGO))).sum())
    if n:
        r.errores.append(f"{etiqueta}: {n} valores de cobertura fuera de [0, 1]")
    dependientes = ["mora_implicita", "brecha_pp", "efecto_mix_pp", "efecto_mora_pp", "d_mora_implicita_aa_pp"]
    baja = (cobertura < COBERTURA_MIN_GOLD).to_numpy()
    con_valor = exp[dependientes].notna().any(axis=1).to_numpy()
    n = int((baja & con_valor).sum())
    if n:
        r.errores.append(
            f"{etiqueta}: {n} filas con cobertura < 0,5 y mora implícita, brecha o efectos no nulos"
        )
    mix = _numero(exp["efecto_mix_pp"])
    mora = _numero(exp["efecto_mora_pp"])
    delta = _numero(exp["d_mora_implicita_aa_pp"])
    vacias = (mix.isna() & mora.isna() & delta.isna()).to_numpy()
    cuadra = ((mix + mora - delta).abs() <= TOL_EFECTOS).to_numpy()
    n = int((~cuadra & ~vacias).sum())
    if n:
        r.errores.append(
            f"{etiqueta}: efecto_mix_pp + efecto_mora_pp ≠ d_mora_implicita_aa_pp en {n} filas "
            f"(tolerancia {TOL_EFECTOS}; o nulos parciales)"
        )
    return r


def verificar_gold_sensibilidad(sens: pd.DataFrame, etiqueta: str = "bk_sensibilidad") -> Resultado:
    """Beta del NIM contra el CDI por banco (SPEC §3.8): con n < 16, beta, IC y R² nulos;
    ic_inf ≤ beta ≤ ic_sup; R² en [0, 1]."""
    r = Resultado()
    if _faltan(sens, COLUMNAS_GOLD["bk_sensibilidad"]):
        return r
    n = _numero(sens["n_trimestres"])
    beta = _numero(sens["beta_nim_cdi"])
    ic_inf = _numero(sens["ic_inf"])
    ic_sup = _numero(sens["ic_sup"])
    r2 = _numero(sens["r2"])
    corta = (n < MIN_TRIMESTRES_BETA).to_numpy()
    con_valor = pd.concat([beta, ic_inf, ic_sup, r2], axis=1).notna().any(axis=1).to_numpy()
    n_mal = int((corta & con_valor).sum())
    if n_mal:
        r.errores.append(
            f"{etiqueta}: {n_mal} bancos con menos de {MIN_TRIMESTRES_BETA} trimestres y beta, IC o R² no nulos"
        )
    completos = (beta.notna() & ic_inf.notna() & ic_sup.notna()).to_numpy()
    ordenado = ((ic_inf <= beta) & (beta <= ic_sup)).to_numpy()
    n_mal = int((completos & ~ordenado).sum())
    if n_mal:
        r.errores.append(f"{etiqueta}: ic_inf ≤ beta ≤ ic_sup no se cumple en {n_mal} bancos")
    n_mal = int((r2.notna() & ~((r2 >= 0) & (r2 <= 1))).sum())
    if n_mal:
        r.errores.append(f"{etiqueta}: R² fuera de [0, 1] en {n_mal} bancos")
    return r


def verificar_gold_cartera_totales(tot: pd.DataFrame, etiqueta: str = "bk_cartera_totales") -> Resultado:
    """Totales publicados por el BCB (informes 11 + 13): brasil = publicado − exterior; exterior nulo cuenta como 0."""
    r = Resultado()
    if _faltan(tot, COLUMNAS_GOLD["bk_cartera_totales"]):
        return r
    publicado = _numero(tot["publicado"])
    exterior = _numero(tot["exterior"]).fillna(0.0)
    brasil = _numero(tot["brasil"])
    esperado = publicado - exterior
    cuadra = ((brasil - esperado).abs() <= TOLERANCIA_ABSOLUTA).to_numpy()
    vacias = (brasil.isna() & esperado.isna()).to_numpy()
    n = int((~cuadra & ~vacias).sum())
    if n:
        r.errores.append(f"{etiqueta}: brasil ≠ publicado − exterior en {n} filas (tolerancia R$ 1)")
    return r


def verificar_gold(gold: Path = GOLD, hoy: pd.Timestamp | None = None,
                   totales_cartera: Path | None = None) -> Resultado:
    """Comprueba las tablas gold bk_* que existan en `gold`. Solo lectura."""
    r = Resultado()
    hoy = pd.Timestamp(date.today()) if hoy is None else pd.Timestamp(hoy).normalize()
    presentes = {ruta.stem: ruta for ruta in sorted(gold.glob("bk_*.parquet"))}
    for nombre in TABLAS_GOLD:
        if nombre not in presentes:
            r.advertencias.append(f"gold: {nombre} aún no existe en {gold}; se omite su comprobación")

    cargadas: dict[str, pd.DataFrame] = {}
    for nombre, ruta in presentes.items():
        df = _leer_parquet(ruta, nombre, r)
        if df is not None:
            cargadas[nombre] = df.reset_index(drop=True)
    for nombre, df in cargadas.items():
        _acumular(r, _comprobar_gold_general(nombre, df, hoy))

    banco = cargadas.get("bk_banco")
    metrica = cargadas.get("bk_metrica")
    panel = cargadas.get("bk_panel")
    if metrica is not None:
        _acumular(r, verificar_gold_metrica(metrica, panel))
    if banco is not None:
        _acumular(r, verificar_gold_banco(banco))
    if panel is not None:
        _acumular(r, verificar_gold_panel(panel, banco))
    if "bk_grupo" in cargadas:
        _acumular(r, verificar_gold_grupo(cargadas["bk_grupo"], panel, banco, metrica))
    if "bk_roe_arbol" in cargadas:
        _acumular(r, verificar_gold_roe_arbol(cargadas["bk_roe_arbol"]))
    if "bk_cartera" in cargadas:
        ruta_totales = totales_cartera or gold / "bk_cartera_totales.parquet"
        totales = _leer_parquet(ruta_totales, "bk_cartera_totales", r) if ruta_totales.exists() else None
        _acumular(r, verificar_gold_cartera(cargadas["bk_cartera"], totales))
    for nombre in ("bk_sistema_m", "bk_sistema_q"):
        if nombre in cargadas:
            _acumular(r, verificar_gold_sistema(cargadas[nombre], nombre, hoy, EXCEPCIONES_OBS.get(nombre)))
    if "bk_scr" in cargadas:
        _acumular(r, verificar_gold_scr(cargadas["bk_scr"]))
    if "bk_exposicion" in cargadas:
        _acumular(r, verificar_gold_exposicion(cargadas["bk_exposicion"]))
    if "bk_sensibilidad" in cargadas:
        _acumular(r, verificar_gold_sensibilidad(cargadas["bk_sensibilidad"]))
    if "bk_cartera_totales" in cargadas:
        _acumular(r, verificar_gold_cartera_totales(cargadas["bk_cartera_totales"]))
    if "bk_manifiesto" in cargadas:
        _acumular(r, verificar_gold_manifiesto(cargadas["bk_manifiesto"], presentes, hoy))
    r.resumen.update({
        "gold_tablas": sorted(cargadas),
        "gold_ausentes": [n for n in TABLAS_GOLD if n not in presentes],
    })
    return r


def _imprimir(r: Resultado, estricto: bool = False) -> None:
    print("VERIFICACIÓN BANCOS WEB (solo lectura)")
    for clave, valor in r.resumen.items():
        print(f"  {clave}: {valor}")
    if r.errores:
        print(f"\nERRORES ({len(r.errores)}):")
        for error in r.errores:
            print(f"  - {error}")
    if r.advertencias:
        print(f"\nADVERTENCIAS ({len(r.advertencias)}):")
        for aviso in r.advertencias:
            print(f"  - {aviso}")
    if r.ok and not (estricto and r.advertencias):
        sufijo = " con advertencias para revisar" if r.advertencias else ""
        print(f"\nOK: estructura, períodos, crédito y validación consistentes{sufijo}")
    elif r.ok:
        print("\nFALLA: --estricto y hay advertencias; no promover el candidato")
    else:
        print("\nFALLA: no promover el candidato")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metricas", type=Path, default=METRICAS)
    parser.add_argument("--ancho", type=Path, default=ANCHO)
    parser.add_argument("--panorama", type=Path, default=PANORAMA)
    parser.add_argument("--calidad", type=Path, default=CALIDAD)
    parser.add_argument("--validacion", type=Path, default=VALIDACION)
    parser.add_argument("--comparar", type=Path, default=None,
                        help="parquet candidato de staging a comparar con el actual")
    parser.add_argument("--auditoria", action="store_true",
                        help="ejecuta también tests/auditoria/auditar_fuentes.py")
    parser.add_argument("--estricto", action="store_true",
                        help="trata las advertencias como errores")
    parser.add_argument("--gold", action="store_true",
                        help="comprueba solo las tablas gold bk_* de datos/gold (encargo 59)")
    parser.add_argument("--json", action="store_true", help="salida JSON")
    args = parser.parse_args(argv)

    if args.gold:
        resultado = verificar_gold()
    else:
        resultado = verificar_todo(
            metricas=args.metricas,
            ancho=args.ancho,
            panorama=args.panorama,
            calidad=args.calidad,
            validacion=args.validacion,
            comparar=args.comparar,
            con_auditoria=args.auditoria,
        )
    if args.json:
        print(json.dumps({
            "ok": resultado.ok and not (args.estricto and resultado.advertencias),
            "errores": resultado.errores,
            "advertencias": resultado.advertencias,
            "resumen": resultado.resumen,
        }, ensure_ascii=False, indent=2))
    else:
        _imprimir(resultado, args.estricto)
    if not resultado.ok:
        return 1
    if args.estricto and resultado.advertencias:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
