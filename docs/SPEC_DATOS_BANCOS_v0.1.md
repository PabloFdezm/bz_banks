# Dashboard Bancos Brasil — Especificación de datos (para Claude Code)

Versión 0.2 · 3-nov-2026 (v0.1: 2-nov-2026)

Este documento define la capa de datos que alimenta el sitio descrito en `ESQUELETO_BANCOS_v0.1.md`. El esqueleto es la fuente de verdad de la narrativa (páginas, tarjetas, qué dato va en cada una). Este documento es la fuente de verdad del **contrato de datos**: tablas gold, columnas, fórmulas, extracciones y verificación. Si una tarjeta del esqueleto no se puede alimentar, se marca FALTA en el inventario y se avisa; no se sustituye por otra serie sin decirlo.

---

## Cambios v0.2 (2026-11-03) — mandan sobre el resto de este archivo

1. **Dónde vive el código:** `preparar_gold_bancos.py` con subcomandos `base`, `rentabilidad`, `sistema`, `cartera`, `exposicion` y `todo` (este último corre todo en orden de dependencias). `sistema`, `cartera` y `exposicion` están en módulos aparte (`preparar_gold_bancos_sistema.py`, `_cartera.py`, `_exposicion.py`) que el principal importa. `cartera` reutiliza las funciones de lectura de `preparar_credito_paginas_powerbi.py`; no lo modifica.
2. **Unidades:** todo en fracción (0,05 = 5 %), columna `unidad` (`fraccion` | `pp`). Columnas de variación en pp llevan sufijo `_pp` salvo `d_cuota_aa` (pp, por contrato del verificador).
3. **`bk_sistema_*` (§3.9), nombres finales:** `dirigido_rural_real_aa`, `dirigido_imob_real_aa`, `dirigido_bndes_real_aa`, `credito_mpme_real_aa`, `credito_grande_real_aa`, `mora90_mpme`, `mora90_grande`, `impulso_credito_pp`, `bis_hiato_credito_pib_pp`. Toda la mora sale del SGS (no de `hogares_modalidades`). Tarjeta = 21129 (total); 21127 y 21128 son detalle. **21114 = personal no consignado.**
4. **§4.3 reemplazado** por `definiciones/bancos__equivalencias_mora.json` (calidad: exacta, proxy o sin_dato).
5. **`bk_exposicion` (§3.6):** columnas `cobertura`, `mora_implicita`, `npl_observado`, `brecha_pp`, `efecto_mix_pp`, `efecto_mora_pp`, `d_mora_implicita_aa_pp`, `quiebre_2025`; vacío si cobertura < 0,5.
6. **`bk_roe_arbol` (§3.7):** 10 líneas + roa, apalancamiento y roe (orden 11–13): se suman `transacciones_pago` (dato desde 202512) y `no_operacional` (sin dato desde 202503 por la renumeración COSIF; pendiente ubicar la cuenta nueva). `despesas_tributarias_ttm` se calcula de 4 trimestres.
7. **`bk_sensibilidad` (§3.8):** NIM trimestral anualizado ~ CDI trimestral; Newey-West implementado a mano (sin statsmodels); n < 16 → beta, IC y R² nulos, `n_trimestres` con valor.
8. **`bk_grupo` (§3.4):** las cuotas `share_*` son suma de los bancos del grupo; el verificador las exceptúa de la regla de rango y exige que sumen 1 por óptica.
9. **`bk_metrica`:** el signo solo aplica a los ratios del esqueleto §0.8; los montos de resultado son `neutro` (vienen en negativo).
10. **`bk_cartera_totales`:** tabla auxiliar del verificador (no se exporta al sitio).
11. **`bk_manifiesto`:** columnas `tabla`, `universo`, `ultimo_corte`, `producido_por`; lo regenera `base` registrando todas las `bk_*` existentes.
12. **IF.Data (informes 5, 7, 9, 10, 12, 14):** Olinda caída; el portal REST los tiene hasta 202412 como `trel<q>_<ID>.json` con IDs inestables. Ver doc 60.

## 1. Reglas de trabajo

