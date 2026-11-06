# Scripts del pipeline (docstring completo y argumentos)

> Generado por `herramientas/generar_spec.py` el 2026-11-06. No editar a mano: se sobrescribe.


## `pipeline/almacen.py` (424 líneas)

```text
Arquitectura de datos: capas, procedencia y rutas.

EL PROBLEMA QUE RESUELVE
------------------------
Antes de esto había 45 CSV sueltos en la raíz, mezclados con el código, sin forma de
responder tres preguntas básicas:

  - ¿de dónde salió este archivo?
  - ¿cuándo se bajó?
  - ¿es lo que la fuente sirvió, o algo que nosotros derivamos?

La tercera es la que más duele. `cvm_dfp_bancos_2024.csv` parecía un dato de la CVM y en
realidad era el resultado de un filtro nuestro — un filtro que estuvo mal y metió 72% de
empresas que no son bancos. Como el ZIP original nunca se guardó, no se podía ni auditar
qué había hecho el filtro ni re-derivar sin volver a descargar.

LAS DOS CAPAS
-------------
    datos/crudo/<fuente>/<dataset>/<version>/    exactamente lo que sirvió la fuente
    datos/derivado/<fuente>/<dataset>/           lo que produce nuestro código

La regla que decide: **crudo es lo que la fuente sirvió, ANTES de cualquier filtro
nuestro.** Si nuestro código lo tocó, es derivado. Un CSV filtrado por bancos es derivado
aunque venga de la CVM.

`crudo/` no se edita nunca. Si un parser falla, se arregla el parser.

PROCEDENCIA
-----------
Cada archivo crudo lleva al lado un `_manifiesto.json` con URL, sha256, tamaño y momento
de descarga. Eso es lo que permite decir "este número salió de esta URL, este día, y el
archivo sigue siendo el mismo".

Los derivados llevan su propio manifiesto que además nombra los crudos de los que salieron,
para poder rehacer la cadena.
```

## `pipeline/bcb_api.py` (316 líneas)

Importa del pipeline: `certificados`

Subcomandos: `datos` — descarga los valores de series; `ultimos` — ultimas N observaciones de una serie

Argumentos: `codigos` — codigo(s) de serie; `--desde` — fecha inicial DD/MM/AAAA; `--hasta` — fecha final DD/MM/AAAA; `-o` — CSV de salida; `--ancho` — formato ancho: una columna por serie; `-n` — cantidad (defecto: 10)

```text
Descarga de DATOS (valores) de las series del SGS/BCB via la API oficial.

Endpoints usados (documentados en https://dadosabertos.bcb.gov.br/):
  GET https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados
      ?formato=json|csv&dataInicial=DD/MM/AAAA&dataFinal=DD/MM/AAAA
  GET https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/{n}

Nota: la API limita las series diarias a ventanas de 10 anios (3652 dias);
el script lo gestiona automaticamente. Metadatos: usar bcb_scraper.py
(no hay endpoint de metadatos en la API actual).

OJO con los errores: una serie inexistente NO da 404. La API contesta una pagina
HTML, con un status que varia (visto 200 y 502), asi que el status code no alcanza
para saber si la respuesta sirve. Ver RespuestaNoJSON mas abajo.

Ejemplos:
  python3 bcb_api.py datos 432                       # serie completa (JSON->CSV)
  python3 bcb_api.py datos 432 11 433 -o tasas.csv   # varias series a un CSV
  python3 bcb_api.py datos 433 --desde 01/01/2024    # rango de fechas
  python3 bcb_api.py datos 11 432 --ancho -o x.csv   # una columna por serie
  python3 bcb_api.py ultimos 432 -n 5                # ultimas 5 observaciones
  # varias series en paralelo: se descargan una a una automaticamente
```

## `pipeline/certificados.py` (149 líneas)

```text
Hace que Python confie en los certificados que ya confia el sistema operativo.

POR QUE EXISTE ESTE MODULO
--------------------------
En una red corporativa el trafico HTTPS suele pasar por un proxy que lo inspecciona
(Zscaler, Netskope, Fortinet, Palo Alto, o el antivirus con "escaneo HTTPS" activado).
Ese proxy corta la conexion y la vuelve a firmar con una CA propia de la empresa, asi
que el certificado que llega NO es el de olinda.bcb.gov.br: es uno emitido por la CA
corporativa.

Windows y el navegador confian en esa CA porque el equipo la tiene instalada por
politica de dominio; por eso las paginas del BCB abren bien en Chrome. Python NO la ve:
requests valida contra el bundle de certifi, que solo trae las CA publicas. El resultado
es que TODOS los hosts fallan a la vez con:

    SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED]
    certificate verify failed: self-signed certificate in certificate chain'))

envuelto en un "Max retries exceeded with url: ...", que es lo que urllib3 imprime
cuando agota sus intentos. El "max retries" despista: no es que el BCB este caido ni que
nos esten limitando el ritmo. Si el error fuese del servidor, fallarian unos hosts y
otros no; que fallen cvm.gov.br, bndes.gov.br y olinda.bcb.gov.br a la vez, y siempre
por certificado, es la firma del proxy.

truststore resuelve el caso parcheando ssl.SSLContext para que valide contra el almacen
del sistema (el de Windows en el equipo del proyecto, el de OpenSSL en Linux/WSL). Eso
arregla de una sola vez requests (bcb_api, bcb_scraper, ifdata, extraer_fuentes) y
urllib.request (bajar_documentacion, verificar.py), porque los dos terminan en el mismo
ssl del stdlib.

Si truststore no esta instalado, se respeta REQUESTS_CA_BUNDLE / SSL_CERT_FILE por si
alguien exporto la CA de la empresa a mano, y si tampoco hay nada se sigue adelante en
silencio: en una red sin proxy no hace falta nada de esto y no queremos ruido.

USO
---
    import certificados   # basta con importarlo, se activa solo

Va como primer import de cada script que salga a la red, ANTES de requests.
```

## `pipeline/diccionario_ifdata.py` (743 líneas)

Importa del pipeline: `almacen`

