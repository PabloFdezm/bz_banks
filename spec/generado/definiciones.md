# Archivos de `definiciones/`

> Generado por `herramientas/generar_spec.py`. No editar a mano: se sobrescribe.


## `bancos__dashboard.json` (8 kB)

- `fuente_definicion`: Claude (arquitecto), 2026-11-02, a partir de bcb_ifdata__bancos_balances.json y del supuesto S4 del esqueleto; tickers a validar por Pablo
- `nota`: color = null: el sitio resalta el banco activo en navy y deja al resto en acero claro (spec web §5). Los cotizados con ADR en EE.UU. (NU, INTR, XP, STNE, PAGS)…
- `bancos`: lista de 34 · campos: `cod_inst`, `nombre_corto`, `slug`, `cotizado`, `ticker`, `ticker_estado`, `ficha`, `color`

## `bancos__equivalencias_mora.json` (3 kB)

- `fuente_definicion`: Arquitecto (Claude), 2026-11-03. Modalidades de definiciones/bcb_ifdata__credito_modalidades.json ↔ series de mora > 90 días del SGS en pb/Banks/bk_sistema_q.p…
- `nota`: Definiciones distintas: el NPL del panel es atraso ≥ 15 días; la mora del SGS es > 90 días. La mora implícita sirve para leer evolución y diferencias entre ban…
- `nota_21114`: 21114 es crédito personal NO consignado: su saldo (SGS 20574) es R$ 400 mil millones contra R$ 792 mil millones del consignado (20576-20578), y la mora pondera…
- `equivalencias`: objeto con 16 claves

## `bcb_balancetes__cuentas.json` (5 kB)

