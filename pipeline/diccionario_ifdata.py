#!/usr/bin/env python3
"""
Genera el DICCIONARIO COMPLETO de la base IFDATA del BCB en HTML
autocontenido, a partir de:
  - datos/crudo/bcb_ifdata/catalogo/actual/relatorios.json            (catalogo OLinda: 16 informes)
  - ifdata_cache/docs/rest_rel2000a2024.json      (catalogo historico web)
  - ifdata_cache/docs/rest_relatorios2025a2030.json (catalogo web era nueva)
  - ifdata_cache/docs/trel_202503/*.json    (estructura+notas por informe)
  - ifdata_cache/docs/nuevo_filtro202503.json (dominios TCB/TC/TD/TI/SR/TCip)
  - ifdata_cache/docs/nuevo_info202503.json  (descripciones de etiquetas)
  - datos/crudo/bcb_ifdata/valores/actual/valores_<último>_{1,2,3}     (inventario de cuentas; --periodo)
  - datos/crudo/bcb_ifdata/valores/actual/valores_200003_3            (ejemplos de renumeracion de era)
  (los crudos de OLinda estan en parquet; se leen con almacen.leer_crudo_tabla)

Las secciones narrativas (generalidades, escopos, API, eras) provienen de la
metodologia oficial de la pagina IF.data, del PDF "Esclarecimentos e
Metodologia" del BCB y de verificaciones empiricas documentadas.

Uso:
    python -X utf8 pipeline/diccionario_ifdata.py [-o ifdata_diccionario.html]
"""

import argparse
import glob
import re
import json
from html import escape as esc
from pathlib import Path

import almacen as A
from ifdata_texto import normalizar as norm

# Los CSV/JSON que sirve OLinda viven en la capa cruda (ver almacen.py). `docs/`
# sigue en ifdata_cache/ porque son capturas manuales de los endpoints REST de
# www3 cuya URL no se puede reconstruir desde el nombre del archivo: sin URL no
# hay procedencia, y un crudo sin procedencia no entra a la capa.
CATALOGO = A.ruta_cruda("bcb_ifdata", "catalogo")
DOCS = A.DATOS / "ifdata_cache" / "docs"

FUENTES = {  # informe (normalizado) -> sistema de origen (PDF metodologia)
    "resumo": "Cosif",
    "ativo": "Cosif",
    "passivo": "Cosif",
    "demonstracao de resultado": "Cosif",
    "informacoes de capital": "DLO (modulo de capital del Cosif)",
    "segmentacao": "Cosif + DLO",
    "cambio": "Sistema Câmbio",
}
for k in ("carteira de credito ativa",):
    FUENTES[k] = "SCR"

SEL_A_ESCOPO = {1005: "financeiro", 1006: "individual", 1009: "prudencial",
                1004: "prudencial", 1007: "cambio", 1008: "financeiro"}

UNIDADES = {
    1: "R$ (API en unidades; el sitio web muestra R$ mil)",
    2: "R$ (API en unidades; el sitio web muestra R$ mil)",
    3: "R$ (API en unidades; el sitio web muestra R$ mil)",
    4: "R$ (API en unidades; el sitio web muestra R$ mil). Flujo acumulado, no trimestral (ver nota Ley 4.595)",
    5: "R$ (API en unidades) y ratios en fraccion",
    6: "R$ y USD (API en unidades; columnas de exposicion). Indicadores 0/1",
    7: "R$ (API en unidades)",
    8: "R$ (API en unidades) [descontinuado]",
    9: "R$ (API en unidades)",
    10: "conteos (clientes / operaciones), sin unidad monetaria",
    11: "R$ (API en unidades)",
    12: "R$ (API en unidades)",
    13: "R$ (API en unidades)",
    14: "R$ (API en unidades)",
    15: "USD (API en unidades; el sitio web muestra miles de USD) y conteos de operaciones",
    16: "R$ (API en unidades)",
}


def _filas(periodo: str, tipo: int) -> list[dict]:
    """Filas de un volcado completo de valores (todas las columnas como texto); [] si no está."""
    ruta = A.ruta_valores(periodo, tipo)
    if not A.existe_crudo(ruta):
        print(f"aviso: falta {ruta.name}")
        return []
    return A.leer_crudo_tabla(ruta).to_dict("records")


def ultimo_volcado() -> str:
    """Último trimestre con volcado completo (todos los informes) del escopo individual en el crudo."""
    periodos = [m.group(1) for r in A.glob_crudo(A.ruta_cruda("bcb_ifdata", "valores"), "valores_*_3.csv")
                if (m := re.fullmatch(r"valores_(\d{6})_3\.csv", r.name))]
    if not periodos:
        raise FileNotFoundError("no hay volcados completos de IF.Data (valores_AAAAMM_3) en el crudo")
    return max(periodos)


