# Scripts del pipeline (docstring completo y argumentos)

> Generado por `herramientas/generar_spec.py`. No editar a mano: se sobrescribe.


## `pipeline/actualizar.py` (95 líneas)

Importa del pipeline: `almacen`, `red`

Argumentos: `--sin-red` — no baja nada: salta los pasos sgs y focus; un dato que falte hace fallar el paso; `--sin-verificacion` — salta pytest y verificar_gold (comparaciones); `--desde` — empieza en este paso; `--hasta` — termina en este paso

```text
Actualiza los datos del sitio de bancos de punta a punta, en orden de dependencias (lo llama actualizar.bat).

Cada paso corre en su propio proceso (``python -X utf8 pipeline/<módulo>.py <argumentos>``, cuyo ``main`` devuelve
0 o 1): así la memoria de un paso no se acumula en el siguiente. Si un paso falla, la corrida se corta y no se
exporta nada. IF.Data no se baja aquí (es trimestral y a mano: ``ifdata.py colectar``).

    python -X utf8 pipeline/actualizar.py              # completo: baja SGS y el SCR del año, ..., verifica, exporta
    python -X utf8 pipeline/actualizar.py --sin-red    # sin descargas: un dato que falta hace fallar el paso
    python -X utf8 pipeline/actualizar.py --desde portada
```

## `pipeline/almacen.py` (437 líneas)

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

## `pipeline/bancos.py` (116 líneas)

Importa del pipeline: `almacen`

```text
Universo de bancos del panel y sus ópticas de grupo: el único lugar que los lee de definiciones/.

El universo (cod_inst, nombre_corto, categoría, modelo de negocio) está en
``definiciones/bcb_ifdata__bancos_balances.json``; los atributos del sitio (slug, ticker, ficha) en
``definiciones/bancos__dashboard.json``. Las dos listas repiten cod_inst y nombre_corto para que se puedan
editar a mano; ``universo()`` falla si dejan de coincidir.
```

## `pipeline/bcb_api.py` (308 líneas)

Importa del pipeline: `certificados`, `red`

Subcomandos: `datos` — descarga los valores de series; `ultimos` — ultimas N observaciones de una serie

Argumentos: `codigos` — codigo(s) de serie; `--desde` — fecha inicial DD/MM/AAAA; `--hasta` — fecha final DD/MM/AAAA; `-o` — CSV de salida; `--ancho` — formato ancho: una columna por serie; `-n` — cantidad (defecto: 10)

```text
Descarga de DATOS (valores) de las series del SGS/BCB via la API oficial.

Endpoints usados (documentados en https://dadosabertos.bcb.gov.br/):
  GET https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados
      ?formato=json|csv&dataInicial=DD/MM/AAAA&dataFinal=DD/MM/AAAA
  GET https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/{n}

Nota: la API limita las series diarias a ventanas de 10 anios (3652 dias);
el script lo gestiona automaticamente. No hay endpoint de metadatos en la API actual.

El pipeline usa descargar_serie a traves de sgs.py; el resto es la linea de comandos.

OJO con los errores: una serie inexistente NO da 404. La API contesta una pagina
HTML, con un status que varia (visto 200 y 502), asi que el status code no alcanza
para saber si la respuesta sirve. Ver RespuestaNoJSON mas abajo.

Ejemplos:
  python -X utf8 pipeline/bcb_api.py datos 432                       # serie completa (JSON->CSV)
  python -X utf8 pipeline/bcb_api.py datos 432 11 433 -o tasas.csv   # varias series a un CSV
  python -X utf8 pipeline/bcb_api.py datos 433 --desde 01/01/2024    # rango de fechas
  python -X utf8 pipeline/bcb_api.py datos 11 432 --ancho -o x.csv   # una columna por serie
  python -X utf8 pipeline/bcb_api.py ultimos 432 -n 5                # ultimas 5 observaciones
```

## `pipeline/capital.py` (399 líneas)

Importa del pipeline: `almacen`, `bancos`, `ifdata_texto`, `periodos`

Argumentos: `--resumen` — no publica: imprime cobertura y avisos

```text
Capital: informe 5 de IF.Data («Informações de Capital») → bk_capital y bk_capital_grupo.

Fuente: el crudo que deja ``ifdata.py colectar --escopo prudencial --informe 5`` en
datos/crudo/bcb_ifdata/valores/actual/valores_<AAAAMM>_1_r5.(csv|parquet). Este paso no baja nada: la colecta de
IF.Data es trimestral y a mano (ver spec/07). Si falta un trimestre, queda como hueco con su motivo.

Trampas (verificadas el 9-nov-2026 sobre 2015-03 a 2026-06; detalle en spec/08):
1. El informe 5 existe desde 2015-03. Los archivos de 2014 vienen vacíos (la API responde, sin filas).
2. Las letras de las columnas cambian por época («RWA (i) = (f)+(g)+(h)» hasta 2022-12, «(j) = (f)+(g)+(h)+(i)»
   desde 2023-03): se casa por el nombre sin la letra (definiciones/bcb_ifdata__capital.json).
3. En 2025-09 la API sirve cada fila tres veces (99.000 filas para 1.375 entidades). Se deduplica por
   entidad × campo y se exige que las copias tengan el mismo valor; si difieren, falla.
4. Desde 2023-03 el informe trae el «Adicional de Capital Principal» exigido en R$: el requerimiento de CP de
   cada banco sale de ahí (lo calcula el BCB). Antes de 2023-03 se reconstruye con
   definiciones/minimos_regulatorios.json; lo que la norma no respalda queda vacío.
5. Saldos con coma decimal y «null» literal (ifdata_texto.a_valor).

Salidas:
- datos/gold/bk_capital.parquet          banco × trimestre (columnas anchas)
- datos/gold/bk_capital_grupo.parquet    óptica × grupo × trimestre; índices = Σ capital / Σ RWA
- datos/derivado/bcb_ifdata/capital/huecos_capital.csv

Uso:  python -X utf8 pipeline/capital.py            (arma y publica)
      python -X utf8 pipeline/capital.py --resumen  (solo imprime cobertura y avisos, sin publicar)
```

## `pipeline/certificados.py` (147 líneas)

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
arregla de una sola vez requests y urllib.request, porque los dos terminan en el mismo
ssl del stdlib.

Si truststore no esta instalado, se respeta REQUESTS_CA_BUNDLE / SSL_CERT_FILE por si
alguien exporto la CA de la empresa a mano, y si tampoco hay nada se sigue adelante en
silencio: en una red sin proxy no hace falta nada de esto y no queremos ruido.

USO
---
    import certificados   # basta con importarlo, se activa solo

Va como primer import de cada modulo que salga a la red (bcb_api, ifdata, sgs, scr_zip), ANTES de requests.
```

## `pipeline/cvm.py` (1091 líneas)

Importa del pipeline: `almacen`, `bancos`, `certificados`, `periodos`, `red`

Argumentos: `--forzar` — vuelve a bajar aunque el tamaño no haya cambiado; `--descargar` — con «todo», baja antes los ZIP: así lo llama actualizar.py. Sin esta opción trabaja ; `--periodo` — para «contrastar»: solo este trimestre (AAAAMM)

```text
Fuente CVM (ITR y DFP) de los bancos cotizados: descarga, extracción filtrada y tabla gold ``bk_publicado``.

POR QUÉ EXISTE
--------------
El IF.Data del BCB llega con rezago: el trimestre cierra y los datos aparecen semanas después. Los bancos
cotizados, en cambio, publican su ITR (Informe Trimestral) en la CVM mucho antes. Esta fuente da el último
trimestre publicado con la base contable rotulada (IFRS o BR GAAP), que es lo que necesita la tarjeta
B8-06-0 «Último trimestre publicado (CVM)».