```text
Genera el DICCIONARIO COMPLETO de la base IFDATA del BCB en HTML
autocontenido, a partir de:
  - datos/crudo/bcb_ifdata/catalogo/actual/relatorios.json            (catalogo OLinda: 16 informes)
  - ifdata_cache/docs/rest_rel2000a2024.json      (catalogo historico web)
  - ifdata_cache/docs/rest_relatorios2025a2030.json (catalogo web era nueva)
  - ifdata_cache/docs/trel_202503/*.json    (estructura+notas por informe)
  - ifdata_cache/docs/nuevo_filtro202503.json (dominios TCB/TC/TD/TI/SR/TCip)
  - ifdata_cache/docs/nuevo_info202503.json  (descripciones de etiquetas)
  - datos/crudo/bcb_ifdata/valores/actual/valores_202603_{1,2,3}.csv  (inventario de cuentas)
  - datos/crudo/bcb_ifdata/valores/actual/valores_200003_3.csv        (ejemplos de renumeracion de era)
  - datos/crudo/bcb_ifdata/cadastro/actual/cadastro_202603.csv         (dominios empiricos del registro)

Las secciones narrativas (generalidades, escopos, API, eras) provienen de la
metodologia oficial de la pagina IF.data, del PDF "Esclarecimentos e
Metodologia" del BCB y de verificaciones empiricas documentadas.

Uso:
    python3 diccionario_ifdata.py [-o ifdata_diccionario.html]
```

## `pipeline/exportar_web_bancos.py` (192 líneas)

```text
Exporta la capa gold de bancos (datos/gold/bk_*.parquet) al JSON del sitio «Bancos Brasil».

Por qué existe: el sitio es estático y sin build, y toda su cifra vive en
`sitio/data/<tabla>.json` con el formato del spec macro §7.1
(`{tabla, columnas, filas}`); Power BI lee los mismos parquet (spec bancos §11). Este
script es el único puente entre ambas capas: aquí no se calcula nada, solo se serializa.

Qué produce en `sitio/data/` (se regenera entero en cada corrida):
- `<tabla>.json` para cada `datos/gold/bk_*.parquet`, salvo `bk_cartera_totales`, que es
  auxiliar del verificador (decisión 59) y está fuera del contrato del sitio.
- `banco/<slug>/<tabla>.json` para `bk_panel`, `bk_cartera` y `bk_roe_arbol`: las filas de
  ese banco, para que la ficha cargue solo lo suyo (spec bancos §7). En `bk_roe_arbol` la
  columna es `entidad`, que también trae grupos agregados («Modelo de negocio|Grandes»…):
  esas filas no son de ningún banco y quedan solo en la tabla completa.
- `metrica/<metrica>/bk_panel.json` y `optica/<slug>/bk_grupo.json`: los dos megatablones
  (17 y 9 MB) partidos por métrica y por óptica (encargo 75), para que las páginas de
  sistema carguen solo el trozo que muestran. Van descritas en el manifiesto con las
  claves `metricas` y `opticas` (filas y bytes).
- `_manifiesto.json` siempre, aunque no haya tablas: el sitio detecta desde ahí qué tablas
  existen (decisión 65b). Por tabla: filas, columnas, rango de fechas, sha256 del parquet
  de origen y bytes del JSON.

Licencias (spec web bancos §9, criterio 17): antes de escribir nada, falla si alguna
columna contiene `px_`, `pbv`, `pe_`, `bbg`, `bloomberg`, `consenso` o `target`.

Uso (desde la raíz del repo, Windows con `-X utf8`):
    python -X utf8 exportar_web_bancos.py
```

## `pipeline/ifdata.py` (865 líneas)

Importa del pipeline: `almacen`, `certificados`