1. **Ajustarse al repo.** Leer `CLAUDE.md` antes de escribir código. Código, comentarios y docstrings en castellano; docstrings de módulo que explican *por qué* existe cada pieza; `import certificados` primero en todo script que salga a la red; todo lo que se baja o se produce pasa por `almacen.py` (crudo / derivado con manifiesto). No crear una estructura paralela.
2. **Reutilizar, no copiar.** El núcleo por banco ya existe: `preparar_bancos_powerbi.py` → `pb/Banks/bank_*.parquet` → `preparar_metricas_bancos.py` → `exportaciones/bancos/metricas_bancos.parquet`. Las tablas de crédito por grupo ya existen: `preparar_credito_paginas_powerbi.py` → `pb/cre_*.parquet`. Las tablas macro ya existen en `pb/` (`fh_deuda`, `hsf_mensual`, `hogares_modalidades`, `tasa_real_exante`, `trayectoria_selic_focus`, `cpib_componentes`, `hcs_ahorro`, `tasas_pnad`, `ingreso_pnad`). Las tablas gold de bancos **leen** de ahí; no rehacen esos cálculos.
3. **Python calcula, el navegador dibuja.** Ninguna fórmula financiera vive en el sitio ni en Power BI. Si una columna no está en gold, no existe para el dashboard.
4. **Lo desconocido va como `null`, nunca inventado.** Cada métrica tiene definición y fuente en `bk_metrica`; sin fila en `bk_metrica`, no se exporta.
5. **Reglas que ya aplica el panel y no se tocan** (`docs/descubrimientos.md` §35): crédito = e+f+g+h (era nueva) / d+e+f (era vieja); TTM = 4 trimestres consecutivos, NaN si falta uno; ROE/ROA con promedio t−4 y t; rotular «conglomerado prudencial (COSIF)».
6. **Reglas de `cre_*` que no se tocan** (docstring de `preparar_credito_paginas_powerbi.py`): cartera activa en Brasil de los informes 11 y 13; NPL por modalidad = atraso ≥ 15 días; E–H hasta 2024 (informe 8, financeiro) y activos problemáticos desde 2025 (informe 16, prudencial); 2024-T4 vacío en carteras por modalidad; variaciones de grupo con los mismos bancos en los dos lados.

---

## 2. Dónde vive cada cosa

```
definiciones/
  bcb_ifdata__bancos_balances.json   ← ya existe: 34 bancos, modelo_negocio, notas. Fuente de verdad del panel
  bancos__dashboard.json             ← NUEVO: cotizados, ticker, slug, color fijo, ficha completa sí/no (§4.1)
manual/
  minimos_regulatorios.csv           ← NUEVO: mínimos de Basilea y colchones por fecha (fuente: resoluciones CMN/BCB)
  ref_graficos/<aaaamm>.xlsx         ← planilla de datos del REF, si el BCB la publica (§5.6)
pb/Banks/
  bank_*.parquet                     ← ya existen
  bk_*.parquet                       ← NUEVO: capa gold de este proyecto (§3)
preparar_gold_bancos.py              ← NUEVO: construye bk_* desde bank_*, metricas, cre_*, tablas macro y fuentes nuevas
exportar_web_bancos.py               ← NUEVO: bk_* → sitio_bancos/site/data/*.json + _manifiesto.json
bancos_web/pipeline/verificar.py     ← se extiende (§6)
```

`preparar_gold_bancos.py` tiene un subcomando por tabla (`python -X utf8 preparar_gold_bancos.py cartera`, `… todo`) y escribe con `guardar_derivado(..., desde=[...], como=...)`.

---

## 3. Contrato de salida (gold)

Todas las fechas son fin de período (`date`). Períodos trimestrales también como texto `AAAAMM` (`periodo`) y etiqueta `2T26` (`trimestre`), igual que `cre_*`. Unidad del modelo: **0,05 = 5 %**; las columnas en puntos porcentuales llevan sufijo `_pp`; montos en R$ unidades (como entrega IF.Data) salvo sufijo `_mm` (millones).

### 3.1 `bk_banco` (dimensión, 34 filas)