- `descripcion`: Concepto → cuentas COSIF del balancete 4060 (conglomerado prudencial), por época del plan de cuentas. Cada cuenta es la base de 7 dígitos (los 8 del archivo si…
- `fuente`: BCB, balancetes COSIF (documento 4060). Sondeo: tareas/borradores/balancetes_sondeo.md; cuadre contra IF.Data en tareas/borradores/balancetes_informe.md.
- `epocas`: objeto con 2 claves
- `conceptos`: objeto con 13 claves
- `publicable_desde`: 202001
- `nota_publicable`: Antes de 2019T4 el 4060 no cuadra con IF.Data (lucro y crédito con diferencias de 2 % a 100 %); causa no verificada.

## `bcb_ifdata__bancos_balances.json` (30 kB)

- `fuente`: bcb_ifdata
- `datasets`: lista de 1
- `nota`: Universo y crosswalk conservador del panel de balances/resultados bancarios. El crudo sigue siendo IF.data completo por trimestre/escopo/informe; aquí solo se …
- `bancos`: lista de 34 · campos: `cod_inst`, `nombre_corto`, `categoria`, `nota`, `fuente_definicion`, `modelo_negocio`
- `excepciones_stock`: objeto con 1 claves
- `conceptos`: objeto con 24 claves
- `columnas`: objeto con 45 claves
- `nota_modelo_negocio`: modelo_negocio: criterio del analista (Opus), aprobado por Pablo 2026-10-09 para la hoja 8 del PBIP dual (docs/orquestacion/38). No es una clasificación del BC…

## `bcb_ifdata__capital.json` (4 kB)

- `fuente`: BCB IF.Data, informe 5 «Informações de Capital», escopo 1 (conglomerado prudencial). API OLinda IfDataValores(AnoMes, TipoInstituicao=1, Relatorio='5').
- `descripcion`: Mapeo de las columnas del informe 5 a los campos de bk_capital. Se casa por el nombre de la columna SIN la letra entre paréntesis: el BCB reetiqueta las letras…
- `verificado`: 2026-11-09
- `unidades`: Montos en R$ (unidades). Índices como fracción (0,1231 = 12,31 %), tal como los publica el BCB.
- `campos`: objeto con 18 claves
- `componentes_rwa`: lista de 4
- `ignorar`: lista de 6
- `ignorar_nota`: Subcomponentes del RWA de mercado (cambio, commodities, tasas, acciones, CVA, DRC). Se leen pero no se publican: el total de mercado ya está en rwa_mercado.

## `bcb_ifdata__credito_modalidades.json` (7 kB)

- `fuente`: bcb_ifdata
- `datasets`: lista de 1
- `nota`: Modalidades de crédito de IF.data para las hojas 'Crédito: panorama' y 'Crédito: calidad' del PBIP dual (doc 41). La clave es el texto del campo Grupo del info…
- `tipos`: objeto con 2 claves
- `columna_saldo_modalidad`: Total
- `columna_vencido_modalidad`: Vencido a Partir de 15 Dias
- `npl`: objeto con 3 claves
- `opticas_derivadas`: objeto con 1 claves
- `fuente_definicion`: Campo Grupo de los informes 11 y 13 de IF.data, verificado en 201406 (financeiro) y 202603 (prudencial); etiquetas en castellano: criterio propio
- `nota_exterior`: El 'Total da Carteira' del BCB incluye las operaciones en el exterior (Itaú 2014-T2: R$ 124 mil millones solo en empresas). Las páginas usan el crédito en Bras…
- `trimestres_anomalos`: objeto con 1 claves
- `nota_duplicados`: El BCB sirvió 2025-09 (informes 11, 13 y 16) con cada fila tres veces; el preparador quita duplicados exactos y falla si queda una clave (banco, grupo, cuenta,…

## `bcb_ref.json` (3 kB)

- `fuente`: BCB, Relatório de Estabilidade Financeira (REF), Anexo Estatístico (xlsx, una hoja por gráfico o tabla). Público.
- `url`: https://www.bcb.gov.br/content/publicacoes/ref/{edicion}/RELESTAB{edicion}-refAnexoEstatistico.xlsx
- `pagina`: https://www.bcb.gov.br/publicacoes/ref
- `descripcion`: Ediciones semestrales. El mes de publicación varía (abr-23, oct-23, abr-24, oct-24, abr-25, oct-25, may-26, oct-26): «ediciones» es la lista verificada; «desca…
- `verificado`: 2026-11-09
- `ediciones`: lista de 8
- `meses_candidatos`: objeto con 2 claves
- `usados`: objeto con 2 claves
- `sitio`: objeto con 2 claves
- `_unidades_por_clave`: Unidad de los gráficos cuya hoja del anexo no trae fila de unidad, por clave de título (ref.clave_titulo: estable entre ediciones; el número del gráfico no). V…
- `unidades_por_clave`: objeto con 4 claves

## `bcb_sgs__catalogo.json` (50 kB)

- `fuente`: Servicio web público del SGS (FachadaWSSGS.getUltimoValorXML)
- `descripcion`: Nombre, unidad y periodicidad oficiales de cada serie de sgs.CODIGOS. Lo escribe herramientas/validar_sgs.py --escribir; la correspondencia clave ↔ nombre se r…
- `validado`: 2026-11-10
- `series`: objeto con 223 claves

## `contrato_gold.json` (10 kB)

- `descripcion`: Contrato de la capa gold (datos/gold/bk_*.parquet): columnas mínimas y clave única de cada tabla. Lo lee herramientas/verificar_gold.py; una tabla bk_* que no …
- `tablas`: objeto con 47 claves

## `cvm__bancos.json` (27 kB)

- `fuente`: cvm
- `descripcion`: Mapa CNPJ de la CVM → cod_inst del panel IF.Data, para la fuente ITR/DFP (pipeline/cvm.py). El filtro de bk_publicado es este mapa: un CNPJ que no está acá no …
- `convenciones`: objeto con 7 claves
- `bancos`: lista de 34 · campos: `cod_inst`, `nombre_corto`, `cnpj_raiz`, `cnpj_ifdata`, `cd_cvm`, `denominacion_cvm`, `tipo_estado`, `usar_individual_si_falta`, `base`, `entrega`, `registro_cvm`, `primera_referencia`, `ultima_referencia`, `referencias`

## `cvm__bancos_lineas.json` (30 kB)

- `fuente`: cvm
- `descripcion`: Mapeo de cuentas del ITR/DFP de la CVM a las líneas mínimas de bk_publicado. Una línea se busca por REGLA (código candidato + texto que debe contener la descri…
- `convenciones`: objeto con 6 claves
- `lineas`: objeto con 11 claves
- `plantillas`: objeto con 2 claves
- `bancos`: objeto con 16 claves

## `cvm__dfp_bancos.json` (9 kB)

- `obsoleto`: True
- `obsoleto_nota`: OBSOLETO desde el 9-nov-2026. Describe el extracto que producía el viejo extraer_fuentes.py cvm-dfp (un CSV filtrado con SETOR_ATIV, solo el activo consolidado…
- `fuente`: cvm
- `datasets`: lista de 1
- `nota`: DFP (Demonstrações Financeiras Padronizadas) de la CVM, ejercicio 2024, filtrado a bancos por `extraer_fuentes.py cvm-dfp`. DERIVADO, no dato crudo de la CVM: …
- `columnas`: objeto con 15 claves

## `cvm__estados_bancos.json` (12 kB)

- `fuente`: cvm
- `datasets`: lista de 1
- `descripcion`: Columnas del derivado de la fuente CVM (datos/derivado/cvm/bancos/estados_<doc>_<año>.parquet) y de la tabla gold bk_publicado. Lo produce pipeline/cvm.py filt…
- `nota`: DERIVADO, no dato crudo: el ZIP oficial trae todas las compañías abiertas y todos los estados contables; acá quedan solo las filas de los 16 bancos del panel q…
- `columnas_derivado`: objeto con 21 claves
- `columnas_bk_publicado`: objeto con 14 claves
- `clave_bk_publicado`: lista de 4
- `lineas_por_diseno_vacias`: Las líneas que un banco no puede tener (Cielo, que es institución de pagos y no tiene cartera ni depósitos) o que la fuente no divulga (la provisión de Banco d…

## `metricas_bancos.json` (49 kB)

- `descripcion`: Registro único de las métricas del panel de bancos: nombre, familia, unidad, formato, signo, definición y, en las razones, numerador y denominador. Lo leen pre…
- `convenciones`: objeto con 5 claves
- `orden_familias`: lista de 7
- `fondeo`: lista de 7
- `cosif_2025`: objeto con 23 claves
- `cosif_pre2025`: objeto con 20 claves
- `flujos`: objeto con 12 claves
- `ttm`: lista de 11
- `metricas`: objeto con 96 claves

## `minimos_regulatorios.json` (18 kB)

- `descripcion`: Mínimos de capital y Adicional de Capital Principal (ACP) por fecha de vigencia, como fracción del RWA. Fuente: texto de las normas CMN/BCB, relevado el 9-nov-…
- `relevado`: 2026-11-09
- `minimos`: lista de 6 · campos: `desde`, `hasta`, `cp`, `nivel1`, `pr`, `norma`, `url`
- `conservacion`: lista de 9 · campos: `desde`, `hasta`, `valor`, `norma`, `url`
- `contraciclico`: lista de 1 · campos: `desde`, `hasta`, `valor`, `norma`, `url`, `nota`
- `sistemico`: objeto con 5 claves

## `pyb_lineas.json` (19 kB)

- `_descripcion`: Mapa de líneas de la hoja «P&L y balance por banco» (frente 15) para las dos épocas del plan contable del IF.Data (conglomerado prudencial). La época sale de l…
- `_actualizado`: 2026-11-11
- `_comparable`: «comparable»: false (decisión de Pablo, 11-nov) = línea bruta que cambia de contenido con el plan contable de 1T25 (variación cambial y hedge dentro de cada lí…
- `epocas`: lista de 2
- `fondeo`: lista de 12
- `_fondeo`: Pasivos con costo explícito: denominador del costo de fondeo de la sección de sensibilidad a la Selic (sin patrimonio ni otros pasivos).
- `lineas`: lista de 45 · campos: `linea`, `seccion`, `rotulo`, `nivel`, `tipo`, `epocas`

## `scr_modalidades_pj.json` (2 kB)

- `_descripcion`: Mapa de modalidade/submodalidade del SCR.data a modalidades de crédito a empresas (PJ), para las hojas MPME y Grandes (frente 13, parte B). Mismo formato y mis…
- `_actualizado`: 2026-11-11
- `productos`: lista de 9 · campos: `producto`, `slug`, `modalidade`, `submodalidade`
- `otros`: objeto con 2 claves

## `scr_productos.json` (5 kB)

- `_descripcion`: Mapa de submodalidades del SCR.data a productos. Se aplica en orden: la primera regla que calza gana (una regla no calza si la submodalidade contiene alguna de…
- `_actualizado`: 2026-11-11
- `productos`: lista de 7 · campos: `producto`, `slug`, `partes`, `_partes`, `submodalidade`
- `otros`: objeto con 2 claves
- `tramos_pf`: objeto con 9 claves
- `hasta_3sm`: lista de 3
- `instituciones`: objeto con 8 claves
- `sectores_cnae`: objeto con 22 claves

## `validacion_bancos.json` (4 kB)