Es OTRA contabilidad, no un reemplazo del IF.Data: el ITR/DFP es el consolidado societario bajo
pronunciamientos del CPC (o IFRS, según el banco), mientras que el IF.Data es el conglomerado prudencial
bajo COSIF. Los dos números del mismo trimestre difieren —por las subsidiarias de seguros, por el método
de participación y por reglas de consolidación— y esa diferencia se mide y se informa
(``contrastar``), nunca se corrige.

CAPAS
-----
    datos/crudo/cvm/itr/<año>/itr_cia_aberta_<año>.zip      el ZIP íntegro de la CVM, sin tocar
    datos/crudo/cvm/dfp/<año>/dfp_cia_aberta_<año>.zip      idem, estados anuales
    datos/crudo/cvm/cadastro/actual/cad_cia_aberta.csv      registro de compañías abiertas
    datos/derivado/cvm/bancos/...                           solo las filas de los bancos del mapa (parquet)
    datos/gold/bk_publicado.parquet                         las líneas mínimas por banco y trimestre

El ZIP se vuelve a bajar cuando cambia de tamaño en el servidor: la CVM regenera el del año en curso casi
todas las semanas (entra el ITR nuevo, o una compañía reentrega y sube la VERSAO).

TRAMPAS DE LA FUENTE (todas verificadas sobre el dato; ver también definiciones/cvm__dfp_bancos.json)
------------------------------------------------------------------------------------------------------
1. Cada cuenta viene DOS veces por ``ORDEM_EXERC`` («ÚLTIMO» y «PENÚLTIMO», el ejercicio comparativo):
   sin filtrar se duplica todo y se mezclan dos años. Este módulo toma «ÚLTIMO» para el cierre del archivo
   y usa ``DT_FIM_EXERC`` para saber de qué periodo es cada cifra.
2. ``ESCALA_MOEDA`` vale «MIL»: los valores están en R$ mil. ``bk_publicado`` los publica en R$ (×1000).
   La escala se LEE de la columna, no se asume: la CVM también usa «UNIDADE».
3. En el ITR, la DRE trae el trimestre y el acumulado del año en la misma cuenta: se distinguen por
   ``DT_INI_EXERC`` (1 de enero = acumulado; inicio del trimestre = trimestre). La DFP solo trae el año.
4. Una compañía puede reentregar (``VERSAO``): se usa la mayor por compañía y documento.
5. ``CD_CONTA`` es jerárquico y el plan de cuentas lo arma cada compañía dentro del esqueleto de la CVM:
   la misma cuenta puede tener códigos distintos entre bancos. De ahí el mapa por banco de
   ``definiciones/cvm__bancos_lineas.json``.
6. Nubank, Inter, XP, Stone y PagSeguro NO entregan ITR/DFP: reportan en EE.UU. (20-F/6-K). Quedan fuera
   de alcance en la v1, con ``bk_publicado`` vacío para ellos.

Uso (desde la raíz del repo, con el .venv):

    python -X utf8 pipeline/cvm.py descargar              # ZIP ITR/DFP + registro, solo si cambiaron
    python -X utf8 pipeline/cvm.py extraer                # derivado filtrado a los bancos del mapa
    python -X utf8 pipeline/cvm.py gold                   # bk_publicado + huecos
    python -X utf8 pipeline/cvm.py contrastar             # contra IF.Data: activo, PL, depósitos, crédito y lucro
    python -X utf8 pipeline/cvm.py todo                   # extraer + gold + contrastar, sin tocar la red
    python -X utf8 pipeline/cvm.py todo --descargar       # idem, bajando antes lo que cambió (actualizar.py)
```

## `pipeline/diccionario_ifdata.py` (714 líneas)

Importa del pipeline: `almacen`, `ifdata_texto`

Argumentos: `--periodo` — trimestre del inventario de cuentas (defecto: el último volcado)

```text
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
```

## `pipeline/exportar_web_bancos.py` (189 líneas)

Importa del pipeline: `almacen`, `bancos`, `reglas_gold`

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
    python -X utf8 pipeline/exportar_web_bancos.py
```

## `pipeline/focus.py` (77 líneas)

Importa del pipeline: `almacen`, `certificados`, `red`

```text
Encuesta Focus del BCB (API Olinda): el único lector y descargador de expectativas del pipeline.

Solo se usa la mediana del IPCA a 12 meses adelante (``ExpectativasMercadoInflacao12Meses``), en la variante
suavizada (``Suavizada = 'S'``) y con todas las respuestas de los últimos 30 días (``baseCalculo = 0``). Es la
que usaba el dashboard macro: cuadra al decimal con la entrada que estaba congelada en
``datos/intermedio/expectativas_focus.parquet`` (validado el 8-nov-2026).

Vive en ``datos/crudo/bcb_focus/expectativas/actual/ipca_12m.json`` tal como lo devuelve la API (la lista
``value``), con su URL en el manifiesto del almacén.
```

## `pipeline/ifdata.py` (774 líneas)

Importa del pipeline: `almacen`, `certificados`, `ifdata_texto`, `red`

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

## `pipeline/ifdata_credito.py` (170 líneas)

Importa del pipeline: `almacen`, `ifdata_texto`, `periodos`

```text
Cartera de crédito por banco y modalidad desde IF.Data (informes 11 personas y 13 empresas) y NPL total.

Lo leen preparar_credito_paginas_powerbi.py (tablas cre_* por grupo) y preparar_gold_bancos_cartera.py
(bk_cartera por banco), para que no haya dos lecturas del mismo crudo que puedan divergir.

Por qué los datos son estos:
* **Cartera activa en Brasil de los informes 11 y 13, no la cuenta del balance.** Solo esos informes abren
  por modalidad. El "Total da Carteira" del BCB incluye las operaciones en el exterior (Itaú 2014-T2:
  R$ 124 mil millones solo en empresas); aquí se valida que Σ modalidades + exterior = total publicado.
* **Antes de 2025 los informes de crédito van en el conglomerado financeiro**, con otros códigos que el panel
  (prudencial). El cadastro de cada trimestre dice qué unidades financeiras forman cada conglomerado
  prudencial (``CodConglomeradoFinanceiro`` / ``CodConglomeradoPrudencial``; ``"null"`` = la institución va sola).
* **NPL total** (E–H): hasta 2024, cartera E–H / AA–H del informe 8 (financeiro). Desde 2025 la Res. 4.966
  eliminó la escala AA–H: "Ativos problemáticos" / (total − exterior) del informe 16 (prudencial).
* **Bancos con cambio de cobertura en 2025** (BNDES y varias fintechs): su cartera cambia en la frontera
  mucho más que su balance (``rupturas_frontera``).
```

## `pipeline/ifdata_texto.py` (60 líneas)

```text
Texto de los CSV de IF.Data (OLinda): limpieza, nulos, saldos y periodos. Sin red.

- Los nombres de cuenta vienen con saltos de línea dentro de las comillas del CSV.
- ``null`` literal (y ``NI``, «no informado», en los saldos) significa sin dato, nunca 0.
- Los saldos usan coma decimal brasileña; si no hay coma, un punto seguido de grupos de 3 dígitos es separador
  de miles.
```

## `pipeline/manifiesto_gold.py` (68 líneas)

Importa del pipeline: `almacen`, `bancos`, `reglas_gold`

```text
bk_manifiesto: una fila por tabla gold (filas, columnas, rango, sha256, quién la produjo) y una por universo
(último corte). Se arma una sola vez, después de que todos los pasos publicaron (actualizar.py).

El comando que produjo cada tabla sale de su procedencia en ``datos/derivado/`` (almacen.publicar_gold).
```

## `pipeline/mora_sistema.py` (25 líneas)

Importa del pipeline: `almacen`

```text
Mora del sistema (SGS > 90 días, bk_sistema_q) para cada modalidad de la cartera IF.Data del panel.

Las equivalencias modalidad → serie del SGS están en ``definiciones/bancos__equivalencias_mora.json``. Las
definiciones no son iguales (panel ≥ 15 días; SGS > 90 días): se comparan en evolución, nunca en nivel.
```

