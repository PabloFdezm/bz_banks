# 03 · Pipeline de datos

Detalle exhaustivo de cada script (docstring completo, subcomandos y argumentos): `generado/scripts.md`.

## Fuentes del BCB

| Fuente | Qué trae | Frecuencia y rezago | Acceso | Dónde queda |
|---|---|---|---|---|
| **IF.Data** | Estados financieros por institución: balance (informe 2 activo, 3 pasivo), resultados (4), cartera por modalidad PF (11) y PJ (13), otros | Trimestral (mar/jun/sep/dic), ~60 días de rezago (~90 en diciembre) | API OLinda (OData) `olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata` | `datos/crudo/bcb_ifdata/{valores,cadastro,catalogo}/actual/` — `valores_AAAAMM_<escopo>_r<informe>.parquet` (ver «Crudo en parquet») |
| **SGS** | Series de sistema: saldos y concesiones de crédito por modalidad, mora, tasas, CDI, IPCA, crédito/PIB… | Mensual (algunas diarias o trimestrales), ~1–2 meses | `api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados` | `datos/crudo/bcb_sgs/<dataset>/actual/serie_<codigo>.json` |
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

Funciones que usan los scripts: `ruta_cruda(fuente, dataset)`, `registrar_crudo(...)` (guarda con
manifiesto), `guardar_derivado(fuente, dataset, nombre, bytes, desde=[...], como=COMANDO, nota=...)`,
`escribir_atomico(destino, bytes)` (escritura vía temporal + rename, segura con OneDrive), `verificar()`.

## Crudo en parquet (desde el 4-nov-2026)

OLinda sirve CSV; `ifdata.py` lo baja, lo registra (URL + sha256 del CSV) y lo convierte de inmediato a
parquet con `almacen.csv_a_parquet`: **todas las columnas como texto, sin inferir tipos**, comprobando que el
parquet reproduce el CSV celda por celda; luego borra el CSV (`GUARDAR_PARQUET`, `BORRAR_CSV` en
`ifdata.py`). Es una recodificación sin pérdida, así que sigue siendo capa cruda; el manifiesto guarda los
datos del CSV y, en la clave `parquet`, archivo, sha256, bytes y filas. IF.Data pasó de 3,5 GB a 62 MB.

Las lecturas usan `almacen.leer_crudo_tabla(ruta_csv, columnas)` (parquet si existe, si no CSV),
`glob_crudo(carpeta, patron.csv)` y `crudo_con_datos(ruta)`: el código sigue nombrando los crudos por su
nombre `.csv`. `herramientas/convertir_crudo_parquet.py [--borrar]` convierte lo que falte. El SCR sigue en
ZIP (ya comprimido; solo se lee para rearmar la historia de `bk_scr`). `diccionario_ifdata.py` todavía lee
los CSV de volcado completo (no es parte de la cadena).

## Scripts y orden (lo que corre `actualizar.bat`)

| # | Script | Lee | Escribe | Red |
|---|---|---|---|---|
| — | `ifdata.py colectar …` | API OLinda | `crudo/bcb_ifdata` | sí (manual, trimestral) |
| 1 | `preparar_bancos_powerbi.py` | crudo IF.Data (inf. 2, 3, 4), `definiciones/bcb_ifdata__bancos_balances.json` | `gold/bank_{hechos,cuentas,instituciones,periodos,balances,resultados}` | no |
| 2 | `preparar_metricas_bancos.py` | `gold/bank_*` | `intermedio/metricas_bancos.parquet`, `panel_bancos_wide.csv` | no |
| 3 | `preparar_credito_paginas_powerbi.py --descargar` | crudo IF.Data (inf. 11, 13), cadastro, SGS 20714 y 4389, `definiciones/bcb_ifdata__credito_modalidades.json` | `intermedio/cre_*.parquet` | sí (2 series SGS) |
| 4 | `preparar_gold_bancos.py todo` | todo lo anterior + `definiciones/*` | `gold/bk_sistema_m/q`, `bk_cartera*`, `bk_cre_*`, `bk_banco`, `bk_metrica`, `bk_panel`, `bk_grupo`, `bk_puente`, `bk_roe_arbol`, `bk_sensibilidad`, `bk_exposicion`, `bk_manifiesto` | sí si faltan series SGS |
| 5 | `preparar_gold_bancos_qcambio.py` | `bk_panel`, `bk_metrica`, `bk_cartera` | `gold/bk_qcambio` | no |
| 6 | `preparar_gold_bancos_portada.py` | SGS, IF.Data (inf. 3, 11, 13 del último trimestre), `bk_panel` | `gold/bk_portada_{credito,mora,roe,tablas,cuotas}` | sí si faltan series |
| 7 | `preparar_gold_bancos_pag_credito.py` | SGS (modalidades, concesiones, crédito/PIB) | `gold/bk_cred_{tablas,series}` | sí si faltan series |
| 8 | `preparar_gold_bancos.py base` + `exportar_web_bancos.py` | `gold/bk_*` | `bk_manifiesto` al día; `sitio/data/**.json` + `_manifiesto.json` | no |