| Columna | Tipo | Origen |
|---|---|---|
| cod_inst | str | `bank_instituciones` |
| slug | str | `bancos__dashboard.json` (`itau`, `bradesco`, `bb`…) |
| nombre_corto | str | `bank_instituciones` |
| institucion_bcb | str | `bank_instituciones.institucion_bcb_ultima` |
| modelo | str | `bcb_ifdata__bancos_balances.json` → `modelo_negocio` |
| segmento_reg | str | `bank_instituciones.sr` (S1–S4; vacío = «Sin segmento») |
| propiedad | str | `bank_instituciones.tc` → 1 Público, 2 Privado nacional, 3 Privado extranjero |
| fintech | str | Digitales o Pagos → Fintech; resto Tradicional (misma regla que `cre_*`) |
| segmento_ref | str | Aproximación a la segmentación del REF: Públicos si propiedad = 1; Digitales si modelo ∈ {Digitales, Pagos}; S1 privados si segmento_reg = S1; Demás en el resto. Las cooperativas no están en el panel |
| cotizado | bool | `bancos__dashboard.json` |
| ticker | str | idem (validar) |
| ficha | str | `completa` / `panel` |
| color | str | idem; solo para el banco activo y los Grandes (los demás van en acero claro) |
| nota | str | `bcb_ifdata__bancos_balances.json` (por ejemplo «Incluye Banco Pan…») |
| primer_periodo, ultimo_periodo | str | `bank_instituciones` |

### 3.2 `bk_metrica` (dimensión)

| Columna | Descripción |
|---|---|
| metrica | Clave, igual a la de `metricas_bancos` cuando existe |
| nombre, nombre_corto | Etiquetas |
| familia | tamaño / crédito / calidad / fondeo / rentabilidad / capital / conducta |
| unidad | `ratio` / `brl` / `pp` / `indice` |
| formato | `pct1` / `pct0` / `brl_mm` / `pp1` / `x1` |
| signo | `mejora_sube` / `mejora_baja` / `neutro` (§0.8 del esqueleto) |
| universo | `panel` / `sistema` / `scr` / `publicado` / `ref` |
| fuente | Fuente pública (BCB IF.Data, BCB SGS, …) |
| definicion | Fórmula en una línea, en castellano |
| en_comparador, en_ficha | bool: si va al B9 y a la tira de percentiles de B8 |
| orden | Orden en tablas |

### 3.3 `bk_panel` (hecho: banco × trimestre × métrica)

Base: `metricas_bancos.parquet` (formato largo) **más** las métricas nuevas de §4.2. Columnas:

| Columna | Descripción |
|---|---|
| cod_inst, periodo, fecha, trimestre | Claves |
| metrica, valor | Valor |
| valor_t1, valor_t4 | Valor un trimestre y cuatro trimestres antes |
| d_tt, d_aa | Diferencia (si `unidad` = ratio, en pp) o variación % (si es monto) contra t−1 y t−4 |
| p10_grupo, p50_grupo, p90_grupo | Percentiles del `modelo` del banco en ese trimestre (solo bancos con dato; null si n < 3) |
| pct_grupo, pct_panel | Percentil del banco dentro de su grupo y del panel (0–1) |
| rank_panel, rank_panel_t4 | Puesto en el panel hoy y hace 4T (para «ranking con movimiento») |

### 3.4 `bk_grupo` (hecho: óptica × grupo × trimestre × métrica)

Agregados con **los mismos bancos en t y en t−4** (como `cre_panorama`). Para montos: suma. Para ratios: cociente de sumas (ROE grupo = Σ lucro TTM / Σ PL medio), no promedio de ratios. Además, la mediana y p25/p75 de los bancos del grupo.

| Columna | Descripción |
|---|---|
| optica, grupo, periodo, fecha, trimestre, metrica | Claves (óptica y grupo con los mismos textos que `cre_institucion`) |
| valor | Agregado (suma o cociente de sumas) |
| mediana, p25, p75, n_bancos | Distribución dentro del grupo |
| valor_aa | Variación a/a con muestra constante |

Métricas exclusivas de `bk_grupo`: `hhi_credito`, `hhi_depositos`, `hhi_ativo` (Σ cuota² × 10 000, sobre el panel), `top5_credito`, `top5_depositos` (Σ de las 5 mayores cuotas).

### 3.5 `bk_cartera` (hecho: banco × trimestre × tipo × modalidad)

Es la tabla que `preparar_credito_paginas_powerbi.py` ya arma internamente (saldo y vencido ≥ 15 días por banco × modalidad × trimestre, función que lee los informes 11 y 13) antes de agregarla por grupo. Hay que **exponerla por banco**, sin rehacer el parseo: refactorizar esa función para que `preparar_gold_bancos.py` la importe.

