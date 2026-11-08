# 03 · Pipeline de datos

Detalle exhaustivo de cada script (docstring completo, subcomandos y argumentos): `generado/scripts.md`.

## Fuentes del BCB

| Fuente | Qué trae | Frecuencia y rezago | Acceso | Dónde queda |
|---|---|---|---|---|
| **IF.Data** | Estados financieros por institución: balance (informe 2 activo, 3 pasivo), resultados (4), cartera por modalidad PF (11) y PJ (13), otros | Trimestral (mar/jun/sep/dic), ~60 días de rezago (~90 en diciembre) | API OLinda (OData) `olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata` | `datos/crudo/bcb_ifdata/{valores,cadastro,catalogo}/actual/` — `valores_AAAAMM_<escopo>_r<informe>.parquet` (ver «Crudo en parquet») |
| **SGS** | Series de sistema: saldos y concesiones de crédito por modalidad, mora, tasas, CDI, IPCA, crédito/PIB… | Mensual (algunas diarias o trimestrales), ~1–2 meses | `api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados` | `datos/crudo/bcb_sgs/bancos_sistema/actual/serie_<codigo>.json` (todo el pipeline lee solo este dataset, vía `sgs.py`; los demás datasets de `bcb_sgs/` son copias congeladas del proyecto macro) |
| **SCR.data** | Cartera y morosidad del sistema por segmento, porte, UF | Mensual; ZIP anuales | descarga de ZIP | `datos/crudo/bcb_scr/scrdata/actual/*.zip` |
| BIS | Brecha crédito/PIB (referencia) | Trimestral | — | `datos/crudo/bis/` |

IF.Data tiene **escopos**: 1 prudencial (conglomerado prudencial, el que usa el panel), 2 financiero, 3
individual, 4 cambio. Desde 2025-03 el BCB renumeró las cuentas (frontera COSIF) y movió los informes de
crédito del escopo 2 al 1: la cartera usa el financiero hasta 2024-T4 y el prudencial desde 2025-T1.

## Almacén (`pipeline/almacen.py`)

```
datos/crudo/<fuente>/<dataset>/<version>/     lo que sirvió la fuente; no se edita
datos/derivado/<fuente>/<dataset>/            lo que produce el código, con manifiesto de entradas y comando
datos/intermedio/                             tablas intermedias (métricas por banco, cre_*, entradas del macro)
datos/gold/                                   la capa que exporta el sitio (bk_*) y los bank_* de base
```

`almacen` es dueño de las rutas (`RAIZ`, `GOLD`, `INTERMEDIO`, `DEFINICIONES`, `ruta_cruda`,
`ruta_valores(periodo, escopo, informe)`, `ruta_cadastro(periodo)`), de leer `definiciones/*.json`
(`leer_definicion`) y de escribir: `registrar_crudo`/`guardar_crudo` (crudo con manifiesto),
`escribir_atomico`/`escribir_parquet` (vía temporal + rename, segura con OneDrive) y
`publicar_gold(nombre, df, dataset=..., desde=[...])`, que valida contra
`definiciones/contrato_gold.json`, escribe `datos/gold/<nombre>.parquet` y deja la procedencia en
`datos/derivado/` con el comando que la produjo (`comando_actual()`). `verificar()` / `verificar_todo()` comprueban los sha256.

Módulos compartidos (no se corren solos):

| Módulo | Qué tiene |
|---|---|
| `bancos.py` | universo de bancos (las dos definiciones, comprobadas entre sí), ópticas, propiedad, regla fintech, `membresia()` / `pertenencia()` (la única regla de qué banco va en qué grupo), `con_quiebre_2025()` |
| `periodos.py` | aritmética AAAAMM (`qi`, `previo`, `rango_trimestres`), fin de mes, etiquetas («1T25», «2025 T1», «sep-26»), `QUIEBRE_2025`, `ANOMALOS`, `variacion_valida()` (la regla de qué variación se publica) |
| `registro_metricas.py` | lee `definiciones/metricas_bancos.json`: códigos COSIF, flujos, TTM, y por métrica nombre, familia, unidad, signo, definición y, en las razones, numerador y denominador; de ahí salen el valor por banco, el agregado por grupo y `bk_metrica` |
| `sgs.py` | catálogo `CODIGOS` (nombre → código), único lector/descargador del SGS (`serie`, `bajar`, `refrescar`), `mensual`, `deflactor`, CDI (`cdi_mensual`, `cdi_trimestral`, `cdi_12m`, `menos_cdi`) |
| `ifdata_texto.py` | texto de los CSV de IF.Data sin red: `limpiar`, `nulo`, `normalizar`, `saldo` (el único parser de saldos) |
| `ifdata_credito.py` | cartera por modalidad (informes 11 y 13) y NPL total (8 y 16); frontera 2025 |
| `mora_sistema.py` | mora SGS equivalente a cada modalidad (`bancos__equivalencias_mora.json`) |
| `tabla_estandar.py` | variaciones de la tabla estándar (saldo, tasa, trimestral) y sus columnas obligatorias |
| `scr_zip.py` | descarga, codificación y lectura de los ZIP del SCR.data |
| `red.py` | la única política de reintentos (`reintentar`, `bajar_a_disco`) y el modo sin red (`exigir_red`) |
| `reglas_gold.py` | tolerancias y umbrales de la capa gold, marcas de licencia, `rango`, `div`, `verificar_mix7`: lo comparten preparadores, exportador y verificador |
| `tabla_estandar.py` (además) | `series_largas` y `fecha_fin`: el formato largo serie·fecha·valor de las tablas `*_series` |
| `manifiesto_gold.py` | arma `bk_manifiesto` una vez, al final |