def cargar(periodo: str):
    d = {}
    d["relatorios"] = json.loads((CATALOGO / "relatorios.json").read_text(encoding="utf-8"))["value"]
    d["cat_viejo"] = json.loads((DOCS / "rest_rel2000a2024.json").read_text(encoding="utf-8"))
    d["cat_nuevo"] = json.loads((DOCS / "rest_relatorios2025a2030.json").read_text(encoding="utf-8"))
    d["trels"] = {}
    for f in glob.glob(str(DOCS / "trel_202503" / "*.json")):
        t = json.loads(Path(f).read_text(encoding="utf-8"))
        t = t.get("trel", t)
        d["trels"].setdefault(norm(t["n"]), []).append(t)
    d["filtro"] = json.loads((DOCS / "nuevo_filtro202503.json").read_text(encoding="utf-8"))
    # inventario de cuentas del volcado completo del trimestre
    inv = {}
    for tipo in (1, 2, 3):
        for x in _filas(periodo, tipo):
            clave = norm(x["NomeRelatorio"])
            cuenta = (x["Conta"], " ".join(x["NomeColuna"].split()),
                      " ".join(x["DescricaoColuna"].split()),
                      "null" if x["Grupo"] == "null" else " ".join(x["Grupo"].split()))
            inv.setdefault(clave, {}).setdefault(cuenta, set()).add(tipo)
    d["inventario"] = inv
    # ejemplos de renumeracion (era 2000-03 vs 2025-03, Resumo individual)
    def resumo(periodo):
        return [(x["Conta"], " ".join(x["NomeColuna"].split())) for x in _filas(periodo, 3)
                if x["CodInst"] == "00000000" and x["NomeRelatorio"] == "Resumo"]
    d["renumeracion"] = (resumo("200003"), resumo(periodo))
    return d


def disponibilidad(datos):
    """Matriz informe x escopo -> lista de periodos (desde catalogs web)."""
    matriz = {}
    for cat in (datos["cat_viejo"], datos["cat_nuevo"]):
        for e in cat:
            for f in e["files"]:
                if "trel" not in f:
                    continue
                t = f["trel"]
                for s in t.get("s", []):
                    escopo = SEL_A_ESCOPO.get(s["id"], str(s["id"]))
                    matriz.setdefault(norm(t["n"]), {}).setdefault(escopo, set()).add(e["dt"])
    return matriz


GENERALIDADES = """
<p><b>IFDATA</b> (Informaciones Financieras Trimestrales) es la publicacion del
Banco Central do Brasil con datos seleccionados de las entidades reguladas:
estados financieros, capital regulatorio, cartera de credito y cambio, con
trimestralidad desde <b>marzo de 2000</b>. Cubre las entidades <b>autorizadas a
funcionar y en operacion normal</b> (bancos, financieras, cooperativas de
credito, corretoras, distribuidoras, agentes de fomento, instituciones de
pago, administradoras de consorcio y conglomerados). <b>No hay datos de
aseguradoras</b> (supervisadas por SUSEP, no por el BCB) ni de administradoras
de consorcio como entidades individualmente (solo dentro del consolidado
prudencial).</p>
<ul>
<li><b>Sistemas de origen</b>: <b>COSIF</b> (Plano Contabil de las
instituciones del SFN; datos contables), <b>SCR</b> (Sistema de Informaciones
de Credito; carteras), <b>DLO</b> (capital regulatorio) y <b>Sistema Cambio</b>
(movimientos de cambio).</li>
<li><b>Plazos de publicacion</b>: hasta 60 dias tras el cierre de marzo,
junio y septiembre; hasta 90 dias tras diciembre.</li>
<li><b>Republicacion</b>: en la base de diciembre se republican los datos
contables, de capital y de credito de los <b>ultimos cuatro trimestres</b> con
la informacion mas reciente recibida (los valores pueden cambiar). Los
documentos sustituidos despues del plazo entran al reprocessamiento anual de
abril.</li>
<li><b>NI</b> = "Nao informado" por la entidad al momento de procesar el
informe (aparece como <code>null</code> en la API).</li>
<li><b>Demonstracao de Resultado</b>: por la Ley 4.595/1964, en marzo y
septiembre las receitas/despesas son saldos <b>acumulados del trimestre</b>
(ene-mar / jul-sep) y en junio y diciembre acumulados <b>del semestre</b>
(ene-jun / jul-dic). No es flujo trimestral comparable directamente.</li>
<li><b>Unidades</b>: la API OLinda entrega los valores monetarios <b>en
unidades de R$</b> (verificado: Itau prudencial Ativo Total 2026-03 =
2.834.355.732.183,17 = R$ 2,83 billones). El sitio web IF.data muestra los
mismos valores en <b>R$ mil</b>, y los captions/nombres de columna heredados
pueden decir "(R$ mil)": la API <u>no</u> esta en miles. El informe de cambio
esta en <b>USD</b> (unidades en la API; el sitio muestra miles de USD).
Indices (Basileia, Imobilizacao) vienen como fraccion (0,1477 = 14,77%).</li>
<li><b>Duplicados</b>: la API a veces devuelve filas exactas repetidas
(republicaciones); el framework las descarta.</li>
<li><b>Decimal</b>: el CSV de la API usa coma decimal brasilena; nombres de
cuenta con saltos de linea embebidos.</li>
<li><b>Licencia</b>: Open Data Commons ODbL. Mantenedor: Departamento de
Monitoramento do Sistema Financeiro (Desig) &mdash; ifdata@bcb.gov.br.</li>
</ul>
"""

ESCOPOS_INTRO = """
<p>La API OLinda expone 4 "formas de divulgacion" (parametro
<code>TipoInstituicao</code>). Las definiciones oficiales (metodologia IF.data
y Resoluciones CMN 4.950/2021 y BCB 168/2021):</p>
"""