| Columna | Descripción |
|---|---|
| cod_inst, periodo, fecha, trimestre | Claves |
| tipo | `PF` / `PJ` |
| modalidad | Las 16 de `definiciones/bcb_ifdata__credito_modalidades.json` (etiquetas como en `cre_panorama.serie`) |
| saldo, vencido15 | R$ |
| npl15 | vencido15 / saldo |
| peso_banco | saldo / saldo total del banco |
| cuota_modalidad | saldo / Σ panel en esa modalidad |
| d_cuota_aa | Δ cuota contra t−4, en pp, con muestra constante |

2024-T4 queda vacío (regla 6). Los bancos con cambio de cobertura en 2025 llevan `quiebre_2025 = true` y quedan fuera de variaciones que cruzan 2025-T1.

### 3.6 `bk_exposicion` (hecho: banco × trimestre)

| Columna | Fórmula |
|---|---|
| mora_implicita | Σ_m peso_banco(m) × mora_sistema(m), con mora_sistema = mora > 90 días del SGS de la modalidad equivalente (promedio del trimestre). Tabla de equivalencias modalidad IF.Data ↔ serie SGS en §4.3 |
| npl_observado | npl15 total del banco (`bk_cartera`) |
| brecha_pp | npl_observado − mora_implicita, en pp. **Ojo:** definiciones distintas (≥ 15 días vs. > 90 días); la brecha se lee en su evolución, no en nivel. Se rotula así en la tarjeta |
| d_mora_implicita_aa | Δ de mora_implicita en 4T, separada en efecto mix y efecto mora (Σ Δpeso × mora_t−4 y Σ peso_t × Δmora) |

### 3.7 `bk_roe_arbol` (hecho: banco o grupo × trimestre × línea)

Todo en TTM y en % del **activo promedio** (t y t−4), desde `bank_resultados` des-acumulado (`metricas_bancos` ya tiene las TTM de cada línea):

| Línea (orden) | Fórmula |
|---|---|
| 1 margen_antes_provisiones | (resultado_intermediacao_financeira_ttm − provisoes_credito_ttm) / ativo_medio. Las provisiones vienen restadas dentro del resultado de intermediación (la misma regla del NIM de `cre_*`) |
| 2 provisiones | provisoes_credito_ttm / ativo_medio (negativo) |
| 3 tarifas_servicios | (rendas_tarifas_ttm + rendas_servicos_ttm) / ativo_medio |
| 4 transacciones_pago | resultado_transacoes_pagamento_ttm / ativo_medio (era 2025; null antes) |
| 5 personal | despesas_pessoal_ttm / ativo_medio |
| 6 administrativos | despesas_administrativas_ttm / ativo_medio |
| 7 tributarios | despesas_tributarias_ttm / ativo_medio (agregar la TTM si no está) |
| 8 otros | antes_tributacao_ttm / ativo_medio − Σ(1..7). Es el residuo que cierra; si supera ± 1 pp del activo en un banco grande, revisar |
| 9 impuesto_participaciones | (lucro_liquido_ttm − antes_tributacao_ttm) / ativo_medio |
| = roa | lucro_liquido_ttm / ativo_medio (debe igualar `roa_ttm`) |
| apalancamiento | ativo_medio / pl_medio |
| = roe | roa × apalancamiento (debe igualar `roe_ttm` ± 0,1 pp) |

Para grupos: las mismas líneas con sumas (Σ numerador / Σ activo medio) y la mediana del grupo por línea. Columnas: `entidad` (cod_inst u `optica|grupo`), `periodo`, `linea`, `orden`, `valor`, `mediana_grupo`.

**Verificación obligatoria:** las identidades «= roa» y «= roe» cierran por banco y trimestre; si no, la fila no se exporta y el verificador falla.

Prueba hecha el 2-nov-2026 sobre 2T26 con `metricas_bancos`: ROA y ROE cierran exacto. Dos advertencias para la tarjeta:
- En **Pagos** (Stone, PagSeguro, Cielo, CloudWalk) el margen antes de provisiones sale negativo (−5 % del activo en Stone y PagSeguro), porque el ingreso del negocio está en `resultado_transacoes_pagamento` y en otras líneas, no en intermediación. El árbol es comparable dentro del grupo, pero no contra bancos. Con banco activo de Pagos, la comparación por defecto es contra su grupo, nunca contra el panel.
- BRB y Neon no tienen TTM completas en 2T26: su árbol queda null y la tarjeta lo dice.
- `despesas_tributarias` solo existe trimestral en `metricas_bancos`: agregar su TTM. Hoy cae en «otros».

