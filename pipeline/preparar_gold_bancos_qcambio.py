# -*- coding: utf-8 -*-
"""«Qué se movió» de la Portada: cambio del último trimestre por banco y métrica, con su z (encargo 78d, plan 57).

POR QUÉ EXISTE
--------------
La Portada (B0-03-0) debe decir qué cambió en los bancos sin obligar a leer 34 bancos × 6 métricas.
Un cambio en pp dice poco si no se compara con lo que esa métrica suele moverse: por eso el ranking
usa z, el cambio dividido por el desvío de los cambios trimestrales de esa misma métrica en todo el
panel. Así un salto de 1 pp en una métrica volátil pesa menos que 0,3 pp en una estable.

REGLAS
------
- Unidades: valores en fracción (0,05 = 5 %), como bk_panel; cambio en pp (fracción × 100). Para las
  seis métricas del encargo la unidad es la misma («pp»).
- El cambio se recalcula desde `valor` y no se toma `d_tt` de bk_panel, porque d_tt no aplica las
  reglas de quiebre. El test comprueba que coincida con d_tt donde ninguna regla aplica.
- 2024-T4 vacío: un cambio que toca 2024-T4 queda vacío (2024-T3→2024-T4 y 2024-T4→2025-T1).
- Quiebre 2025 (quiebre_2025 = true en bk_cartera): para esos bancos, los cambios que tocan 2025-T1
  quedan vacíos (2024-T4→2025-T1 y 2025-T1→2025-T2), igual que en la sensibilidad de
  preparar_gold_bancos.py. Es una decisión a confirmar por el arquitecto (ver resultado 78d).
- Desvío: desvío estándar muestral (ddof 1) de todos los cambios no vacíos de la métrica, pooled
  entre bancos, cuyo trimestre final cae en los últimos 20 trimestres del panel.
- Trimestre evaluado: el último del panel. Bancos sin valor en ese trimestre no entran.
- sentido: según `signo` de bk_metrica. «mejora_sube»: cambio > 0 mejora; «mejora_baja»: cambio < 0
  mejora; neutro o cambio 0 → «neutro». Cambio vacío → sentido vacío.
- rango: 1 = mayor |z|; las filas sin z quedan sin rango. Se guardan todas; la página muestra cinco.
- Solo lectura de bk_panel, bk_metrica, bk_banco y bk_cartera.

Entradas: datos/gold/bk_panel.parquet, bk_metrica.parquet, bk_banco.parquet, bk_cartera.parquet
Salida:   datos/gold/bk_qcambio.parquet (escrito con almacen.guardar_derivado)
Uso:      python -X utf8 preparar_gold_bancos_qcambio.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import almacen as A

RAIZ = Path(__file__).resolve().parents[1]
BANKS = RAIZ / "datos" / "gold"
COMANDO = "python -X utf8 preparar_gold_bancos_qcambio.py"

METRICAS = ["share_credito", "roe_ttm", "npl15_total", "costo_riesgo_ttm", "credito_aa", "eficiencia_ttm"]
PERIODO_FIJO = "202412"       # 2024-T4 vacío: ningún cambio que lo toque es válido
PERIODO_QUIEBRE = "202503"    # ruptura de cobertura 2025: solo para bancos con quiebre_2025 = true
VENTANA = 20                  # trimestres para el desvío de los cambios
COLUMNAS = ["periodo", "fecha", "trimestre", "cod_inst", "slug", "nombre_corto", "modelo", "metrica",
            "nombre_metrica", "valor_antes", "valor_ahora", "cambio", "unidad_cambio", "z", "sentido", "rango"]


def _trimestre(periodo: str) -> str:
    return f"{(int(periodo[4:]) - 1) // 3 + 1}T{periodo[2:4]}"


def _cambios(valor: pd.DataFrame, quiebre: set[str]) -> pd.DataFrame:
    """valor: trimestre × banco (fracción) sobre la grilla completa. Devuelve el cambio vs t−1 en pp,
    vacío donde una regla de ruptura lo prohíbe."""
    grilla = list(valor.index)
    siguiente = {p: grilla[i + 1] for i, p in enumerate(grilla[:-1])}
    c = (valor - valor.shift(1)) * 100
    fijos = [p for p in (PERIODO_FIJO, siguiente.get(PERIODO_FIJO)) if p in c.index]
    c.loc[fijos, :] = np.nan
    qcols = [b for b in c.columns if b in quiebre]
    if qcols:
        qper = [p for p in (PERIODO_QUIEBRE, siguiente.get(PERIODO_QUIEBRE)) if p in c.index]
        c.loc[qper, qcols] = np.nan
    return c


def _desvio(c: pd.DataFrame, ventana: list[str]) -> float:
    """Desvío muestral de los cambios no vacíos de la ventana, pooled entre bancos."""
    v = c.loc[[p for p in ventana if p in c.index]].to_numpy(dtype=float).ravel()
    v = v[~np.isnan(v)]
    return float(v.std(ddof=1)) if v.size > 1 else np.nan


def _sentido(cambio: float, signo: str) -> str | None:
    if pd.isna(cambio):
        return None
    if signo not in ("mejora_sube", "mejora_baja") or cambio == 0:
        return "neutro"
    mejor = cambio > 0 if signo == "mejora_sube" else cambio < 0
    return "mejora" if mejor else "deterioro"


def calcular(panel: pd.DataFrame, meta: pd.DataFrame, banco: pd.DataFrame, quiebre: set[str],
             metricas: list[str] = METRICAS) -> pd.DataFrame:
    """panel: cod_inst, periodo, fecha, trimestre, metrica, valor. meta: índice metrica con nombre y signo.
    banco: cod_inst, slug, nombre_corto, modelo. quiebre: cod_inst con quiebre_2025."""
    panel = panel[panel["metrica"].isin(metricas)]
    grilla = sorted(panel["periodo"].unique())
    P, Pant = grilla[-1], grilla[-2]
    ventana = grilla[-VENTANA:]
    ref = panel.loc[panel["periodo"] == P].iloc[0]
    nombres = banco.drop_duplicates("cod_inst").set_index("cod_inst")

    filas = []
    for m in metricas:
        sub = panel[panel["metrica"] == m]
        if sub.empty:
            continue
        valor = sub.set_index(["periodo", "cod_inst"])["valor"].unstack("cod_inst").reindex(grilla)
        c = _cambios(valor, quiebre)
        sd = _desvio(c, ventana)
        cam, ahora, antes = c.loc[P], valor.loc[P], valor.loc[Pant]
        signo, nombre = meta.at[m, "signo"], meta.at[m, "nombre"]
        for cod in valor.columns[ahora.notna().to_numpy()]:
            cambio = cam[cod]
            z = cambio / sd if (pd.notna(cambio) and pd.notna(sd) and sd > 0) else np.nan
            fila = {
                "periodo": P, "fecha": ref["fecha"], "trimestre": ref["trimestre"], "cod_inst": cod,
                "slug": nombres.at[cod, "slug"] if cod in nombres.index else None,
                "nombre_corto": nombres.at[cod, "nombre_corto"] if cod in nombres.index else None,
                "modelo": nombres.at[cod, "modelo"] if cod in nombres.index else None,
                "metrica": m, "nombre_metrica": nombre,
                "valor_antes": antes[cod], "valor_ahora": ahora[cod], "cambio": cambio,
                "unidad_cambio": "pp", "z": z, "sentido": _sentido(cambio, signo),
            }
            filas.append(fila)

    df = pd.DataFrame(filas, columns=COLUMNAS)
    df["rango"] = df["z"].abs().rank(ascending=False, method="first", na_option="keep").astype("Int64")
    return df.sort_values(["rango", "metrica", "cod_inst"], na_position="last").reset_index(drop=True)


UMBRAL_RELEVANTE = 0.005  # cuota de crédito mínima para la lista «relevantes» de la Portada


def construir() -> pd.DataFrame:
    panel = pd.read_parquet(BANKS / "bk_panel.parquet",
                            columns=["cod_inst", "periodo", "fecha", "trimestre", "metrica", "valor"])
    panel["cod_inst"] = panel["cod_inst"].astype(str)
    meta = pd.read_parquet(BANKS / "bk_metrica.parquet", columns=["metrica", "nombre", "signo"]).set_index("metrica")
    banco = pd.read_parquet(BANKS / "bk_banco.parquet", columns=["cod_inst", "slug", "nombre_corto", "modelo"])
    banco["cod_inst"] = banco["cod_inst"].astype(str)
    cart = pd.read_parquet(BANKS / "bk_cartera.parquet", columns=["cod_inst", "quiebre_2025"])
    cart = cart.drop_duplicates("cod_inst")
    quiebre = set(cart.loc[cart["quiebre_2025"].fillna(False).astype(bool), "cod_inst"].astype(str))
    t = calcular(panel, meta, banco, quiebre)
    # Arquitecto: los mayores |z| son casi siempre bancos chicos (CloudWalk, Agibank). Para la Portada
    # interesan los que mueven el sistema: cuota de crédito del trimestre y una marca de relevancia
    # (≥ 0,5 % del crédito del panel, ~17 bancos) con su propio orden. La tabla completa se conserva.
    P = t["periodo"].iloc[0] if len(t) else None
    cuota = (panel[(panel["metrica"] == "share_credito") & (panel["periodo"] == P)]
             .set_index("cod_inst")["valor"])
    t["cuota_credito"] = t["cod_inst"].map(cuota)
    t["relevante"] = t["cuota_credito"].ge(UMBRAL_RELEVANTE)
    rel = t["relevante"] & t["z"].notna()
    t["rango_relevantes"] = pd.Series(pd.NA, index=t.index, dtype="Int64")
    t.loc[rel, "rango_relevantes"] = t.loc[rel, "z"].abs().rank(ascending=False, method="first").astype("Int64")
    return t


def main() -> int:
    t = construir()
    b = io.BytesIO()
    t.to_parquet(b, index=False)
    datos = b.getvalue()
    A.guardar_derivado("bcb_ifdata", "bancos_gold_qcambio", "bk_qcambio.parquet", datos,
                       desde=["bcb_ifdata/valores"], como=COMANDO,
                       nota="Derivado de datos/gold/bk_panel, bk_metrica, bk_banco y bk_cartera (gold).")
    A.escribir_atomico(BANKS / "bk_qcambio.parquet", datos)
    print(f"bk_qcambio: {len(t):,} filas, periodo {t['periodo'].iloc[0] if len(t) else '-'}")
    print(t.head(5)[["nombre_corto", "metrica", "valor_antes", "valor_ahora", "cambio", "z", "sentido", "rango"]]
          .to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