ESCOPOS_DEFS = [
    ("1", "prudencial", "Conglomerados Prudenciales e Instituciones Independientes",
     "Grupo de instituciones financieras y no financieras consolidadas para fines "
     "prudenciales y contables, bajo el control de una institucion lider autorizada "
     "por el BCB. Incluye: (i) IFs y demas autorizadas por el BCB; (ii) administradoras "
     "de consorcio; (iii) instituciones de pago no autorizadas; (iv) entidades que "
     "adquieren operaciones de credito (incluido inmobiliario) o derechos crediticios "
     "(fomento mercantil/factoring, securitizadoras, sociedades de objeto exclusivo); "
     "(v) personas juridicas de participacion exclusiva en las anteriores; (vi) fondos "
     "de inversion donde el lider asume o retiene riesgos y beneficios sustanciales. "
     "NO integran: controladas en conjunto o en liquidacion, sociedades del Sandbox "
     "Regulatorio (y NO incluye aseguradoras).",
     "OLinda: desde 03/2014 (sel web 1004 2014-03..2023-06; sel 1009 desde 2023-09). "
     "Hasta 2023-08 se llamaba conglomerado prudencial conforme Res. CMN 4.280/2013."),
    ("2", "financeiro", "Conglomerados Financieros e Instituciones Independientes",
     "Subgrupo de las entidades del conglomerado prudencial autorizadas a funcionar "
     "por el BCB, presentadas de manera consolidada como una unica entidad. Desde "
     "2018, los datos de las instituciones independientes suman las operaciones de "
     "la entidad en el pais y sus agencias en el exterior. NO integran: instituciones "
     "de pago y administradoras de consorcio (a pesar de autorizadas).",
     "OLinda: desde 03/2000 (sel web 1005). Los informes de credito estan aqui "
     "desde 06/2012 (SCR) hasta 12/2024; migraron al escopo prudencial en 03/2025."),
    ("3", "individual", "Instituciones Individuales",
     "Cada institucion por personalidad juridica (CNPJ), a nivel NO consolidado. "
     "Las participaciones societarias en Brasil o en el exterior y las agencias en "
     "el exterior se registran como inversiones (metodo de equivalencia patrimonial).",
     "OLinda: desde 03/2000 (sel web 1006)."),
    ("4", "cambio", "Instituciones con Operaciones de Cambio",
     "Conglomerados prudenciales (Res. CMN 4.950/2021) e instituciones individuales "
     "fuera de conglomerados que realizaron operaciones de cambio en el periodo.",
     "OLinda: 12/2014..06/2023 (sel web 1007; verificado empiricamente: 2023-09 en "
     "adelante devuelve 0 filas). Solo contiene el informe 15 (Movimentacao de "
     "Cambio no Trimestre)."),
]

API_ENDPOINTS = [
    ("IfDataValores", "Valores de los informes",
     "IfDataValores(AnoMes=@AnoMes,TipoInstituicao=@TipoInstituicao,Relatorio=@Relatorio)?@AnoMes=AAAAMM&@TipoInstituicao={1|2|3|4}&@Relatorio='T'|'N'&$format=text/csv",
     "AnoMes: trimestre AAAAMM (03/06/09/12). TipoInstituicao: escopo 1-4. "
     "Relatorio: 'T' = todos, o numero de informe ('1'..'16'). Soporta $top, $skip, "
     "$filter, $orderby, $select. En CSV: 10 columnas (ver abajo)."),
    ("IfDataCadastro", "Registro de entidades",
     "IfDataCadastro(AnoMes=@AnoMes)?@AnoMes=AAAAMM&$format=text/csv",
     "Una fila por entidad que informo en el trimestre (incluye inactivas). "
     "17 columnas con clasificaciones y vinculos a conglomerados."),
    ("ListaDeRelatorio", "Catalogo de informes",
     "ListaDeRelatorio()?$format=json",
     "16 informes con NumeroRelatorio y NomeRelatorio."),
]

API_COLUMNAS = [
    ("TipoInstituicao", "int", "Escopo: 1=prudencial, 2=financeiro, 3=individual, 4=cambio"),
    ("CodInst", "texto", "Codigo de la entidad: CNPJ de 8 digitos (institucion) o codigo interno C####### (conglomerado). Ej.: 00000000 = Banco do Brasil; C0080099 = Itau prudencial"),
    ("AnoMes", "texto", "Trimestre AAAAMM (fecha-base, no de publicacion)"),
    ("NomeRelatorio", "texto", "Nombre del informe (ej. 'Resumo', 'Ativo', 'Carteira de credito ativa - por indexador')"),
    ("NumeroRelatorio", "texto", "Numero del informe (1-16; estable entre eras)"),
    ("Grupo", "texto", "Agrupacion de la cuenta dentro del informe ('null' cuando no aplica)"),
    ("Conta", "texto", "Codigo de la cuenta (renumerado en 2025-03; ver Eras)"),
    ("NomeColuna", "texto", "Nombre de la cuenta/rubrica (con saltos de linea embebidos a veces)"),
    ("DescricaoColuna", "texto", "Descripcion/composicion: formula de rubricas COSIF entre corchetes o texto explicativo"),
    ("Saldo", "decimal", "Valor: coma decimal brasilena; 'null' = NI (no informado). Unidades: ver Generalidades"),
]

