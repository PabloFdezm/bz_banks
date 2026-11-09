# -*- coding: utf-8 -*-
"""Pone las notas a mano en definiciones/cvm__bancos.json (borrador de un solo uso).

    Set-Location C:\\dev\\bz_banks
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_notas_mapa.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "definiciones" / "cvm__bancos.json"

FUERA_EEUU = ("No entrega ITR/DFP a la CVM: el grupo cotiza en EE.UU. y reporta con 20-F/6-K "
              "(tareas/07_fuente_cvm.md, fuera de alcance en la v1).")
NO_EMISOR = "No es emisor registrado en la CVM con el CNPJ líder del conglomerado prudencial: no entrega ITR/DFP."
PAGOS = "Institución de pagos; no es emisor registrado en la CVM."

NOTAS = {
    "C0080099": "Filer = ITAU UNIBANCO HOLDING S.A. (CD_CVM 019348; el registro 001279 está cancelado). "
                "Consolidado completo y entrega el 3T26. Es el banco de referencia para validar el mapeo de "
                "líneas (2T26, ver tareas/borradores/cvm_informe.md).",
    "C0080075": "Filer = BCO BRADESCO S.A. (no hay holding separada). El consolidado societario incluye el brazo "
                "de seguros, que el conglomerado prudencial del IF.Data trata distinto: es la mayor parte de la "
                "diferencia en el contraste (ver la nota «el consol. IFRS da −18,4 % (seguros)» de "
                "definiciones/validacion_bancos.json).",
    "C0080329": "Filer = BCO BRASIL S.A. (CNPJ 00.000.000/0001-91). Consolidado completo; todas las entregas en "
                "versión 1.",
    "C0080185": "Filer = BCO SANTANDER (BRASIL) S.A. Consolidado completo; 3T26 en versión 2.",
    "C0080336": "Filer = BCO BTG PACTUAL S.A. (el banco emite las units BPAC11). Consolidado completo; hasta 6 "
                "versiones en el 1T25. Banco Pan, que está dentro del conglomerado prudencial de BTG en el IF.Data, "
                "dejó de entregar ITR propio después del 3T25.",
    "C0080154": "Filer = BANCO DO ESTADO DO RIO GRANDE DO SUL SA. Consolidado completo; todas las entregas en "
                "versión 1.",
    "C0080147": "Filer = BANESTES S.A. - BCO EST ESPIRITO SANTO. Consolidado completo.",
    "C0081744": "Serie consolidada salvo el 3T26, que a la fecha de la descarga solo existe en versión individual: "
                "esa referencia entra con consolidacion=ind (usar_individual_si_falta). Vigilar si la CVM publica "
                "después el consolidado.",
    "C0080178": "Dos registros de la CVM con el mismo CNPJ: 001716 (cancelado en 1994) y 024600 (vigente). "
                "Consolidado completo; entrega el 3T26.",
    "C0080123": "Filer = BCO MERCANTIL DO BRASIL S.A. Consolidado completo; 3T26 en versión 2.",
    "C0080312": "Desde el DFP 2024 entrega SOLO estados individuales (el DFP 2023 sí trae consolidado). La serie se "
                "toma entera en individual para no mezclar bases; cobertura completa hasta el 3T26.",
    "C0080374": "Filer = BCO PINE S.A. Consolidado completo; varias reentregas (hasta versión 3 en el DFP 2023 y "
                "2025 y en el 1T26).",
    "C0080288": "Última entrega: ITR 2T25, y solo en versión individual (el consolidado se corta en el 1T25). El "
                "registro sigue ATIVO en la CVM: conviene averiguar por qué dejó de entregar antes de publicar sus "
                "cifras. Serie en individual.",
    "C0081249": "Registrado (Categoria A, emisor en bolsa) pero nunca entrega estados consolidados en el período: "
                "serie en individual, completa hasta el 2T26 (el 3T26 todavía no está).",
    "C0081593": "Registrado (Categoria A, emisor en bolsa) pero nunca entrega estados consolidados en el período: "
                "serie en individual, completa hasta el 2T26 (el 3T26 todavía no está).",
    "C0084710": "Institución de pagos, no banco: entrega ITR/DFP consolidado (Categoria B) pero su plan de cuentas "
                "no tiene cartera de crédito, depósitos ni resultado de intermediación financiera. DECISIÓN "
                "PENDIENTE de Pablo: entra a bk_publicado con las líneas que sí tiene (activo, PL, lucro) o queda "
                "fuera del mapa.",
    # Sin entrega
    "C0084693": FUERA_EEUU,
    "C0080996": FUERA_EEUU + " Registro CVM cancelado el 02-dic-2022 (pasó a cotizar en Nasdaq).",
    "C0082475": FUERA_EEUU,
    "C0084686": FUERA_EEUU,
    "C0084813": FUERA_EEUU,
    "C0083694": "Registro CVM cancelado el 18-ene-2019: no entrega ITR/DFP en el período.",
    "C0080109": "Registro CVM cancelado: banco cerrado, no entrega ITR/DFP.",
    "C0080271": "Registro CVM cancelado el 24-nov-2016: dejó de cotizar y no entrega ITR/DFP.",
    "C0080738": "No es emisor registrado en la CVM (empresa pública federal). " + NO_EMISOR,
    "C0081847": NO_EMISOR + " El que tiene registro en la CVM es BNDESPAR, otra compañía del grupo.",
    "C0084844": NO_EMISOR,
    "C0080484": NO_EMISOR,
    "C0080903": NO_EMISOR,
    "C0080642": "El CNPJ líder del conglomerado prudencial no está registrado en la CVM; el emisor del grupo es una "
                "aseguradora (sector «Seguradoras e Corretoras»), no un banco, y sus estados no tienen las líneas "
                "bancarias. Fuera de alcance en la v1.",
    "C0086581": PAGOS,
    "C0085702": PAGOS,
    "C0088022": PAGOS,
    "C0084820": PAGOS + " El emisor del grupo (Mercado Libre) cotiza en EE.UU.",
}


def main() -> int:
    doc = json.loads(DESTINO.read_text(encoding="utf-8"))
    faltan = [b["cod_inst"] for b in doc["bancos"] if b["cod_inst"] not in NOTAS]
    sobran = sorted(set(NOTAS) - {b["cod_inst"] for b in doc["bancos"]})
    if faltan or sobran:
        raise SystemExit(f"faltan notas {faltan}; sobran {sobran}")
    for b in doc["bancos"]:
        b["nota"] = NOTAS[b["cod_inst"]]
    DESTINO.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[+] {len(doc['bancos'])} bancos con nota en {DESTINO.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
