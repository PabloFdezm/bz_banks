# -*- coding: utf-8 -*-
"""Hoja «Fondeo y liquidez» (frente 14): agregados monetarios de la metodología nueva del BCB (SGS).

Lleva a gold la sección F1 (volumen) que el canvas calculaba con el borrador `extraer_fondeo.py`. Las secciones F3,
F4, F6 y F7 leen `bk_ref` directo (REF, sección 1.2.1) y no pasan por esta tabla.

TABLA (datos/gold/)
-------------------
- bk_fondeo_m (SGS, mensual, larga): serie, medida, fecha (último día del mes), valor. Clave: serie, medida, fecha.
  * Series: los componentes y agregados de ``COMPONENTES`` (moneda, depósitos a la vista, M1, depósitos a plazo,
    letras financieras, letras de crédito LCI/LCA, otros títulos privados, títulos privados, cuentas de ahorro, M2,
    cuotas de fondos monetarios, compromisadas con títulos privados, M3 sin desglose, M3, títulos federales, M4) y,
    si están en el crudo, las tasas de los depósitos a plazo por inversionista (``TASAS_INVERSIONISTA``).
  * Medidas: ``saldo`` (R$ millones, fin de período), ``aa`` (saldo / saldo de 12 meses antes − 1, fracción),
    ``share_m2`` (solo las 7 hojas de M2: saldo / Σ hojas de M2, fracción; suman 1) y ``share_m4`` (las 11 hojas de
    M4, incluida «M3 sin desglose»; suman 1). Las tasas llevan ``tasa`` (el % del SGS / 100).

REGLAS
------
- Unidad de la fuente: todos los códigos, incluida la poupança 1835, vienen en «u.m.c. (mil)» = R$ mil (catálogo SGS).
  Se dividen por 1.000 para R$ millones, como el resto de las tablas gold de saldos SGS.
- Identidades de la fuente (verificadas el 10-nov, ±2 R$ mil por redondeo): M1 = 27789 + 27790; títulos privados
  27809 = 27805 + 27806 + 27807 + 27808; M2 = M1 + 27809 + 1835 (la poupança está DENTRO de M2 en la metodología
  nueva); M4 = M3 + 27814.
- M3 no cierra con sus partes publicadas: M3 − M2 − 27811 − 27812 deja un residuo de R$ 9–219 mil millones según el
  mes (R$ 161 mil millones a sep-26). Va como serie ``m3_sin_desglose`` (resta de cifras publicadas, no una
  estimación) para que las participaciones en M4 sumen 100 %; buscar en el SGS el código que lo explique.
- 27807 es «Letras de crédito» (LCI/LCA), no letras de cambio; 27811 son «Quotas de fundos monetários».
- Tasas por inversionista (28583, 28611, 28614, 28617): la API del SGS fallaba al bajarlas (10-nov). No están en
  sgs.CODIGOS; se leen solo si el crudo existe, y si no la tabla no las trae (la hoja las marca «en preparación»).
"""
from __future__ import annotations

import sys
from typing import Callable

import pandas as pd

import almacen as A
import sgs as SG
import tabla_estandar as T

DATASET = "bancos_gold_fondeo"
DESDE = "2002-01"          # primer mes con todos los agregados de la metodología nueva (M1 empieza en ene-02)

# serie → clave de sgs.CODIGOS (en orden de presentación)
COMPONENTES: dict[str, str] = {
    "moneda": "mp_moneda", "depositos_vista": "mp_depositos_vista", "m1": "mp_m1",
    "depositos_plazo": "mp_depositos_plazo", "letras_financieras": "mp_letras_financieras",
    "letras_credito": "mp_letras_credito", "otros_titulos_privados": "mp_otros_titulos_privados",
    "titulos_privados": "mp_titulos_privados", "ahorro": "mp_ahorro", "m2": "mp_m2",
    "fondos_monetarios": "mp_fondos_monetarios", "compromisadas_privados": "mp_compromisadas_privados",
    "m3": "mp_m3", "titulos_federales": "mp_titulos_federales", "m4": "mp_m4",
}
RESTO_M3 = "m3_sin_desglose"
# agregado → partes que lo forman (para las pruebas de cuadre)
PARTES = {
    "m1": ["moneda", "depositos_vista"],
    "titulos_privados": ["depositos_plazo", "letras_financieras", "letras_credito", "otros_titulos_privados"],
    "m2": ["m1", "titulos_privados", "ahorro"],
    "m3": ["m2", "fondos_monetarios", "compromisadas_privados", RESTO_M3],
    "m4": ["m3", "titulos_federales"],
}
HOJAS_M2 = ["moneda", "depositos_vista", "depositos_plazo", "letras_financieras", "letras_credito",
            "otros_titulos_privados", "ahorro"]
HOJAS_M4 = HOJAS_M2 + ["fondos_monetarios", "compromisadas_privados", RESTO_M3, "titulos_federales"]
TASAS_INVERSIONISTA = {"tasa_plazo_personas": 28583, "tasa_plazo_empresas": 28611,
                       "tasa_plazo_institucionales": 28614, "tasa_plazo_financieras": 28617}
A_MILLONES = 1e3           # R$ mil → R$ millones


def _existe_crudo(codigo: int) -> bool:
    return SG.ruta(codigo).exists()


def construir_sgs(leer: Callable[[int], pd.Series] = SG.serie_mensual,
                  existe: Callable[[int], bool] = _existe_crudo) -> pd.DataFrame:
    """bk_fondeo_m. ``leer(codigo)`` devuelve la serie mensual (PeriodIndex) de un código SGS, en R$ mil."""
    saldo = pd.DataFrame({s: leer(SG.CODIGOS[k]) for s, k in COMPONENTES.items()})
    saldo = saldo.loc[pd.Period(DESDE, "M"):] / A_MILLONES
    saldo[RESTO_M3] = saldo["m3"] - saldo["m2"] - saldo["fondos_monetarios"] - saldo["compromisadas_privados"]
    filas = []

    def agregar(serie, medida, s):
        s = s.dropna()
        filas.append(pd.DataFrame({"serie": serie, "medida": medida, "fecha": T.fecha_fin(s.index),
                                   "valor": s.to_numpy(dtype=float)}))

    orden = list(COMPONENTES)
    orden.insert(orden.index("m3"), RESTO_M3)
    for serie in orden:
        agregar(serie, "saldo", saldo[serie])
        previo = saldo[serie].shift(12)
        agregar(serie, "aa", saldo[serie] / previo.where(previo > 0) - 1)   # sin base (saldo 0 al nacer la serie): vacío
    for medida, hojas in (("share_m2", HOJAS_M2), ("share_m4", HOJAS_M4)):
        base = saldo[hojas].sum(axis=1, min_count=len(hojas))
        for serie in hojas:
            agregar(serie, medida, saldo[serie] / base)
    for serie, codigo in TASAS_INVERSIONISTA.items():
        if existe(codigo):
            agregar(serie, "tasa", leer(codigo) / 100)
    return pd.concat(filas, ignore_index=True)


def main(argv: list[str] | None = None) -> int:
    df = construir_sgs()
    A.publicar_gold("bk_fondeo_m", df, fuente="bcb_sgs", dataset=DATASET, desde=[f"crudo/{SG.FUENTE}"],
                    nota="Hoja «Fondeo y liquidez» (frente 14)")
    print(f"bk_fondeo_m: {len(df):,} filas; series de tasa: "
          f"{sorted(set(df.loc[df.medida == 'tasa', 'serie'])) or 'ninguna (crudo ausente)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