CADASTRO_COLS = [
    ("CodInst", "texto", "Codigo de reporte: CNPJ 8 digitos o C####### (conglomerado). En escopo individual, CodInst = CNPJ."),
    ("Data", "texto", "Trimestre del registro (AAAAMM)"),
    ("NomeInstituicao", "texto", "Nombre oficial de la entidad"),
    ("DataInicioAtividade", "int", "Inicio de actividad (AAAAMM)"),
    ("Tcb", "codigo", "TCB - Tipo de Consolidado Bancario (clasificacion interna para segmentar bancarios/no bancarios). Dominio: ver tabla TCB."),
    ("Td", "codigo", "TD - Tipo de Consolidacion: C = Conglomerado, I = Institucion independiente"),
    ("Tc", "int", "TC - Tipo de Control: 1 = Publico, 2 = Privado nacional, 3 = Privado con control extranjero"),
    ("SegmentoTb", "texto", "Tipo de institucion (version textual del codigo TI): 'Banco Comercial', 'Cooperativa de Credito', 'Sociedade Corretora de TVM', etc. Dominio completo: ver tabla TI."),
    ("Atividade", "texto", "Actividad tipica de la institucion (ej. 'Credito Atacado', 'Mutuo PF con cuenta corriente', 'Corretoras de Cambio'). Vacio para muchas entidades."),
    ("Uf", "texto", "Estado (sigla) de la sede"),
    ("Municipio", "texto", "Municipio de la sede"),
    ("Sr", "codigo", "SR - Segmento Resolucion 4.553/2017: S1-S5 (vacio si no aplica, ej. entidades no bancarias)"),
    ("CodConglomeradoFinanceiro", "texto", "Codigo del conglomerado financiero al que pertenece (C#######)"),
    ("CodConglomeradoPrudencial", "texto", "Codigo del conglomerado prudencial al que pertenece (C#######)"),
    ("CnpjInstituicaoLider", "int", "CNPJ (8 digitos) de la institucion lider del conglomerado"),
    ("Situacao", "codigo", "A = Activa; I = Inactiva; F = En fusion/encampacion; LO = En liquidacion ordinaria; LE = En liquidacion extrajudicial"),
    ("DataInicioAtividade", "int", "(repetida por compatibilidad) inicio de actividad"),
]

# Traduccion al espanol de los dominios que llegan en portugues desde
# ifdata_cache/docs/nuevo_filtro202503.json (ver cargar()). Clave = sigla del dominio tal
# como se usa en las llamadas a tabla_dominio() mas abajo; cada valor mapea CODIGO (no el
# texto completo) a la traduccion, para no depender de que el texto oficial no cambie de
# forma. Un codigo que llegue del cache y no este aca se reporta en portugues con un aviso
# (ver tabla_dominio) en vez de fallar en silencio.
TRADUCCION_DOMINIO = {
    "TCB": {
        "b1": "Banco Comercial, Banco Multiple con Cartera Comercial, o Caja de Ahorro (Caixa Economica)",
        "b2": "Banco Multiple sin Cartera Comercial, Banco de Inversion, o Banco de Cambio",
        "b3S": "Cooperativa de Credito Singular (individual)",
        "b3C": "Central o Confederacion de Cooperativas de Credito",
        "b4": "Banco de Desarrollo",
        "n1": "No Bancario de Credito",
        "n2": "No Bancario de Mercado de Capitales",
        "n4": "Institucion de Pago",
    },
    "TC": {
        "1": "Publico",
        "2": "Privado Nacional",
        "3": "Privado con Control Extranjero",
    },
    "TD": {
        "C": "Conglomerado",
        "I": "Institucion independiente",
    },
    "SR": {
        "S1": "Segmento 1", "S2": "Segmento 2", "S3": "Segmento 3",
        "S4": "Segmento 4", "S5": "Segmento 5",
    },
    "TCip": {
        "1": "Tipo 1", "2": "Tipo 2", "3": "Tipo 3",
    },
    "TI": {
        "1": "Banco do Brasil - Banco Multiple",
        "2": "Banco Comercial",
        "3": "Banco Comercial Cooperativo",
        "4": "BNDES",
        "5": "Banco de Desarrollo",
        "6": "Caja de Ahorro Federal (Caixa Economica Federal)",
        "7": "Caja de Ahorro Estadual (Caixa Economica Estadual)",
        "8": "Banco Multiple",
        "9": "Cooperativa de Credito",
        "10": "Sociedad de Credito al Microemprendedor",
        "11": "Banco Multiple Cooperativo",
        "13": "Banco de Inversion",
        "14": "Sociedad de Credito, Financiamiento e Inversion",
        "15": "Sociedad Corredora de Valores (TVM)",
        "16": "Sociedad Distribuidora de Valores (TVM)",
        "19": "Sociedad de Arrendamiento Mercantil (leasing)",
        "21": "Sociedad Corredora de Cambio",
        "25": "Asociacion de Ahorro y Prestamo",
        "28": "Banco Comercial Extranjero - Sucursal en el pais",
        "29": "Compania Hipotecaria",
        "30": "Agencia de Fomento",
        "31": "Sociedad de Credito Inmobiliario - Repasadora (fondeo mayorista)",
        "39": "Banco de Cambio",
        "41": "Institucion de Pago",
        "43": "Sociedades de Credito Directo",
        "44": "Sociedades de Prestamo entre Personas (P2P)",
    },
}