## `pipeline/periodos.py` (96 líneas)

Importa del pipeline: `almacen`

```text
Periodos AAAAMM (trimestres de IF.Data y meses del SGS/SCR): aritmética, etiquetas y quiebres conocidos.

Los quiebres de la fuente viven aquí una sola vez:

- ``QUIEBRE_2025`` (2025-T1): el BCB renumeró las cuentas COSIF y movió los informes de crédito del
  escopo financeiro al prudencial. Los bancos con cambio de cobertura (``quiebre_2025`` en bk_cartera)
  quedan fuera de las variaciones que cruzan este trimestre.
- ``ANOMALOS``: trimestres que el BCB sirve con saltos imposibles; se dejan vacíos, nunca interpolados.
  La lista y el motivo están en ``definiciones/bcb_ifdata__credito_modalidades.json`` (``trimestres_anomalos``).
```

## `pipeline/preparar_bancos_powerbi.py` (614 líneas)

Importa del pipeline: `almacen`, `bancos`, `ifdata_texto`, `periodos`

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

    python pipeline/ifdata.py colectar --desde 201403 --hasta 202606 --escopo prudencial         --informe 2 --informe 3 --informe 4
    python pipeline/preparar_bancos_powerbi.py
```

## `pipeline/preparar_credito_paginas_powerbi.py` (552 líneas)

Importa del pipeline: `almacen`, `bancos`, `ifdata_credito`, `periodos`, `reglas_gold`, `sgs`

```text
Tablas de las hojas "Crédito: panorama" y "Crédito: calidad" del PBIP dual (prefijo ``cre_``), trimestral.

POR QUÉ EXISTE
--------------
Pablo vio la hoja 8 "Bancos" el 2026-10-13 y pidió otro concepto:
no comparar bancos, sino ver **de qué está hecho el crédito** del panel según dos cortes que se cruzan:

* **tipo de institución**: segmento S1–S4, propiedad, modelo de negocio, tradicional vs fintech; siempre grupos,
  nunca bancos sueltos;
* **tipo de crédito**: personas / empresas y sus modalidades (tarjeta, consignado, vehículos, capital de giro…).

Un botón decide qué dimensión se apila. El slicer de tipo tiene solo Total, Personas y Empresas (Pablo,
2026-10-20): apilado por tipo de crédito, "Total" muestra Personas contra Empresas (azul / naranjo) y cada uno
muestra sus modalidades. Del 2026-10-14 al 2026-10-20 "Total" apilaba las 16 modalidades y cada modalidad era un
nodo del slicer; se sacaron (no se elige un producto suelto). "Panorama" muestra nivel,
aportes al crecimiento, tabla y momentum;
"calidad", NPL / NIM / ROE y la tasa de los créditos nuevos contra el CDI.

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

    python -X utf8 pipeline/preparar_credito_paginas_powerbi.py   # SGS ya al día (actualizar.py lo refresca al empezar)

La lectura de IF.data (informes 11, 13, 8 y 16) está en ``ifdata_credito.py``; los informes se bajan a mano
(``ifdata.py colectar``). Corre después de ``preparar_bancos_powerbi.py`` (usa ``datos/gold``).
```

## `pipeline/preparar_gold_bancos.py` (766 líneas)

Importa del pipeline: `almacen`, `bancos`, `periodos`, `registro_metricas`, `reglas_gold`, `sgs`

Subcomandos: `base` — bk_banco, bk_metrica, bk_panel, bk_grupo y bk_puente; necesita bk_cartera y bk_sistema_q; `rentabilidad` — bk_roe_arbol y bk_sensibilidad (encargo 64)

```text
Capa gold base del dashboard de bancos: tablas bk_* que leen el sitio, y el puente IF.Data ↔ publicado.

POR QUÉ EXISTE
--------------
El sitio de bancos no calcula nada («Python calcula, el navegador dibuja»,
docs/SPEC_DATOS_BANCOS_v0.1.md §1.3). Las fórmulas viven aquí, una sola vez, y el
sitio lee tablas ya listas. Este subcomando (``base``) no baja nada de la red: reordena lo que ya
existe —el panel de métricas por banco y trimestre (``datos/intermedio/metricas_bancos.parquet``), las
dimensiones de los bancos (``bancos.py``), las métricas (``registro_metricas.py``) y el cruce IF.Data ↔
publicado (``definiciones/validacion_bancos.json``)— y lo entrega en cinco tablas: ``bk_banco``, ``bk_metrica``
(definición de cada métrica), ``bk_panel`` (banco × trimestre × métrica, con rezagos, percentiles del grupo y
rankings), ``bk_grupo`` (óptica × grupo × trimestre × métrica, con muestra constante) y ``bk_puente``.

Reglas que no se tocan: no se recalculan TTM, ROE, ROA, cuotas ni crédito total (salen de
preparar_metricas_bancos.py). Los agregados de grupo son sumas o cocientes de sumas, nunca promedios de ratios.
Lo que no tiene definición segura queda en null.

Uso:

    python -X utf8 pipeline/preparar_gold_bancos.py base

El subcomando ``rentabilidad`` (encargo 64) añade ``bk_roe_arbol`` (árbol del ROE por banco y
por grupo) y ``bk_sensibilidad`` (beta del NIM contra el CDI); no reescribe las tablas de base.

    python -X utf8 pipeline/preparar_gold_bancos.py rentabilidad
```

## `pipeline/preparar_gold_bancos_cartera.py` (282 líneas)

Importa del pipeline: `almacen`, `bancos`, `ifdata_credito`, `mora_sistema`, `periodos`, `reglas_gold`

```text
Cartera de crédito por banco × modalidad (capa gold del dashboard de bancos): bk_cartera, bk_cartera_totales,
bk_cartera_grupo y bk_cartera_mix7.

POR QUÉ EXISTE
--------------
La ficha por banco del dashboard web necesita el saldo y el vencido ≥15 días de cada modalidad por banco
(los `cre_*` del PBIP solo tienen grupos). La lectura de los informes 11 (PF) y 13 (PJ) es la de
`ifdata_credito.py`, la misma que usa preparar_credito_paginas_powerbi.py.

Reglas (ver ifdata_credito.py):
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
Se publican con almacen.publicar_gold (procedencia en datos/derivado/bcb_ifdata/bancos_gold_cartera/).

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

Uso:  python -X utf8 pipeline/preparar_gold_bancos_cartera.py               (reconstruye desde el crudo, vía ifdata_credito.py)
      python -X utf8 pipeline/preparar_gold_bancos_cartera.py --solo-mix7  (lee datos/gold/bk_cartera*.parquet; reescribe
                                                                   solo bk_cartera_grupo y bk_cartera_mix7)

La comprobación de mix7 contra cartera_saldo de bk_panel la hace `preparar_gold_bancos.py base`, que es
quien produce bk_panel (y lo produce después de este script).
```

## `pipeline/preparar_gold_bancos_concesiones.py` (183 líneas)

Importa del pipeline: `almacen`, `sgs`, `tabla_estandar`

```text
Concesiones libre / dirigido por segmento y el índice de concesiones reales frente a la actividad.

Es la base de la sección 01 de la Portada (canvas, láminas 06–08): libre = SGS 20634 (total), 20635 (empresas) y
20662 (personas); dirigido = total − libre. El índice compara el crédito concedido real con la actividad (IBC-Br).

TABLAS (datos/gold/)
------------------
- bk_concesiones (larga, una fila por segmento y mes): segmento, fecha (último día del mes),
  concesiones (R$ millones, flujo del mes), conc_12m (suma móvil de 12 meses, R$ millones), conc_12m_aa (a/a de esa suma, fracción),
  conc_real_12m (suma móvil de 12 meses deflactada, R$ millones a precios del último mes), ibc_12m (promedio móvil de
  12 meses del IBC-Br desestacionalizado), indice (concesiones reales 12m / IBC-Br 12m, base promedio 2014 = 100),
  indice_aa (a/a del índice, fracción) e indice_z120 (z-score del índice en 120 meses).
  Clave: segmento, fecha. Segmentos: tot, pf, pj, li, di, pfli, pfdi, pjli, pjdi.