### 3.8 `bk_sensibilidad` (hecho: banco)

| Columna | Fórmula |
|---|---|
| beta_nim_cdi | Pendiente MCO de NIM trimestral (anualizado) contra CDI medio del trimestre, 2016-T1 al último, sin 2024-T4 ni los trimestres que cruzan un cambio de perímetro del banco |
| ic_inf, ic_sup | Intervalo de 90 % (errores robustos HAC, 4 rezagos) |
| r2, n_trimestres | Calidad del ajuste; si n < 16, todo null |

El CDI sale de la misma fuente que `cre_contexto` (CDI y CDI media 4T).

### 3.9 `bk_sistema_m` y `bk_sistema_q` (hecho: serie × fecha)

Series mensuales del SGS y de las tablas macro de `pb/`, en formato largo `fecha, serie_id, valor`, más su versión trimestral alineada al panel (saldos y tasas: promedio del trimestre para tasas, fin de trimestre para saldos; flujos: suma). Columnas extra: `p10`, `p50`, `p90` (rolling 120 meses) y `es_ultimo`.

| serie_id | Código / origen | Transformación |
|---|---|---|
| `credito_total_real_aa` / `_pf_` / `_pj_` | SGS 20539 / 20541 / 20540 | Deflactar con IPCA, a/a |
| `credito_pib` | SGS 20622 (o `cpib_componentes`) | Nivel |
| `impulso_credito` | SGS 20539 + 4382 | (flujo12_t − flujo12_t−12) / PIB nominal 12m × 100. Ya construido en el macro (nb 00/03): reutilizar |
| `conc_pf_livre_sa` | SGS 24444 | Real, 3m/3m anualizado |
| `mora90_total` / `_pf_livre` / `_pj_livre` | SGS 21082 / 21112 / 21086 | Nivel con bandas |
| `atraso15_90_pf` / `_pj` | SGS 21005 / 21004 | Nivel (validar la unidad de la familia 21003+) |
| `mora90_<modalidad>` | 21116–21119 (consignado privado/público/INSS/total), 21121 (vehículos), 21127 (rotativo), 21128–21129 (parcelado/a la vista), 21149–21151 (inmobiliario), 21114 (personal) | Nivel. Lo mismo que ya usa `hogares_modalidades`: preferir esa tabla si cubre la modalidad |
| `credito_mpme_real_aa` / `_grande_` | SGS 27701 / 27702 | Real a/a |
| `mora90_mpme` / `_grande` | SGS 27703 / 27704 | Nivel |
| `dirigido_rural` / `_imob` / `_bndes` | 20597+20609 / 20600+20612 / 20604+20616 | Real a/a |
| `spread_livre`, `icc` | SGS 20786 / 25351 | Nivel |
| `comprometimento`, `endividamento` | SGS 29034 / 29037 (ya en `fh_deuda`, `hsf_mensual`) | Leer de esas tablas |
| `desocupacion` | `tasas_pnad` (SGS 24369) | Leer |
| `selic_real_exante` | `tasa_real_exante` | Promedio del trimestre |
| `bis_hiato_credito_pib` | crudo `bis/credit_gap` | Trimestral, tal cual |
| `pix_share` | MPV Olinda (meios de pagamento, mensual) | Pix / (Pix + TED + boleto + tarjetas) en valor; **definir en `bk_metrica` antes de publicar** y contrastar con el ~31 % del REF |

Todo código no marcado «ya» en `docs/dashboard/codigos_y_formulas.md` se valida con `bcb_api.py ultimos <código>` antes de usarlo (la API devuelve HTML con 200 si la serie no existe).

### 3.10 `bk_scr` (hecho: segmento × cliente × modalidad × porte × UF × mes)

Desde los ZIP de SCR.data (`datos/crudo/bcb_scr/scrdata/`), agregado con la tasa oficial: **inadimplencia = Σ carteira_inadimplencia / Σ carteira_ativa** (la columna es en R$, no en %). Columnas: `fecha`, `segmento_inst` (Banco, Financeira, Fintech, Cooperativa…), `cliente` (PF/PJ), `modalidad`, `porte`, `uf`, `carteira_ativa`, `vencido_15_90`, `vencido_90`, `inadimplencia_brl`, `ativo_problematico`, `tasa_inad`, `tasa_ap`. Se publican tres cortes agregados (no el cubo entero): por segmento × cliente × mes; por porte (PJ) × mes; por UF × mes.

