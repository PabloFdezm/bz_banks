# -*- coding: utf-8 -*-
"""Verificador de solo lectura de la fuente CVM (ITR/DFP) y de su tabla gold ``bk_publicado``.

POR QUÉ EXISTE
--------------
``bk_publicado`` se arma encadenando decisiones: qué CNPJ es cada banco del panel, si se lee el estado
consolidado o el individual, qué versión de la entrega vale, si la DRE es el trimestre o el acumulado, en qué
escala viene el número y qué cuenta del plan de cada banco es «la cartera de crédito». Un error en cualquiera
no revienta: publica un número plausible y equivocado. Este script comprueba la cadena de punta a punta sin
escribir nada, y además compara contra IF.Data (dos contabilidades del mismo trimestre) para que una
diferencia grande sea ruido visible y no una sorpresa en el sitio.

Comprueba:
- integridad del crudo (sha256 de los manifiestos de ``datos/crudo/cvm/``);
- que el mapa cubra exactamente el universo del panel, sin CNPJ repetidos y con tipo de estado válido;
- que ningún CNPJ fuera del mapa haya entrado al derivado ni a ``bk_publicado``;
- estructura de ``bk_publicado``: contrato gold, dominio de medida/documento/consolidación, periodos de fin
  de trimestre, sin valores nulos ni infinitos;
- la escala: rehace el valor de una muestra de filas desde el derivado (VL_CONTA × 1000 si ESCALA_MOEDA=MIL)
  y exige que coincida al céntimo — es la prueba de que no se publicó en R$ mil;
- coherencia interna del balance: el activo total de la CVM contra la suma de sus cuentas de nivel 1.0x;
- que cada banco que entrega tenga datos en el último trimestre que le corresponde;
- el contraste contra IF.Data (activo, PL, depósitos, crédito y lucro del trimestre), avisando de las
  diferencias mayores al umbral.

Uso desde la raíz del repo:

    python -X utf8 herramientas/verificar_cvm.py                 # errores y avisos
    python -X utf8 herramientas/verificar_cvm.py --estricto      # los avisos también fallan
    python -X utf8 herramientas/verificar_cvm.py --json
    python -X utf8 herramientas/verificar_cvm.py --sin-contraste  # no lee bk_panel

Código de salida: 0 si no hay errores (o solo avisos sin ``--estricto``), 1 si los hay.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import almacen as A          # noqa: E402
import bancos as B           # noqa: E402
import cvm                   # noqa: E402
import periodos as PER       # noqa: E402

GOLD = A.GOLD / "bk_publicado.parquet"
MUESTRA_ESCALA = 40          # filas revisadas contra el derivado
SEMILLA = 0                  # la muestra es reproducible
TOL_ESCALA = 0.01            # R$ 1 centavo: los valores vienen con 10 decimales de formato
TOL_BALANCE = 1.0            # R$ 1: el activo contra la suma de sus partes (redondeo de la fuente)

DOMINIO_MEDIDA = {"saldo", "trimestre", "acumulado"}
DOMINIO_DOCUMENTO = {"ITR", "DFP", "DFP−ITR"}
DOMINIO_CONSOLIDACION = {"con", "ind"}


@dataclass
class Resultado:
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    resumen: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errores


def _corto(seq, n: int = 8) -> str:
    seq = [str(x) for x in seq]
    return ", ".join(seq) if len(seq) <= n else ", ".join(seq[:n]) + f"… (+{len(seq) - n})"


def cargar_publicado(r: Resultado) -> pd.DataFrame | None:
    if not GOLD.exists():
        r.errores.append(f"falta {GOLD}: correr «python -X utf8 pipeline/cvm.py gold»")
        return None
    df = pd.read_parquet(GOLD)
    try:
        A.validar_contrato("bk_publicado", df)
    except ValueError as e:
        r.errores.append(str(e))
    return df


def verificar_crudo(r: Resultado) -> None:
    """Los ZIP y el registro bajados siguen siendo los que se anotaron en su manifiesto."""
    base = A.CRUDO / cvm.FUENTE
    if not base.exists():
        r.advertencias.append(f"no hay crudo de la CVM en {base}: nada que verificar (bajar con cvm.py descargar)")
        return
    problemas = []
    for d in sorted(p.parent for p in base.rglob(A.MANIFIESTO)):
        problemas += A.verificar(d)
    if problemas:
        r.errores += [f"crudo cvm: {p}" for p in problemas]
    archivos = sorted({f["archivo"] for f in A.inventario() if f["fuente"] == cvm.FUENTE and f["capa"] == "crudo"})
    r.resumen["crudo_cvm"] = archivos


def verificar_mapa(r: Resultado) -> pd.DataFrame | None:
    """El mapa cubre el universo del panel, sin CNPJ repetidos, con tipos y códigos coherentes."""
    try:
        mapa = cvm.mapa_bancos()          # ya falla si falta un banco, sobra o se repite un CNPJ
    except (ValueError, FileNotFoundError) as e:
        r.errores.append(f"mapa de bancos: {e}")
        return None
    universo = {b["cod_inst"] for b in B.universo()}
    if set(mapa["cod_inst"]) != universo:
        r.errores.append("el mapa no tiene exactamente el universo del panel")
    entrega = mapa[mapa["entrega"]]
    if entrega["cd_cvm"].eq("").any():
        r.errores.append(f"bancos con entrega=true y sin cd_cvm: "
                         f"{_corto(entrega.loc[entrega['cd_cvm'].eq(''), 'cod_inst'])}")
    if not entrega["tipo_estado"].isin(["con", "ind"]).all():
        r.errores.append("tipo_estado fuera de con|ind en algún banco que entrega")
    sin_nota = entrega.loc[entrega["nota"].eq(""), "nombre_corto"].tolist()
    if sin_nota:
        r.advertencias.append(f"bancos que entregan sin nota en el mapa: {_corto(sin_nota)}")
    r.resumen["bancos_mapa"] = int(len(mapa))
    r.resumen["bancos_que_entregan"] = int(len(entrega))
    return mapa


def verificar_derivado(r: Resultado, mapa: pd.DataFrame) -> None:
    """Ningún CNPJ fuera del mapa entró al derivado, y todo lo filtrado trae las columnas esperadas."""
    rutas = sorted(A.ruta_derivada(cvm.FUENTE, cvm.DS_DERIVADO).glob("estados_*.parquet"))
    if not rutas:
        r.advertencias.append("no hay derivados de la CVM: correr «python -X utf8 pipeline/cvm.py extraer»")
        return
    validos = set(mapa.loc[mapa["entrega"], "cod_inst"])
    raices = set(mapa.loc[mapa["entrega"], "cnpj_raiz"])
    d = pd.concat([pd.read_parquet(p) for p in rutas], ignore_index=True)
    fuera = sorted(set(d["cod_inst"]) - validos)
    if fuera:
        r.errores.append(f"el derivado trae bancos fuera del mapa: {_corto(fuera)}")
    raices_fuera = sorted({cvm.raiz_cnpj(c) for c in d["cnpj"]} - raices)
    if raices_fuera:
        r.errores.append(f"el derivado trae CNPJ fuera del mapa: {_corto(raices_fuera)}")
    if not set(d["ordem_exerc"]) <= {"ÚLTIMO", "PENÚLTIMO"}:
        r.errores.append(f"ORDEM_EXERC fuera de dominio: {_corto(sorted(set(d['ordem_exerc'])))}")
    if not set(d["escala"]) <= set(cvm.ESCALAS):
        r.errores.append(f"ESCALA_MOEDA fuera de {sorted(cvm.ESCALAS)}: {_corto(sorted(set(d['escala'])))}")
    r.resumen["derivado_filas"] = int(len(d))
    r.resumen["derivado_archivos"] = [p.name for p in rutas]


def verificar_estructura(pub: pd.DataFrame, mapa: pd.DataFrame, defn: dict, r: Resultado) -> None:
    """Dominios, formato de periodo, coherencia con el mapa y ausencia de nulos en lo publicado."""
    lineas_validas = set(defn["lineas"])
    fuera = sorted(set(pub["linea"]) - lineas_validas)
    if fuera:
        r.errores.append(f"líneas fuera de definiciones/{cvm.DEF_LINEAS}.json: {_corto(fuera)}")
    for columna, dominio in (("medida", DOMINIO_MEDIDA), ("documento", DOMINIO_DOCUMENTO),
                             ("consolidacion", DOMINIO_CONSOLIDACION)):
        malos = sorted(set(pub[columna]) - dominio)
        if malos:
            r.errores.append(f"{columna} fuera de dominio: {_corto(malos)}")
    periodos = pub["periodo"].astype(str)
    if not periodos.str.match(r"^\d{4}(03|06|09|12)$").all():
        r.errores.append(f"periodo con formato inválido: {_corto(sorted(set(periodos))[:5])}")
    if pub["valor"].isna().any():
        r.errores.append(f"{int(pub['valor'].isna().sum())} filas publicadas con valor nulo "
                         f"(un hueco no se publica: va al CSV de huecos)")
    dinero = pub[pub["linea"] != cvm.LINEA_ROE]
    if (dinero["valor"] == 0).any():
        malas = dinero[dinero["valor"] == 0]
        r.errores.append(f"{len(malas)} filas de saldo/flujo en 0 (la fuente no las divulga; no van al gold): "
                         f"{_corto(malas['linea'].unique())}")
    # La base de consolidación publicada tiene que ser la del mapa (o el individual de respaldo, declarado).
    tipo = dict(zip(mapa["cod_inst"], mapa["tipo_estado"]))
    respaldo = set(mapa.loc[mapa["usar_individual_si_falta"], "cod_inst"])
    for cod, g in pub.groupby("cod_inst"):
        usos = set(g["consolidacion"])
        esperado = {tipo.get(cod, "")}
        if cod in respaldo:
            esperado |= {"ind"}
        if not usos <= esperado:
            r.errores.append(f"{cod}: consolidación {sorted(usos)} distinta de la del mapa {sorted(esperado)}")
    r.resumen["periodos"] = f"{periodos.min()}–{periodos.max()}"
    r.resumen["filas"] = int(len(pub))
    r.resumen["bancos_con_datos"] = int(pub["cod_inst"].nunique())


def _leer_derivado_todo() -> pd.DataFrame:
    rutas = sorted(A.ruta_derivada(cvm.FUENTE, cvm.DS_DERIVADO).glob("estados_*.parquet"))
    if not rutas:
        return pd.DataFrame()
    d = pd.concat([pd.read_parquet(p) for p in rutas], ignore_index=True)
    d = d[d["ordem_exerc"] == "ÚLTIMO"].copy()
    d["valor"] = [cvm.numero_cvm(v) * cvm.ESCALAS[e] for v, e in zip(d["vl_conta"], d["escala"])]
    d["versao_n"] = pd.to_numeric(d["versao"], errors="coerce").fillna(0).astype(int)
    d = d[d["versao_n"] == d.groupby(["cod_inst", "documento", "dt_refer"])["versao_n"].transform("max")]
    d["dt_refer_corto"] = d["dt_refer"].str[:7]
    return d


def verificar_escala(pub: pd.DataFrame, defn: dict, r: Resultado) -> None:
    """Rehace una muestra de valores desde el derivado: VL_CONTA × 1000 cuando ESCALA_MOEDA = MIL.

    Es la prueba de que ``bk_publicado`` está en R$ y no en R$ mil: si alguien toca la escala, esto falla.
    Se comparan en valor absoluto porque alguna línea cambia el signo a propósito (la provisión viene
    negativa en la fuente), y solo filas de una sola cuenta: las que suman o restan cuentas se comprueban
    en ``verificar_balance`` y en las pruebas.
    """
    d = _leer_derivado_todo()
    if d.empty:
        r.advertencias.append("sin derivado de la CVM: no se comprueba la escala contra la fuente")
        return
    estados = {k: v.get("estado", "") for k, v in defn["lineas"].items()}
    una_cuenta = ~pub["cd_conta"].astype(str).str.contains(" + ", regex=False)
    candidatas = pub[(pub["documento"] != "DFP−ITR") & una_cuenta
                     & (pub["linea"] != cvm.LINEA_ROE) & (pub["cd_conta"] != "")]
    if candidatas.empty:
        r.advertencias.append("no hay filas de una sola cuenta para comprobar la escala")
        return
    muestra = candidatas.sample(min(MUESTRA_ESCALA, len(candidatas)), random_state=SEMILLA)
    malas = []
    for _, f in muestra.iterrows():
        dt_refer = _dt_refer(str(f["periodo"]))
        estado = estados.get(f["linea"], "")
        ref = d[(d["cod_inst"] == f["cod_inst"]) & (d["dt_refer"] == dt_refer) & (d["estado"] == estado)
                & (d["cd_conta"] == f["cd_conta"])]
        if ref.empty:
            malas.append(f"{f['cod_inst']} {f['periodo']} {f['linea']}: la cuenta {f['cd_conta']} "
                         f"no está en el derivado de {dt_refer}")
            continue
        if not any(abs(abs(v) - abs(float(f["valor"]))) <= max(TOL_ESCALA, abs(v) * 1e-9) for v in ref["valor"]):
            malas.append(f"{f['cod_inst']} {f['periodo']} {f['linea']}: gold {float(f['valor']):,.2f} contra "
                         f"derivado {_corto([f'{v:,.2f}' for v in ref['valor']])}")
    if malas:
        r.errores += [f"la escala no reproduce el derivado: {m}" for m in malas]
    r.resumen["muestra_escala"] = int(len(muestra))


def _dt_refer(periodo: str) -> str:
    """202606 → 2026-06-30."""
    return str(PER.fin_de_mes(pd.Series([str(periodo)]))[0].date())


def verificar_balance(pub: pd.DataFrame, r: Resultado) -> None:
    """El activo total de la CVM contra la suma de sus componentes de nivel 1.0x (misma entrega y versión).

    No es una regla nuestra: es la aritmética del estado. Si falla, o se leyó otra versión o el ZIP cambió.
    """
    d = _leer_derivado_todo()
    if d.empty:
        return
    d = d[d["estado"] == "BPA"].copy()
    d["nivel"] = d["cd_conta"].str.count(r"\.")
    partes = d[d["nivel"] == 1].groupby(["cod_inst", "documento", "dt_refer"])["valor"].sum()
    total = d[d["cd_conta"] == "1"].set_index(["cod_inst", "documento", "dt_refer"])["valor"]
    comunes = partes.index.intersection(total.index)
    dif = (partes.loc[comunes] - total.loc[comunes]).abs()
    malas = dif[dif > TOL_BALANCE]
    if len(malas):
        r.errores.append(f"el activo total no suma sus partes en {len(malas)} entregas: "
                         f"{_corto([f'{k[0]} {k[2]}' for k in malas.index])}")
    r.resumen["entregas_balance_cuadradas"] = int(len(comunes) - len(malas))


def verificar_cobertura(pub: pd.DataFrame, mapa: pd.DataFrame, r: Resultado) -> None:
    """Cada banco que entrega tiene datos en su última referencia, y el último trimestre del panel CVM
    tiene al menos la mitad de los bancos."""
    entregas = pd.read_parquet(A.ruta_derivada(cvm.FUENTE, cvm.DS_DERIVADO) / "entregas.parquet") \
        if (A.ruta_derivada(cvm.FUENTE, cvm.DS_DERIVADO) / "entregas.parquet").exists() else pd.DataFrame()
    ultimo_pub = pub.groupby("cod_inst")["periodo"].max()
    if len(entregas):
        ultimo_ent = (entregas.assign(p=entregas["dt_refer"].map(cvm.periodo_de_referencia))
                      .dropna(subset=["p"]).groupby("cod_inst")["p"].max())
        for cod, per in ultimo_ent.items():
            if cod in set(mapa.loc[mapa["entrega"], "cod_inst"]) and ultimo_pub.get(cod, "") != per:
                r.advertencias.append(f"{cod}: su última entrega es {per} pero bk_publicado llega a "
                                      f"{ultimo_pub.get(cod, 'nada')}")
    ultimo = pub["periodo"].max()
    n = int((pub["periodo"] == ultimo).groupby(pub["cod_inst"]).any().sum()) if len(pub) else 0
    r.resumen["ultimo_periodo"] = str(ultimo)
    r.resumen["bancos_en_el_ultimo"] = n
    if n < max(1, int(len(mapa[mapa["entrega"]]) * 0.5)):
        r.advertencias.append(f"en {ultimo} solo hay {n} bancos de {int(mapa['entrega'].sum())} que entregan")


def verificar_contraste(r: Resultado) -> None:
    """CVM contra IF.Data: la diferencia es de definición, pero por encima del umbral hay que explicarla."""
    if not (A.GOLD / "bk_panel.parquet").exists():
        r.advertencias.append("sin bk_panel: no se contrasta contra IF.Data")
        return
    tabla = cvm.contrastar(guardar=False)
    if tabla.empty:
        r.advertencias.append("el contraste contra IF.Data no dio ninguna comparación")
        return
    malas = tabla[tabla["supera_umbral"] & tabla["principal"]]
    otras = tabla[tabla["supera_umbral"] & ~tabla["principal"]]
    r.resumen["contraste_comparaciones"] = int(len(tabla))
    r.resumen["contraste_principales"] = int(tabla["principal"].sum())
    r.resumen["contraste_sobre_umbral"] = int(len(malas))
    r.resumen["contraste_secundarias_sobre_umbral"] = int(len(otras))
    if len(malas):
        detalle = (malas.assign(txt=lambda x: x["nombre_corto"] + " " + x["periodo"].astype(str) + " "
                                + x["linea_cvm"] + "→" + x["metrica_ifdata"] + " "
                                + (x["dif_pct"] * 100).round(1).astype(str) + "%")["txt"].tolist())
        r.advertencias.append(f"{len(malas)} comparaciones principales superan el {cvm.UMBRAL_DIF_PCT:.0%} "
                              f"contra IF.Data (esperable por definición; una por una en "
                              f"tareas/borradores/cvm_informe.md): {_corto(detalle, 12)}")


def verificar(ruta: Path = GOLD, *, contraste: bool = True) -> Resultado:
    r = Resultado()
    verificar_crudo(r)
    mapa = verificar_mapa(r)
    if mapa is not None:
        verificar_derivado(r, mapa)
    pub = cargar_publicado(r)
    if pub is None:
        return r
    try:
        defn = cvm.definicion_lineas()
    except FileNotFoundError as e:
        r.errores.append(f"definiciones: {e}")
        return r
    if mapa is not None:
        verificar_estructura(pub, mapa, defn, r)
        verificar_cobertura(pub, mapa, r)
    verificar_escala(pub, defn, r)
    verificar_balance(pub, r)
    if contraste:
        verificar_contraste(r)
    return r


def _imprimir(r: Resultado, estricto: bool) -> None:
    print("VERIFICACIÓN FUENTE CVM (solo lectura)")
    for k, v in r.resumen.items():
        print(f"  {k}: {v}")
    if r.errores:
        print(f"\nERRORES ({len(r.errores)}):")
        for e in r.errores:
            print(f"  - {e}")
    if r.advertencias:
        print(f"\nADVERTENCIAS ({len(r.advertencias)}):")
        for a in r.advertencias:
            print(f"  - {a}")
    if r.errores or (estricto and r.advertencias):
        print("\nFALLA: revisar antes de publicar")
    else:
        print("\nOK: fuente CVM y bk_publicado consistentes")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--estricto", action="store_true", help="las advertencias también fallan")
    ap.add_argument("--json", action="store_true", help="salida en JSON")
    ap.add_argument("--sin-contraste", action="store_true", help="no compara contra IF.Data")
    args = ap.parse_args(argv)
    r = verificar(contraste=not args.sin_contraste)
    if args.json:
        print(json.dumps({"ok": r.ok and not (args.estricto and r.advertencias),
                          "errores": r.errores, "advertencias": r.advertencias, "resumen": r.resumen},
                         ensure_ascii=False, indent=1, default=str))
    else:
        _imprimir(r, args.estricto)
    return 0 if (r.ok and not (args.estricto and r.advertencias)) else 1


if __name__ == "__main__":
    sys.exit(main())