- bk_concesiones_tablas: tabla estándar (bloque, orden, fila, grupo, ultimo, d1, d3, d12, dventana, corte, unidades,
  share, z120). Bloques: «mes» (concesiones del mes, R$ mil millones), «12m» (suma móvil, R$ mil millones) e «indice»
  (índice de concesiones reales frente a la actividad, puntos con base 2014 = 100). Clave: bloque, orden.
  La fila Total del bloque «mes» es «Concesiones totales» de bk_cred_tablas: mismas cifras (control en las pruebas).

REGLAS
------
- Segmentos: total = SGS 20631; personas = 20633; empresas = 20632; libre = 20634; libre empresas = 20635;
  libre personas = 20662. Dirigido = total − libre del mismo grupo: di = 20631 − 20634, pfdi = 20633 − 20662,
  pjdi = 20632 − 20635. Así li + di = total exacto y pf/pj se reconstruyen con sus libres y dirigidos.
  Identidades de la fuente: 20631 = 20632 + 20633 y 20634 = 20635 + 20662. Las series están en millones enteros, así
  que cada identidad puede fallar en ±1 R$ millón por redondeo (pruebas de integración).
- Deflactación: índice de precios a partir de la variación mensual del IPCA (SGS 433), encadenado
  (producto acumulado de 1 + var/100) y normalizado al último mes (sgs.deflactor). Cada concesión mensual se divide
  por el índice de su mes (precios del último mes). La normalización a 2014 = 100 del índice final elimina esa
  escala y no cambia la forma de la serie.
- Índice: concesiones reales 12m / IBC-Br desestacionalizado promedio 12m (SGS 24364), dividido por su promedio de los
  meses de 2014 y multiplicado por 100. El IBC-Br publica con dos meses de atraso: el índice llega al último mes del
  IBC-Br; el último mes de concesiones queda sin índice (no se rellena).
- Tabla estándar. En «mes» (flujo): m/m y a/a son el mes contra el anterior y contra el mismo mes del año anterior;
  3m/3m es el promedio de tres meses contra los tres anteriores; 12m/12m es la suma de doce meses contra la de los
  doce anteriores. En «12m» e «indice» (saldos): las ventanas son promedios de valores. Share: segmento contra total
  en el mismo mes («mes» y «12m»); vacío en el índice.
- Z-score del índice: (índice_t − media) / desviación típica muestral (ddof = 1) de los 120 meses que terminan en t.
  Solo con los 120 meses completos; antes queda vacío.
```

## `pipeline/preparar_gold_bancos_empresas.py` (292 líneas)

Importa del pipeline: `almacen`, `preparar_gold_bancos_producto_pf`, `preparar_gold_bancos_scr_productos`, `sgs`, `tabla_estandar`

```text
Hojas de empresas «MPME» y «Grandes» (frente 13).

Lleva a gold las cifras que el canvas de rediseño calculaba con el borrador `extraer_empresas.py`. Mismas fórmulas
que las hojas por producto de personas (`preparar_gold_bancos_producto_pf.py`, frente 12), de donde se importan los
cálculos de celdas y efectos.

TABLAS (datos/gold/)
--------------------
- bk_empresas_m (SGS, mensual): segmento, sub, medida, fecha (último día del mes), valor.
  Clave: segmento, sub, medida, fecha.
  * Segmentos: ``empresas`` (sub ``total``, ``libres``, ``direccionados``), ``mpme`` y ``grandes`` (sub ``total``),
    ``modalidad`` (sub = modalidad PJ del SGS: capital de giro, descuento de duplicatas, comercio exterior, BNDES…)
    y ``referencia`` (sub ``selic``, medida ``tasa``: Selic efectiva del mes anualizada, SGS 4189).
  * Niveles: ``saldo`` y ``concesiones`` (R$ millones; concesiones = flujo del mes); ``tasa``, ``mora90``,
    ``atraso15_90``, ``spread``, ``icc``, ``riesgo_eh`` y ``riesgo_4966`` (fracción: el % del SGS / 100).
  * Derivadas: ``saldo_aa`` (fracción) en todo lo que tiene saldo; ``peso`` de mpme y grandes en (mpme + grandes)
    (suman 1) y de cada modalidad en el saldo de empresas total (no suman 1: faltan modalidades chicas).
  * Descomposición de la tasa media de las modalidades libres con tasa (sub ``media`` y por modalidad, misma función
    que el frente 12): ``tasa_media``, ``d_tasa_media``, ``efecto_mezcla``, ``peso_saldo``, ``efecto_tasa``.
    Pondera por SALDO, no por concesiones: con concesiones el cheque especial (357 % a.a., concesiones del mes
    ≈ saldo) lleva la media a 52,8 % contra 24,4 % de la 20718 (sep-26); con saldo queda a ~2 pp. No es la 20718
    (faltan «outros créditos livres», sin tasa publicada).
- bk_empresas_scr_m (SCR.data, mensual desde ene-18): hoja, dimension, segmento, medida, fecha, valor.
  Clave: hoja, dimension, segmento, medida, fecha. Hojas: ``mpme`` (micro + pequeña + mediana) y ``grandes``.
  * Dimensiones: ``total`` («Total»), ``porte`` (solo mpme), ``sector`` (10 secciones CNAE + «Otros sectores»),
    ``institucion`` y la celda de la descomposición (``porte_sector`` en mpme, ``sector_institucion`` en grandes).
  * Medidas de nivel: ``saldo``, ``mora90``, ``atraso15_90``, ``activo_problematico`` (R$), ``ops``, ``cart_ops``;
    razones ``tasa_mora``, ``tasa_atraso``, ``tasa_apr``, ``peso``, ``saldo_aa``, ``ops_aa``, ``ticket``
    (cart_ops / ops, R$) y ``ticket_real`` (R$ del último mes, IPCA).
  * Aportes por dimensión (fracción; suman el total cada mes): ``aporte_crec``, ``aporte_mora``/``aporte_atraso``,
    ``efecto_tasa_x``, ``efecto_mezcla_x`` (fórmulas en preparar_gold_bancos_producto_pf.py).
  * Tres partes (dimensiones ``descomp_<a>_primero`` y ``descomp_<b>_primero``, medidas ``mora`` y ``atraso``):
    ``efecto_tasa`` (en celdas a × b), ``mezcla_<a>``, ``mezcla_<b>`` y ``variacion_total``. MPME: a = porte,
    b = sector. Grandes: a = sector, b = institución.

REGLAS
------
- 27706/27707 (riesgo E–H por porte) están DESACTIVADAS y terminan en dic-24; desde ene-25 el SGS publica el % de
  mayor riesgo de la Res. CMN 4.966 (29581–29583). No empalman: son definiciones distintas.
- 27701 + 27702 no es exactamente 20540 (diferencia de hasta R$ 37 mil millones): el peso de cada porte se mide sobre
  la suma de los dos, no sobre el total de empresas.
- SCR: el porte «Indisponível» queda fuera de las dos hojas (R$ 124 mil millones en sep-26). Instituciones como el
  canvas: Bancos, Desarrollo y fomento, Cooperativas, Financieras, Fintechs, Inst. de pago y Otros.
```

## `pipeline/preparar_gold_bancos_exposicion.py` (92 líneas)

Importa del pipeline: `almacen`, `mora_sistema`, `periodos`, `reglas_gold`

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
Salida:   datos/gold/bk_exposicion.parquet (banco × trimestre).
Uso:      python -X utf8 pipeline/preparar_gold_bancos_exposicion.py
```

## `pipeline/preparar_gold_bancos_fondeo.py` (115 líneas)

