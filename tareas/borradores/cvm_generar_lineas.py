# -*- coding: utf-8 -*-
"""Genera y valida definiciones/cvm__bancos_lineas.json (borrador de trabajo, queda como procedencia).

    Set-Location C:\\dev\\bz_banks
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_generar_lineas.py            # valida e informa
    .venv\\Scripts\\python.exe -X utf8 tareas/borradores/cvm_generar_lineas.py --escribir  # además escribe el JSON

Las reglas salen del relevamiento de los planes de cuenta de los 16 bancos que entregan ITR/DFP
(tareas/borradores/cvm_sondeo.py y cvm_sondeo2.py sobre los ZIP de 2023-2026). Cada regla es
código candidato + texto que debe contener la descripción: el código solo no sirve porque el esqueleto
de la CVM cambió (CPC 48) y cada banco migró en un momento distinto.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "pipeline"))
import cvm                   # noqa: E402

DESTINO = RAIZ / "definiciones" / "cvm__bancos_lineas.json"

# ------------------------------------------------------------------ líneas

LINEAS = {
    "ativo_total": {
        "cero_es_vacio": True,
        "nombre": "Ativo total", "estado": "BPA", "medida": "saldo", "unidad": "R$", "orden": 1,
        "definicion": "Cuenta 1 del activo. Consolidado cuando el banco lo entrega; si no, individual "
                      "(lo dice la columna consolidacion de bk_publicado).",
    },
    "credito_bruto": {
        "cero_es_vacio": True,
        "nombre": "Cartera de crédito bruta", "estado": "BPA", "medida": "saldo", "unidad": "R$", "orden": 2,
        "definicion": "Operações de crédito ANTES de la provisión por pérdida esperada. El alcance varía por "
                      "banco (Itaú y BMG incluyen arrendamento mercantil financeiro en la misma cuenta): la "
                      "nota de cada banco lo dice.",
    },
    "credito_liquido": {
        "cero_es_vacio": True,
        "nombre": "Cartera de crédito neta", "estado": "BPA", "medida": "saldo", "unidad": "R$", "orden": 3,
        "definicion": "Operações de crédito NETAS de provisión. Se usa cuando el banco no publica la provisión "
                      "en las cuentas estándar de la CVM (1.02.04.05 = 0 en todos los periodos) y por tanto su "
                      "saldo de crédito ya viene neto. Clasificado así por contraste contra IF.Data.",
    },
    "provisao_perda": {
        "cero_es_vacio": True,
        "nombre": "Provisión para pérdidas esperadas (saldo)", "estado": "BPA", "medida": "saldo", "unidad": "R$",
        "orden": 4,
        "definicion": "Saldo de la provisión por pérdida esperada de crédito, en positivo (en la fuente viene "
                      "negativa, como contra-activo). Vacía cuando el banco no la divulga en el archivo "
                      "estructurado.",
    },
    "depositos": {
        "cero_es_vacio": True,
        "nombre": "Depósitos", "estado": "BPP", "medida": "saldo", "unidad": "R$", "orden": 5,
        "definicion": "Depósitos de clientes (cuenta estandarizada del pasivo). No incluye captaciones en "
                      "mercado abierto ni recursos interfinancieros, que van en cuentas separadas.",
    },
    "patrimonio_liquido": {
        "cero_es_vacio": True,
        "nombre": "Patrimonio líquido", "estado": "BPP", "medida": "saldo", "unidad": "R$", "orden": 6,
        "definicion": "Patrimonio líquido total, incluida la participación de los no controladores.",
    },
    "patrimonio_liquido_controlador": {
        "cero_es_vacio": True,
        "nombre": "Patrimonio líquido del controlador", "estado": "BPP", "medida": "saldo", "unidad": "R$",
        "orden": 7,
        "definicion": "Patrimonio líquido atribuible a los accionistas de la controladora. Es el denominador "
                      "del ROE anualizado, para que sea consistente con el lucro atribuible.",
    },
    "resultado_intermediacion": {
        "nombre": "Resultado bruto de intermediación financiera", "estado": "DRE", "medida": "flujo",
        "unidad": "R$", "orden": 8,
        "definicion": "Cuenta 3.03 de la DRE. OJO: no es comparable entre bancos sin leer la nota — Itaú y "
                      "Santander incluyen ahí servicios, seguros y cambio; Banco do Nordeste y Mercantil "
                      "incluyen la provisión de crédito en las despesas de intermediación.",
    },
    "lucro_liquido": {
        "nombre": "Lucro líquido del período", "estado": "DRE", "medida": "flujo", "unidad": "R$", "orden": 9,
        "definicion": "Lucro o prejuízo líquido consolidado (o del período, en estados individuales), "
                      "incluidos los no controladores.",
    },
    "lucro_liquido_controlador": {
        "nombre": "Lucro líquido atribuible al controlador", "estado": "DRE", "medida": "flujo", "unidad": "R$",
        "orden": 10,
        "definicion": "Lucro atribuible a los accionistas de la controladora. En estados individuales no hay "
                      "no controladores: coincide con el lucro del período.",
    },
    "roe_anualizado": {
        "nombre": "ROE anualizado", "estado": "", "medida": "trimestre", "unidad": "ratio", "orden": 11,
        "definicion": "Lucro atribuible del trimestre × 4 / PL promedio de 12 meses del controlador "
                      "((PL_t + PL_t−4) / 2, la convención del repo para el ROE de IF.Data). Derivado: no sale "
                      "de una cuenta de la CVM. Vacío si falta el PL de t−4.",
    },
}

# ------------------------------------------------------------------ plantillas
# Reglas genéricas que sirven para los dos esqueletos de la CVM (el viejo bancario y el del CPC 48) porque
# combinan código candidato con texto. El orden importa: la primera alternativa que casa gana.

PLANTILLA_BANCO = {
    "ativo_total": {"alternativas": [
        {"suma": [{"cd": ["1"], "ds": ["ativo total"]}]}]},
    "depositos": {"cero_es_vacio": True, "alternativas": [
        {"suma": [{"cd": ["2.02.01", "2.03.01", "2.03.02", "2.03.03"], "ds": ["depositos"],
                   "ds_no": ["banco central", "instituicoes de credito", "interfinanceiros"]}]}]},
    "patrimonio_liquido": {"alternativas": [
        {"suma": [{"cd": ["2.07", "2.08", "2.03"], "ds": ["patrimonio liquido", "consolidado"]}]},
        {"suma": [{"cd": ["2.07", "2.08", "2.03"], "ds": ["patrimonio liquido"]}]}]},
    "patrimonio_liquido_controlador": {"alternativas": [
        {"suma": [{"cd": ["2.07.01"], "ds": ["patrimonio liquido", "controlador"]}]},
        {"suma": [{"cd": ["2.07", "2.08", "2.03"], "ds": ["patrimonio liquido"]}],
         "resta": [{"cd": ["2.07.02", "2.08.09", "2.03.09"], "ds": ["nao controladores"]}]},
        {"suma": [{"cd": ["2.07", "2.08", "2.03"], "ds": ["patrimonio liquido"]}]}]},
    "resultado_intermediacion": {"alternativas": [
        {"suma": [{"cd": ["3.03"], "ds": ["resultado bruto", "intermediacao financeir"]}]}]},
    "lucro_liquido": {"alternativas": [
        {"suma": [{"cd": ["3.11", "3.09"], "ds": ["lucro", "periodo"],
                   "ds_no": ["antes das participacoes", "operacoes continuadas", "operacoes descontinuadas"]}]}]},
    "lucro_liquido_controlador": {"alternativas": [
        # 1) la atribución directa; 2) total menos no controladores (Banestes deja la atribución en 0 en los
        # ITR de 1T y 3T); 3) el total, para estados individuales donde no hay no controladores.
        {"suma": [{"cd": ["3.11.01", "3.09.01"], "ds": ["atribuido", "controladora"]}],
         "cero_es_vacio": True},
        {"suma": [{"cd": ["3.11", "3.09"], "ds": ["lucro", "periodo"],
                   "ds_no": ["antes das participacoes", "operacoes continuadas", "operacoes descontinuadas"]}],
         "resta": [{"cd": ["3.11.02", "3.09.02"], "ds": ["atribuido", "nao controladores"]}]},
        {"suma": [{"cd": ["3.11", "3.09"], "ds": ["lucro", "periodo"],
                   "ds_no": ["antes das participacoes", "operacoes continuadas", "operacoes descontinuadas"]}]}]},
    # Crédito y provisión: por banco (ver OVERRIDES). Por defecto, el esqueleto viejo.
    "credito_bruto": {"alternativas": [
        {"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"]}]}]},
    "provisao_perda": {"signo": "positivo", "cero_es_vacio": True, "alternativas": [
        {"suma": [{"cd": ["1.02.04.05"], "ds": ["perdas esperadas", "risco de credito"]}]}]},
}

PLANTILLA_NO_FINANCIERA = {
    "ativo_total": PLANTILLA_BANCO["ativo_total"],
    "patrimonio_liquido": PLANTILLA_BANCO["patrimonio_liquido"],
    "patrimonio_liquido_controlador": PLANTILLA_BANCO["patrimonio_liquido_controlador"],
    "lucro_liquido": PLANTILLA_BANCO["lucro_liquido"],
    "lucro_liquido_controlador": PLANTILLA_BANCO["lucro_liquido_controlador"],
}

CREDITO_LIQUIDO = {"alternativas": [{"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"]}]}]}

# ------------------------------------------------------------------ overrides por banco
# Solo crédito, provisión y depósitos, que es donde los planes difieren de verdad. Verificado cuenta por
# cuenta en el ITR/DFP de 2023 a 2026 (tareas/borradores/_sondeo2_*.txt).

NOTA_ITAU_CREDITO = ("1.02.03.05 «Operações de Crédito e Arrendamento Mercantil Financeiro»: incluye el "
                     "arrendamento mercantil financiero. El código era 1.02.03.04 hasta el DFP 2023.")
NOTA_ITAU_PDD = ("1.02.03.07 «(-) Provisão para Perda Esperada» cubre TODOS los activos financieros al costo "
                 "amortizado (1.02.03), no solo la cartera de crédito: sobreestima la provisión de crédito. "
                 "El código era 1.02.03.06 hasta el DFP 2023.")

OVERRIDES = {
    # --- esqueleto CPC 48 (plan B)
    "C0080099": {  # Itaú Unibanco
        "credito_bruto": {"alternativas": [{"suma": [{"cd": ["1.02.03.05", "1.02.03.04"],
                                                     "ds": ["operacoes de credito"]}]}],
                          "nota": NOTA_ITAU_CREDITO},
        "provisao_perda": {"signo": "positivo", "cero_es_vacio": True,
                           "alternativas": [{"suma": [{"cd": ["1.02.03.07", "1.02.03.06"],
                                                       "ds": ["provisao para perda esperada"]}]}],
                           "nota": NOTA_ITAU_PDD},
        "depositos": {"alternativas": [{"suma": [{"cd": ["2.03.01"], "ds": ["depositos"]}]}],
                      "nota": "2.03.01 «Depósitos»: cuadra al R$ mil con definiciones/validacion_bancos.json "
                              "(1.134,49 bn en 2T26)."},
        "resultado_intermediacion": {"alternativas": [
            {"suma": [{"cd": ["3.03"], "ds": ["resultado bruto", "intermediacao financeir"]}]}],
            "nota": "Itaú mete en 3.01 las tarifas bancarias (3.01.05) y el resultado de seguros y "
                    "previdência (3.01.06): su 3.03 NO es comparable con el de un banco que los deja fuera."},
    },
    "C0080178": {  # BMG
        "credito_bruto": {"alternativas": [{"suma": [{"cd": ["1.02.03.05"], "ds": ["operacoes de credito"]}]}],
                          "nota": "1.02.03.05 «Operações de crédito e arrendamento mercantil»: incluye leasing."},
        "provisao_perda": {"signo": "positivo", "cero_es_vacio": True,
                           "alternativas": [{"suma": [{"cd": ["1.02.03.06"],
                                                       "ds": ["provisao para perdas por nao recuperacao"]}]}],
                           "nota": "1.02.03.06 «Provisão para perdas por não recuperação (Impairment)»."},
        "depositos": {"alternativas": [{"suma": [{"cd": ["2.03.01"], "ds": ["depositos de clientes"]}]}]},
    },
    "C0080336": {  # BTG Pactual
        "credito_bruto": {"alternativas": [{"suma": [{"cd": ["1.02.03.04"], "ds": ["operacoes de credito"]}]}],
                          "nota": "1.02.03.04 «Operações de crédito». BTG no publica la provisión en el archivo "
                                  "estructurado, así que no se pudo verificar si el saldo es bruto o neto: se "
                                  "clasificó como bruto por el contraste contra IF.Data (ver cvm_informe.md)."},
        "provisao_perda": {"signo": "positivo", "cero_es_vacio": True, "alternativas": [],
                           "vacia": "BTG no divulga la provisión de crédito en las cuentas estructuradas de "
                                    "la CVM (solo 2.04.02, provisión de avales y fianzas, que es otra cosa).",
                           "nota": "BTG no divulga la provisión de crédito en las cuentas estructuradas de la "
                                   "CVM (solo 2.04.02, provisión de avales y fianzas, que es otra cosa)."},
    },
    "C0080185": {  # Santander Brasil
        "credito_bruto": {"alternativas": [
            {"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"]}]}],
            "nota": "Santander llena el archivo estructurado de forma irregular: solo el DFP 2024 trae la "
                    "cartera abierta (1.02.04.04 bruto, con la provisión en 1.02.04.05). En el DFP 2023 y 2025 "
                    "vuelca todo el costo amortizado en 1.02.04.01 y deja 1.02.04.04 en 0; en los ITR de 2025 "
                    "en adelante no abre 1.02.03. Por eso esta línea solo tiene valor en 2024."},
        "credito_liquido": {"alternativas": [
            {"suma": [{"cd": ["1.02.03.02"], "ds": ["emprestimos e adiantamentos a clientes"]}]}],
            "nota": "Solo el ITR 1T25: 1.02.03.02 «Empréstimos e Adiantamentos a Clientes» (536,19 bn), que "
                    "suma exactamente a 1.02.03 sin cuenta de provisión, o sea que viene neto."},
        "provisao_perda": {"signo": "positivo", "cero_es_vacio": True,
                           "alternativas": [{"suma": [{"cd": ["1.02.04.05"],
                                                       "ds": ["perdas esperadas", "risco de credito"]}]}],
                           "nota": "Solo el DFP 2024 trae la provisión."},
        "depositos": {"cero_es_vacio": True, "alternativas": [
            {"suma": [{"cd": ["2.03.02"], "ds": ["depositos de clientes"]}]},
            {"suma": [{"cd": ["2.02.01"], "ds": ["depositos"],
                       "ds_no": ["banco central", "instituicoes de credito"]}]}],
            "nota": "Santander detalla los depósitos solo en algunas entregas (1T25: 2.03.02 «Depósitos de "
                    "Clientes», 608,16 bn). En las demás deja 2.02.01 en 0 y no abre 2.03: la línea queda "
                    "vacía antes que en 0."},
        "lucro_liquido": {"alternativas": [
            {"suma": [{"cd": ["3.11.01", "3.09.01"], "ds": ["atribuido", "controladora"]},
                      {"cd": ["3.11.02", "3.09.02"], "ds": ["atribuido", "nao controladores"]}]}],
            "nota": "TRAMPA: en varios ITR Santander entrega 3.06 «Imposto de Renda» en 0, así que su 3.09 "
                    "«Lucro/Prejuízo Consolidado do Período» queda ANTES de impuestos (1S26: 8,104 bn contra "
                    "6,244 bn de 3.09.01 + 3.09.02; también en el 3T25). El total se reconstruye sumando la "
                    "atribución a controladores y a no controladores, que sí viene después de impuestos y que "
                    "en las entregas correctas da el mismo número."},
        "resultado_intermediacion": {"alternativas": [
            {"suma": [{"cd": ["3.03"], "ds": ["resultado bruto", "intermediacao financeir"]}]}],
            "nota": "Santander deja en 3.01 solo «Receitas com Juros e Similares»; el cambio, los servicios y "
                    "las pérdidas de crédito van en 3.04 (otras receitas/despesas operacionales). Su 3.03 no "
                    "es comparable con el de Itaú ni con el del esqueleto viejo."},
    },
    "C0080374": {  # Pine
        "credito_liquido": {"alternativas": [
            {"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"], "desde": "2025-03-31"}]}],
            "nota": "Pine no publica la provisión de crédito (1.02.04.05 = 0 en todos los periodos; solo "
                    "1.02.04.07, de arrendamento, y 1.04.03.03/04, de activos a valor justo). Antes del 1T25 "
                    "usaba el esqueleto CPC 48 sin detalle: no hay cartera."},
        "credito_bruto": {"alternativas": [],
                          "vacia": "Pine no publica la provisión de crédito (1.02.04.05 = 0 siempre), así que "
                                   "su saldo de crédito se publica como neto (credito_liquido)."},
        "provisao_perda": {"signo": "positivo", "cero_es_vacio": True, "alternativas": [],
                           "vacia": "No divulga la provisión de crédito en cuenta estándar: solo 1.02.04.07 "
                                    "(arrendamento) y 1.04.03.03/04 (activos a valor justo), que no son la "
                                    "provisión de la cartera al costo amortizado.",
                           "nota": "No divulga la provisión de crédito en cuenta estándar."},
    },
    "C0080329": {  # Banco do Brasil
        "credito_liquido": dict(CREDITO_LIQUIDO, nota="BB entrega 1.02.04.05 «Provisão para Perdas Esperadas» "
                                                      "en 0 en todos los periodos: su 1.02.04.04 viene neto. "
                                                      "Confirmado contra definiciones/validacion_bancos.json "
                                                      "(«Neto de provisión p.64, bruto 1.245,87»)."),
        "credito_bruto": {"alternativas": [],
                          "vacia": "BB entrega 1.02.04.04 neto de provisión: se publica como credito_liquido."},
        "provisao_perda": {"signo": "positivo", "cero_es_vacio": True, "alternativas": [],
                           "vacia": "BB no publica el saldo de la provisión en las cuentas estándar de la CVM "
                                    "(1.02.04.05 = 0 siempre). La despesa del período sí está (3.04.01).",
                           "nota": "BB no publica el saldo de la provisión en las cuentas estándar de la CVM "
                                   "(1.02.04.05 = 0 siempre). La despesa del período sí está (3.04.01)."},
    },
    "C0080147": {  # Banestes
        "credito_liquido": dict(CREDITO_LIQUIDO, nota="Banestes entrega 1.02.04.05 en 0 en todos los periodos: "
                                                       "su 1.02.04.04 viene neto (contraste contra IF.Data)."),
        "credito_bruto": {"alternativas": [],
                          "vacia": "Banestes entrega 1.02.04.04 neto de provisión: se publica como "
                                   "credito_liquido."},
        "provisao_perda": {"signo": "positivo", "cero_es_vacio": True, "alternativas": [],
                           "vacia": "No publica el saldo de la provisión (1.02.04.05 = 0 siempre).",
                           "nota": "No publica el saldo de la provisión (1.02.04.05 = 0 siempre)."},
    },
    "C0080312": {  # ABC Brasil
        "credito_bruto": {"alternativas": [
            {"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"], "desde": "2025-03-31"}]}],
            "nota": "Desde el 1T25 ABC publica la provisión (1.02.04.05): el saldo de crédito pasa a ser bruto."},
        "credito_liquido": {"alternativas": [
            {"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"], "hasta": "2024-12-31"}]}],
            "nota": "Hasta el DFP 2024 la provisión viene en 0: el saldo es neto y no es comparable con el "
                    "crédito bruto de 2025 en adelante."},
    },
    "C0080123": {  # Mercantil do Brasil
        "credito_bruto": {"alternativas": [
            {"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"], "desde": "2025-03-31"}]}],
            "nota": "Desde el 1T25 publica la provisión (1.02.04.05): el saldo pasa a ser bruto."},
        "credito_liquido": {"alternativas": [
            {"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"], "hasta": "2024-12-31"}]}],
            "nota": "Hasta el DFP 2024 la provisión viene en 0: el saldo es neto."},
        "resultado_intermediacion": {"alternativas": [
            {"suma": [{"cd": ["3.03"], "ds": ["resultado bruto", "intermediacao financeir"]}]}],
            "nota": "Mercantil pone la provisión de crédito DENTRO de las despesas de intermediación (3.02.03) "
                    "y deja 3.04.01 en 0: su 3.03 ya viene después de provisiones, al revés que el esqueleto "
                    "estándar."},
    },
    "C0081593": {  # Banco do Nordeste
        "resultado_intermediacion": {"alternativas": [
            {"suma": [{"cd": ["3.03"], "ds": ["resultado bruto", "intermediacao financeir"]}]}],
            "nota": "Nordeste pone la provisión de crédito dentro de las despesas de intermediación (3.02.04) "
                    "y deja 3.04.01 en 0: su 3.03 ya viene después de provisiones."},
    },
    "C0084710": {  # Cielo
        "plantilla_override": "no_financiera",
        "nota_banco": "Institución de pagos: entrega el plan de cuentas de una compañía no financiera "
                      "(activo/passivo circulante, PL en 2.03). No tiene cartera de crédito, depósitos ni "
                      "resultado de intermediación. DECISIÓN PENDIENTE de Pablo: entra a bk_publicado con "
                      "activo, PL y lucro, o queda fuera.",
    },
}

SIN_LINEA: dict = {}          # reservado: líneas que se deciden vacías a propósito van en OVERRIDES


def construir() -> dict:
    mapa = cvm.mapa_bancos()
    bancos = {}
    for _, b in mapa.iterrows():
        if not b["entrega"]:
            continue
        ov = dict(OVERRIDES.get(b["cod_inst"], {}))
        plantilla = ov.pop("plantilla_override", "banco")
        nota_banco = ov.pop("nota_banco", "")
        entrada = {"nombre_corto": b["nombre_corto"], "plantilla": plantilla}
        if nota_banco:
            entrada["nota"] = nota_banco
        if ov:
            entrada["lineas"] = ov
        bancos[b["cod_inst"]] = entrada
    return {
        "fuente": "cvm",
        "descripcion": "Mapeo de cuentas del ITR/DFP de la CVM a las líneas mínimas de bk_publicado. Una línea "
                       "se busca por REGLA (código candidato + texto que debe contener la descripción), no por "
                       "código fijo: el esqueleto de la CVM cambió con el CPC 48 y cada banco migró en un "
                       "momento distinto, así que el mismo concepto vive en códigos distintos según banco y año. "
                       "Si una regla no casa, la línea queda VACÍA con su motivo: nunca se inventa un número.",
        "convenciones": {
            "regla": "«cd» lista códigos candidatos; «ds» lista textos que la descripción debe contener TODOS "
                     "(comparados normalizados: minúsculas, sin acentos ni puntuación); «ds_no» textos que NO "
                     "debe contener; «desde»/«hasta» acotan por DT_REFER cuando el banco cambió de criterio. "
                     "Una regla que casa con más de una cuenta es un error (ambigua), no un empate.",
            "alternativas": "Se prueban en orden; gana la primera cuyas reglas casan todas. «suma» suma cuentas "
                            "y «resta» las descuenta (p. ej. el PL del controlador = PL total − no controladores).",
            "cero_es_vacio": "true en la provisión: un banco con cartera siempre tiene provisión esperada, así "
                             "que un 0 en esa cuenta significa «no la divulgo», no «no tengo».",
            "signo": "«positivo» publica el valor absoluto (la provisión viene negativa en la fuente).",
            "plantillas": "«banco» cubre los dos esqueletos con reglas genéricas; «no_financiera» es para "
                          "Cielo. Las líneas de cada banco reemplazan a las de la plantilla (no se mezclan).",
            "generado_por": "tareas/borradores/cvm_generar_lineas.py, 9-nov-2026, sobre el relevamiento de los "
                            "ZIP de ITR 2025-2026 y DFP 2023-2026. Los overrides están validados cuenta por "
                            "cuenta; las notas de cada banco dicen qué trampa tiene.",
        },
        "lineas": LINEAS,
        "plantillas": {"banco": PLANTILLA_BANCO, "no_financiera": PLANTILLA_NO_FINANCIERA},
        "bancos": bancos,
    }


if __name__ == "__main__":
    doc = construir()
    if "--escribir" in sys.argv:
        DESTINO.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[+] escrito {DESTINO.relative_to(RAIZ)}")
    print(f"{len(doc['bancos'])} bancos, {len(doc['lineas'])} líneas, {len(doc['plantillas'])} plantillas")
