# 04 · Modelo de datos (capa gold)

Columnas, tipos, nulos, ejemplos y rangos de **todas** las tablas: `generado/tablas.md`. Catálogo de las 84
métricas: `generado/metricas.md`. Universo de 34 bancos: `generado/bancos.md`.

## Convenciones

- Archivos: `datos/gold/<tabla>.parquet`, escritos con `almacen.escribir_atomico` y registrados con
  `almacen.guardar_derivado` (manifiesto con entradas y comando).
- **Unidades:** tasas y ratios en fracción (0,05 = 5 %). Cambios de tasas en pp solo cuando la columna lo
  indica (`*_pp`, `unidad_cambio = 'pp'`). Saldos IF.Data en R$; saldos SGS en R$ millones; en las tablas
  descriptivas `ultimo` va en R$ mil millones cuando `unidad_ultimo = 'brl_mm'`.
- **Períodos:** `periodo` trimestral como entero AAAAMM (201403…202606) o texto; `fecha` = último día del
  período (`AAAA-MM-DD`); `trimestre` como «2T26».
- **Banco:** `cod_inst` (código del conglomerado prudencial en IF.Data) y `slug` (URL: `?banco=itau`).
- **Grupos («ópticas»):** Modelo de negocio (Grandes, Digitales, Medianos y nicho, Pagos, Desarrollo),
  Segmento regulatorio (S1–S4), Propiedad, Tradicional vs Fintech, Total panel («Todos los grupos»).

## Tablas y quién las usa

| Tabla | Grano | Productor | Lo usan |
|---|---|---|---|
| `bank_hechos`, `bank_cuentas`, `bank_instituciones`, `bank_periodos`, `bank_balances`, `bank_resultados` | banco × trimestre × cuenta (y dimensiones) | `preparar_bancos_powerbi.py` | `preparar_metricas_bancos`, `preparar_credito_paginas`, Power BI |
| `bk_banco` | banco (34) | `preparar_gold_bancos base` | casi todas las tarjetas de banco; `estado.js` arma la lista de bancos desde aquí |
| `bk_metrica` | métrica (84) | `base` | B6-05, B8 (nombres, formato, `signo` que colorea cambios) |
| `bk_panel` | banco × trimestre × métrica: `valor`, rezagos (`valor_t1`, `valor_t4`), cambios (`d_tt`, `d_aa`, unidad en `unidad_d`), percentiles del grupo (`p10/p50/p90_grupo`), posición (`pct_grupo`, `pct_panel`) y ranking (`rank_panel`) | `base` | particiones `metrica/<m>/bk_panel` (B4, B6, franja de B8) y `banco/<slug>/bk_panel` (B8) |
| `bk_grupo` | óptica × grupo × trimestre × métrica, con muestra constante a/a, mediana y p25/p75 | `base` | particiones `optica/<slug>/bk_grupo` (franjas de B4 y B6, B6-01) |
| `bk_puente` | banco × concepto: IF.Data contra lo publicado por el banco | `base` | B8-06-1 |
| `bk_manifiesto` | tabla gold: filas, rango, sha256, último corte | `base` | B8 (cortes), tests |
| `bk_roe_arbol` | entidad (banco o grupo) × trimestre × línea del árbol ROE | `base` (rentabilidad) | B6-02, B8 (`banco/<slug>/`) |
| `bk_sensibilidad` | banco: beta del margen a la Selic | `base` (rentabilidad) | B6-04 |
| `bk_sistema_m`, `bk_sistema_q` | serie de sistema × mes / trimestre (SGS + entradas del macro) | `preparar_gold_bancos sistema` | B4-01, franja de B4 |
| `bk_cartera` | banco × trimestre × tipo × modalidad (saldo, vencido ≥15 d, `quiebre_2025`) | `cartera` | B8 (`banco/<slug>/`), `bk_exposicion`, `bk_qcambio` |
| `bk_cartera_totales` | totales publicados por el BCB | `cartera` | solo el verificador (no se exporta) |
| `bk_cartera_grupo`, `bk_cartera_mix7` | grupo × trimestre × modalidad (mix y NPL) | `cartera` | B8-03 |
| `bk_cre_panorama`, `bk_cre_calidad`, `bk_cre_contexto` | copias de `intermedio/cre_*` (crédito por grupo) | `cartera` | B4-03 |
| `bk_exposicion` | banco × trimestre: mora implícita del mix vs NPL observado, efectos mix y mora | `preparar_gold_bancos_exposicion.py` | B4-04 |
| `bk_qcambio` | banco × métrica en el último trimestre: cambio, z, sentido, rango | `preparar_gold_bancos_qcambio.py` | Portada antigua («qué se movió»); hoy sin tarjeta visible |
| `bk_scr` | mes × corte (segmento/cliente, porte, UF) | `preparar_gold_bancos_scr.py` | páginas ocultas (B1, B2) |
| `bk_portada_credito` | mes × modo (nominal/real) × componente: a/a y contribución en pp | `preparar_gold_bancos_portada.py` | B0-01 |
| `bk_portada_mora` | mes: nivel y cambio a/a en pp | portada | B0-03 |
| `bk_portada_roe` | trimestre: ROE del panel, CDI 4T, ROE − CDI | portada | B0-05 |
| `bk_portada_cuotas` | vista × banco: cuota (10 mayores + Resto), grupo | portada | B0-07 |
| `bk_portada_tablas` | bloque × fila: tabla estándar (ver abajo) | portada | B0-02, B0-04, B0-06 |
| `bk_cred_tablas` | bloque × fila: tabla estándar | `preparar_gold_bancos_pag_credito.py` | B3 (todas las tablas y las barras) |
| `bk_cred_series` | serie × fecha (largo): `conc12_aa`, `stock_aa`, `aa\|<modalidad>`, `aa\|Total`, `cpib_nivel/tendencia/brecha` | pag_credito | B3-01 (vista Líneas), B3-05, B3-07 |