Importa del pipeline: `almacen`, `sgs`, `tabla_estandar`

```text
Hoja «Fondeo y liquidez» (frente 14): agregados monetarios de la metodología nueva del BCB (SGS).

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
```

## `pipeline/preparar_gold_bancos_pag_credito.py` (149 líneas)

Importa del pipeline: `almacen`, `periodos`, `sgs`, `tabla_estandar`

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

## `pipeline/preparar_gold_bancos_portada.py` (192 líneas)

Importa del pipeline: `almacen`, `bancos`, `ifdata_texto`, `sgs`, `tabla_estandar`

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
  d12, dventana, corte y las unidades de la tabla estándar. En crédito: saldo (R$ mil millones), y % de variación; en mora: nivel
  en % y cambios en pp; en ROE: % y pp con d1 = t/t, d3 vacío, d12 = a/a, dventana = 4T/4T.
- bk_portada_cuotas: vista, orden, banco, cuota (fracción), grupo, periodo. Diez mayores + «Resto».

REGLAS
------
- 3m/3m y 12m/12m: promedio de la ventana sobre el de la ventana anterior (saldos) o diferencia de
  promedios (tasas). m/m y a/a: punta contra punta.
- Real: saldo deflactado por el índice IPCA encadenado (SGS 433), base último mes.
- Contribución: (componente_t − componente_t−12) / total_t−12, en pp. Libre + direccionado = total
  (diferencia < 1 %); PF + PJ = total.
- Series SGS: saldos del crudo bcb_sgs/bancos_sistema (sgs.py); mora > 90 días de bk_sistema_m; CDI de
  sgs.cdi_12m (promedio de los 12 meses que terminan en el trimestre).
- Cuotas: último trimestre del panel IF.Data con informes de pasivo (r3) y cartera PF/PJ (r11, r13);
  activos y crédito total desde bk_panel (share_ativo, share_credito). Solo conglomerados del panel.
```

## `pipeline/preparar_gold_bancos_producto_pf.py` (368 líneas)

Importa del pipeline: `almacen`, `preparar_gold_bancos_scr_productos`, `sgs`, `tabla_estandar`

```text
Hojas por producto de personas (frente 12): tarjeta, personal sin planilla, descuento por planilla y vehículos.

Lleva a gold las cifras que el canvas de rediseño calculaba con el borrador `extraer_producto.py`. Dos tablas largas,
genéricas por producto (columna ``producto``), en vez de una tabla por hoja.

TABLAS (datos/gold/)
--------------------
- bk_producto_pf_m (SGS, mensual): producto, sub, medida, fecha (último día del mes), valor.
  Clave: producto, sub, medida, fecha.
  * Niveles: ``saldo`` y ``concesiones`` (R$ millones; concesiones = flujo del mes), ``tasa`` y ``mora90``
    (fracción: el % del SGS / 100).
  * Descomposición de la tasa media (solo productos con submodalidades en ``DESCOMPONER``), con
    ``sub = "media"``: ``tasa_media`` (Σ w_i·r_i, w = peso de la submodalidad en las concesiones del mes),
    ``d_tasa_media`` (a/a, fracción), ``efecto_mezcla``; y por submodalidad ``peso_conc`` y ``efecto_tasa``.
    efecto_tasa_i = w̄_i·Δr_i; efecto_mezcla = Σ (r̄_i − r̄)·Δw_i, con promedios de t y t−12. Suman d_tasa_media.
  * Productos de referencia: ``personas`` (total personas: saldo, concesiones, tasa, mora) y ``referencia``
    (sub ``selic``, medida ``tasa``: Selic efectiva del mes anualizada, SGS 4189; sub ``salario_minimo``, medida ``nivel``:
    R$, último dato del mes y arrastrado a los meses sin cambio).
- bk_producto_pf_scr_m (SCR.data, mensual desde ene-18): producto, dimension, segmento, medida, fecha, valor.
  Clave: producto, dimension, segmento, medida, fecha. Productos: tarjeta, tarjeta_interes, tarjeta_contado,
  personal, planilla y vehiculos. Las instituciones de pago tienen solo tarjeta al contado: la mora por institución
  de la tarjeta se lee en tarjeta_interes (verificaciones del 10-nov).
  * Dimensiones: ``total`` (segmento «Total»), ``renta`` (7 tramos + «Sin renta / N.D.»), ``institucion``,
    ``ocupacion``, ``renta_institucion`` y ``renta_ocupacion`` (celdas «tramo · institución» y «tramo · ocupación») y ``tope_3sm`` («Hasta 3 SM»,
    «Más de 3 SM» y «Sin renta / N.D.», aparte desde el 10-nov).
  * Medidas de nivel (todas las dimensiones): ``saldo``, ``mora90``, ``atraso15_90``, ``activo_problematico``
    (R$), ``ops`` (número de operaciones), ``cart_ops`` (R$ de las celdas con operaciones) y las razones
    ``tasa_mora``, ``tasa_atraso``, ``tasa_apr``, ``peso`` (saldo / saldo total del producto), ``saldo_aa`` y
    ``ticket`` (cart_ops / ops, R$) y ``ticket_real`` (R$ del último mes, IPCA).
  * Aportes (renta, institución, ocupación), en fracción (pp / 100), suman el total en cada mes:
    ``aporte_crec`` = (S_i,t − S_i,t−12) / S_total,t−12; para x en {mora, atraso}: ``aporte_x`` =
    w_i,t·m_i,t − w_i,t−12·m_i,t−12, ``efecto_tasa_x`` = w̄_i·Δm_i, ``efecto_mezcla_x`` = m̄_i·Δw_i.
  * Tres partes (dimensiones ``descomp_renta_primero`` y ``descomp_institucion_primero``, medidas ``mora`` y
    ``atraso``): segmentos ``efecto_tasa`` (en celdas renta × institución), ``mezcla_renta``,
    ``mezcla_institucion`` y ``variacion_total``. La mezcla del primer factor se mide sola; la del segundo es la
    mezcla de las celdas menos la del primero.
  * Meses de renta por operación (dimensión ``renta``, 7 tramos con renta): ``meses_renta_medio``,
    ``meses_renta_piso`` (renta en el piso del tramo: cota alta) y ``meses_renta_techo`` (cota baja) = ticket /
    (salario mínimo × múltiplo del tramo). «Hasta 1 SM» usa 0,75 / 0,5 / 1 y «Más de 20 SM» 20 en las tres.

REGLAS
------
- SGS: el personal no consignado TOTAL (20574, 20666, 20742, 21114) ya incluye la renegociación (20575, 20667,
  20743, 21115); el total de la hoja personal es personal + sobregiro y la renegociación es una parte, nunca un
  sumando (validado el 10-nov: 20580 = 20574 + 20579).
- Tarjeta: 22024 incluye el contado a tasa 0 y no se reconstruye con 22022/22023; la descomposición se hace contra la
  tasa media reconstruida (rotativo + cuotas ponderadas por concesiones), que no es 22024.
- Aportes: si un segmento no existe en t o en t−12, su tasa faltante toma la del otro período (todo su aporte cae en
  mezcla). Celdas sin saldo pesan 0.
- Agrupación de instituciones del canvas: Bancos, Cooperativas, Fintechs, Inst. de pago, Financieras y Otros. Difiere
  de definiciones/scr_productos.json (que manda Fintech a «Otras»): es la que Pablo aprobó en la hoja Tarjeta.
- Ocupación: asalariado privado incluye entidades sin fines de lucro; empresarios incluye MEI; el resto (incluido
  el valor «Outros» de la fuente) va a «Otros».
- Quiebres del SCR (no se suavizan): jul-25 reclasificación de renta; ago-26 ~R$ 15 mil millones de tarjeta pasan
  de «más de 20 SM» a «Indisponível».
```

## `pipeline/preparar_gold_bancos_pyb.py` (422 líneas)

Importa del pipeline: `almacen`

```text
Hoja «P&L y balance por banco» (frente 15): estado de resultados, balance y capital por banco y trimestre.