Ampliación necesaria: hoy hay crudo 2024–2026 y derivados solo PJ. Bajar 2012–2023 y derivar PF. Los ZIP pesan cientos de MB: procesar año por año con lectura por partes (`chunksize`), `sep=';'`, encoding cp1252.

### 3.11 `bk_capital` (hecho: banco × trimestre) — FALTA

Informe **5 «Informações de Capital»** de IF.Data, escopo prudencial, todos los trimestres desde 2014-T1: `ifdata.py colectar` con ese informe. Columnas: `cod_inst`, `periodo`, `pr` (patrimonio de referencia), `nivel1`, `capital_principal`, `rwa_total`, `rwa_credito`, `rwa_mercado`, `rwa_operacional`, `basilea`, `indice_nivel1`, `indice_cp`, `densidad_rwa` (= rwa_total / ativo_total), `requerimiento_cp` (de `manual/minimos_regulatorios.csv`, con los colchones vigentes en la fecha, incluido ACCP = 0 %), `holgura_cp_pp`, `holgura_crecimiento` (esqueleto B7-03-0).

Las cuentas exactas del informe 5 se resuelven contra `ifdata_diccionario.html` (que documenta las 394 cuentas y el cambio de era 2025-03) y se escriben en `definiciones/bcb_ifdata__capital.json`. Los cinco CSV sueltos de `datos/derivado/bcb_ifdata/valores/ifdata_capital_*.csv` sirven para validar el parser.

### 3.12 `bk_apertura` (hecho: banco × trimestre × dimensión × categoría) — FALTA

Informes de IF.Data por banco, prudencial desde 2025 y financeiro antes (misma regla de cadastro que `cre_*`): **7** (indexador), **9** (región geográfica), **10** (cantidad de clientes y operaciones), **12** (PJ por CNAE), **14** (PJ por porte del tomador). Columnas: `cod_inst`, `periodo`, `dimension`, `categoria`, `saldo`, `participacion`. El informe 10 además da el **número de clientes**, denominador de los reclamos por millón.

### 3.13 `bk_publicado` (hecho: banco × trimestre × línea) — FALTA

CVM ITR (trimestral) y DFP (anual) de los cotizados con registro CVM. `extraer_fuentes.py cvm-dfp` ya baja la DFP; agregar el ITR (`itr_cia_aberta_<año>.zip`, misma estructura). Líneas mínimas: activo total, cartera de crédito, provisiones, depósitos, PL, resultado de intermediación, lucro líquido. Columnas: `cod_inst`, `periodo`, `linea`, `valor`, `base` (IFRS consolidado / BR GAAP), `fecha_entrega`, `cd_cvm`. El mapeo de cuentas por banco va en `definiciones/cvm__bancos_lineas.json`. Nubank, Inter, XP, Stone y PagSeguro cotizan en EE.UU. y reportan con 20-F/6-K; verificar caso por caso si la entidad brasileña entrega ITR a la CVM. Si no lo hace, quedan con `ficha = completa` pero `bk_publicado` vacío en la v1, y la tarjeta B8-06-0 lo dice.

### 3.14 `bk_conducta` (hecho: banco × trimestre)

Ranking de reclamos (REST del BCB, trimestral) mapeado a `cod_inst` por CNPJ del conglomerado; `reclamos_por_millon` tal como lo publica el BCB y `clientes` del informe 10. Tarifas (Olinda, function-import por grupo × servicio). Hoy hay un corte (2T26); bajar la historia disponible.

### 3.15 `bk_ref` (hecho: serie × fecha de corte)

Planilla de datos de los gráficos del REF, una por edición (abril y octubre). Si el BCB no la publica, estas tarjetas quedan FALTA. Columnas: `edicion` (`202610`), `grafico` (`1.2.1.15`), `serie`, `fecha`, `valor`, `unidad`. Se carga a mano a `manual/ref_graficos/` y se ingiere como cualquier crudo.

### 3.16 `bk_qcambio` (hecho: tira «Qué se movió»)