## Crudo en parquet (desde el 4-nov-2026)

OLinda sirve CSV; `ifdata.py` lo baja, lo registra (URL + sha256 del CSV) y lo convierte de inmediato a
parquet con `almacen.csv_a_parquet`: **todas las columnas como texto, sin inferir tipos**, comprobando que el
parquet reproduce el CSV celda por celda; luego borra el CSV. Es una recodificación sin pérdida, así que sigue siendo capa cruda; el manifiesto guarda los
datos del CSV y, en la clave `parquet`, archivo, sha256, bytes y filas. IF.Data pasó de 3,5 GB a 62 MB.

Las lecturas usan `almacen.leer_crudo_tabla(ruta_csv, columnas)` (parquet si existe, si no CSV),
`glob_crudo(carpeta, patron.csv)` y `crudo_con_datos(ruta)`: el código sigue nombrando los crudos por su
nombre `.csv`. `herramientas/convertir_crudo_parquet.py [--borrar]` convierte lo que falte. El SCR sigue en
ZIP (ya comprimido). `diccionario_ifdata.py` (no es parte de la cadena) también lee los volcados en parquet.

## Pasos y orden (`pipeline/actualizar.py`, que llama `actualizar.bat`)

Cada paso es el `main(argv) -> int` de un módulo; si uno devuelve distinto de 0 la corrida se corta y no se
exporta. `--sin-red` no baja nada: un dato que falte hace fallar el paso (variable `BZ_SIN_RED`, `red.exigir_red`); `--desde/--hasta` corren un tramo; `--sin-verificacion` salta pytest.
IF.Data se baja aparte y a mano (`ifdata.py colectar …`, trimestral).

| Paso | Módulo | Lee | Escribe | Red |
|---|---|---|---|---|
| sgs | `sgs.refrescar` | API del SGS | `crudo/bcb_sgs/bancos_sistema` (todas las series de `CODIGOS`) | sí |
| balances | `preparar_bancos_powerbi.py` | crudo IF.Data (inf. 2, 3, 4), `bcb_ifdata__bancos_balances.json` | `gold/bank_*` | no |
| metricas | `preparar_metricas_bancos.py` | `gold/bank_*`, `metricas_bancos.json` | `intermedio/metricas_bancos.parquet` | no |
| credito | `preparar_credito_paginas_powerbi.py` | crudo IF.Data (11, 13, 8, 16), cadastro, SGS 20714 y CDI | `intermedio/cre_*`, `gold/bk_cre_{panorama,calidad,contexto}` | no |
| sistema | `preparar_gold_bancos_sistema.py` | SGS, BIS, Focus, tasa real | `gold/bk_sistema_m/q` | no |
| cartera | `preparar_gold_bancos_cartera.py` | crudo IF.Data (11, 13), `bk_sistema_q` | `gold/bk_cartera*` | no |
| base | `preparar_gold_bancos.py base` | `metricas_bancos`, `bk_cartera`, `bk_sistema_q` | `gold/bk_{banco,metrica,panel,grupo,puente}` | no |
| rentabilidad | `preparar_gold_bancos.py rentabilidad` | `metricas_bancos`, CDI | `gold/bk_roe_arbol`, `bk_sensibilidad` | no |
| exposicion | `preparar_gold_bancos_exposicion.py` | `bk_cartera`, `bk_sistema_q` | `gold/bk_exposicion` | no |
| qcambio | `preparar_gold_bancos_qcambio.py` | `bk_panel`, `bk_metrica`, `bk_banco`, `bk_cartera` | `gold/bk_qcambio` | no |
| portada | `preparar_gold_bancos_portada.py` | SGS, `bk_sistema_m`, `bk_grupo`, `bk_panel`, `bank_balances`, `bk_cartera_totales`, inf. 3 | `gold/bk_portada_*` | no |
| pag_credito | `preparar_gold_bancos_pag_credito.py` | SGS (modalidades, concesiones, crédito/PIB) | `gold/bk_cred_*` | no |
| scr_productos | `preparar_gold_bancos_scr_productos.py --descargar` | ZIP del SCR.data (baja el del año) | `intermedio/scr_productos/`, `gold/bk_scr_{tablas,series}` | sí |
| scr | `preparar_gold_bancos_scr.py` | ZIP del SCR.data (caché por ZIP en `intermedio/scr/`) | `gold/bk_scr` | solo si falta un año |
| manifiesto | `manifiesto_gold.py` | `gold/bk_*`, `datos/derivado/` | `gold/bk_manifiesto` | no |
| verificacion | `pytest -q` y `verificar_gold.py --gold` | todo | — | no |
| exportar | `exportar_web_bancos.py` | `gold/bk_*` | `sitio/data/**.json` + `_manifiesto.json` | no |