Lleva a gold lo que el canvas calculaba con el borrador ``extraer_pyb.py``. El mapa de cuentas por época del plan
contable (antes y desde 1T25, Res. CMN 4.966) está en ``definiciones/pyb_lineas.json``, no en el código.

FUENTES
-------
- bank_hechos (IF.Data, conglomerado prudencial, informes 2 activo, 3 pasivo y 4 resultados). ``valor`` del informe 4
  es el flujo del trimestre (ya desacumulado del semestre).
- bk_panel: crédito bruto y pérdida esperada acumulada (balance), activo y patrimonio medio 12m (denominadores),
  ROE y modelo de negocio (grupo de la mediana).
- bk_capital y bk_capital_grupo (informe 5): sección P7 Capital.
- bk_producto_pf_m (referencia/selic): Selic efectiva del mes, para el costo de fondeo relativo.

TABLAS (datos/gold/)
--------------------
- bk_pyb: cod_inst, periodo (AAAAMM), trimestre («2T26»), seccion, linea, medida, valor.
  Clave: cod_inst, periodo, linea, medida.
  * seccion ``pyl``: medidas ``rs_trim`` (R$ del trimestre), ``rs_12m`` (R$, suma de cuatro trimestres
    consecutivos; si falta uno, no hay fila) y ``pct_activo_medio_12m`` (rs_12m / ativo_medio_ttm de bk_panel,
    en fracción).
  * secciones ``activo`` y ``pasivo``: ``rs`` (saldo a fin de trimestre, R$) y ``pct_activo`` (rs / activo total,
    fracción). El pasivo se divide por el activo total (= pasivo total).
  * seccion ``indicador``: ``roe`` (roe_ttm de bk_panel), medida ``fraccion``.
  * seccion ``capital``: índices del informe 5 (``fraccion``) y variaciones del capital principal (``rs``); ver
    CAPITAL_FRACCION y CAPITAL_RS.
  * seccion ``sensibilidad`` (``fraccion``): ``mfb_qa`` = margen financiero antes de pérdida esperada del trimestre
    × 4 / activo medio del trimestre (promedio de dos cierres consecutivos); ``cf_qa`` = −gasto de captación × 4 /
    fondeo medio (líneas ``fondeo`` de la definición); ``cf_pct`` = cf_qa / Selic efectiva media del trimestre.
- bk_pyb_grupo: grupo, periodo, trimestre, seccion, linea, medida, valor, n_bancos.
  Clave: grupo, periodo, linea, medida.
  * ``grupo`` = modelo de negocio de bk_panel: mediana de los bancos del grupo con dato (n_bancos = cuántos).
  * ``grupo`` = «Panel»: razón de sumas de los bancos con numerador y denominador (no promedio de razones):
    Σ rs_12m / Σ ativo_medio_ttm, Σ rs / Σ activo total, ROE = Σ utilidad 12m / Σ pl_medio_ttm. Capital: los
    índices cp, bas, dens, hol y req_cp se toman de bk_capital_grupo («Total panel», sus n_bancos) y apalancamiento
    y crecimientos son razón de sumas de los bancos de bk_pyb (decisión pendiente: unificar en 31 o 34 bancos).
    Sensibilidad: Σ(mfb × 4) / Σ activo medio, Σ(−captación × 4) / Σ fondeo medio y su cociente con la Selic.
  * ``grupo`` = «Referencia»: linea ``selic`` (seccion sensibilidad), promedio de los meses del trimestre de la
    Selic efectiva anualizada (bk_producto_pf_m, referencia/selic, SGS 4189), en fracción.

REGLAS
------
- La época de cada banco-trimestre sale de la columna ``era`` de bank_hechos, no de si la cuenta existe.
- Las cuentas se buscan por (informe, cuenta_base): 'ativo total' está en los informes 2 y 4 e 'instrumentos
  derivativos' en el 2 y el 3. Una cuenta usada que aparezca dos veces en el mismo informe hace fallar el paso.
- Los trimestres se ordenan por (año, trimestre); el 12m y los a/a se calculan sobre una grilla completa de
  trimestres, así un hueco deja vacío el 12m en vez de sumar trimestres no consecutivos.
- Las líneas residuales cierran contra la cuenta publicada (resultado de intermediación, resultado antes de
  impuestos, utilidad, activo total y pasivo total): las sumas cuadran por construcción y los tests lo vigilan.
```

## `pipeline/preparar_gold_bancos_qcambio.py` (156 líneas)

Importa del pipeline: `almacen`, `bancos`, `periodos`

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
Uso:      python -X utf8 pipeline/preparar_gold_bancos_qcambio.py
```

## `pipeline/preparar_gold_bancos_scr.py` (202 líneas)

Importa del pipeline: `almacen`, `scr_zip`

Argumentos: `--solo-descargar` — solo baja los ZIP 2012-2023 que falten, no deriva

```text
bk_scr: SCR.data 2012-2026 agregado en tres cortes para el dashboard de bancos.

POR QUÉ EXISTE
--------------
El spec de datos (``docs/SPEC_DATOS_BANCOS_v0.1.md`` §3.10) pide
publicar del SCR.data solo tres cortes agregados — mes × segmento × cliente,
mes × porte (solo PJ) y mes × UF — y no el cubo granular, porque el sitio
grafica series de sistema y el cubo entero son cientos de MB por año. Este
módulo lee los ZIP anuales crudos **por partes**: un año no cabe entero en memoria.

La tasa es la oficial del BCB: ``tasa = Σ carteira_inadimplencia / Σ carteira_ativa``. La columna
``carteira_inadimplencia`` del SCR.data está en R$, NO en %; escribirla como porcentaje es un error. Las tasas van como fracción (0,05 = 5 %),
igual que el resto de la capa gold.

Decisiones del encargo 67 (03-11-2026):

- Descarga y codificación de los ZIP: ver ``scr_zip.py``. Un año que falla 3 veces corta la corrida.
- **``numero_de_operacoes`` == -1 es secreto estadístico**, no un número; no se
  suma (aquí ni se usa: los cortes son de saldo). Las filas con -1 sí traen
  valores en R$ y entran a las sumas de cartera.
- **``porte`` del corte PJ va tal cual lo publica el BCB** (Micro, Pequeno,
  Médio, Grande, Indisponível); la etiqueta del sitio va aparte en ``porte_es``.
- Cada ZIP se agrega una vez y queda en ``datos/intermedio/scr/scrdata_<año>.parquet``; se recalcula si el ZIP
  es más nuevo (el del año en curso cambia cada mes).

Receta::

    python -X utf8 pipeline/preparar_gold_bancos_scr.py                # baja 2012-2023 y deriva
    python -X utf8 pipeline/preparar_gold_bancos_scr.py --solo-descargar
```

## `pipeline/preparar_gold_bancos_scr_productos.py` (338 líneas)

Importa del pipeline: `almacen`, `reglas_gold`, `scr_zip`, `tabla_estandar`

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
   (dims: fecha, cliente, segmento, porte, cnae_ocupacao, producto; un producto con «partes» se guarda
   abierto, p. ej. la tarjeta en contado y con interés, y se junta antes de construir). Un mes se recalcula si falta o si su
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
  (salto del mix); jul-26 pico de un mes en «más de 20 SM» de tarjeta (+R$ 14 mil millones, se revierte en
  ago-26); ene–feb-26 la mora de «Indisponível» en tarjeta salta de ~9 % a ~28 % (revisado el 10-nov).

Uso (desde pipeline/, Windows con -X utf8):
    python -X utf8 pipeline/preparar_gold_bancos_scr_productos.py [--descargar] [--desde AAAA]
```

## `pipeline/preparar_gold_bancos_sistema.py` (357 líneas)

Importa del pipeline: `almacen`, `focus`, `sgs`

```text
Series del Sistema financiero (SGS + tablas del macro) para el dashboard de bancos.

