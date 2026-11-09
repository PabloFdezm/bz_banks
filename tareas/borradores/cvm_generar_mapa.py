# -*- coding: utf-8 -*-
"""Genera definiciones/cvm__bancos.json desde los datos (borrador; el JSON queda en git y se revisa a mano).

    Set-Location C:\\dev\\bz_banks
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_generar_mapa.py [--escribir]

De dónde sale cada campo:
- cnpj_raiz: CnpjInstituicaoLider del cadastro del IF.Data (último trimestre con dato) para el cod_inst del panel.
- cd_cvm / denominacion_cvm / registro: cad_cia_aberta.csv de la CVM, cruzado por raíz de CNPJ.
- entrega y tipo_estado: los ZIP de ITR/DFP bajados (quién aparece de verdad y con qué estados).
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pipeline"))
import cvm                   # noqa: E402

DESTINO = RAIZ / "definiciones" / "cvm__bancos.json"
ANIOS = (("itr", cvm.ANIOS_ITR), ("dfp", cvm.ANIOS_DFP))


def coberturas() -> pd.DataFrame:
    """Una fila por (raiz, documento, DT_REFER) con qué tipo de estado existe y la versión mayor."""
    filas = []
    for doc, anios in ANIOS:
        for anio in anios:
            ruta = cvm.ruta_zip(doc, anio)
            if not ruta.exists():
                continue
            with zipfile.ZipFile(ruta) as z:
                nombre = f"{doc}_cia_aberta_{anio}.csv"
                if nombre not in {n.split("/")[-1] for n in z.namelist()}:
                    continue
                d = pd.read_csv(z.open(nombre), sep=";", dtype=str, keep_default_na=False, encoding="cp1252")
            d["raiz"] = d["CNPJ_CIA"].map(cvm.raiz_cnpj)
            for (raiz_, refer, ver), g in d.groupby(["raiz", "DT_REFER", "VERSAO"]):
                filas.append({"raiz": raiz_, "documento": doc.upper(), "dt_refer": refer, "versao": int(ver),
                              "denominacion": g["DENOM_CIA"].iloc[0], "cd_cvm": g["CD_CVM"].iloc[0],
                              "dt_receb": g["DT_RECEB"].max()})
    out = pd.DataFrame(filas)
    if out.empty:
        return out
    # Qué tipo de estado existe de verdad en el ZIP para esa compañía y referencia. Basta con el BPA: una
    # compañía entrega los tres estados (BPA, BPP, DRE) en el mismo tipo, o no entrega consolidado en ninguno.
    tipos: dict[tuple[str, str, str], set[str]] = {}
    for doc, anios in ANIOS:
        for anio in anios:
            ruta = cvm.ruta_zip(doc, anio)
            if not ruta.exists():
                continue
            with zipfile.ZipFile(ruta) as z:
                for tipo in ("con", "ind"):
                    n = cvm.nombre_interno(z, doc, "BPA", anio, tipo)
                    if n is None:
                        continue
                    for parte in cvm.leer_estado(z, n, ["CNPJ_CIA", "DT_REFER"]):
                        for r, refer in {(cvm.raiz_cnpj(a), b) for a, b in zip(parte["CNPJ_CIA"], parte["DT_REFER"])}:
                            tipos.setdefault((r, doc.upper(), refer), set()).add(tipo)
            print(f"  [~] tipos {doc.upper()} {anio}: {len(tipos):,} claves", flush=True)
    out["tipos"] = [tipos.get((r, d, f), set()) for r, d, f in zip(out["raiz"], out["documento"], out["dt_refer"])]
    return out


def main(argv: list[str] | None = None) -> int:
    escribir = "--escribir" in (argv or [])
    panel = cvm.cnpj_lider_panel()
    cad = cvm.registro_cvm()
    # Si una raíz tiene dos registros (Itaú y BMG tienen uno cancelado y uno vigente), se toma el vigente.
    cad = cad.assign(orden=cad["SIT"].ne("ATIVO").astype(int)) \
             .sort_values(["raiz", "orden", "DT_REG"], ascending=[True, True, False]) \
             .drop_duplicates("raiz", keep="first")
    cad = cad.set_index("raiz")
    cov = coberturas()
    notas_viejas = {}
    if DESTINO.exists():                       # las notas son a mano: no se pisan al regenerar
        notas_viejas = {b["cod_inst"]: b.get("nota", "")
                        for b in json.loads(DESTINO.read_text(encoding="utf-8"))["bancos"]}

    bancos = []
    for _, f in panel.iterrows():
        raiz_ = f["raiz"]
        reg = cad.loc[raiz_] if raiz_ in cad.index else None
        c = cov[cov["raiz"] == raiz_] if len(cov) else cov
        entrega = len(c) > 0
        refs = sorted(set(c["dt_refer"])) if entrega else []
        con = sorted(set(c.loc[c["tipos"].map(lambda s: "con" in s), "dt_refer"])) if entrega else []
        ultimo = refs[-1] if refs else ""
        if not entrega:
            tipo, respaldo = "", False
        elif ultimo in con:
            tipo, respaldo = "con", False
        elif len(con) * 2 >= len(refs) and ultimo >= "2026-01-01":
            # Entrega consolidado casi siempre y sigue activo: se queda en consolidado y cae al individual
            # solo en la referencia que todavía no tiene consolidado (Daycoval 3T26).
            tipo, respaldo = "con", True
        else:
            # El consolidado se corta antes que el individual (ABC desde 2024, BRB desde el 2T25) o nunca
            # existió (Amazônia, Nordeste): serie homogénea en individual.
            tipo, respaldo = "ind", False
        bancos.append({
            "cod_inst": f["cod_inst"],
            "nombre_corto": f["nombre_corto"],
            "cnpj_raiz": raiz_ if entrega else "",
            "cnpj_ifdata": raiz_,
            "cd_cvm": c["cd_cvm"].max() if entrega else (reg["CD_CVM"] if reg is not None else ""),
            "denominacion_cvm": c["denominacion"].max() if entrega else (reg["DENOM_SOCIAL"] if reg is not None else ""),
            "tipo_estado": tipo,
            "usar_individual_si_falta": respaldo,
            "base": "CPC" if entrega else "",
            "entrega": bool(entrega),
            "registro_cvm": ("" if reg is None else
                             "{}{}".format(reg["SETOR_ATIV"], f", {reg['CATEG_REG']}" if reg["CATEG_REG"] else "")
                             + (f", SIT={reg['SIT']}" if reg["SIT"] == "ATIVO"
                                else f", SIT={reg['SIT']} desde {reg['DT_INI_SIT']}")),
            "primera_referencia": refs[0] if refs else "",
            "ultima_referencia": ultimo,
            "referencias": refs,
            "referencias_consolidadas": con,
            "nota": notas_viejas.get(f["cod_inst"], ""),
        })

    doc = {
        "fuente": "cvm",
        "descripcion": "Mapa CNPJ de la CVM → cod_inst del panel IF.Data, para la fuente ITR/DFP (pipeline/cvm.py). "
                       "El filtro de bk_publicado es este mapa: un CNPJ que no está acá no entra, aunque el ZIP lo traiga.",
        "convenciones": {
            "cnpj_raiz": "Los 8 primeros dígitos del CNPJ. Sale de CnpjInstituicaoLider del cadastro del IF.Data "
                         "(pipeline/cvm.py::cnpj_lider_panel), verificado contra cad_cia_aberta.csv el 9-nov-2026.",
            "tipo_estado": "«con» = estados consolidados del ZIP; «ind» = solo la controladora. Es la base de la "
                            "serie del banco y se elige para que no cambie a mitad de camino: «ind» cuando la "
                            "compañía no entrega consolidado en su última referencia y tampoco lo hizo en la mitad "
                            "de ellas (ABC Brasil desde 2024, BRB desde el 2T25) o nunca lo entregó (Banco da "
                            "Amazônia, Banco do Nordeste).",
            "usar_individual_si_falta": "true = en una referencia sin estado consolidado se usa el individual y la "
                                        "fila de bk_publicado lo dice en `consolidacion`. Solo Daycoval (3T26).",
            "cnpj_ifdata": "CnpjInstituicaoLider del cadastro del IF.Data para ese cod_inst: es la procedencia de "
                            "cnpj_raiz y se conserva aunque el banco no entregue nada a la CVM.",
            "base": "Marco contable de las cifras: «CPC» = pronunciamientos del CPC que exige la CVM (BR GAAP "
                    "convergido con IFRS). NO es COSIF (IF.Data) ni IFRS tal como lo emite el IASB: los bancos con "
                    "ADR publican además cifras IFRS que pueden diferir de las del ITR.",
            "entrega": "false = el banco no aparece en ningún ZIP de ITR/DFP bajado. La nota dice por qué.",
            "generado_por": "tareas/borradores/cvm_generar_mapa.py, 9-nov-2026; revisado a mano antes de quedar en git.",
        },
        "bancos": bancos,
    }
    texto = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    if escribir:
        DESTINO.write_text(texto, encoding="utf-8")
        print(f"[+] escrito {DESTINO.relative_to(RAIZ)}")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
