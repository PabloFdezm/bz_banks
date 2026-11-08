# Archivos de `definiciones/`

> Generado por `herramientas/generar_spec.py`. No editar a mano: se sobrescribe.


## `bancos__dashboard.json` (7 kB)

- `fuente_definicion`: Claude (arquitecto), 2026-11-02, a partir de bcb_ifdata__bancos_balances.json y del supuesto S4 del esqueleto; tickers a validar por Pablo
- `nota`: color = null: el sitio resalta el banco activo en navy y deja al resto en acero claro (spec web §5). Los cotizados con ADR en EE.UU. (NU, INTR, XP, STNE, PAGS)…
- `bancos`: lista de 34 · campos: `cod_inst`, `nombre_corto`, `slug`, `cotizado`, `ticker`, `ticker_estado`, `ficha`, `color`

## `bancos__equivalencias_mora.json` (3 kB)

- `fuente_definicion`: Arquitecto (Claude), 2026-11-03. Modalidades de definiciones/bcb_ifdata__credito_modalidades.json ↔ series de mora > 90 días del SGS en pb/Banks/bk_sistema_q.p…
- `nota`: Definiciones distintas: el NPL del panel es atraso ≥ 15 días; la mora del SGS es > 90 días. La mora implícita sirve para leer evolución y diferencias entre ban…
- `nota_21114`: 21114 es crédito personal NO consignado: su saldo (SGS 20574) es R$ 400 mil millones contra R$ 792 mil millones del consignado (20576-20578), y la mora pondera…
- `equivalencias`: objeto con 16 claves

## `bcb_ifdata__bancos_balances.json` (30 kB)

- `fuente`: bcb_ifdata
- `datasets`: lista de 1
- `nota`: Universo y crosswalk conservador del panel de balances/resultados bancarios. El crudo sigue siendo IF.data completo por trimestre/escopo/informe; aquí solo se …
- `bancos`: lista de 34 · campos: `cod_inst`, `nombre_corto`, `categoria`, `nota`, `fuente_definicion`, `modelo_negocio`
- `excepciones_stock`: objeto con 1 claves
- `conceptos`: objeto con 24 claves
- `columnas`: objeto con 45 claves
- `nota_modelo_negocio`: modelo_negocio: criterio del analista (Opus), aprobado por Pablo 2026-10-09 para la hoja 8 del PBIP dual (docs/orquestacion/38). No es una clasificación del BC…

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

## `contrato_gold.json` (6 kB)

- `descripcion`: Contrato de la capa gold (datos/gold/bk_*.parquet): columnas mínimas y clave única de cada tabla. Lo lee herramientas/verificar_gold.py; una tabla bk_* que no …
- `tablas`: objeto con 29 claves

## `cvm__dfp_bancos.json` (8 kB)

- `fuente`: cvm
- `datasets`: lista de 1
- `nota`: DFP (Demonstrações Financeiras Padronizadas) de la CVM, ejercicio 2024, filtrado a bancos por `extraer_fuentes.py cvm-dfp`. DERIVADO, no dato crudo de la CVM: …
- `columnas`: objeto con 15 claves

## `metricas_bancos.json` (45 kB)

- `descripcion`: Registro único de las métricas del panel de bancos: nombre, familia, unidad, formato, signo, definición y, en las razones, numerador y denominador. Lo leen pre…
- `convenciones`: objeto con 5 claves
- `orden_familias`: lista de 7
- `fondeo`: lista de 7
- `cosif_2025`: objeto con 23 claves
- `cosif_pre2025`: objeto con 20 claves
- `flujos`: objeto con 12 claves
- `ttm`: lista de 11
- `metricas`: objeto con 86 claves

## `scr_productos.json` (4 kB)

- `_descripcion`: Mapa de submodalidades del SCR.data a productos. Se aplica en orden: la primera regla que calza gana; lo que no calza va a «Otros». Comparación sin mayúsculas …
- `_actualizado`: 2026-11-06
- `productos`: lista de 7 · campos: `producto`, `slug`, `submodalidade`
- `otros`: objeto con 2 claves
- `tramos_pf`: objeto con 9 claves
- `hasta_3sm`: lista de 3
- `instituciones`: objeto con 8 claves
- `sectores_cnae`: objeto con 22 claves

## `validacion_bancos.json` (4 kB)