POR QUÉ EXISTE
--------------
El spec de datos del dashboard de bancos (``docs/SPEC_DATOS_BANCOS_v0.1.md``
§3.9) pide las series del Sistema —mora 90, atrasos 15-90, crédito real, crédito dirigido,
spread, ICC, deuda de hogares— en formato largo mensual y trimestral con bandas. Esas series
vienen del SGS, de la encuesta Focus (``focus.py``) y del BIS;
reunirlas en cada página del sitio produciría cifras divergentes. Este módulo es el único
lugar donde se transforman, y escribe ``datos/gold/bk_sistema_m.parquet`` y
``datos/gold/bk_sistema_q.parquet``.

Decisiones del encargo 61 y su corrección 61b (02-11-2026, «Decisiones del arquitecto»
en ``docs/PENDIENTES.md``), registradas aquí para el que relea:

- Los 38 códigos del encargo respondieron con JSON y fechas recientes (2-nov-2026). Ninguno se reemplazó.
- ``impulso_credito`` no existe como tabla en ``pb/`` (se revisó el inventario; solo aparece
  en un docstring), así que se recalcula con SGS 20539 + 4382. Se publica en pp del PIB
  como ``impulso_credito_pp``.
- 61b · Unidades: TODA la tabla va en fracción (0,05 = 5 %): mora, atrasos, spread, icc,
  credito_pib, crecimientos reales y las series que ya venían en fracción de pb. Solo el
  impulso y el hiato del BIS quedan en pp, marcados con sufijo ``_pp`` y columna ``unidad``
  (fraccion | pp).
- 61b · mora90 por modalidad: TODAS salen del SGS (21119, 21121, 21127, 21151 incluidas);
  ``hogares_modalidades`` queda fuera de esta tabla (solo B4-02). ``mora90_personal`` =
  21114 (personal NO consignado, nombre oficial del SGS). Equivalencia «Tarjeta de crédito» = 21129 (total); 21127 y
  21128 son detalle.
- 61b · Nombres sin la expansión mecánica del shorthand de §3.9:
  ``dirigido_{rural,imob,bndes}_real_aa``, ``credito_grande_real_aa`` (27702),
  ``mora90_grande`` (27704).
- ``comprometimento`` (29034), ``endividamento`` (29037) y ``desocupación`` (24369, PNADC = IBGE
  t6381|v4099) se leen del SGS desde el 6-nov-2026 (tarea 1.3; antes venían congeladas de
  ``datos/intermedio/``). Desde el 8-nov-2026 tampoco quedan entradas congeladas: ``ipca_esperado_12m`` sale
  de Focus (``focus.py``) y ``selic_real_exante`` = (1 + meta Selic SGS 432) / (1 + Focus IPCA 12m) − 1 por día
  de encuesta, media mensual (23 trimestres es excepción aceptada). Reproduce al decimal la entrada congelada
  ``datos/intermedio/tasa_real_exante.parquet`` que dejó el dashboard macro.
- ``bis_hiato_credito_pib_pp`` se lee del crudo local ``datos/crudo/bis/credit_gap`` tal
  cual, en pp (solo trimestral). ``pix_share`` queda fuera: encargo propio en la ola 2.

78c (encargo 78, ola 4): ipca_12m (acumulado 12 meses desde SGS 433), ipca_esperado_12m
(mediana Focus a 12 meses, último envío de cada mes), icc_real_exante (ex ante),
mora90_pf_livre_adel3m (mora 90 de t+3 en la fecha t) y d_1m / d_3m en bk_sistema_m.
En _q, ipca_12m toma el último mes del trimestre; el resto, promedio como siempre.

Receta:

    python -X utf8 pipeline/preparar_gold_bancos_sistema.py   # deriva; una serie que falte en el crudo se baja
                                                     # (el refresco de todas: paso «sgs» de actualizar.py)
```

## `pipeline/preparar_metricas_bancos.py` (177 líneas)

Importa del pipeline: `almacen`, `periodos`, `registro_metricas`

```text
Prepara la capa de métricas del dashboard de bancos (proyecto independiente).

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
```

## `pipeline/red.py` (62 líneas)

```text
Reintentos y descargas a disco: la única política de reintento del pipeline (bcb_api, ifdata, scr_zip).
```

## `pipeline/ref.py` (479 líneas)

Importa del pipeline: `almacen`, `certificados`, `red`

Argumentos: `--forzar` — vuelve a bajar las ediciones ya bajadas; `--descargar` — con «todo», baja antes las ediciones que falten; sin esta opción no toca la red; `--resumen` — con «gold», no publica

```text
REF del BCB: Anexo Estatístico (xlsx) de cada edición → bk_ref (edición × gráfico × serie × punto).

Fuente: https://www.bcb.gov.br/publicacoes/ref. Cada edición semestral del Relatório de Estabilidade Financeira
publica un xlsx con una hoja por gráfico o tabla («Graf 1.2.2.16», «Tab 1.2.4.1»). Es público, a diferencia del
PDF guardado en referencias/: el xlsx se baja a datos/crudo/bcb_ref/anexo/<edicion>/ con su manifiesto.

Trampas (verificadas el 9-nov-2026 sobre las ediciones 202304 a 202610):
1. El mes de publicación varía (may-26 en vez de abr-26): las ediciones se listan en definiciones/bcb_ref.json y
   «descargar» sondea los meses candidatos del semestre siguiente para avisar de una nueva.
2. Cada hoja tiene su forma: título, «Fonte», notas, una fila de unidad («%», «R$ bilhões»), uno o dos niveles de
   encabezado (el superior en celdas combinadas que openpyxl lee como vacías a la derecha) y después los datos.
3. Las fechas vienen como datetime, como «2020-12», o como «Jun\n2023» seguido de «Jul», «Ago»… sin año.
4. Hay hojas sin eje temporal (distribuciones, tablas por categoría, resultados del estrés): se guardan con
   ``categoria`` en vez de ``fecha_ref``. La hoja de supuestos del estrés («Grafs 1.2.5.1 a 1.2.5.5») tiene su
   propio lector (leer_escenarios): bloques por variable, una fila por escenario y trimestres en columnas.
5. Algunas columnas vienen vacías a propósito (el contrafactual de 1.2.2.21 solo existe en la proyección):
   no se rellena nada; una celda vacía no genera fila.

Uso:  python -X utf8 pipeline/ref.py descargar   (baja las ediciones que falten y sondea la siguiente)
      python -X utf8 pipeline/ref.py gold        (lee todas las ediciones bajadas → bk_ref)
      python -X utf8 pipeline/ref.py --descargar (las dos cosas; así lo llama actualizar.py, que quita
                                                   --descargar cuando corre sin red)
```

## `pipeline/registro_metricas.py` (73 líneas)

Importa del pipeline: `almacen`

```text
Registro único de las métricas del panel (``definiciones/metricas_bancos.json``).

De aquí salen los valores por banco (preparar_metricas_bancos.py y preparar_gold_bancos.py), los agregados por
grupo (Σ numerador / Σ denominador) y el texto de ``bk_metrica``. Cambiar una fórmula es cambiar el JSON.
```

## `pipeline/reglas_gold.py` (59 líneas)

Importa del pipeline: `periodos`

```text
Reglas de la capa gold que comparten los preparadores, el exportador y herramientas/verificar_gold.py:
tolerancias y umbrales, marcas de dato con licencia, rango de fechas de una tabla y la comprobación de mix7.

Va aparte para que el verificador no tenga que importar los scripts que producen las tablas.
```

## `pipeline/scr_zip.py` (85 líneas)

Importa del pipeline: `almacen`, `certificados`, `red`

```text
ZIP anuales del SCR.data (``datos/crudo/bcb_scr/scrdata/actual/scrdata_<año>.zip``): descarga y lectura.