def traducir_dominio(sigla: str, valores: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
    """(codigo, texto_pt) -> (codigo, texto_es o texto_pt con aviso, texto_pt original).

    El original en portugues siempre se conserva en la 3a posicion: la traduccion no
    reemplaza la evidencia, la acompana (mismo criterio que 'dominio observado' en
    deep_research_brazil).
    """
    tabla = TRADUCCION_DOMINIO.get(sigla, {})
    out = []
    for codigo, pt in valores:
        es = tabla.get(codigo)
        if es is None:
            print(f"aviso: {sigla} codigo {codigo!r} sin traduccion (queda en portugues): {pt!r}")
            es = f"{pt} [sin traducir]"
        out.append((codigo, es, pt))
    return out


ERAS = """
<p>La estructura cambia con el tiempo; hay dos grandes rupturas y varias
transiciones de cobertura:</p>
<table>
<tr><th>Cuando</th><th>Cambio</th><th>Impacto en los datos</th></tr>
<tr><td>03/2000</td><td>Inicio de la serie</td>
<td>Escopos financeiro e individual (Cosif). Capital (DLO) desde 12/2000 en
financeiro.</td></tr>
<tr><td>06/2012</td><td>Entran los informes de credito (SCR)</td>
<td>Escopo financeiro (sel 1008 hasta 2014-03; 1005 desde 2014-06). Solo
conglomerados financieros + independientes.</td></tr>
<tr><td>03/2014</td><td>Entra el escopo prudencial</td>
<td>Informes contables (Resumo/Ativo/Passivo/DRE) disponibles tambien en
prudencial (hasta entonces solo financeiro/individual).</td></tr>
<tr><td>12/2014</td><td>Entra el informe de cambio</td>
<td>Escopo 4 (instituciones con operaciones de cambio), informe 15.</td></tr>
<tr><td>03/2015</td><td>Capital en prudencial</td>
<td>Informe 5 (Informacoes de Capital) pasa al escopo prudencial; en
financeiro existio 12/2000..12/2014.</td></tr>
<tr><td>03/2017</td><td>Entra el informe de Segmentacion</td>
<td>Solo escopo prudencial.</td></tr>
<tr><td>09/2023</td><td>Fin del informe de cambio</td>
<td>El ultimo periodo con datos de cambio es 06/2023 (verificado en la API;
2023-09 en adelante devuelve 0 filas).</td></tr>
<tr><td><b>03/2025</b></td><td><b>Nuevo estandar contable COSIF 2025</b>
(Instrucciones Normativas BCB 426-433, vigentes desde 01/01/2025)</td>
<td><b>Renumeracion de codigos de cuenta</b> (ej. Resumo: Ativo Total
78182&rarr;140220). Estructura actualizada de ativos y resultados; passivo
mantiene estructura similar. <b>Migracion de credito</b>: los informes de
cartera pasan del escopo financeiro al prudencial. Se discontinua el informe
8 (por nivel de riesgo de la operacion) y entra el 16 (por carteras de
instrumentos financieros). Recomendacion del BCB: no mezclar cuentas por
codigo a traves de 03/2025; usar el nombre de la cuenta.</td></tr>
</table>
"""

MAPEO = [
    ("periodo", "AnoMes", "Trimestre AAAAMM (fecha-base)"),
    ("escopo", "TipoInstituicao", "1/2/3/4 &rarr; prudencial/financeiro/individual/cambio"),
    ("cod_inst", "CodInst", "CNPJ 8 digitos o C#######"),
    ("institucion", "(cadastro)", "Nombre resuelto desde IfDataCadastro del mismo trimestre"),
    ("informe", "NomeRelatorio", "Nombre del informe"),
    ("num_informe", "NumeroRelatorio", "Numero del informe"),
    ("grupo", "Grupo", "Agrupacion de la cuenta ('' si null)"),
    ("cod_cuenta", "Conta", "Codigo de cuenta (era-dependiente)"),
    ("cuenta", "NomeColuna", "Nombre de la cuenta, saltos de linea colapsados"),
    ("composicion", "DescricaoColuna", "Formula COSIF o descripcion"),
    ("valor", "Saldo", "Coma decimal &rarr; punto; null/NI &rarr; ''"),
]


ESTILO = """
  :root { --bg:#f4f6f9; --panel:#fff; --border:#dde3ec; --text:#1f2937;
          --muted:#6b7280; --accent:#003366; --accent2:#0a5daa; --hover:#eef4fb; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
         background:var(--bg); color:var(--text); font-size:14px; line-height:1.55; }
  header { background:var(--accent); color:#fff; padding:18px 28px;
           display:flex; flex-wrap:wrap; gap:24px; align-items:center; }
  header h1 { margin:0; font-size:19px; font-weight:600; }
  header .stats { display:flex; gap:18px; margin-left:auto; flex-wrap:wrap; }
  .stat { text-align:center; min-width:90px; background:rgba(255,255,255,.08);
          border-radius:8px; padding:6px 12px; }
  .stat b { display:block; font-size:18px; } .stat span { font-size:11px; opacity:.85; }
  .barra { background:var(--panel); border-bottom:1px solid var(--border);
           padding:12px 28px; display:flex; flex-wrap:wrap; gap:10px;
           position:sticky; top:0; z-index:5; }
  .barra input { padding:7px 10px; border:1px solid var(--border); border-radius:6px;
                 font-size:13px; min-width:260px; flex:1; max-width:480px; }
  .barra .contador { align-self:center; color:var(--muted); font-size:12.5px; }
  .barra nav { display:flex; gap:6px; flex-wrap:wrap; }
  .barra nav a { padding:6px 10px; border-radius:6px; background:#eaf0f8;
                 color:var(--accent); text-decoration:none; font-size:12.5px; }
  .barra nav a:hover { background:#dfe9f5; }
  main { padding:18px 28px 60px; max-width:1280px; }
  section { background:var(--panel); border:1px solid var(--border);
            border-radius:10px; padding:20px 24px; margin-bottom:22px; }
  section > h2 { margin:0 0 12px; color:var(--accent); font-size:17px;
                 border-bottom:2px solid var(--border); padding-bottom:8px; }
  section > h3 { color:var(--accent2); font-size:14.5px; margin:18px 0 8px; }
  table { border-collapse:collapse; width:100%; margin:8px 0 14px; }
  th { background:#eaf0f8; color:var(--accent); text-align:left; padding:7px 10px;
       font-size:12px; text-transform:uppercase; letter-spacing:.03em;
       border-bottom:2px solid var(--border); }
  td { padding:7px 10px; border-bottom:1px solid var(--border); vertical-align:top; }
  tr:hover td { background:var(--hover); }
  code { background:#eef2f7; border-radius:4px; padding:1px 5px;
         font-family:ui-monospace,Consolas,monospace; font-size:12.5px; }
  .badge { display:inline-block; background:#e3edf7; color:var(--accent2);
           border-radius:10px; padding:1px 8px; font-size:11px; white-space:nowrap; }
  .mono { font-family:ui-monospace,Consolas,monospace; white-space:nowrap; }
  details.rep { border:1px solid var(--border); border-radius:8px;
                margin:10px 0; overflow:hidden; }
  details.rep > summary { cursor:pointer; padding:12px 16px; background:#f0f5fb;
                          color:var(--accent); font-weight:600; list-style:none; }
  details.rep > summary:hover { background:#e6eef8; }
  details.rep[open] > summary { border-bottom:1px solid var(--border); }
  .rep-body { padding:12px 16px; }
  .notas { background:#f8fafd; border-left:3px solid var(--accent2);
           padding:10px 14px; margin:10px 0; font-size:13px; }
  .notas b { color:var(--accent); }
  .oculto { display:none; }
  footer { padding:10px 28px 30px; color:var(--muted); font-size:11.5px;
           line-height:1.5; }
  dl.metadatos { display:grid; grid-template-columns:170px 1fr; gap:3px 14px;
                 margin:6px 0; }
  dl.metadatos dt { color:var(--muted); font-size:12px; }
  dl.metadatos dd { margin:0; font-size:12.5px; }
"""

JS = """
function escBusqueda() {
  const q = document.getElementById('fTexto').value.trim().toLowerCase();
  let visibles = 0;
  document.querySelectorAll('[data-blob]').forEach(el => {
    const ok = !q || el.dataset.blob.toLowerCase().includes(q);
    el.classList.toggle('oculto', !ok);
    if (ok && el.tagName === 'TR') visibles++;
  });
  // abrir/cerrar detalles segun tenga filas visibles
  document.querySelectorAll('details.rep').forEach(d => {
    if (q) {
      const filas = d.querySelectorAll('tr[data-blob]');
      const algunas = [...filas].some(f => !f.classList.contains('oculto'));
      const cuerpo = d.querySelector('.rep-body');
      if (algunas) { d.open = true; cuerpo.classList.remove('oculto'); }
      else { d.open = false; cuerpo.classList.add('oculto'); }
    } else {
      d.querySelector('.rep-body').classList.remove('oculto');
    }
  });
  const contador = document.getElementById('contador');
  if (q) contador.textContent = visibles.toLocaleString('es') + ' filas de cuentas coinciden';
  else contador.textContent = '';
}
document.getElementById('fTexto').addEventListener('input', escBusqueda);
"""


def tabla_dominio(nombre, sigla, valores_pt):
    """valores_pt: [(codigo, texto_portugues)], tal como llega del cache oficial."""
    traducidos = traducir_dominio(sigla, valores_pt)
    filas = "".join(
        f"<tr data-blob=\"{esc(v)} {esc(es)} {esc(pt)}\"><td class='mono'><b>{esc(v)}</b></td>"
        f"<td>{esc(es)}<br><span style='color:#6b7280;font-size:11.5px'>PT: {esc(pt)}</span></td></tr>"
        for v, es, pt in traducidos)
    return f"<h3>{esc(nombre)}</h3><table><tr><th>Codigo</th><th>Significado (ES, con original PT)</th></tr>{filas}</table>"


def main():
    ap = argparse.ArgumentParser(description="Genera el diccionario HTML de IFDATA")
    ap.add_argument("-o", "--salida", default="ifdata_diccionario.html")
    ap.add_argument("--periodo", default="", help="trimestre del inventario de cuentas (defecto: el último volcado)")
    args = ap.parse_args()

    periodo = args.periodo or ultimo_volcado()
    etiqueta = f"{periodo[:4]}-{periodo[4:]}"
    datos = cargar(periodo)
    disp = disponibilidad(datos)
    filtro = {f["n"]: f["d"] for f in datos["filtro"]}

    dom_tcb = [(v["v"], v["n"]) for v in filtro.get("TCB - Tipo de Consolidado Bancário", [])]
    dom_tc = [(v["v"], v["n"]) for v in filtro.get("TC - Tipo de Controle", [])]
    dom_td = [(v["v"], v["n"]) for v in filtro.get("TD - Tipo de Consolidação", [])]
    dom_sr = [(v["v"], v["n"]) for v in filtro.get("SR - Segmento Resolução nº 4.553/2017", [])]
    dom_tcip = [(v["v"], v["n"]) for v in filtro.get("TCip - Resolução nº 197/2022", [])]
    dom_ti = [(v["v"], v["n"]) for v in filtro.get("TI - Tipo de Instituição", [])]

    partes = []
    n_cuentas = 0
    for rel in sorted(datos["relatorios"], key=lambda r: int(r["NumeroRelatorio"])):
        num = int(rel["NumeroRelatorio"])
        nombre = rel["NomeRelatorio"]
        nk = norm(nombre)
        trels = datos["trels"].get(nk, [])
        trel = trels[0] if trels else None
        inv = datos["inventario"].get(nk, {})
        filas_inv = []
        for (conta, nome, desc, grupo) in sorted(inv, key=lambda x: int(x[0])):
            escopos = inv[(conta, nome, desc, grupo)]
            nombres_e = ([("prudencial" if 1 in escopos else "")]
                         + [("financeiro" if 2 in escopos else "")]
                         + [("individual" if 3 in escopos else "")])
            badges = "".join(f"<span class='badge'>{e}</span> "
                             for e in [x for x in nombres_e if x])
            filas_inv.append(
                f"<tr data-blob=\"{esc(nome)} {conta} {esc(desc)} {esc(grupo)}\">"
                f"<td class='mono'>{esc(conta)}</td><td><b>{esc(nome)}</b></td>"
                f"<td style='font-size:12px;color:#6b7280'>{esc(desc)}</td>"
                f"<td>{badges or '&mdash;'}</td></tr>")
            n_cuentas += 1
        # disponibilidad
        ventanas = []
        for escopo in ("prudencial", "financeiro", "individual", "cambio"):
            per = disp.get(nk, {}).get(escopo)
            if per:
                ps = sorted(per)
                ventanas.append(f"<span class='badge'>{escopo}</span> {min(ps)}&ndash;{max(ps)} ({len(ps)})")
        notas = ""
        if trel and trel.get("rp"):
            texto = trel["rp"].replace("<br />", "\n").replace("<br>", "\n")
            notas = f"<div class='notas'><b>Notas tecnicas oficiales del informe (portugues):</b><br>{esc(texto).replace(chr(10), '<br>')}</div>"
        elif num in (8, 15):
            # trels extra de informes discontinuados
            for patron in ("nivel de risco", "cambio"):
                for nk2, ts in datos["trels"].items():
                    if patron in nk2:
                        texto = ts[0]["rp"].replace("<br />", "\n")
                        notas = (f"<div class='notas'><b>Notas tecnicas (version final del informe, "
                                 f"{esc(patron)}):</b><br>{esc(texto).replace(chr(10), '<br>')}</div>")
                        break
                if notas:
                    break
        caption = esc(" ".join((trel.get("cp") or "").replace("<br", " ").split())) if trel else ""
        fuente = FUENTES.get(nk, FUENTES.get(nk.split(" - ")[0], ""))
        disc = " <span class='badge' style='background:#fde8e8;color:#b91c1c'>DESCONTINUADO</span>" if num == 8 else ""
        nuevo15 = " <span class='badge' style='background:#e8fde8;color:#15803d'>SOLO ESCOPO CAMBIO (4)</span>" if num == 15 else ""
        tabla_inv = ""
        if filas_inv:
            tabla_inv = (f"<h3>Inventario de cuentas ({etiqueta}, desde el crudo)</h3>"
                         "<table><tr><th>Cod.</th><th>Cuenta (NomeColuna)</th>"
                         "<th>Composicion / descripcion (DescricaoColuna)</th><th>Escopos</th></tr>"
                         + "".join(filas_inv) + "</table>")
        elif num == 15:
            tabla_inv = (f"<p style='color:#6b7280'>Sin datos en {etiqueta} (informe finalizado en 06/2023). "
                         "Cuentas tipicas: 23024-23035 y 87404-87413 (N. Operacoes y Valor por tipo de "
                         "operacion de cambio: exportaciones, importaciones, transferencias financieras, etc.).</p>")
        partes.append(f"""
<details class="rep" data-blob="{esc(nombre)} {num} {esc(fuente)}">
<summary>{num}. {esc(nombre)}{disc}{nuevo15}</summary>
<div class="rep-body">
<dl class="metadatos">
<dt>Numero OLinda</dt><dd>{num} (&mdash; <code>@Relatorio='{num}'</code>)</dd>
<dt>Fuente</dt><dd>{esc(fuente)}</dd>
<dt>Unidades</dt><dd>{esc(UNIDADES.get(num, ''))}</dd>
<dt>Caption oficial</dt><dd>{caption or '&mdash;'}</dd>
<dt>Disponibilidad</dt><dd>{'<br>'.join(ventanas) or 'ver Eras'}</dd>
</dl>
{notas}
{tabla_inv}
</div>
</details>""")

    informes_html = "".join(partes)

    viejo, nuevo = datos["renumeracion"]
    ren_html = "<table><tr><th colspan='2'>Era 2000-03 (Resumo, BB)</th><th colspan='2'>Era 2025-03+ (Resumo, BB)</th></tr>"
    for i in range(max(len(viejo), len(nuevo))):
        v = f"<td class='mono'>{viejo[i][0]}</td><td>{esc(viejo[i][1])}</td>" if i < len(viejo) else "<td></td><td></td>"
        n = f"<td class='mono'>{nuevo[i][0]}</td><td>{esc(nuevo[i][1])}</td>" if i < len(nuevo) else "<td></td><td></td>"
        ren_html += f"<tr>{v}{n}</tr>"
    ren_html += "</table>"

    escopos_html = ESCOPOS_INTRO + "<table><tr><th>Tipo</th><th>Escopo</th><th>Nombre oficial</th><th>Definicion</th><th>Disponibilidad</th></tr>"
    for num, nombre, oficial, definicion, disp_txt in ESCOPOS_DEFS:
        escopos_html += (f"<tr data-blob='{esc(nombre)} {esc(oficial)} {esc(definicion)}'>"
                         f"<td class='mono'><b>{num}</b></td><td><b>{nombre}</b></td>"
                         f"<td>{esc(oficial)}</td><td>{esc(definicion)}</td>"
                         f"<td style='font-size:12px'>{esc(disp_txt)}</td></tr>")
    escopos_html += "</table>"

    api_html = ("<table><tr><th>Endpoint</th><th>Que devuelve</th><th>URL</th><th>Parametros</th></tr>"
                + "".join(f"<tr data-blob=\"{esc(n)} {esc(d)}\"><td class='mono'><b>{esc(n)}</b></td>"
                          f"<td>{esc(q)}</td><td><code>{esc(u)}</code></td><td>{esc(d)}</td></tr>"
                          for n, q, u, d in API_ENDPOINTS)
                + "</table><h3>Columnas del CSV de valores</h3><table><tr><th>Columna</th><th>Tipo</th><th>Significado</th></tr>"
                + "".join(f"<tr data-blob=\"{esc(c)} {esc(s)}\"><td class='mono'><b>{esc(c)}</b></td>"
                          f"<td>{esc(t)}</td><td>{esc(s)}</td></tr>" for c, t, s in API_COLUMNAS)
                + "</table>")

    cadastro_html = ("<table><tr><th>Columna</th><th>Tipo</th><th>Significado</th></tr>"
                     + "".join(f"<tr data-blob=\"{esc(c)} {esc(s)}\"><td class='mono'><b>{esc(c)}</b></td>"
                               f"<td>{esc(t)}</td><td>{esc(s)}</td></tr>" for c, t, s in CADASTRO_COLS)
                     + "</table>"
                     + tabla_dominio("TCB - Tipo de Consolidado Bancario", "TCB", dom_tcb)
                     + tabla_dominio("TC - Tipo de Control", "TC", dom_tc)
                     + tabla_dominio("TD - Tipo de Consolidacion", "TD", dom_td)
                     + tabla_dominio("SR - Segmento (Res. 4.553/2017)", "SR", dom_sr)
                     + tabla_dominio("TCip (Res. 197/2022)", "TCip", dom_tcip)
                     + tabla_dominio("TI - Tipo de Institucion (SegmentoTb)", "TI", dom_ti))

    mapeo_html = ("<table><tr><th>Columna tidy (ifdata.py)</th><th>Origen OLinda</th><th>Transformacion</th></tr>"
                  + "".join(f"<tr data-blob=\"{esc(a)} {esc(b)}\"><td class='mono'><b>{esc(a)}</b></td>"
                            f"<td class='mono'>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in MAPEO)
                  + "</table>")

    n_informes = len(datos["relatorios"])
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IFDATA BCB &mdash; Diccionario de datos</title>
<style>{ESTILO}</style>
</head>
<body>
<header>
  <h1>IFDATA BCB &mdash; Diccionario de datos completo</h1>
  <div class="stats">
    <div class="stat"><b>{n_informes}</b><span>informes</span></div>
    <div class="stat"><b>{len(ESCOPOS_DEFS)}</b><span>escopos</span></div>
    <div class="stat"><b>{n_cuentas}</b><span>cuentas inventariadas</span></div>
    <div class="stat"><b>2000&ndash;</b><span>desde mar/2000</span></div>
  </div>
</header>
<div class="barra">
  <nav>
    <a href="#generalidades">Generalidades</a>
    <a href="#escopos">Escopos</a>
    <a href="#api">API</a>
    <a href="#cadastro">Registro</a>
    <a href="#informes">Informes</a>
    <a href="#eras">Eras</a>
    <a href="#mapeo">Framework</a>
  </nav>
  <input type="search" id="fTexto" placeholder="Buscar cuenta, codigo, informe, dominio...">
  <span class="contador" id="contador"></span>
</div>
<main>
<section id="generalidades"><h2>1. Generalidades</h2>{GENERALIDADES}</section>
<section id="escopos"><h2>2. Escopos (TipoInstituicao)</h2>{escopos_html}</section>
<section id="api"><h2>3. API OLinda</h2>
<p>Base: <code>https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata</code>.
Formato CSV con <code>$format=text/csv</code> (UTF-8). Documentacion oficial:
<a href="https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao">/documentacao</a>
&middot; <a href="https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/swagger-ui3#/">Swagger</a>.</p>
{api_html}</section>
<section id="cadastro"><h2>4. Registro de entidades (IfDataCadastro)</h2>
<p>Una fila por entidad presente en el trimestre (incluye inactivas: en 2026-03,
5.856 entidades, de las cuales 2.384 activas). Es la tabla de dimensiones para
resolver nombres, conglomerados y clasificaciones.</p>
{cadastro_html}</section>
<section id="informes"><h2>5. Informes (16) &mdash; definiciones, notas y cuentas</h2>
<p>Cada informe con su fuente, unidades, disponibilidad por escopo, notas
tecnicas oficiales y el inventario de cuentas verificado contra el cache
({etiqueta}). Usa el buscador para filtrar cuentas por nombre/codigo.</p>
{informes_html}</section>
<section id="eras"><h2>6. Eras y cambios historicos</h2>{ERAS}
<h3>Ejemplo de renumeracion de cuentas (Resumo, Banco do Brasil)</h3>{ren_html}</section>
<section id="mapeo"><h2>7. Mapeo del framework (ifdata.py)</h2>
<p>El CSV tidy que genera <code>ifdata.py</code> a partir del CSV crudo de la
API (cache <code>ifdata_cache/</code>):</p>{mapeo_html}</section>
</main>
<footer>
Generado por diccionario_ifdata.py (bcb-scraper). Fuentes: metodologia oficial
IF.data (www3.bcb.gov.br/ifdata), PDF "Esclarecimentos e Metodologia" (BCB/Desig),
catalogos internos del sitio (rest/relatorios*), API OLinda y verificaciones
empiricas documentadas. Unidades de la API verificadas contra magnitudes
conocidas (Itau/BB 2025-2026).
</footer>
<script>{JS}</script>
</body>
</html>"""

    Path(args.salida).write_text(html, encoding="utf-8")
    print(f"[+] Diccionario -> {args.salida} "
          f"({Path(args.salida).stat().st_size / 1024:.0f} KB, "
          f"{n_informes} informes, {n_cuentas} cuentas)")


if __name__ == "__main__":
    main()