Para cada página, los N mayores movimientos del último trimestre, por |z| del cambio t/t respecto de la distribución histórica de cambios t/t de esa métrica y ese banco. Columnas: `pagina`, `orden`, `cod_inst` o `grupo`, `metrica`, `valor`, `d_tt`, `z`, `texto` (plantilla «{banco}: {métrica} {d_tt con signo} t/t, a {valor}»). Solo hechos; sin adjetivos.

### 3.17 `bk_puente` y `bk_manifiesto`

- `bk_puente`: `bancos_web/backend/validacion.json` en tabla (`banco, linea, periodo, gaap, ifdata, dif_pct`), con `dif_pct` calculado (nunca a mano).
- `bk_manifiesto`: una fila por tabla con `filas`, `columnas`, `rango`, `sha256`, `producido_por`, y una fila por universo con su **último corte** (Panel, Sistema, SCR, Publicado, REF). La portada lee de aquí.

---

## 4. Definiciones nuevas

### 4.1 `definiciones/bancos__dashboard.json`

```json
{
  "fuente_definicion": "Pablo, 2026-11-02 (supuesto S4 del esqueleto; a confirmar)",
  "bancos": [
    {"cod_inst": "C0080099", "slug": "itau", "cotizado": true, "ticker": "ITUB4", "ficha": "completa"},
    {"cod_inst": "C0080336", "slug": "btg", "cotizado": true, "ticker": "BPAC11", "ficha": "completa",
     "nota": "Incluye Banco Pan (BPAN4) en el conglomerado prudencial"}
  ]
}
```

Lista inicial de fichas completas: Itaú (ITUB4), Bradesco (BBDC4), Banco do Brasil (BBAS3), Santander (SANB11), BTG Pactual (BPAC11), ABC Brasil (ABCB4), Banrisul (BRSR6), BMG (BMGB4), Nubank (NU), Inter (INTR), XP (XP), Stone (STNE), PagSeguro (PAGS). **Validar tickers** antes de publicar.

### 4.2 Métricas nuevas de `bk_panel`

| metrica | Fórmula |
|---|---|
| credito_depositos | credito_total / depositos |
| pf_share | saldo PF / (PF + PJ), de `bk_cartera` |
| npl15_total | Σ vencido15 / Σ saldo, de `bk_cartera` |
| margem_antes_prov_ttm | línea 1 de `bk_roe_arbol` |
| tarifas_ativo_ttm | línea 3 de `bk_roe_arbol` |
| apalancamiento | ativo_medio_ttm / pl_medio_ttm |
| basilea, indice_cp, holgura_crecimiento | de `bk_capital` cuando exista |
| costo_captacion_ttm | **FALTA**: el DRE de `bank_resultados` no separa el gasto de captación. Revisar en `bank_cuentas` si el informe 4 lo trae en alguna era; si no, queda null |

### 4.3 Equivalencia modalidad IF.Data ↔ mora del Sistema (para `bk_exposicion`)

| Modalidad (`cre_*`) | Serie de mora del Sistema |
|---|---|
| Tarjeta de crédito | rotativo + parcelado (21127, 21128) ponderado por saldo, o `hogares_modalidades` |
| Consignado | 21119 (total) |
| Personal sin consignación | 21114 con el consignado restado por saldos, o `hogares_modalidades` |
| Vehículos | 21121 |
| Hipotecario | 21149–21151 (validar cuál es el total) |
| Rural y agroindustrial | validar en el catálogo (dirigido rural PF) |
| Modalidades PJ | 21086 (PJ libre) para capital de giro, rotativo, comercio exterior, recebibles y otros; 27703/27704 según porte cuando exista `bk_apertura` |

Toda equivalencia dudosa se marca `validar` en `definiciones/bancos__equivalencias_mora.json` y se lista en el inventario.

---

## 5. Orden de extracción y construcción