## Contrato de la tabla estándar (`bk_portada_tablas`, `bk_cred_tablas`)

Una fila por indicador; el componente `tabla_estandar` la dibuja sin cálculo.

| Columna | Contenido |
|---|---|
| `bloque` | agrupa las filas de una tabla (`credito_nominal`, `mora`, `roe`, `tipos`, `contrib`, `conc`, `ciclo`) |
| `orden`, `fila`, `grupo` | orden de la fila, texto del indicador, grupo (Personas/Empresas/Total…) |
| `corte` | último período con dato de **esa fila** («sep-26», «3T26») |
| `ultimo` | nivel del último dato |
| `share` | peso en el total (fracción); vacío → «—» |
| `d1`, `d3`, `d12`, `dventana` | m/m, 3m/3m, a/a, 12m/12m (trimestral: t/t, —, a/a, 4T/4T) |
| `unidad_ultimo`, `unidad_cambio` | `brl_mm` (R$ mil millones), `pct` (fracción → %), `pp`, `pct_nivel` (ya en %) |
| `trimestral` | true → cabecera t/t · — · a/a · 4T/4T |

La fila cuyo `fila` es el total del bloque se marca en la página (`destacar`) y va en negrita.

## Exportación al sitio (`exportar_web_bancos.py`)

- Formato: `{"tabla": "...", "columnas": [...], "filas": [[...], ...]}`; NaN → null; fechas como texto.
- `sitio/data/_manifiesto.json`: `generado`, `tablas` (por tabla: filas, columnas, rango, sha256 del parquet,
  bytes), `bancos`, `metricas`, `opticas` (particiones). El sitio decide qué tablas existen leyendo esto.
- Se regenera **entera** la carpeta en cada corrida (borra y escribe). `bk_cartera_totales` no se exporta.
- Particiones: `banco/<slug>/{bk_panel,bk_cartera,bk_roe_arbol}.json`, `metrica/<metrica>/bk_panel.json`,
  `optica/{modelo,segmento,propiedad,fintech,panel}/bk_grupo.json`.