- La descarga va streameada a disco y se registra con ``almacen.registrar_crudo`` (los ZIP pesan cientos de MB).
- Los CSV del SCR.data son UTF-8 con BOM, no cp1252 como el resto de los archivos del gobierno brasileño
  (verificado byte a byte en 2012 y 2024); se prueba UTF-8 estricto y se cae a cp1252 solo si falla.
- Valores con coma decimal y sin separador de miles.
```

## `pipeline/sgs.py` (213 líneas)

Importa del pipeline: `almacen`, `bcb_api`, `certificados`, `red`

```text
Series del SGS del BCB: el único lector y descargador del pipeline.

Cada serie vive en ``datos/crudo/bcb_sgs/<dataset>/actual/serie_<codigo>.json`` con la forma
``[{"data": "DD/MM/AAAA", "valor": "..."}]``. Si falta, se baja con ``bcb_api.descargar_serie`` (que sabe
que una serie inexistente llega como HTML y no como 404) y se guarda por ``almacen`` con su URL.

Siempre se pide con ``dataInicial``: sin fechas el SGS llegó a servir series atrasadas.
```

## `pipeline/tabla_estandar.py` (85 líneas)

Importa del pipeline: `periodos`

```text
La tabla estándar del sitio (Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m): sus variaciones.

Mensuales:
- saldos: m/m y a/a punta contra punta; 3m/3m y 12m/12m = promedio de la ventana sobre el de la ventana
  anterior (en flujos, 12m/12m compara sumas de doce meses);
- tasas: las mismas ventanas como diferencias (en la unidad de la serie × ``escala``).
Trimestrales: d1 = t/t, d3 vacío, d12 = a/a, dventana = 4T/4T, como diferencias.

Las variaciones son un dict con ultimo, d1, d3, d12, dventana y corte; ``fila`` les antepone las columnas propias
de cada tabla, en el orden en que se pasan (ese es el orden de las columnas del parquet), y exige ``COLUMNAS``.
```

## `herramientas/comparar_gold.py` (56 líneas)

```text
Compara celda por celda dos carpetas de parquets gold (misma forma, mismas columnas, mismos valores).

Uso: python -X utf8 herramientas/comparar_gold.py <carpeta_a> <carpeta_b>
Los floats se comparan con tolerancia relativa 1e-12 (solo ruido de redondeo); todo lo demás exacto.
`bk_manifiesto` se compara sin bytes ni sha256.
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

## `herramientas/generar_spec.py` (187 líneas)

```text
Regenera spec/generado/: el inventario automático del repo (tablas gold, métricas, bancos, páginas,
componentes, scripts y definiciones). La parte narrativa de spec/ se escribe a mano; esta se regenera
para que no quede desactualizada.

Uso (desde la raíz del repo):  python -X utf8 herramientas/generar_spec.py
Requiere los parquet de datos/gold (no van a git) y Node para leer la configuración de páginas.
```

## `herramientas/validar_sgs.py` (95 líneas)

Importa del pipeline: `almacen`, `certificados`, `red`, `sgs`

Argumentos: `--escribir` — reescribe definiciones/bcb_sgs__catalogo.json

```text
Valida las series de sgs.CODIGOS contra el catálogo oficial del SGS (nombre, unidad, periodicidad).

Consulta el servicio web público del SGS (FachadaWSSGS.getUltimoValorXML), que devuelve el nombre oficial de cada
código, y lo compara con definiciones/bcb_sgs__catalogo.json. Sirve para no volver a identificar una serie solo
porque «los montos cuadran» (spec/08 punto 5, cerrado el 9-nov-2026).

Uso:
    python -X utf8 herramientas/validar_sgs.py            compara y avisa diferencias (no escribe)
    python -X utf8 herramientas/validar_sgs.py --escribir   reescribe el catálogo con lo que dice hoy el SGS
Después de --escribir, revisar a mano que cada nombre oficial corresponda a la clave que lo usa.
```

## `herramientas/verificar_cvm.py` (371 líneas)

Importa del pipeline: `almacen`, `bancos`, `cvm`, `periodos`

Argumentos: `--estricto` — las advertencias también fallan; `--json` — salida en JSON; `--sin-contraste` — no compara contra IF.Data

```text
Verificador de solo lectura de la fuente CVM (ITR/DFP) y de su tabla gold ``bk_publicado``.

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
```

## `herramientas/verificar_f1.py` (241 líneas)

Argumentos: `--url` — sitio publicado (sin / final); si falta, levanta uno local; `--anchos` — anchos en px separados por coma, p. ej. 1920,1280,390

```text
Verifica el sitio de bancos sobre todas las páginas de config.js (PAGINAS), con y sin ?banco=itau.

Qué comprueba, con un Chromium real sobre un servidor propio (python -m http.server, que se cierra
al terminar con su mismo PID; no se usa ningún servidor que ya estuviera corriendo):
  1. cada página responde 200 y carga sin errores de consola ni de página;
  2. el número de secciones y de tarjetas es el de la config y el del esqueleto (esqueleto_tarjetas.json);
  3. cada tarjeta lleva el título de su config; si la config NO tiene armar(), la tarjeta está
     «en preparación» (esa exigencia no aplica a las tarjetas con armar());
  4. ninguna tarjeta con armar() muestra error de carga o de cálculo, y ninguna queda cargando: se espera a
     <html data-pagina="lista"> y a que ningún nodo siga en data-estado cargando/actualizando (ciclo de vida
     explícito de pagina.js; el estado se lee de data-estado, no del texto visible);
  5. ningún «[» visible en el texto de la página;
  6. la cabecera tiene una pestaña por página visible (las de config.js sin oculta: true) y la marca de config.js;
  7. en cada ancho de --anchos, la página no tiene scroll horizontal;
  8. cada color de tokens.js (COLOR) es igual a su token de tokens.css (navy → --navy, texto2 → --texto-2).
Las configs, el esqueleto y los colores salen de herramientas/inventario_paginas.mjs (Node).
Captura de página completa solo si se pide con --captura DIR.

Con --url BASE (p. ej. https://banks-bz.pages.dev) revisa el sitio publicado en vez del local, con las fuentes
reales de Google (en local se cortan, para no depender de la red) y reporta si cargaron.

Uso: python -X utf8 herramientas/verificar_f1.py [--puerto 8080] [--url BASE] [--anchos 1920,1280,390] [--captura DIR]
```

## `herramientas/verificar_gold.py` (1261 líneas)

Importa del pipeline: `almacen`, `bancos`, `periodos`, `reglas_gold`

Argumentos: `--comparar` — parquet candidato de staging a comparar con el actual; `--estricto` — trata las advertencias como errores; `--gold` — comprueba solo las tablas gold bk_* de datos/gold (encargo 59); `--json` — salida JSON

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
  trimestrales continuos, cobertura mínima y cuotas de mercado.
- `cre_panorama.parquet` y `cre_calidad.parquet`: contrato que consume la API,
  duplicados y períodos.
- `validacion.json`: claves, números y `dif_pct` calculado.
- Opcionalmente, compara un candidato de staging contra el parquet actual.

No audita PDFs: son otra fuente, con estados explícitos (`verificado`,
`aproximado_press_release`, etc.).

Con `--gold` comprueba, en cambio, las tablas gold bk_* de datos/gold contra el
contrato de `definiciones/contrato_gold.json` y sus reglas propias.

Uso desde la raíz del repo:

    python herramientas/verificar_gold.py            # intermedio, crédito y validación
    python herramientas/verificar_gold.py --gold     # tablas gold bk_*
    python herramientas/verificar_gold.py --json
    python herramientas/verificar_gold.py --comparar <ruta>/metricas.parquet
    python herramientas/verificar_gold.py --estricto

Código de salida: 0 si no hay errores (o advertencias con `--estricto`), 1 si
hay algún error. Las advertencias no bloquean por defecto: los saltos de un
banco que sale del panel son datos reales y requieren revisión humana, no un
`assert` ciego.
```