| # | Tarea | Comando / archivo | Desbloquea |
|---|---|---|---|
| 1 | `bk_banco`, `bk_metrica`, `bk_panel`, `bk_grupo`, `bk_puente`, `bk_manifiesto` desde lo existente | `preparar_gold_bancos.py base` | B0, B2, B6, B8 (parte), B9 |
| 2 | Refactor de `preparar_credito_paginas_powerbi.py` para exponer la tabla por banco → `bk_cartera`, `bk_exposicion` | `preparar_gold_bancos.py cartera` | B2-03, B3-03, B4-03/04, B8-03 |
| 3 | `bk_roe_arbol`, `bk_sensibilidad` | `preparar_gold_bancos.py rentabilidad` | B6, B8-04 |
| 4 | `bk_sistema_m` / `_q`: bajar los códigos SGS que falten | `bcb_api.py datos …` vía almacén; `preparar_gold_bancos.py sistema` | B1, B3-01, B4-01/02 |
| 5 | Informe 5 de IF.Data → `bk_capital` | `ifdata.py colectar` + `preparar_gold_bancos.py capital` | B7, B8-05 |
| 6 | Informes 7, 9, 10, 12, 14 → `bk_apertura` | `ifdata.py colectar` + `preparar_gold_bancos.py aperturas` | B3-04, reclamos por millón |
| 7 | SCR.data 2012–2023 + derivado PF → `bk_scr` | `extraer_fuentes.py scrdata` + `scrdata-agg` ampliado | B2-04, B4-05 |
| 8 | CVM ITR → `bk_publicado` | `extraer_fuentes.py cvm-dfp` ampliado a ITR | B8-06 |
| 9 | Reclamos y tarifas históricos → `bk_conducta` | `extraer_fuentes.py ranking`, `tarifas` | B2-05, B8-07 |
| 10 | Planilla del REF → `bk_ref` | carga manual + `preparar_gold_bancos.py ref` | B1-05, B5-04, B7-03-1 |
| 11 | Exportar a JSON | `exportar_web_bancos.py` | Sitio |

Las tareas 1–3 no bajan nada y alcanzan para la primera maqueta (Ficha) salvo capital y publicado.

---

## 6. Verificación (extiende `bancos_web/pipeline/verificar.py`)

Además de lo que ya comprueba (estructura, períodos, cuotas que suman 1, identidad de crédito, sin `inf`):

1. `bk_roe_arbol`: las identidades ROA y ROE cierran (± 0,1 pp) por banco y trimestre.
2. `bk_grupo`: el grupo «Total panel» coincide con la suma de los bancos; los grupos de cada óptica suman el panel.
3. `bk_cartera`: Σ modalidades por banco contra el total de los informes 11 + 13 (tolerancia `TOLERANCIA_TOTAL` de `cre_*`); 2024-T4 vacío.
4. `bk_panel`: percentiles por grupo solo con n ≥ 3; `pct_grupo` en [0, 1].
5. `bk_sistema_*`: cada `serie_id` existe en el catálogo SGS y no devolvió HTML; último dato no posterior a hoy.
6. `bk_scr`: la tasa recalculada de jun-26 por segmento coincide con la del catálogo de fuentes (Banco 4,42 %, Financeira 12,31 %, Fintech 16,42 %, Cooperativa 5,20 %).
7. Cruces contra el REF (aviso, no error): ROE del panel vs. el del REF ± 1 pp; mora PF del Sistema vs. REF.
8. `bk_manifiesto`: cada universo tiene fecha de corte y ninguna es futura.

Los tests nuevos van en `tests/test_gold_bancos.py`, con el patrón de `tests/test_pipeline_bancos.py`.

---

## 7. Inventario inicial (estado al 2-nov-2026)

| Tabla | Estado | Bloquea |
|---|---|---|
| `bk_banco`, `bk_metrica`, `bk_panel`, `bk_grupo` | DERIVAR (todo el insumo existe) | — |
| `bk_cartera`, `bk_exposicion` | DERIVAR (refactor) | — |
| `bk_roe_arbol`, `bk_sensibilidad` | DERIVAR | — |
| `bk_sistema_m`/`_q` | DERIVAR (la mayoría de los códigos ya bajados; validar el resto) | — |
| `bk_scr` | DERIVAR parcial (PJ 2024–26) / FALTA (PF, historia) | B2-04, B4-05 completas |
| `bk_capital` | FALTA | B7 entera, Basilea en B0/B8/B9 |
| `bk_apertura` | FALTA | B3-04 |
| `bk_publicado` | FALTA | B8-06-0 |
| `bk_conducta` | DERIVAR (un corte) / FALTA (serie) | B8-07 |
| `bk_ref` | FALTA (confirmar que exista la planilla) | B1-05, B5-04, B7-03-1 |
| `bk_qcambio`, `bk_puente`, `bk_manifiesto` | DERIVAR | — |