`sistema`, `cartera` y `scr` verifican antes de publicar: si su verificación falla, no escriben nada.

## Convenciones de cálculo

- **TTM:** suma de los últimos cuatro trimestres de flujos. IF.Data publica resultados **acumulados** con
  reseteo en julio (Lei 4.595): `preparar_bancos_powerbi.py` los des-acumula antes de nada.
- **ROE** = lucro de 4 trimestres / patrimonio promedio (t y t−4). ROA análogo con activo medio.
  El promedio exige los dos extremos (t y t−4); si falta uno, queda vacío.
- **Tres NIM distintos, a propósito:** `margem_intermediacao_ttm` (bk_panel: RIF + transacciones de pago, 12
  meses, neto de provisiones, / activo medio); el NIM de la página Crédito (`cre_calidad`: RIF − provisiones,
  4 trimestres, antes de provisiones, / activo medio t y t−4); y el de `bk_sensibilidad` (RIF − provisiones del
  trimestre × 4 / activo medio t−1 y t).
- **CDI:** promedio mensual de la serie diaria (`sgs.cdi_mensual`); trimestral = media de sus 3 meses; «12
  meses» = media de los 12 meses que terminan en el trimestre. ROE − CDI = `sgs.menos_cdi`.
- **Variaciones publicables:** `periodos.variacion_valida`. Ningún extremo puede ser un trimestre anómalo
  (`ANOMALOS`, hoy 2024-T4). Bancos con quiebre 2025: regla «cruza» en bk_panel.valor_tt, bk_grupo y
  bk_cartera; regla «toca» en bk_qcambio (ver pendientes de metodología).
- **Variaciones de la tabla estándar** (`d1, d3, d12, dventana`):
  - saldos: m/m y a/a punta contra punta; 3m/3m y 12m/12m = promedio de la ventana contra el de la
    ventana anterior; en concesiones (flujos) 12m/12m compara sumas de doce meses;
  - tasas: diferencias en pp, con el mismo esquema de ventanas;
  - trimestrales: d1 = t/t, d3 vacío, d12 = a/a, dventana = 4T/4T.
- **Contribución al crecimiento (pp):** (componente_t − componente_t−k) / total_t−k × 100. Suma el
  crecimiento del total; el script lo comprueba (`assert`). «Otros» = total − modalidades listadas.
- **Real:** saldo deflactado por IPCA encadenado (SGS 433), base último mes.
- **Mora:** panel IF.Data = atraso ≥ 15 días; SGS = > 90 días. No se comparan en nivel.
- **Mora implícita** (`bk_exposicion`): la mora que tendría el banco si cada modalidad se comportara como
  el sistema; equivalencias en `definiciones/bancos__equivalencias_mora.json`; vacía si cobertura < 50 %.
- **Crédito/PIB con HP unilateral:** promedio trimestral de SGS 20622, filtro HP con λ = 400.000 (BIS)
  re-estimado en cada t con datos hasta t; requiere ≥ 20 trimestres. La brecha difiere de la del BIS
  porque el BIS usa crédito total al sector privado.
- **Cuotas:** suma del banco / suma del universo del informe (activos, crédito total/PF/PJ, depósitos
  totales/vista/ahorro/plazo); diez mayores + «Resto».
- **«Qué se movió» (`bk_qcambio`):** z = cambio trimestral / desvío de los cambios de esa métrica en el panel
  (últimos 20 trimestres); los cambios que tocan 2024-T4 o el quiebre 2025 del banco quedan vacíos.

## Series SGS

El catálogo es `CODIGOS` en `pipeline/sgs.py` (nombre → código): saldos y concesiones de crédito por modalidad,
mora > 90 días y atrasos, spread, ICC, CDI, IPCA, crédito/PIB, PIB 12 meses, endeudamiento, comprometimiento y
desocupación. Pendiente: validar contra el catálogo del SGS los nombres de las series de modalidades y
concesiones (se identificaron cuadrando montos).

## Entradas congeladas (vienen del dashboard macro)

`preparar_gold_bancos_sistema.py` lee dos tablas que construyó el proyecto macro y que se copiaron a
`datos/intermedio/` el 4-nov-2026: `tasa_real_exante` y `expectativas_focus`. **Aquí no se actualizan.**
Endeudamiento, comprometimiento y desocupación se leen del SGS (29037, 29034, 24369) desde el 6-nov.
`fh_deuda` y `tasas_pnad` siguen en `datos/intermedio/` pero ya nadie las lee.

## Red corporativa

En la red de la oficina el HTTPS pasa por un proxy que re-firma certificados. `pipeline/certificados.py`
(se importa al inicio de los scripts que bajan) usa `truststore` para que Python confíe en el almacén de
Windows. Si todos los hosts fallan a la vez con `CERTIFICATE_VERIFY_FAILED`, es eso.