Subcomandos: `relatorios` — catalogo de informes disponibles (numero y nombre); `instituciones` — buscar entidades en el registro del trimestre; `cadastro` — exportar el registro de entidades; `valores` — exportar valores (todas las entidades); `datos` — datos de UNA entidad a lo largo del tiempo ; `colectar` — descarga masiva al cache (valores completos + 

Argumentos: `--periodo` — un trimestre AAAAMM (ej. 202603); `--desde` — trimestre inicial del rango (AAAAMM); `--hasta` — trimestre final del rango (AAAAMM); `--delay` — pausa entre peticiones en segundos (defecto: 0.3); `--refrescar` — ignorar el cache y volver a descargar; `--max-edad-dias` — dias tras los cuales un trimestre reciente se vuelve a bajar ; `-q` — silenciar el progreso; `--periodo` — trimestre AAAAMM; `--texto` — texto a buscar en nombre/codigo/UF/municipio; `--todos` — incluir entidades inactivas o en liquidacion; `--limite` — maximo de resultados a listar (defecto: 40); `--texto` — filtrar por texto; `--situacion` — filtrar por situacion (A=activa, I=inactiva, ; `--informe` — nombre o numero de informe (ej. Resumo o 1); vacio = todos; `--cuenta` — filtrar cuentas por texto (ej. 'Ativo Total'); `--institucion` — codigo (C0080099 / 60394079) o nombre (ej. 'itau'); `--informe` — nombre o numero de informe (reduce la descarga); `--cuenta` — filtrar cuentas por texto (ej. 'Ativo Total'); `--informe` — nombre o numero de informe a descargar; se puede repetir o ; `--sin-cadastro` — no descargar los registros de entidades

```text
Framework de descarga del IFDATA (Informaciones Financieras Trimestrales)
del Banco Central do Brasil: datos financieros de las entidades reguladas
(bancos, financieras, cooperativas, corretoras, distribuidoras,
administradoras de consorcio y conglomerados financieros/prudenciales, que
pueden incluir aseguradoras y otras entidades no bancarias del grupo).

Fuente: API OLinda (OData) de datos abiertos del BCB:
  https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata

  - IfDataValores(AnoMes, TipoInstituicao, Relatorio) -> valores del trimestre
  - IfDataCadastro(AnoMes)                            -> registro de entidades
  - ListaDeRelatorio()                                -> catalogo de informes

Escopos (TipoInstituicao):
  1 = prudencial   conglomerado prudencial (IFs + administradoras de consortium,
                   instituciones de pago, adquirentes de credito/factoring,
                   securitizadoras, holdings puras y fondos con riesgo retenido)
  2 = financeiro   conglomerado financiero (solo entidades autorizadas por el BCB)
  3 = individual   la entidad aislada (por CNPJ, no consolidado)
  4 = cambio       instituciones con operaciones de cambio en el periodo
                   (solo informe 15, 12/2014-06/2023)

Trimestral (mar/jun/sep/dic) desde 2000-03. Valores en R$ (unidades).
Publicacion con ~60 dias de rezago (~90 para la base de diciembre).

Cambios de era a tener en cuenta:
  - 2025-03: el BCB renumero codigos de cuentas y migro los informes de
    credito del escopo financeiro (2) al prudencial (1).
  - Los informes disponibles varian por escopo y epoca.

Flujo y capas (ver almacen.py):

  descarga -> datos/crudo/bcb_ifdata/{catalogo,cadastro,valores}/actual/
                 el CSV tal cual lo sirvio OLinda, con manifiesto (URL + sha256).
                 Hace de cache: una respuesta vacia valida tambien queda registrada
                 por bytes/sha256, y los ultimos trimestres caducan a los 95 dias
                 porque la base de diciembre republica los cuatro trimestres previos.
           -> normalizacion y filtros nuestros
           -> datos/derivado/bcb_ifdata/{cadastro,valores,datos}/
                 CSV tidy con manifiesto que nombra los crudos de los que salio y
                 el comando que lo produjo.

Todo lo que sale de `cadastro`, `valores` y `datos` es DERIVADO aunque cada numero
venga del BCB: esta filtrado por escopo, informe, cuenta, institucion o situacion.
```

## `pipeline/preparar_bancos_powerbi.py` (666 líneas)

Importa del pipeline: `almacen`, `certificados`, `ifdata`

Argumentos: `--desde` — trimestre inicial AAAAMM (opcional); `--hasta` — trimestre final AAAAMM (opcional)

```text
Prepara balances y resultados trimestrales de bancos brasileños para Power BI.

POR QUÉ EXISTE
--------------
IF.data publica informes planos por trimestre, escopo y cuenta. Tres cosas impiden
usar esos CSV directamente en un panel:

1. el informe 4 (Demonstração de Resultado) viene acumulado según la Lei 4.595, con
   reset en julio: marzo y septiembre son acumulados de enero-marzo y julio-septiembre,
   mientras junio y diciembre son acumulados de enero-junio y julio-diciembre;
2. los códigos de cuenta cambian en la frontera COSIF 2025-03, así que la serie
   continua no puede armarse por código;
3. la capa cruda completa trae todas las instituciones del escopo prudencial, y el
   panel usa un universo aprobado por Pablo.

Este módulo lee únicamente el crudo ya descargado por `ifdata.py colectar`, no sale a
la red, filtra el universo declarado en `definiciones/bcb_ifdata__bancos_balances.json`,
des-acumula los flujos, conserva intactos los stocks y escribe parquets atómicos en
`datos/gold/`.

Receta:

    python ifdata.py colectar --desde 201403 --hasta 202606 --escopo prudencial         --informe 2 --informe 3 --informe 4
    python preparar_bancos_powerbi.py
```

## `pipeline/preparar_credito_paginas_powerbi.py` (763 líneas)

Importa del pipeline: `almacen`, `bcb_api`, `certificados`

Argumentos: `--descargar` — baja antes las series SGS 20714 y 4389; `--solo-descargar` — solo baja las series SGS (runner, paso D7)

```text
Tablas de las hojas "Crédito: panorama" y "Crédito: calidad" del PBIP dual (prefijo ``cre_``), trimestral.

POR QUÉ EXISTE
--------------
Pablo vio la hoja 8 "Bancos" el 2026-10-13 y pidió otro concepto (``docs/orquestacion/41_diseno_paginas_credito.md``):
no comparar bancos, sino ver **de qué está hecho el crédito** del panel según dos cortes que se cruzan:

* **tipo de institución**: segmento S1–S4, propiedad, modelo de negocio, tradicional vs fintech; siempre grupos,
  nunca bancos sueltos;
* **tipo de crédito**: personas / empresas y sus modalidades (tarjeta, consignado, vehículos, capital de giro…).

Un botón decide qué dimensión se apila. El slicer de tipo tiene solo Total, Personas y Empresas (Pablo,
2026-10-20): apilado por tipo de crédito, "Total" muestra Personas contra Empresas (azul / naranjo) y cada uno
muestra sus modalidades. Del 2026-10-14 al 2026-10-20 "Total" apilaba las 16 modalidades y cada modalidad era un
nodo del slicer; se sacaron (no se elige un producto suelto). "Panorama" muestra nivel,
aportes al crecimiento, tabla y momentum;
"calidad", NPL / NIM / ROE y la tasa de los créditos nuevos contra el CDI. Reemplaza a ``preparar_bancos_pagina_powerbi``.

Por qué los datos son estos y no otros
--------------------------------------
* **IF.data, no SGS.** Solo IF.data abre el crédito por banco (y así por grupo). Es trimestral: nada de m/m. Lo
  mensual del sistema (consignado privado, dirigido / no dirigido) va a la hoja 9, con el SGS.
* **Cartera activa en Brasil de los informes 11 (personas) y 13 (empresas), no la cuenta del balance.** Solo
  esos informes abren por modalidad, y para que el apilado sume hay que usar la misma fuente en el total. El
  "Total da Carteira" del BCB incluye las operaciones en el exterior (Itaú 2014-T2: R$ 124 mil millones solo en
  empresas); aquí un nodo vale la suma de sus modalidades, que es Brasil, y se valida que Σ modalidades +
  exterior = total publicado. No coincide con "Operações de crédito" del balance (hoja 8): la cartera incluye
  tarjetas y leasing, el balance incluye el exterior.
* **Antes de 2025 los informes de crédito van en el conglomerado financeiro**, con otros códigos que el panel
  (prudencial). El cadastro de cada trimestre dice qué unidades financeiras forman cada conglomerado prudencial
  (``CodConglomeradoFinanceiro`` / ``CodConglomeradoPrudencial``; ``"null"`` = la institución va sola). Validación:
  en la frontera 2024-T4 → 2025-T1 cada banco no puede saltar más que su propio balance.
* **NPL** (Pablo: E–H): hasta 2024, cartera E–H / AA–H del informe 8 (financeiro; AA–H es Brasil). Desde 2025
  la Res. 4.966 eliminó la escala AA–H: "Ativos problemáticos" / (total − exterior) del informe 16 (prudencial),
  lo más parecido. Quiebre
  marcado en la página. Por modalidad no hay ni uno ni otro: atraso de 15 días o más (informes 11 y 13).
* **NIM** = resultado de intermediación + provisiones (vienen restadas dentro), 4 trimestres / activo total
  promedio (t y t−4). **ROE** = lucro 4 trimestres / patrimonio promedio. Del panel (``datos/gold``).
* **Bancos con cambio de cobertura en 2025** (BNDES y varias fintechs: su cartera cambia en la frontera mucho más
  que su balance): su nivel salta y la página lo avisa, pero quedan fuera de las variaciones que cruzan 2025-T1.
  Los grandes (Itaú, BB, Bradesco, Caixa, Santander) cuadran con su balance a menos de 3 p.p.
* **2024-T4 se deja vacío en las carteras por modalidad**: el BCB lo sirve con un salto imposible (+20 % el panel,
  Itaú +67 %, y vuelve en 2025-T1). La frontera financeiro → prudencial se valida de 2024-T3 a 2025-T1.
* **Variaciones de grupo con los mismos bancos en los dos lados** (como la hoja 8): la entrada de un banco no es
  crecimiento. Los aportes suman exacto la variación del total. Nada anualizado.
* **Slicers planos** (columna ``etiqueta``, sangrada con espacios eme): en un slicer jerárquico, un clic en el
  padre ("Total", "Propiedad") elige todos sus hijos y las medidas, que piden un solo valor, quedan en blanco. Le
  pasó a Pablo en Desktop el 2026-10-14.
* **Medias de 2 y 4 trimestres** (Pablo, 2026-10-14: series más suaves; IF.data es trimestral, así que "3m" es el
  propio trimestre). Media 4T a/a = Σ de los 4 trimestres / Σ de los mismos 4 de un año antes − 1, armada por
  pares de trimestres con las reglas de la variación simple (mismos bancos, frontera 2025). 2024-T4 (vacío) saca
  su par de la media y se usa el resto; nunca se interpola. Los aportes también suman exacto la variación.
* **NPL por tipo de crédito** ("Ver por", hoja de calidad): el atraso de 15 días o más de los informes 11 y 13, y
  la línea de referencia es el mismo atraso sobre todas las modalidades del nodo. Nunca junto al E–H / ativos
  problemáticos del total: son definiciones distintas (2026-T2: 8,0 % E–H contra ~3,4 % de atraso ≥15 días).
  NIM y ROE no existen por producto: IF.data los publica solo por banco.
* **Contexto de tasas** (``cre_contexto``, trimestral), según la medida de la hoja de calidad: ROE − CDI (media de
  los 12 meses del ROE), NIM con el CDI de los mismos 12 meses, y para el NPL la tasa promedio de los créditos
  nuevos (SGS 20714) contra el CDI (SGS 4389), sistema completo. El spread oficial del BCB (20783) descuenta un
  costo de captación menor que el CDI porque incluye el fondeo del crédito dirigido; por eso dice "vs CDI".

Uso::

    python preparar_credito_paginas_powerbi.py               # con el crudo en disco
    python preparar_credito_paginas_powerbi.py --descargar   # antes baja SGS 20714 y 4389
    python preparar_credito_paginas_powerbi.py --solo-descargar   # solo eso (runner, paso D7)

Los informes de IF.data se bajan a mano (``ifdata.py colectar``; ver doc 41 §4). Corre después de
``preparar_bancos_powerbi.py`` (usa ``datos/gold``).
```

## `pipeline/preparar_gold_bancos.py` (1379 líneas)

Importa del pipeline: `almacen`, `preparar_gold_bancos_cartera`, `preparar_gold_bancos_exposicion`, `preparar_gold_bancos_sistema`, `preparar_metricas_bancos`

Subcomandos: `base` — construye bk_banco, bk_metrica, bk_panel, bk_grupo, bk_puente y bk_manifiesto, sin red; `rentabilidad` — construye bk_roe_arbol y bk_sensibilidad (encargo 64), sin red; `sistema` — construye bk_sistema_m y bk_sistema_q (SGS; baja lo que falte); `cartera` — construye bk_cartera y bk_cartera_totales desde los informes 11 y 13, sin red; `exposicion` — construye bk_exposicion (mora implícita del mix), sin red; `todo` — corre todo en orden de dependencias

Argumentos: `--descargar` — re-baja las series del SGS aunque el crudo exista; `--descargar` — pasa --descargar a sistema

```text
Capa gold base del dashboard de bancos: tablas bk_* que leen el sitio, y el puente IF.Data ↔ publicado.

POR QUÉ EXISTE
--------------
El sitio de bancos no calcula nada («Python calcula, el navegador dibuja»,
docs/dashboard_bancos/SPEC_DATOS_BANCOS_v0.1.md §1.3). Las fórmulas viven aquí, una sola vez, y el
sitio lee tablas ya listas. Este subcomando (``base``) no baja nada de la red: reordena lo que ya
existe en el repo —el panel de métricas por banco y trimestre, con TTM, ROE, ROA, cuotas y crédito
total (``datos/intermedio/metricas_bancos.parquet``); las dimensiones de los bancos
(``datos/gold/bank_instituciones.parquet`` y ``definiciones/bcb_ifdata__bancos_balances.json``); los
cotizados y tickers (``definiciones/bancos__dashboard.json``); las ópticas de grupo que ya usa
``cre_*`` (``datos/intermedio/cre_institucion.parquet``) y el cruce IF.Data ↔ publicado
(``definiciones/validacion_bancos.json``)— y lo entrega en seis tablas: ``bk_banco`` (34 bancos),
``bk_metrica`` (definición de cada métrica), ``bk_panel`` (banco × trimestre × métrica, con rezagos,
percentiles del grupo y rankings), ``bk_grupo`` (óptica × grupo × trimestre × métrica, con muestra
constante a/a), ``bk_puente`` y ``bk_manifiesto`` (filas, rangos, sha256 y último corte de cada
universo).

Reglas que no se tocan (SPEC §1.5 y cabeceras de ``preparar_metricas_bancos.py`` y
``preparar_credito_paginas_powerbi.py``): no se recalculan TTM, ROE, ROA, cuotas ni crédito total.
Los agregados de grupo son sumas o cocientes de sumas, nunca promedios de ratios. Lo que no tiene
definición segura queda en null y se lista en el resultado del encargo.

Salidas: ``datos/derivado/bcb_ifdata/bancos_gold/`` (con ``almacen.guardar_derivado``, que deja en el
manifiesto de qué entradas salió cada tabla y con qué comando) y una copia en ``datos/gold/``, donde
las leen el exportador y el sitio.

Uso:

    python -X utf8 preparar_gold_bancos.py base

El subcomando ``rentabilidad`` (encargo 64) añade ``bk_roe_arbol`` (árbol del ROE por banco y
por grupo) y ``bk_sensibilidad`` (beta del NIM contra el CDI); no reescribe las tablas de base.

    python -X utf8 preparar_gold_bancos.py rentabilidad
```

## `pipeline/preparar_gold_bancos_cartera.py` (354 líneas)

Importa del pipeline: `almacen`, `preparar_credito_paginas_powerbi`

```text
Cartera de crédito por banco × modalidad (capa gold del dashboard de bancos): bk_cartera, bk_cartera_totales,
bk_cartera_grupo, bk_cartera_mix7 y las copias bk_cre_*.

POR QUÉ EXISTE
--------------
`preparar_credito_paginas_powerbi.py` ya lee los informes 11 (PF) y 13 (PJ) de IF.data y arma, por banco,
el saldo y el vencido ≥15 días de cada modalidad; pero solo publica agregados por grupo (`cre_*`), porque
la hoja del PBIP compara grupos, nunca bancos sueltos. La ficha por banco del dashboard web necesita el
dato por banco. En vez de copiar el parser (y dejar dos lecturas del mismo crudo que pueden divergir),
este módulo **importa** sus funciones (`periodos_credito`, `bancos`, `leer_credito`, `rupturas_frontera`)
y solo agrega lo que el panel por banco necesita. No toca `cre_*` ni el PBIP.

Reglas heredadas, que no se tocan (docstring de preparar_credito_paginas_powerbi.py):
- Cartera activa en Brasil de los informes 11 y 13; financeiro hasta 2024-T4 (vía cadastro) y prudencial desde 2025.
- NPL por modalidad = atraso ≥ 15 días.
- 2024-T4 vacío (trimestre anómalo del BCB, `trimestres_anomalos` en definiciones).
- Bancos con cambio de cobertura en la frontera 2025 (`rupturas_frontera`): su nivel se publica, pero
  quedan fuera de las variaciones que cruzan 2025-T1 (columna `quiebre_2025`).

Salidas (spec de datos §3.5 y decisión del arquitecto del 2026-11-02 sobre la tabla auxiliar):
- datos/gold/bk_cartera.parquet          banco × trimestre × tipo × modalidad
- datos/gold/bk_cartera_totales.parquet  totales publicados por el BCB (para que el verificador valide Σ modalidades)
- datos/gold/bk_cartera_grupo.parquet    mix y NPL por modalidad por grupo y panel, con la mora del sistema al lado (B8-03);
                                       desde 78b, columna `dirigido_peso` (ver abajo)
- datos/gold/bk_cartera_mix7.parquet     (78b) mix en 7 categorías por banco, grupo y panel (B3-03-0)
- datos/gold/bk_cre_panorama / bk_cre_calidad / bk_cre_contexto: copia de cre_* (aportes, calidad, ROE/NIM/CDI por grupo) para el sitio
Se escriben con almacen.guardar_derivado en datos/derivado/bcb_ifdata/bancos_gold_cartera/ y se copian a datos/gold/.

78b · Mix en 7 categorías (B3-03-0) y peso del dirigido aproximado
-------------------------------------------------------------------
Categorías: tarjeta, personal, consignado, vehículos, hipotecario, rural (personas) y PJ (empresas, todas las
modalidades, incluida Rural y agroindustrial de empresas). «Personal» = Personal sin consignación + Otros (personas).
Mapeo en `MIX7_PF` (personas) y regla por tipo (PJ → «PJ»); una modalidad sin mapeo hace fallar el script.

«Dirigido aproximado» (modalidades con fondeo o tasa regulada): Hipotecario + Rural y agroindustrial (personas)
+ Rural (empresas) + Inmobiliario (empresas) + Infraestructura y proyectos. Es una APROXIMACIÓN por modalidad del
informe 11/13 de IF.data; NO es el dirigido contable del BCB (que se define por destino del crédito y tasa,
no por nombre de modalidad).

`dirigido_peso` se publica en bk_cartera_mix7 (banco, grupo y panel, repetido en cada categoría del mismo
trimestre) y en bk_cartera_grupo (grupo y panel). Es el peso del dirigido aproximado sobre la cartera de Brasil.

Uso:  python -X utf8 preparar_gold_bancos_cartera.py               (reconstruye desde el crudo vía el parser de cre_*)
      python -X utf8 preparar_gold_bancos_cartera.py --solo-mix7  (lee datos/gold/bk_cartera*.parquet; reescribe
                                                                   solo bk_cartera_grupo y bk_cartera_mix7)
```

## `pipeline/preparar_gold_bancos_exposicion.py` (104 líneas)

Importa del pipeline: `almacen`

```text
Exposición de cada banco al deterioro del sistema: bk_exposicion (spec de datos §3.6, esqueleto B4-04 y B8-03).

POR QUÉ EXISTE
--------------
El NPL de un banco mezcla dos cosas: en qué carteras está (mix) y qué tan bien originó dentro de cada una.
La «mora implícita» separa la primera: es la mora que tendría el banco si cada modalidad de su cartera se
comportara como el promedio del sistema (SGS). Contra ella, el NPL observado dice si el banco está mejor o
peor que su mix; su cambio en 12 meses se abre en efecto mix (el banco movió su cartera) y efecto mora
(el sistema se deterioró en lo que el banco ya tenía).

Las definiciones no son iguales (panel ≥ 15 días; SGS > 90 días): la brecha se lee en su evolución, no en
nivel. Las modalidades sin serie del SGS quedan fuera y la columna `cobertura` dice qué parte de la
cartera entra en el cálculo; con cobertura < 50 % (bancos de desarrollo, cartera dirigida) todo queda vacío. Equivalencias en definiciones/bancos__equivalencias_mora.json.

Entradas: datos/gold/bk_cartera.parquet, datos/gold/bk_sistema_q.parquet.
Salida:   datos/gold/bk_exposicion.parquet (banco × trimestre), con almacen.guardar_derivado.
Uso:      python -X utf8 preparar_gold_bancos_exposicion.py
```

## `pipeline/preparar_gold_bancos_pag_credito.py` (162 líneas)

Importa del pipeline: `almacen`, `preparar_gold_bancos_portada`

```text
Tablas de la página Crédito v3 (canvas «Bancos Brasil — propuesta visual», tablero 06).

Cuatro láminas, cada una con gráfico (izquierda) y tabla descriptiva estándar (derecha):
  01 por tipo de crédito, 02 contribución al crecimiento del último mes, 03 concesiones contra stock,
  04 crédito/PIB con tendencia HP unilateral y brecha.

TABLAS (datos/gold/)
- bk_cred_tablas: bloque, orden, fila, grupo, ultimo, d1, d3, d12, dventana, corte, unidad_ultimo,
  unidad_cambio, trimestral. Misma estructura que bk_portada_tablas, así la página usa una sola tabla.
- bk_cred_series: serie, fecha, valor (largo). Series: conc12_aa, stock_aa (fracción), cpib_nivel,
  cpib_tendencia (%), cpib_brecha (pp).

REGLAS
- Modalidades: códigos SGS identificados cuadrando montos (consignado = 20576 + 20577 + 20578; libres PF
  ≈ suma de modalidades). «Otros» = total − modalidades listadas, para que la contribución sume el total.
- Contribución (pp): cambio del saldo de la modalidad sobre el saldo total del período base, en las mismas
  cuatro ventanas que la tabla estándar; suma el crecimiento del total en cada ventana.
- Concesiones: flujo mensual; 12m/12m compara sumas de doce meses; conc12_aa = suma 12m a/a.
- HP unilateral sobre el promedio trimestral de SGS 20622, λ = 400.000 (convención del BIS), con
  al menos 20 trimestres de historia; el punto t usa solo datos hasta t.
```

## `pipeline/preparar_gold_bancos_portada.py` (238 líneas)

Importa del pipeline: `almacen`, `preparar_gold_bancos_sistema`

```text
Tablas de la Portada v3 del sitio de bancos (canvas «Bancos Brasil — propuesta visual», tablero 05).

POR QUÉ EXISTE
--------------
La Portada muestra cuatro bloques, cada uno con un gráfico y una tabla descriptiva de estructura fija
(m/m, 3m/3m, a/a, 12m/12m; en trimestrales t/t, a/a, 4T/4T). Por regla del sitio, el navegador no
calcula: todas las variaciones, contribuciones, deflactados y cuotas salen de aquí.

TABLAS (datos/gold/)
------------------
- bk_portada_credito: fecha, modo (nominal|real), componente (total, libre, direccionado, pf, pj),
  aa (fracción) y contrib_pp (contribución al a/a del total, en pp). Mensual desde 2016.
- bk_portada_mora: fecha, nivel (fracción) y d_aa_pp del total (SGS 21082). Mensual desde 2016.
- bk_portada_roe: periodo, fecha, trimestre, roe, cdi_4t, roe_cdi_pp (ROE del panel menos CDI promedio
  de 4 trimestres, en pp).
- bk_portada_tablas: bloque (credito_nominal, credito_real, mora, roe), orden, fila, ultimo, d1, d3,
  d12, dventana, unidad, corte. En crédito: saldo (R$ mil millones), y % de variación; en mora: nivel
  en % y cambios en pp; en ROE: % y pp con d1 = t/t, d3 vacío, d12 = a/a, dventana = 4T/4T.
- bk_portada_cuotas: vista, orden, banco, cuota (fracción), grupo, periodo. Diez mayores + «Resto».

REGLAS
------
- 3m/3m y 12m/12m: promedio de la ventana sobre el de la ventana anterior (saldos) o diferencia de
  promedios (tasas). m/m y a/a: punta contra punta.
- Real: saldo deflactado por el índice IPCA encadenado (SGS 433), base último mes.
- Contribución: (componente_t − componente_t−12) / total_t−12, en pp. Libre + direccionado = total
  (diferencia < 1 %); PF + PJ = total.
- Series SGS: se leen del crudo (cualquier dataset de bcb_sgs). Si falta, se bajan con el mismo
  mecanismo de preparar_gold_bancos_sistema; sin red, la fila queda vacía y se avisa.
- Cuotas: último trimestre del panel IF.Data con informes de pasivo (r3) y cartera PF/PJ (r11, r13);
  activos y crédito total desde bk_panel (share_ativo, share_credito). Solo conglomerados del panel.
```

## `pipeline/preparar_gold_bancos_qcambio.py` (175 líneas)

Importa del pipeline: `almacen`

```text
«Qué se movió» de la Portada: cambio del último trimestre por banco y métrica, con su z (encargo 78d, plan 57).

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
```

## `pipeline/preparar_gold_bancos_scr.py` (297 líneas)

Importa del pipeline: `almacen`, `certificados`

Argumentos: `--solo-descargar` — solo baja los ZIP 2012-2023 que falten, no deriva

```text
bk_scr: SCR.data 2012-2026 agregado en tres cortes para el dashboard de bancos.

POR QUÉ EXISTE
--------------
El spec de datos (``docs/dashboard_bancos/SPEC_DATOS_BANCOS_v0.1.md`` §3.10) pide
publicar del SCR.data solo tres cortes agregados — mes × segmento × cliente,
mes × porte (solo PJ) y mes × UF — y no el cubo granular, porque el sitio
grafica series de sistema y el cubo entero son cientos de MB por año. Este
módulo lee los ZIP anuales crudos (``datos/crudo/bcb_scr/scrdata/actual/``)
**por partes** (``chunksize``): un año no cabe entero en memoria y
``credito_garantizado.py scr`` ya estableció el patrón de lectura por chunks
desde el ZIP sin descomprimir a disco.

La tasa es la oficial del BCB (docs/fuentes_datos_sector_bancario_brasil.md §15):
``tasa = Σ carteira_inadimplencia / Σ carteira_ativa``. La columna
``carteira_inadimplencia`` del SCR.data está en R$, NO en %; escribirla como
porcentaje es el error que §15 corrige. Las tasas van como fracción (0,05 = 5 %),
igual que el resto de la capa gold.

Decisiones del encargo 67 (03-11-2026) registradas para el que relea:

- **Los CSV del SCR.data son UTF-8 con BOM**, verificado byte a byte en 2012 y
  2024 (el encargo decía cp1252, que es lo normal en los archivos del gobierno
  brasileño, pero estos no: leerlos como cp1252 mojibakea «mínimos» y las UFs).
  La lectura prueba UTF-8 estricto sobre una muestra y cae a cp1252 solo si
  falla, por si el BCB cambia de era otra vez.
- **La descarga de 2012-2023 va streameada a disco con ``almacen.registrar_crudo``**,
  no con ``extraer_fuentes.py scrdata``: ese comando publica en el crudo un CSV
  combinado re-codificado (con nombre que colisiona entre años), no el ZIP anual
  que este preparador y ``credito_garantizado.py`` leen. Misma URL, misma
  procedencia; el patrón streameado es el del repo para archivos de decenas de
  MB (``ifdata.py``). Política de reintentos del encargo: 3 intentos por año,
  30 s de pausa; un año que falla 3 veces se anota y se sigue.
- **``numero_de_operacoes`` == -1 es secreto estadístico**, no un número; no se
  suma (aquí ni se usa: los cortes son de saldo). Las filas con -1 sí traen
  valores en R$ y entran a las sumas de cartera.
- **``porte`` del corte PJ va tal cual lo publica el BCB** (Micro, Pequeno,
  Médio, Grande, Indisponível): traducirlo es una decisión de presentación que
  no pide el encargo y mejor la toma quien consume la tabla.
- **``modalidad`` va siempre vacía**: el contrato gold del verificador la exige
  (y §3.10 la lista), pero los tres cortes publicados no abren por modalidad.

Receta::

    python -X utf8 preparar_gold_bancos_scr.py                # baja 2012-2023 y deriva
    python -X utf8 preparar_gold_bancos_scr.py --solo-descargar
```

## `pipeline/preparar_gold_bancos_scr_productos.py` (411 líneas)

Importa del pipeline: `almacen`, `certificados`

Argumentos: `--descargar` — baja de nuevo el ZIP del año en curso; `--desde` — primer año del cubo (default 2018)

```text
Gold del SCR.data por producto, tramo de renta, tipo de institución y sector (páginas Personas y Mora).

POR QUÉ EXISTE
--------------
`bk_scr` (preparar_gold_bancos_scr.py) publica tres cortes sin modalidad. Las páginas Personas y Mora
necesitan el SCR abierto por producto (tarjeta, consignado, personal, vehículos, inmobiliario, rural, cheque
especial), por tramo de renta del deudor PF, por tipo de institución y, en PJ, por sección CNAE. Es la base
de la réplica de crédito por renta (tarea 3; detalle en referencias/, fuera de git) y de los gráficos
1.2.2.15/1.2.2.16 del REF.

FLUJO
-----
1. (opcional, --descargar) baja de nuevo el ZIP del año en curso (y del anterior en enero-febrero): el BCB
   lo reescribe cada mes con el mes nuevo.
2. Agregado mensual incremental en `datos/intermedio/scr_productos/<version>/scr_AAAAMM.parquet`
   (dims: fecha, cliente, segmento, porte, cnae_ocupacao, producto). Un mes se recalcula si falta o si su
   ZIP es más nuevo que el agregado. <version> = sha corto de las reglas de producto de definiciones/scr_productos.json:
   cambiar el mapa de productos invalida el caché entero; cambiar traducciones no.
3. Gold:
   - bk_scr_tablas: filas de la tabla estándar (bloque, producto, orden, fila, grupo, ultimo, share, d1, d3,
     d12, dventana, corte, unidad_ultimo, unidad_cambio, trimestral, destacar).
   - bk_scr_series: serie, fecha, valor (largo).

REGLAS
------
- Mora = carteira_inadimplencia / carteira_ativa (fracción). La columna está en R$, no en %.
- Mora temprana = vencido_de_15_ate_90_dias / carteira_ativa.
- Activo problemático = ativo_problematico / carteira_ativa. Desde ene-25 rige la Res. 4.966 (otra definición).
- Ticket = cartera de las celdas con numero_de_operacoes > 0 / Σ operaciones. −1 es secreto estadístico
  (menos de 15 operaciones): esas celdas entran al saldo pero no al ticket.
- Mix por renta: sobre los 7 tramos con renta declarada (sin «N.D.» ni «Sin renta»).
- Cambios de saldo y ticket en % (m/m, 3m/3m con promedios, a/a, 12m/12m con promedios); de tasas en pp.
- Quiebres conocidos de la fuente (no se suavizan; van en las notas del sitio): jul-25 reclasificación de renta
  (salto del mix); ago-26 ~R$ 15 mil millones de tarjeta pasan de «más de 20 SM» a «Indisponível».

Uso (desde pipeline/, Windows con -X utf8):
    python -X utf8 preparar_gold_bancos_scr_productos.py [--descargar] [--desde AAAA]
```

## `pipeline/preparar_gold_bancos_sistema.py` (458 líneas)

Importa del pipeline: `almacen`, `bcb_api`, `certificados`

Argumentos: `--descargar` — re-baja las series del SGS aunque el crudo exista

```text
Series del Sistema financiero (SGS + tablas del macro) para el dashboard de bancos.

POR QUÉ EXISTE
--------------
El spec de datos del dashboard de bancos (``docs/dashboard_bancos/SPEC_DATOS_BANCOS_v0.1.md``
§3.9) pide las series del Sistema —mora 90, atrasos 15-90, crédito real, crédito dirigido,
spread, ICC, deuda de hogares— en formato largo mensual y trimestral con bandas. Esas series
viven mitad en el SGS y mitad en tablas que el dashboard macro ya construyó en ``pb/``;
reunirlas en cada página del sitio produciría cifras divergentes. Este módulo es el único
lugar donde se transforman, y escribe ``datos/gold/bk_sistema_m.parquet`` y
``datos/gold/bk_sistema_q.parquet``.

Es un archivo aparte de ``preparar_gold_bancos.py`` a propósito: ese lo escribe otro worker
en la misma ola del plan 57 y el arquitecto integra ambos como subcomandos.

Decisiones del encargo 61 y su corrección 61b (02-11-2026, «Decisiones del arquitecto»
en ``docs/dashboard_bancos/PENDIENTES.md``), registradas aquí para el que relea:

- Los 38 códigos del encargo respondieron con JSON y fechas recientes (paso 1, tabla en
  ``docs/orquestacion/61_resultado_sgs_sistema_2026-11-02.md``). Ninguno se reemplazó.
- ``impulso_credito`` no existe como tabla en ``pb/`` (se revisó el inventario; solo aparece
  en un docstring), así que se recalcula con SGS 20539 + 4382. Se publica en pp del PIB
  como ``impulso_credito_pp``.
- 61b · Unidades: TODA la tabla va en fracción (0,05 = 5 %): mora, atrasos, spread, icc,
  credito_pib, crecimientos reales y las series que ya venían en fracción de pb. Solo el
  impulso y el hiato del BIS quedan en pp, marcados con sufijo ``_pp`` y columna ``unidad``
  (fraccion | pp).
- 61b · mora90 por modalidad: TODAS salen del SGS (21119, 21121, 21127, 21151 incluidas);
  ``hogares_modalidades`` queda fuera de esta tabla (solo B4-02). ``mora90_personal`` =
  21114 (incluye consignado). Equivalencia «Tarjeta de crédito» = 21129 (total); 21127 y
  21128 son detalle.
- 61b · Nombres sin la expansión mecánica del shorthand de §3.9:
  ``dirigido_{rural,imob,bndes}_real_aa``, ``credito_grande_real_aa`` (27702),
  ``mora90_grande`` (27704).
- ``comprometimento`` (29034), ``endividamento`` (29037) y ``desocupación`` (24369, PNADC = IBGE
  t6381|v4099) se leen del SGS desde el 6-nov-2026 (tarea 1.3; antes venían congeladas de
  ``datos/intermedio/``). ``selic_real_exante`` sigue en ``datos/intermedio/tasa_real_exante.parquet``
  (media mensual de la serie diaria; 23 trimestres es excepción aceptada) y no se re-baja.
- ``bis_hiato_credito_pib_pp`` se lee del crudo local ``datos/crudo/bis/credit_gap`` tal
  cual, en pp (solo trimestral). ``pix_share`` queda fuera: encargo propio en la ola 2.

78c (encargo 78, ola 4): ipca_12m (acumulado 12 meses desde SGS 433), ipca_esperado_12m
(mediana Focus a 12 meses, último envío de cada mes), icc_real_exante (ex ante),
mora90_pf_livre_adel3m (mora 90 de t+3 en la fecha t) y d_1m / d_3m en bk_sistema_m.
En _q, ipca_12m toma el último mes del trimestre; el resto, promedio como siempre.

Receta:

    python -X utf8 preparar_gold_bancos_sistema.py             # baja lo que falta y deriva
    python -X utf8 preparar_gold_bancos_sistema.py --descargar  # fuerza re-descarga del SGS
```

## `pipeline/preparar_metricas_bancos.py` (297 líneas)

```text
Prepara la capa de métricas del dashboard de bancos (proyecto independiente).

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
```

## `herramientas/comparar_gold.py` (51 líneas)

```text
Compara celda por celda dos carpetas de parquets gold (misma forma, mismas columnas, mismos valores).

Uso: python -X utf8 herramientas/comparar_gold.py <carpeta_a> <carpeta_b>
Los floats se comparan con tolerancia relativa 1e-12 (solo ruido de redondeo); todo lo demás exacto.
`bk_manifiesto` se compara sin las columnas que dependen del momento de la corrida (bytes, sha256, generado).
```

## `herramientas/convertir_crudo_parquet.py` (53 líneas)

Importa del pipeline: `almacen`

Argumentos: `--borrar` — borra cada CSV cuyo parquet ya está anotado en el manifiesto

```text
Convierte a parquet los CSV crudos de IF.Data (valores y cadastro) que todavía no lo están.

El parquet guarda todas las columnas como texto, igual que el CSV (sin pérdida; ver almacen.csv_a_parquet),
y el manifiesto anota URL y sha256 del CSV original más los del parquet. Por defecto NO borra los CSV.

Uso (desde la raíz del repo):
    python -X utf8 herramientas/convertir_crudo_parquet.py            # convierte lo que falte
    python -X utf8 herramientas/convertir_crudo_parquet.py --borrar   # además borra cada CSV ya convertido
```

## `herramientas/generar_spec.py` (183 líneas)

```text
Regenera spec/generado/: el inventario automático del repo (tablas gold, métricas, bancos, páginas,
componentes, scripts y definiciones). La parte narrativa de spec/ se escribe a mano; esta se regenera
para que no quede desactualizada.

Uso (desde la raíz del repo):  python -X utf8 herramientas/generar_spec.py
Requiere los parquet de datos/gold (no van a git) y Node para leer la configuración de páginas.
```

## `herramientas/verificar_f1.py` (220 líneas)

Argumentos: `--url` — sitio publicado (sin / final); si falta, levanta uno local; `--anchos` — anchos en px separados por coma, p. ej. 1920,1280,390

```text
Verifica la F1 del sitio de bancos (encargo 76) sobre las once páginas, con y sin ?banco=itau.

Qué comprueba, con un Chromium real sobre un servidor propio (python -m http.server, que se cierra
al terminar con su mismo PID; no se usa ningún servidor que ya estuviera corriendo):
  1. cada página responde 200 y carga sin errores de consola ni de página;
  2. el número de secciones y de tarjetas es el de la config y el del esqueleto (contar_tarjetas.mjs);
  3. cada tarjeta lleva el título de su config; si la config NO tiene armar(), la tarjeta está
     «en preparación» (esa exigencia no aplica a las tarjetas con armar());
  4. ninguna tarjeta con armar() muestra error de carga o de cálculo;
  5. ningún «[» visible en el texto de la página;
  6. la cabecera tiene una pestaña por página visible (las de config.js sin oculta: true) y la marca BANCOS BRASIL.
  7. en cada ancho de --anchos, la página no tiene scroll horizontal.
Captura de página completa solo si se pide con --captura DIR.

Con --url BASE (p. ej. https://banks-bz.pages.dev) revisa el sitio publicado en vez del local, con las fuentes
reales de Google (en local se cortan, para no depender de la red) y reporta si cargaron.

Uso: python -X utf8 herramientas/verificar_f1.py [--puerto 8080] [--url BASE] [--anchos 1920,1280,390] [--captura DIR]
```

## `herramientas/verificar_gold.py` (1480 líneas)

Argumentos: `--comparar` — parquet candidato de staging a comparar con el actual; `--auditoria` — ejecuta también tests/auditoria/auditar_fuentes.py; `--estricto` — trata las advertencias como errores; `--gold` — comprueba solo las tablas gold bk_* de datos/gold (encargo 59); `--json` — salida JSON

```text
Verificador de solo lectura del pipeline del dashboard de bancos.

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
    python herramientas/verificar_gold.py --comparar <ruta>/metricas.parquet
    python herramientas/verificar_gold.py --estricto --auditoria
    python herramientas/verificar_gold.py --gold

Código de salida: 0 si no hay errores (o advertencias con `--estricto`), 1 si
hay algún error. Las advertencias no bloquean por defecto: los saltos de un
banco que sale del panel son datos reales y requieren revisión humana, no un
`assert` ciego.
```