`preparar_gold_bancos.py todo` corre internamente: sistema → cartera → base → rentabilidad → exposición → base.
`preparar_gold_bancos_scr.py` (bk_scr) solo se corre cuando hay que rearmar la historia 2012–2023 del SCR;
lee los ZIP por partes. `preparar_gold_bancos.py` tiene subcomandos sueltos: `base`, `rentabilidad`,
`sistema [--descargar]`, `cartera`, `exposicion`, `todo`.

**Importante:** el paso 8 rehace `bk_manifiesto` al final. Si se corre un script de gold suelto, hay que
volver a correr `preparar_gold_bancos.py base` antes de exportar, o `tests/test_gold_bancos.py` falla por
sha256 que no coincide.

## Convenciones de cálculo

- **TTM:** suma de los últimos cuatro trimestres de flujos. IF.Data publica resultados **acumulados** con
  reseteo en julio (Lei 4.595): `preparar_bancos_powerbi.py` los des-acumula antes de nada.
- **ROE** = lucro de 4 trimestres / patrimonio promedio (t y t−4). ROA análogo con activo medio.
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

## Series SGS principales

| Uso | Códigos |
|---|---|
| Saldo de crédito: total, libre, direccionado, PF, PJ | 20539, 20542, 20593, 20541, 20540 |
| Modalidades (página Crédito) | tarjeta 20590; consignado 20576+20577+20578; personal no consignado 20574; vehículos 20581; inmobiliario PF 20612; rural PF 20609; empresas libre 20543; BNDES PJ 20604; rural PJ 20597; inmobiliario PJ 20600 |
| Concesiones: libres, PF, PJ | 20631, 20633, 20632 |
| Crédito/PIB | 20622 |
| Mora > 90 días: total, libre, direccionado, PF, PJ, PF libre, PJ libre | 21082, 21085, 21132, 21084, 21083, 21112, 21086 |
| CDI · IPCA | 4389 · 433 |
| Endeudamiento y compromiso de renta de hogares | 29037, 29034 (hoy vía `intermedio/fh_deuda`) |

Pendiente: validar contra el catálogo del SGS los nombres de las series de modalidades y concesiones
(se identificaron cuadrando montos).

## Entradas congeladas (vienen del dashboard macro)

`preparar_gold_bancos_sistema.py` lee cuatro tablas que construye el proyecto macro y que se copiaron a
`datos/intermedio/` el 4-nov-2026: `fh_deuda` (SGS 29034/29037), `tasa_real_exante`, `tasas_pnad`
(desocupación PNAD, t6381 v4099) y `expectativas_focus`. **Aquí no se actualizan.** Las tres primeras se
pueden leer directo del SGS; la desocupación requiere IBGE/SIDRA.

## Red corporativa

En la red de la oficina el HTTPS pasa por un proxy que re-firma certificados. `pipeline/certificados.py`
(se importa al inicio de los scripts que bajan) usa `truststore` para que Python confíe en el almacén de
Windows. Si todos los hosts fallan a la vez con `CERTIFICATE_VERIFY_FAILED`, es eso.
