# Tablas de datos (gold e intermedio)

> Generado por `herramientas/generar_spec.py`. No editar a mano: se sobrescribe.

Unidades: las tasas y ratios van en **fracción** (0,05 = 5 %); los cambios de tasas, en pp cuando la columna lo dice; los saldos en R$ (IF.Data) o R$ millones (SGS) salvo que la columna diga otra cosa. Ver `spec/04_modelo_de_datos.md`.

## Gold (`datos/gold/`) — lo que exporta el sitio y lee Power BI

Carpeta `datos/gold/`.

### `bank_balances`

1,490 filas · 12 columnas · periodo: 201403 → 202606 · 0.11 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `cod_inst` | str | 0 | C0080312 | 34 |
| `nombre_corto` | str | 0 | ABC Brasil | 34 |
| `categoria` | str | 0 | nucleo | 4 |
| `ativo_total` | float64 | 1 | 18401052706.81 | 1475 |
| `operacoes_credito` | float64 | 1 | 9210361138.02 | 1410 |
| `operacoes_credito_liquidas` | float64 | 1 | 9040130200.73 | 1410 |
| `depositos` | float64 | 1 | 4648679071.45 | 1440 |
| `captacoes` | float64 | 1 | 13493599379.67 | 1464 |
| `passivo_total` | float64 | 1 | 18401052706.81 | 1475 |
| `patrimonio_liquido` | float64 | 1 | 1986349875.68 | 1475 |

### `bank_cuentas`

171 filas · 18 columnas · — · 0.04 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cuenta_id` | str | 0 | r2_dcf3bde23bd8 | 171 |
| `num_informe` | int64 | 0 | 2 | 3 |
| `informe` | str | 0 | Ativo | 3 |
| `era` | str | 0 | cosif_2025 | 2 |
| `cod_cuenta` | str | 0 | 140204 | 165 |
| `cuenta` | str | 0 | Ajuste a Valor Justo (e4) | 153 |
| `cuenta_base` | str | 0 | ajuste a valor justo | 125 |
| `grupo` | str | 0 | Operações de Crédito | 22 |
| `grupo_norm` | str | 0 | operacoes de credito | 22 |
| `composicion` | str | 0 | [1611001806] + [1612001805] + [1613001804] + [1630501806] + [1631501805] + [1632501804] +… | 167 |
| `composicion_primera` | str | 0 | [1611001806] + [1612001805] + [1613001804] + [1630501806] + [1631501805] + [1632501804] +… | 167 |
| `n_composiciones` | int64 | 0 | 1 | 2 |
| `concepto_era` | str | 0 | r2_ajuste_a_valor_justo_operacoes_de_credito | 137 |
| `concepto` | str | 73 | ativo_total | 24 |
| `tipo_valor` | str | 0 | stock | 2 |
| `primer_periodo` | str | 0 | 202503 | 5 |
| `ultimo_periodo` | str | 0 | 202606 | 5 |
| `n_bancos` | int64 | 0 | 34 | 4 |

### `bank_hechos`

107,855 filas · 25 columnas · periodo: 201403 → 202606 · 1.80 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `anio` | int64 | 0 | 2014 | 13 |
| `trimestre` | int64 | 0 | 1 | 4 |
| `escopo` | str | 0 | prudencial | 1 |
| `cod_inst` | str | 0 | C0080075 | 34 |
| `institucion_bcb` | str | 0 | BRADESCO - PRUDENCIAL | 40 |
| `nombre_corto` | str | 0 | Bradesco | 34 |
| `categoria` | str | 0 | nucleo | 4 |
| `num_informe` | int64 | 0 | 2 | 3 |
| `informe` | str | 0 | Ativo | 3 |
| `era` | str | 0 | cosif_pre2025 | 2 |
| `cod_cuenta` | str | 0 | 78182 | 165 |
| `cuenta` | str | 0 | Ativo Total (k) = (i) - (j) | 153 |
| `cuenta_base` | str | 0 | ativo total | 125 |
| `grupo` | str | 0 |  | 22 |
| `grupo_norm` | str | 0 |  | 22 |
| `composicion` | str | 0 | [10000007]+[20000004] | 174 |
| `cuenta_id` | str | 0 | r2_fee998449df1 | 171 |
| `concepto_era` | str | 0 | r2_ativo_total | 137 |
| `concepto` | str | 69 | ativo_total | 24 |
| `tipo_valor` | str | 0 | stock | 2 |
| `es_acumulado` | bool | 0 | False | 2 |
| `valor_publicado` | float64 | 1 | 784373108871.62 | 80906 |
| `valor` | float64 | 1 | 784373108871.62 | 80764 |

### `bank_instituciones`

34 filas · 15 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0084710 | 34 |
| `nombre_corto` | str | 0 | Cielo | 34 |
| `categoria` | str | 0 | fintech_pago | 4 |
| `institucion_bcb_ultima` | str | 0 | CIELO IP - PRUDENCIAL | 34 |
| `tcb` | str | 0 | N4 | 4 |
| `td` | str | 0 | C | 2 |
| `tc` | str | 0 | 2 | 3 |
| `sr` | str | 0 |  | 5 |
| `segmento` | str | 0 |  | 1 |
| `actividad` | str | 0 | IP Credenciadora | 12 |
| `situacion` | str | 0 | A | 1 |
| `primer_periodo` | str | 0 | 201712 | 7 |
| `ultimo_periodo` | str | 0 | 202606 | 1 |
| `n_filas` | int64 | 0 | 2573 | 7 |
| `nota` | str | 76 | Institución de pago dentro de conglomerado prudencial. | 4 |

### `bank_periodos`

50 filas · 6 columnas · periodo: 201403 → 202606 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `anio` | int64 | 0 | 2014 | 13 |
| `trimestre` | int64 | 0 | 1 | 4 |
| `anio_trimestre` | str | 0 | 2014 T1 | 50 |
| `orden_anio_trimestre` | int64 | 0 | 8057 | 50 |

### `bank_resultados`

1,490 filas · 19 columnas · periodo: 201403 → 202606 · 0.19 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `cod_inst` | str | 0 | C0080312 | 34 |
| `nombre_corto` | str | 0 | ABC Brasil | 34 |
| `categoria` | str | 0 | nucleo | 4 |
| `resultado_intermediacao_financeira` | float64 | 2 | 80296419.5700001 | 1464 |
| `outras_receitas_despesas` | float64 | 2 | 45264722.99 | 1464 |
| `resultado_antes_tributacao_participacoes` | float64 | 2 | 125220329.8 | 1464 |
| `imposto_renda_contribuicao_social` | float64 | 2 | -33448465.02 | 1464 |
| `participacoes_lucro` | float64 | 2 | -19633875.77 | 1184 |
| `lucro_liquido` | float64 | 2 | 72137989.0100001 | 1464 |
| `despesas_pessoal` | float64 | 2 | -35803125.25 | 1464 |
| `despesas_administrativas` | float64 | 2 | -21009066.51 | 1464 |
| `despesas_tributarias` | float64 | 2 | -10983530.86 | 1464 |
| `provisoes_credito` | float64 | 2 | -26417192.13 | 1437 |
| `resultado_transacoes_pagamento` | float64 | 87 | 13421748.26 | 187 |
| `resultado_nao_operacional` | float64 | 15 | -340812.76 | 1207 |
| `rendas_tarifas_bancarias` | float64 | 2 | 3254802.61 | 1266 |
| `rendas_prestacao_servicos` | float64 | 2 | 37701383.13 | 1459 |

### `bk_balancete_m`

19,012 filas · 7 columnas · fecha: 2020-01-31 → 2026-03-31 · 0.20 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 34 |
| `mes` | str | 0 | 202001 | 75 |
| `fecha` | object | 0 | 2020-01-31 | 75 |
| `concepto` | str | 0 | ativo_total | 9 |
| `tipo` | str | 0 | saldo | 2 |
| `valor` | float64 | 0 | 1172020718993.15 | 18982 |
| `cuadra_ifdata` | boolean | 0 | True | 2 |

### `bk_banco`

34 filas · 17 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080312 | 34 |
| `slug` | str | 0 | abc | 34 |
| `nombre_corto` | str | 0 | ABC Brasil | 34 |
| `institucion_bcb` | str | 0 | ABC-BRASIL - PRUDENCIAL | 34 |
| `modelo` | str | 0 | Medianos y nicho | 5 |
| `segmento_reg` | str | 0 | S3 | 5 |
| `propiedad` | str | 0 | Privado extranjero | 3 |
| `fintech` | str | 0 | Tradicional | 2 |
| `segmento_ref` | str | 0 | Demás | 4 |
| `cotizado` | bool | 0 | True | 2 |
| `ticker` | str | 62 | ABCB4 | 13 |
| `ticker_estado` | str | 62 | validar | 1 |
| `ficha` | str | 0 | completa | 2 |
| `color` | object | 100 |  | 0 |
| `nota` | str | 71 | Entrega IF.Data al día, pero no entrega ITR/DFP a la CVM desde el 2T25. En 2T26 la carter… | 6 |
| `primer_periodo` | str | 0 | 201403 | 7 |
| `ultimo_periodo` | str | 0 | 202606 | 1 |

### `bk_capital`

1,390 filas · 41 columnas · periodo: 201503 → 202606 · 0.32 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 34 |
| `periodo` | str | 0 | 201503 | 46 |
| `fecha` | object | 0 | 2015-03-31 | 46 |
| `trimestre` | str | 0 | 1T15 | 46 |
| `capital_principal` | float64 | 11 | 74094585634.92 | 1236 |
| `capital_complementar` | float64 | 11 | 0.0 | 553 |
| `nivel1` | float64 | 11 | 74094585634.92 | 1236 |
| `nivel2` | float64 | 11 | 19513014808.41 | 781 |
| `pr` | float64 | 9 | 93607600443.33 | 1255 |
| `rwa_credito` | float64 | 9 | 557017644945.93 | 1255 |
| `rwa_mercado` | float64 | 9 | 18441506611.76 | 1242 |
| `rwa_operacional` | float64 | 9 | 39117366603.7 | 661 |
| `rwa_sp` | float64 | 71 | 0.0 | 155 |
| `rwa_total` | float64 | 9 | 614576518161.39 | 1255 |
| `exposicion_total` | float64 | 16 | 988502623527.27 | 1045 |
| `indice_cp` | float64 | 11 | 0.120562018634533 | 1235 |
| `indice_nivel1` | float64 | 11 | 0.120562018634533 | 1235 |
| `basilea` | float64 | 10 | 0.152312360913777 | 1254 |
| `razon_apalancamiento` | float64 | 25 | 0.0784084419223211 | 1044 |
| `indice_inmovilizacion` | float64 | 13 | 0.47889936855414 | 1178 |
| `acp_requerido` | float64 | 68 | 33079066502.64 | 424 |
| `irrbb` | float64 | 83 | 5957744925.58 | 219 |
| `ativo_total` | float64 | 1 | 869914674568.74 | 1379 |
| `densidad_rwa` | float64 | 9 | 0.7064790790729748 | 1255 |
| `min_cp` | float64 | 0 | 0.045 | 1 |
| `min_nivel1` | float64 | 0 | 0.06 | 1 |
| `min_pr` | float64 | 0 | 0.11 | 5 |
| `acp_pct` | float64 | 0 | 0.0 | 427 |
| `fuente_acp` | str | 0 | normas (definiciones/minimos_regulatorios.json) | 2 |
| `requerimiento_cp` | float64 | 0 | 0.045 | 424 |
| `requerimiento_nivel1` | float64 | 0 | 0.06 | 420 |
| `requerimiento_pr` | float64 | 0 | 0.11 | 422 |
| `holgura_cp_pp` | float64 | 11 | 0.075562018634533 | 1235 |
| `holgura_nivel1_pp` | float64 | 11 | 0.060562018634533005 | 1235 |
| `holgura_basilea_pp` | float64 | 10 | 0.042312360913777006 | 1254 |
| `exceso_cp` | float64 | 11 | 46438642317.65745 | 1236 |
| `holgura_crecimiento` | float64 | 11 | 1.6791559696562892 | 1235 |
| `var_cp_4t` | float64 | 20 | 2609741542.4400024 | 1106 |
| `lucro_ttm` | float64 | 4 | 15902624880.74001 | 1329 |
| `otros_var_cp_4t` | float64 | 21 | -14455212162.809998 | 1099 |
| `alerta` | str | 0 |  | 8 |

### `bk_capital_grupo`

806 filas · 26 columnas · periodo: 201503 → 202606 · 0.10 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `optica` | str | 0 | Total panel | 5 |
| `grupo` | str | 0 | Todos los grupos | 15 |
| `periodo` | str | 0 | 201503 | 46 |
| `fecha` | object | 0 | 2015-03-31 | 46 |
| `trimestre` | str | 0 | 1T15 | 46 |
| `n_bancos` | int64 | 0 | 24 | 27 |
| `capital_principal` | float64 | 0 | 463156580184.35 | 542 |
| `nivel1` | float64 | 0 | 493932988699.7 | 542 |
| `pr` | float64 | 0 | 653476178592.98 | 542 |
| `rwa_credito` | float64 | 0 | 3852134138712.3403 | 542 |
| `rwa_mercado` | float64 | 0 | 202928241983.91 | 542 |
| `rwa_operacional` | float64 | 0 | 214161236459.25 | 390 |
| `rwa_total` | float64 | 0 | 4269223617155.5 | 542 |
| `ativo_total` | float64 | 0 | 6737628344118.91 | 542 |
| `indice_cp` | float64 | 0 | 0.10848730863457139 | 542 |
| `indice_nivel1` | float64 | 0 | 0.11569620919243342 | 542 |
| `basilea` | float64 | 0 | 0.15306674870977557 | 542 |
| `densidad_rwa` | float64 | 0 | 0.6336389303636772 | 542 |
| `acp_brl` | float64 | 0 | 0.0 | 499 |
| `acp_pct` | float64 | 0 | 0.0 | 347 |
| `min_cp` | float64 | 0 | 0.045 | 1 |
| `requerimiento_cp` | float64 | 0 | 0.045 | 338 |
| `holgura_cp_pp` | float64 | 0 | 0.06348730863457139 | 542 |
| `holgura_crecimiento` | float64 | 0 | 1.410829080768253 | 542 |
| `orden_optica` | int64 | 0 | 1 | 5 |
| `orden_grupo` | int64 | 0 | 0 | 15 |

### `bk_cartera`

22,864 filas · 14 columnas · periodo: 201406 → 202606 · 0.91 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 34 |
| `periodo` | str | 0 | 201406 | 48 |
| `fecha` | datetime64[us] | 0 | 2014-06-30 00:00:00 | 48 |
| `trimestre` | str | 0 | 2T14 | 48 |
| `tipo` | str | 0 | PF | 2 |
| `modalidad_id` | str | 0 | pf_consignado | 16 |
| `modalidad` | str | 0 | Consignado | 16 |
| `saldo` | float64 | 0 | 28148737758.22 | 15590 |
| `vencido15` | float64 | 0 | 163677797.34 | 13642 |
| `npl15` | float64 | 32 | 0.0058147473164121815 | 13699 |
| `peso_banco` | float64 | 6 | 0.09691747914433411 | 15632 |
| `cuota_modalidad` | float64 | 0 | 0.13157147764593047 | 15643 |
| `d_cuota_aa` | float64 | 14 | 0.49156960893824986 | 13976 |
| `quiebre_2025` | bool | 0 | False | 2 |

### `bk_cartera_grupo`

5,206 filas · 16 columnas · periodo: 201406 → 202606 · 0.19 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `optica` | str | 0 | Modelo de negocio | 2 |
| `grupo` | str | 0 | Desarrollo | 6 |
| `periodo` | str | 0 | 201406 | 48 |
| `fecha` | datetime64[us] | 0 | 2014-06-30 00:00:00 | 48 |
| `trimestre` | str | 0 | 2T14 | 48 |
| `tipo` | str | 0 | PF | 3 |
| `modalidad_id` | str | 0 | pf_consignado | 19 |
| `modalidad` | str | 0 | Consignado | 19 |
| `saldo` | float64 | 0 | 123938776.39999999 | 4603 |
| `vencido15` | float64 | 0 | 826825.15 | 4414 |
| `npl15` | float64 | 11 | 0.006671238606806192 | 4423 |
| `peso` | float64 | 3 | 0.00040284295104984846 | 4354 |
| `n_bancos` | int64 | 0 | 3 | 15 |
| `mora_sistema` | float64 | 42 | 0.026033333333333335 | 313 |
| `calidad_equivalencia` | str | 16 | exacta | 3 |
| `dirigido_peso` | float64 | 3 | 0.974861630565386 | 241 |

### `bk_cartera_mix7`

11,921 filas · 13 columnas · periodo: 201406 → 202606 · 0.23 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `nivel` | str | 0 | banco | 3 |
| `optica` | str | 0 | Banco | 3 |
| `grupo` | str | 0 | Desarrollo | 6 |
| `cod_inst` | str | 16 | C0081249 | 34 |
| `periodo` | str | 0 | 201406 | 48 |
| `fecha` | datetime64[us] | 0 | 2014-06-30 00:00:00 | 48 |
| `trimestre` | str | 0 | 2T14 | 48 |
| `categoria` | str | 0 | PJ | 7 |
| `categoria_etiqueta` | str | 0 | Empresas (todas las modalidades, incluida rural) | 7 |
| `saldo` | float64 | 0 | 1992989917.84 | 8600 |
| `peso` | float64 | 6 | 0.7329834386017534 | 8779 |
| `total` | float64 | 0 | 2719010843.74 | 1605 |
| `dirigido_peso` | float64 | 6 | 0.45558254211525007 | 1294 |

### `bk_cartera_totales`

2,858 filas · 6 columnas · periodo: 201406 → 202606 · 0.07 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 34 |
| `periodo` | str | 0 | 201406 | 48 |
| `tipo` | str | 0 | PF | 2 |
| `publicado` | float64 | 3 | 132234603100.38 | 2637 |
| `exterior` | float64 | 64 | 293700778.06 | 1037 |
| `brasil` | float64 | 3 | 131940902322.32 | 2637 |

### `bk_concesiones`

1,683 filas · 10 columnas · fecha: 2011-03-31 → 2026-09-30 · 0.09 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `segmento` | str | 0 | tot | 9 |
| `fecha` | str | 0 | 2011-03-31 | 187 |
| `concesiones` | float64 | 0 | 215654.0 | 1680 |
| `conc_12m` | float64 | 6 | 2733927.0 | 1584 |
| `conc_12m_aa` | float64 | 12 | 0.09426806202213878 | 1476 |
| `conc_real_12m` | float64 | 6 | 6273800.280177835 | 1584 |
| `ibc_12m` | float64 | 1 | 96.82733999999999 | 186 |
| `indice` | float64 | 6 | 97.82186152642328 | 1575 |
| `indice_aa` | float64 | 13 | 0.022570660202960946 | 1467 |
| `indice_z120` | float64 | 70 | 1.7485622413044588 | 504 |

### `bk_concesiones_tablas`

27 filas · 15 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `bloque` | str | 0 | mes | 3 |
| `orden` | int64 | 0 | 0 | 9 |
| `fila` | str | 0 | Total | 9 |
| `grupo` | str | 0 | Total | 3 |
| `unidad_ultimo` | str | 0 | brl_mm | 2 |
| `unidad_cambio` | str | 0 | pct | 1 |
| `trimestral` | bool | 0 | False | 1 |
| `z120` | float64 | 67 | 1.5164829223656708 | 9 |
| `ultimo` | float64 | 0 | 747.13 | 27 |
| `d1` | float64 | 0 | 0.014858915688999108 | 27 |
| `d3` | float64 | 0 | 0.03332653488885473 | 27 |
| `d12` | float64 | 0 | 0.06724929005273883 | 27 |
| `dventana` | float64 | 0 | 0.10492135067563524 | 27 |
| `corte` | str | 0 | sep-26 | 2 |
| `share` | float64 | 33 | 1.0 | 17 |

### `bk_cre_calidad`

36,781 filas · 13 columnas · periodo: 201406 → 202606 · 0.44 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | str | 0 | panel\|todos | 20 |
| `tipo_key` | str | 0 | total | 3 |
| `ver` | str | 0 | Institución | 2 |
| `medida_cal` | str | 0 | NPL | 3 |
| `periodo` | str | 0 | 201406 | 49 |
| `trimestre` | str | 0 | 2014 T2 | 49 |
| `orden_trim` | int64 | 0 | 201406 | 49 |
| `pos` | int64 | 0 | 48 | 49 |
| `serie` | str | 0 | Panel | 35 |
| `valor` | float64 | 0 | 0.048779120347128675 | 11935 |
| `d_aa` | float64 | 15 | 0.0012017027420686346 | 10016 |
| `d_tt` | float64 | 4 | 0.00014873270250666953 | 11484 |
| `npl_def` | str | 0 | E–H | 4 |

### `bk_cre_contexto`

8,196 filas · 8 columnas · periodo: 201406 → 202606 · 0.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | str | 0 | panel\|todos | 20 |
| `medida_cal` | str | 0 | ROE | 3 |
| `periodo` | str | 0 | 201506 | 49 |
| `trimestre` | str | 0 | 2015 T2 | 49 |
| `orden_trim` | int64 | 0 | 201506 | 49 |
| `pos` | int64 | 0 | 44 | 49 |
| `serie` | str | 0 | Panel | 20 |
| `valor` | float64 | 0 | 0.06361468359557602 | 1399 |

### `bk_cre_panorama`

25,602 filas · 26 columnas · periodo: 201406 → 202606 · 1.64 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | str | 0 | fintech\|Fintech | 20 |
| `tipo_key` | str | 0 | PF | 3 |
| `apilar` | str | 0 | Institución | 2 |
| `medida` | str | 0 | Crédito | 2 |
| `periodo` | str | 0 | 201406 | 49 |
| `trimestre` | str | 0 | 2014 T2 | 49 |
| `orden_trim` | int64 | 0 | 201406 | 49 |
| `pos` | int64 | 0 | 48 | 49 |
| `serie` | str | 0 | Fintechs | 35 |
| `nivel` | float64 | 0 | 1.5223688215200002 | 11002 |
| `participacion` | float64 | 0 | 1.0 | 12298 |
| `d_participacion` | float64 | 15 | 0.0 | 10200 |
| `n_bancos` | int64 | 0 | 4 | 30 |
| `aa` | float64 | 11 | 0.46634757630621415 | 9784 |
| `tt` | float64 | 4 | 0.15914582372890296 | 10535 |
| `aa2` | float64 | 11 | 0.46634757630621415 | 9800 |
| `aa4` | float64 | 15 | 0.4470741652380379 | 9428 |
| `aporte_aa` | float64 | 10 | 0.4663475763062144 | 13156 |
| `aporte_tt` | float64 | 4 | 0.15914582372890318 | 14116 |
| `aporte_aa2` | float64 | 10 | 0.4663475763062144 | 13190 |
| `aporte_aa4` | float64 | 14 | 0.447074165238038 | 12702 |
| `total_nivel` | float64 | 0 | 1.5223688215200002 | 2796 |
| `total_aa` | float64 | 10 | 0.46634757630621415 | 2648 |
| `total_tt` | float64 | 4 | 0.15914582372890296 | 2846 |
| `total_aa2` | float64 | 10 | 0.46634757630621415 | 2617 |
| `total_aa4` | float64 | 14 | 0.4470741652380379 | 2471 |

### `bk_cred_series`

3,293 filas · 3 columnas · fecha: 2000-03-31 → 2026-09-30 · 0.04 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `serie` | str | 0 | aa\|Tarjeta | 16 |
| `fecha` | str | 0 | 2008-03-31 | 313 |
| `valor` | float64 | 0 | 0.40415534601246605 | 2981 |

### `bk_cred_tablas`

30 filas · 14 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `bloque` | str | 0 | tipos | 4 |
| `orden` | int64 | 0 | 0 | 13 |
| `fila` | str | 0 | Tarjeta | 19 |
| `grupo` | str | 0 | Personas | 7 |
| `unidad_ultimo` | str | 0 | brl_mm | 3 |
| `unidad_cambio` | str | 0 | pct | 2 |
| `trimestral` | bool | 0 | False | 2 |
| `ultimo` | float64 | 0 | 741.557 | 18 |
| `d1` | float64 | 0 | -0.002093894199132529 | 29 |
| `d3` | float64 | 10 | 0.01710180955361107 | 26 |
| `d12` | float64 | 0 | 0.12298249705457431 | 29 |
| `dventana` | float64 | 0 | 0.15378929918783446 | 29 |
| `corte` | str | 0 | sep-26 | 2 |
| `share` | float64 | 23 | 0.0996152982291736 | 12 |

### `bk_empresas_m`

31,375 filas · 5 columnas · fecha: 2000-01-31 → 2026-09-30 · 0.24 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `segmento` | str | 0 | empresas | 5 |
| `sub` | str | 0 | total | 22 |
| `medida` | str | 0 | saldo | 16 |
| `fecha` | str | 0 | 2007-03-31 | 321 |
| `valor` | float64 | 0 | 413952.0 | 24957 |

### `bk_empresas_scr_m`

255,285 filas · 6 columnas · fecha: 2018-01-31 → 2026-09-30 · 2.16 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `hoja` | str | 0 | mpme | 2 |
| `dimension` | str | 0 | total | 11 |
| `segmento` | str | 0 | Total | 142 |
| `medida` | str | 0 | saldo | 23 |
| `fecha` | str | 0 | 2018-01-31 | 105 |
| `valor` | float64 | 0 | 531969912493.93 | 228144 |

### `bk_exposicion`

1,429 filas · 12 columnas · periodo: 201406 → 202606 · 0.09 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 34 |
| `periodo` | str | 0 | 201406 | 48 |
| `fecha` | datetime64[us] | 0 | 2014-06-30 00:00:00 | 48 |
| `trimestre` | str | 0 | 2T14 | 48 |
| `cobertura` | float64 | 0 | 0.7087912257886846 | 1145 |
| `mora_implicita` | float64 | 14 | 0.04110942527836453 | 1232 |
| `npl_observado` | float64 | 6 | 0.02879038288379002 | 1316 |
| `brecha_pp` | float64 | 14 | -1.231904239457451 | 1232 |
| `efecto_mix_pp` | float64 | 23 | -0.08550866426012442 | 1104 |
| `efecto_mora_pp` | float64 | 23 | 0.16870595642516403 | 1104 |
| `d_mora_implicita_aa_pp` | float64 | 23 | 0.08319729216503961 | 1104 |
| `quiebre_2025` | bool | 0 | False | 2 |

### `bk_fondeo_m`

14,774 filas · 4 columnas · fecha: 2002-01-31 → 2026-09-30 · 0.15 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `serie` | str | 0 | moneda | 17 |
| `medida` | str | 0 | saldo | 6 |
| `fecha` | str | 0 | 2002-01-31 | 297 |
| `valor` | float64 | 0 | 27239.411 | 14051 |

### `bk_grupo`

68,547 filas · 17 columnas · periodo: 201403 → 202606 · 2.89 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `optica` | str | 0 | Total panel | 5 |
| `grupo` | str | 0 | Todos los grupos | 16 |
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | object | 0 | 2014-03-31 | 50 |
| `trimestre` | str | 0 | 1T14 | 50 |
| `metrica` | str | 0 | antes_tributacao_q | 86 |
| `valor` | float64 | 0 | 26472980693.65998 | 47640 |
| `valor_aa` | float64 | 15 | -0.5665442247503278 | 40805 |
| `unidad_aa` | str | 5 | fraccion | 3 |
| `valor_tt` | float64 | 12 | 0.06986940405139297 | 42187 |
| `unidad_tt` | str | 5 | fraccion | 3 |
| `mediana` | float64 | 0 | 107388301.725 | 43278 |
| `p25` | float64 | 0 | 53016640.519999996 | 44715 |
| `p75` | float64 | 0 | 1566001653.8399925 | 46199 |
| `n_bancos` | Int64 | 0 | 24 | 34 |
| `orden_optica` | int64 | 0 | 1 | 5 |
| `orden_grupo` | int64 | 0 | 0 | 16 |

### `bk_manifiesto`

49 filas · 12 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `tipo` | str | 0 | tabla | 2 |
| `tabla` | str | 6 | bk_balancete_m | 46 |
| `archivo` | str | 6 | bk_balancete_m.parquet | 46 |
| `filas` | float64 | 6 | 19012.0 | 45 |
| `columnas` | float64 | 6 | 7.0 | 18 |
| `rango` | str | 27 | 2020-01-31–2026-03-31 | 20 |
| `sha256` | str | 6 | 0826660a7cb601602cc80acb4efefa23188659bf0c1f99dfa772c6c0afbd0435 | 46 |
| `bytes` | float64 | 6 | 197378.0 | 46 |
| `producido_por` | str | 6 | python -X utf8 balancetes.py gold | 21 |
| `universo` | str | 94 | Panel | 3 |
| `ultimo_corte` | str | 94 | 2026-06-30 | 3 |
| `nota` | str | 94 | IF.Data prudencial, trimestral | 3 |

### `bk_metrica`

86 filas · 11 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `metrica` | str | 0 | aplic_interfinanceiras | 86 |
| `nombre` | str | 0 | Aplicaciones interfinancieras | 86 |
| `familia` | str | 0 | tamaño | 6 |
| `unidad` | str | 0 | brl | 3 |
| `formato` | str | 3 | brl_mm | 3 |
| `signo` | str | 0 | neutro | 3 |
| `signo_fuente` | str | 0 | neutro_por_defecto | 4 |
| `fuente` | str | 0 | BCB IF.Data (prudencial) | 2 |
| `definicion` | str | 0 | Saldo al cierre, conglomerado prudencial: COSIF 140199 (desde 2025); COSIF 78189 (hasta 2… | 86 |
| `en_ficha` | bool | 0 | False | 2 |
| `orden` | int64 | 0 | 1 | 86 |

### `bk_panel`

106,342 filas · 21 columnas · periodo: 201403 → 202606 · 6.98 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 34 |
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | object | 0 | 2014-03-31 | 50 |
| `trimestre` | str | 0 | 1T14 | 50 |
| `metrica` | str | 0 | antes_tributacao_q | 81 |
| `valor` | float64 | 0 | 5091645750.05999 | 101501 |
| `valor_t1` | float64 | 3 | 5091645750.05999 | 98395 |
| `valor_t4` | float64 | 11 | 5091645750.05999 | 90316 |
| `d_tt` | float64 | 6 | 0.10773339709534135 | 98399 |
| `d_aa` | float64 | 14 | -0.904011131580739 | 90378 |
| `valor_tt` | float64 | 10 | 0.10773339709534135 | 94196 |
| `unidad_d` | str | 0 | fraccion | 3 |
| `p10_grupo` | float64 | 1 | 1620620509.499995 | 15666 |
| `p50_grupo` | float64 | 1 | 3059346379.835 | 16111 |
| `p90_grupo` | float64 | 1 | 6406130837.479995 | 16365 |
| `pct_grupo` | float64 | 1 | 0.8333333333333334 | 52 |
| `pct_panel` | float64 | 0 | 0.9583333333333334 | 387 |
| `rank_panel` | float64 | 90 | 4.0 | 34 |
| `rank_panel_t4` | float64 | 91 | 4.0 | 34 |
| `modelo` | str | 0 | Grandes | 5 |
| `n_grupo` | int64 | 0 | 6 | 11 |

### `bk_portada_credito`

1,290 filas · 5 columnas · fecha: 2016-01-31 → 2026-09-30 · 0.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | str | 0 | 2016-01-31 | 129 |
| `modo` | str | 0 | nominal | 2 |
| `componente` | str | 0 | total | 5 |
| `aa` | float64 | 0 | 0.06132153522752537 | 1290 |
| `contrib_pp` | float64 | 0 | 6.132153522752544 | 1290 |

### `bk_portada_cuotas`

88 filas · 7 columnas · periodo: 202606 → 202606 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `vista` | str | 0 | Activos totales | 8 |
| `orden_vista` | int64 | 0 | 0 | 8 |
| `orden` | int64 | 0 | 0 | 11 |
| `banco` | str | 0 | Itaú Unibanco | 23 |
| `cuota` | float64 | 0 | 0.18133029882058213 | 88 |
| `grupo` | str | 0 | Grandes | 6 |
| `periodo` | str | 0 | 202606 | 1 |

### `bk_portada_m`

9,432 filas · 5 columnas · fecha: 2011-03-31 → 2026-09-30 · 0.04 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `seccion` | str | 0 | 02 | 2 |
| `indicador` | str | 0 | tasa | 9 |
| `segmento` | str | 0 | tot | 9 |
| `fecha` | str | 0 | 2011-03-31 | 187 |
| `valor` | float64 | 0 | 0.2735 | 3672 |

### `bk_portada_m_tablas`

51 filas · 17 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `seccion` | str | 0 | 02 | 2 |
| `indicador` | str | 0 | tasa | 8 |
| `orden` | int64 | 0 | 0 | 9 |
| `fila` | str | 0 | Total | 9 |
| `segmento` | str | 0 | tot | 9 |
| `ultimo` | float64 | 0 | 0.3236 | 51 |
| `d1` | float64 | 0 | 0.13000000000000234 | 46 |
| `d3` | float64 | 0 | -0.770000000000004 | 51 |
| `d12` | float64 | 0 | 0.8900000000000019 | 49 |
| `dventana` | float64 | 0 | 1.894166666666658 | 51 |
| `corte` | str | 0 | sep-26 | 1 |
| `z120` | float64 | 0 | 1.2713525045501792 | 51 |
| `p25` | float64 | 0 | 0.2391 | 49 |
| `p50` | float64 | 0 | 0.2759 | 50 |
| `p75` | float64 | 0 | 0.3054 | 51 |
| `minimo` | float64 | 0 | 0.1791 | 51 |
| `maximo` | float64 | 0 | 0.3336 | 51 |

### `bk_portada_mora`

129 filas · 3 columnas · fecha: 2016-01-31 → 2026-09-30 · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | str | 0 | 2016-01-31 | 129 |
| `nivel` | float64 | 0 | 0.0352 | 96 |
| `d_aa_pp` | float64 | 0 | 0.6700000000000002 | 110 |

### `bk_portada_roe`

42 filas · 6 columnas · periodo: 201603 → 202606 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | str | 0 | 201603 | 42 |
| `fecha` | object | 0 | 2016-03-31 | 42 |
| `trimestre` | str | 0 | 1T16 | 42 |
| `roe` | float64 | 0 | 0.17426386966404497 | 42 |
| `cdi_4t` | float64 | 0 | 0.13839715407177364 | 42 |
| `roe_cdi_pp` | float64 | 0 | 3.586671559227134 | 42 |

### `bk_portada_tablas`

19 filas · 14 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `bloque` | str | 0 | credito_nominal | 4 |
| `orden` | int64 | 0 | 0 | 7 |
| `fila` | str | 0 | Total | 9 |
| `unidad_ultimo` | str | 0 | brl_mm | 3 |
| `unidad_cambio` | str | 0 | pct | 2 |
| `trimestral` | bool | 0 | False | 2 |
| `destacar` | bool | 0 | True | 2 |
| `ultimo` | float64 | 0 | 7444.208 | 14 |
| `d1` | float64 | 0 | 0.004296471798931556 | 18 |
| `d3` | float64 | 11 | 0.013687145039547044 | 17 |
| `d12` | float64 | 0 | 0.08631671726712309 | 19 |
| `dventana` | float64 | 0 | 0.09769985870984277 | 19 |
| `corte` | str | 0 | sep-26 | 2 |
| `share` | float64 | 47 | 1.0 | 5 |

### `bk_producto_pf_m`

19,569 filas · 5 columnas · fecha: 2000-01-31 → 2026-09-30 · 0.15 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `producto` | str | 0 | tarjeta | 7 |
| `sub` | str | 0 | total | 16 |
| `medida` | str | 0 | saldo | 12 |
| `fecha` | str | 0 | 2007-03-31 | 321 |
| `valor` | float64 | 0 | 31285.0 | 16387 |

### `bk_producto_pf_scr_m`

1,106,360 filas · 6 columnas · fecha: 2018-01-31 → 2026-09-30 · 9.08 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `producto` | str | 0 | tarjeta | 7 |
| `dimension` | str | 0 | total | 9 |
| `segmento` | str | 0 | Total | 114 |
| `medida` | str | 0 | saldo | 25 |
| `fecha` | str | 0 | 2018-01-31 | 105 |
| `valor` | float64 | 0 | 203907904862.24 | 1048039 |

### `bk_publicado`

2,019 filas · 14 columnas · periodo: 202312 → 202609 · 0.04 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 15 |
| `periodo` | str | 0 | 202312 | 12 |
| `linea` | str | 0 | ativo_total | 11 |
| `valor` | float64 | 0 | 1927523249000.0 | 1732 |
| `base` | str | 0 | CPC | 1 |
| `fecha_entrega` | str | 0 | 2024-02-07 | 118 |
| `cd_cvm` | str | 0 | 000906 | 15 |
| `versao` | int64 | 0 | 1 | 5 |
| `documento` | str | 0 | DFP | 3 |
| `medida` | str | 0 | saldo | 3 |
| `consolidacion` | str | 0 | con | 2 |
| `cd_conta` | str | 0 | 1 | 42 |
| `ds_conta` | str | 0 | Ativo Total | 29 |
| `nota` | str | 0 |  | 220 |

### `bk_puente`

26 filas · 8 columnas · periodo: 202606 → 202606 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `banco` | str | 0 | Itaú Unibanco | 10 |
| `cod_inst` | str | 0 | C0080099 | 10 |
| `linea` | str | 0 | Ativo total | 8 |
| `periodo` | str | 0 | 202606 | 1 |
| `gaap` | float64 | 0 | 3226.84 | 26 |
| `ifdata` | float64 | 0 | 2846.42 | 26 |
| `dif_pct` | float64 | 0 | -0.11789242726630389 | 23 |
| `nota` | str | 0 | Puente seguros +382,02 → +0,05% | 25 |

### `bk_pyb`

179,630 filas · 7 columnas · periodo: 201403 → 202606 · 1.53 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 34 |
| `periodo` | str | 0 | 201403 | 50 |
| `trimestre` | str | 0 | 1T14 | 50 |
| `seccion` | str | 0 | activo | 6 |
| `linea` | str | 0 | activo | 65 |
| `medida` | str | 0 | pct_activo | 6 |
| `valor` | float64 | 0 | 1.0 | 144342 |

### `bk_pyb_grupo`

15,465 filas · 8 columnas · periodo: 201403 → 202606 · 0.14 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `grupo` | str | 0 | Desarrollo | 7 |
| `periodo` | str | 0 | 201403 | 50 |
| `trimestre` | str | 0 | 1T14 | 50 |
| `seccion` | str | 0 | activo | 6 |
| `linea` | str | 0 | activo | 61 |
| `medida` | str | 0 | pct_activo | 3 |
| `valor` | float64 | 0 | 1.0 | 12801 |
| `n_bancos` | int64 | 0 | 3 | 21 |

### `bk_qcambio`

194 filas · 19 columnas · periodo: 202606 → 202606 · 0.02 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | str | 0 | 202606 | 1 |
| `fecha` | object | 0 | 2026-06-30 | 1 |
| `trimestre` | str | 0 | 2T26 | 1 |
| `cod_inst` | str | 0 | C0086581 | 34 |
| `slug` | str | 0 | cloudwalk | 34 |
| `nombre_corto` | str | 0 | CloudWalk | 34 |
| `modelo` | str | 0 | Pagos | 5 |
| `metrica` | str | 0 | npl15_total | 6 |
| `nombre_metrica` | str | 0 | NPL ≥ 15 días (cartera total) | 6 |
| `valor_antes` | float64 | 2 | 0.317048998158269 | 191 |
| `valor_ahora` | float64 | 0 | 0.21867007524783716 | 194 |
| `cambio` | float64 | 2 | -9.837892291043183 | 191 |
| `unidad_cambio` | str | 0 | pp | 1 |
| `z` | float64 | 2 | -4.577169176476363 | 191 |
| `sentido` | str | 2 | mejora | 3 |
| `rango` | Int64 | 2 | 1 | 191 |
| `cuota_credito` | float64 | 1 | 0.00013711871001216252 | 33 |
| `relevante` | bool | 0 | False | 2 |
| `rango_relevantes` | Int64 | 47 | 1 | 102 |

### `bk_ref`

306,577 filas · 12 columnas · — · 1.79 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `edicion` | str | 0 | 202304 | 8 |
| `hoja` | str | 0 | Graf 1.1.2 | 233 |
| `grafico` | str | 0 | 1.1.2 | 229 |
| `titulo` | str | 0 | Gráfico 1.1.2 – Taxas de política monetária em economias avançadas | 650 |
| `clave` | str | 0 | taxas de política monetária em economias avançadas | 478 |
| `unidad` | str | 0 |  | 25 |
| `tipo` | str | 0 | serie | 2 |
| `serie` | str | 0 | EUA | 1375 |
| `orden` | int64 | 0 | 8 | 6037 |
| `fecha_ref` | str | 9 | 2019-03 | 315 |
| `categoria` | str | 0 |  | 1399 |
| `valor` | float64 | 0 | 2.5 | 81584 |

### `bk_ref_sitio`

1,166 filas · 12 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `edicion` | str | 0 | 202610 | 1 |
| `hoja` | str | 0 | Graf 1.2.3.1 | 3 |
| `grafico` | str | 0 | 1.2.3.1 | 3 |
| `titulo` | str | 0 | Gráfico 1.2.3.1 - Evolução do ROE dos segmentos do SFN | 3 |
| `clave` | str | 0 | evolução do roe dos segmentos do sfn | 3 |
| `unidad` | str | 0 |  | 2 |
| `tipo` | str | 0 | serie | 1 |
| `serie` | str | 0 | SFN \| LL | 29 |
| `orden` | int64 | 0 | 10 | 56 |
| `fecha_ref` | str | 0 | 2020-12 | 59 |
| `categoria` | str | 0 |  | 1 |
| `valor` | float64 | 0 | 119383060387.0 | 616 |

### `bk_roe_arbol`

35,100 filas · 12 columnas · periodo: 201403 → 202606 · 0.55 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `entidad` | str | 0 | C0080075 | 54 |
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | object | 0 | 2014-03-31 | 50 |
| `trimestre` | str | 0 | 1T14 | 50 |
| `linea` | str | 0 | margen_antes_provisiones | 13 |
| `nombre` | str | 0 | Margen antes de provisiones | 13 |
| `orden` | int64 | 0 | 1 | 13 |
| `es_resumen` | bool | 0 | False | 2 |
| `unidad` | str | 0 | fraccion | 2 |
| `valor` | float64 | 26 | 0.031493213429097056 | 22613 |
| `mediana_grupo` | float64 | 24 | 0.03119135369352134 | 6032 |
| `brecha` | float64 | 28 | 0.00030185973557571646 | 21254 |

### `bk_scr`

7,810 filas · 14 columnas · fecha: 2012-07-31 → 2026-09-30 · 0.54 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `corte` | str | 0 | porte_pj | 3 |
| `fecha` | datetime64[us] | 0 | 2012-07-31 00:00:00 | 171 |
| `segmento_inst` | str | 69 | Arrendamento | 8 |
| `cliente` | str | 69 | PF | 2 |
| `porte` | str | 90 | Grande | 5 |
| `uf` | str | 41 | AC | 27 |
| `carteira_ativa` | float64 | 0 | 563755769741.65 | 7810 |
| `vencido_15_90` | float64 | 0 | 896951444.74 | 7796 |
| `vencido_90` | float64 | 0 | 1088121084.37 | 7783 |
| `inadimplencia_brl` | float64 | 0 | 2738371289.29 | 7781 |
| `ativo_problematico` | float64 | 0 | 10345113805.74 | 7787 |
| `tasa_inad` | float64 | 0 | 0.00485737164259073 | 7788 |
| `tasa_ap` | float64 | 0 | 0.018350346658945613 | 7793 |
| `porte_es` | str | 90 | Grande | 5 |

### `bk_scr_series`

14,503 filas · 3 columnas · fecha: 2019-01-31 → 2026-09-30 · 0.14 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `serie` | str | 0 | aa\|Tarjeta\|Hasta 1 SM | 325 |
| `fecha` | str | 0 | 2023-01-31 | 93 |
| `valor` | float64 | 0 | 0.4349751974528233 | 13948 |

### `bk_scr_tablas`

397 filas · 16 columnas · — · 0.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `bloque` | str | 0 | saldo | 9 |
| `producto` | str | 0 | Tarjeta | 9 |
| `orden` | int64 | 0 | 0 | 12 |
| `fila` | str | 0 | Hasta 1 SM | 43 |
| `grupo` | str | 0 | Tramo | 4 |
| `unidad_ultimo` | str | 0 | brl_mm | 3 |
| `unidad_cambio` | str | 0 | pct | 2 |
| `trimestral` | bool | 0 | False | 1 |
| `destacar` | bool | 0 | False | 2 |
| `share` | float64 | 20 | 0.0892021706077773 | 130 |
| `ultimo` | float64 | 0 | 67.61582059299 | 381 |
| `d1` | float64 | 0 | -0.011071523183337484 | 381 |
| `d3` | float64 | 0 | -0.016595358865371 | 381 |
| `d12` | float64 | 0 | 0.07510662724967987 | 381 |
| `dventana` | float64 | 0 | 0.03952049357960763 | 381 |
| `corte` | str | 0 | sep-26 | 1 |

### `bk_sensibilidad`

34 filas · 8 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080312 | 34 |
| `modelo` | str | 0 | Medianos y nicho | 5 |
| `beta_nim_cdi` | float64 | 6 | 0.042848735017183594 | 32 |
| `ic_inf` | float64 | 6 | -0.032122054867327964 | 32 |
| `ic_sup` | float64 | 6 | 0.11781952490169514 | 32 |
| `r2` | float64 | 6 | 0.010204728303748078 | 32 |
| `n_trimestres` | Int64 | 0 | 41 | 12 |
| `excluidos` | str | 0 | 202412 | 3 |

### `bk_sistema_bal_m`

1,485 filas · 17 columnas · fecha: 2020-01-31 → 2026-03-31 · 0.11 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `optica` | str | 0 | Total panel | 5 |
| `grupo` | str | 0 | Todos los grupos | 16 |
| `mes` | str | 0 | 202001 | 75 |
| `fecha` | object | 0 | 2020-01-31 | 75 |
| `n_bancos` | int64 | 0 | 30 | 26 |
| `lucro_12m` | float64 | 16 | 109716852716.14998 | 924 |
| `pl_medio_12m` | float64 | 16 | 754079380889.7849 | 924 |
| `roe_12m` | float64 | 16 | 0.14549774930417575 | 924 |
| `ativo_total` | float64 | 0 | 8148187375284.838 | 1110 |
| `patrimonio_liquido` | float64 | 0 | 716956729181.6602 | 1110 |
| `credito_liquido` | float64 | 1 | 2776143068354.4004 | 1089 |
| `depositos` | float64 | 0 | 2430188252505.62 | 1110 |
| `depositos_aa` | float64 | 16 | 0.3908874868001868 | 930 |
| `credito_depositos` | float64 | 1 | 1.1423572085380986 | 1092 |
| `patrimonio_activo` | float64 | 0 | 0.08798972043234307 | 1110 |
| `orden_optica` | int64 | 0 | 1 | 5 |
| `orden_grupo` | int64 | 0 | 0 | 16 |

### `bk_sistema_m`

8,819 filas · 10 columnas · fecha: 2000-01-01 → 2026-11-01 · 0.24 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[us] | 0 | 2000-01-01 00:00:00 | 323 |
| `serie_id` | str | 0 | credito_pib | 44 |
| `unidad` | str | 0 | fraccion | 2 |
| `valor` | float64 | 3 | 0.2631 | 4764 |
| `p10` | float64 | 32 | 0.24165000000000003 | 2610 |
| `p50` | float64 | 32 | 0.2551 | 2636 |
| `p90` | float64 | 32 | 0.27044 | 3054 |
| `es_ultimo` | bool | 0 | False | 2 |
| `d_1m` | float64 | 3 | -0.0040999999999999925 | 3849 |
| `d_3m` | float64 | 4 | -0.0021999999999999797 | 4273 |

### `bk_sistema_q`

2,930 filas · 10 columnas · fecha: 2000-03-31 → 2026-09-30 · 0.11 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[us] | 0 | 2011-06-30 00:00:00 | 107 |
| `serie_id` | str | 0 | atraso15_90_pf | 45 |
| `unidad` | str | 0 | fraccion | 2 |
| `valor` | float64 | 0 | 0.06166666666666667 | 2562 |
| `p10` | float64 | 29 | 0.05390333333333333 | 1129 |
| `p50` | float64 | 29 | 0.05859999999999999 | 1270 |
| `p90` | float64 | 29 | 0.061926666666666665 | 1265 |
| `es_ultimo` | bool | 0 | False | 2 |
| `d_tt` | float64 | 2 | -0.0010333333333333306 | 2236 |
| `d_aa` | float64 | 6 | 0.0008000000000000021 | 2401 |

## Intermedio (`datos/intermedio/`) — entradas del gold

Carpeta `datos/intermedio/`.

### `cre_apilar`

2 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `apilar` | str | 0 | Institución | 2 |
| `orden_apilar` | int64 | 0 | 1 | 2 |

### `cre_calidad`

36,781 filas · 13 columnas · periodo: 201406 → 202606 · 0.44 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | str | 0 | panel\|todos | 20 |
| `tipo_key` | str | 0 | total | 3 |
| `ver` | str | 0 | Institución | 2 |
| `medida_cal` | str | 0 | NPL | 3 |
| `periodo` | str | 0 | 201406 | 49 |
| `trimestre` | str | 0 | 2014 T2 | 49 |
| `orden_trim` | int64 | 0 | 201406 | 49 |
| `pos` | int64 | 0 | 48 | 49 |
| `serie` | str | 0 | Panel | 35 |
| `valor` | float64 | 0 | 0.048779120347128675 | 11935 |
| `d_aa` | float64 | 15 | 0.0012017027420686346 | 10016 |
| `d_tt` | float64 | 4 | 0.00014873270250666953 | 11484 |
| `npl_def` | str | 0 | E–H | 4 |

### `cre_contexto`

8,196 filas · 8 columnas · periodo: 201406 → 202606 · 0.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | str | 0 | panel\|todos | 20 |
| `medida_cal` | str | 0 | ROE | 3 |
| `periodo` | str | 0 | 201506 | 49 |
| `trimestre` | str | 0 | 2015 T2 | 49 |
| `orden_trim` | int64 | 0 | 201506 | 49 |
| `pos` | int64 | 0 | 44 | 49 |
| `serie` | str | 0 | Panel | 20 |
| `valor` | float64 | 0 | 0.06361468359557602 | 1399 |

### `cre_institucion`

20 filas · 7 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | str | 0 | panel\|todos | 20 |
| `optica` | str | 0 | Total panel | 5 |
| `orden_optica` | int64 | 0 | 1 | 5 |
| `grupo` | str | 0 | Todos los grupos | 16 |
| `orden_grupo` | int64 | 0 | 0 | 16 |
| `etiqueta` | str | 0 | Total panel | 20 |
| `orden_etiqueta` | int64 | 0 | 0 | 20 |

### `cre_medida`

2 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `medida` | str | 0 | Crédito | 2 |
| `orden_medida` | int64 | 0 | 1 | 2 |

### `cre_medida_cal`

3 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `medida_cal` | str | 0 | NPL | 3 |
| `orden_medida_cal` | int64 | 0 | 1 | 3 |

### `cre_panorama`

25,602 filas · 26 columnas · periodo: 201406 → 202606 · 1.64 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | str | 0 | fintech\|Fintech | 20 |
| `tipo_key` | str | 0 | PF | 3 |
| `apilar` | str | 0 | Institución | 2 |
| `medida` | str | 0 | Crédito | 2 |
| `periodo` | str | 0 | 201406 | 49 |
| `trimestre` | str | 0 | 2014 T2 | 49 |
| `orden_trim` | int64 | 0 | 201406 | 49 |
| `pos` | int64 | 0 | 48 | 49 |
| `serie` | str | 0 | Fintechs | 35 |
| `nivel` | float64 | 0 | 1.5223688215200002 | 11002 |
| `participacion` | float64 | 0 | 1.0 | 12298 |
| `d_participacion` | float64 | 15 | 0.0 | 10200 |
| `n_bancos` | int64 | 0 | 4 | 30 |
| `aa` | float64 | 11 | 0.46634757630621415 | 9784 |
| `tt` | float64 | 4 | 0.15914582372890296 | 10535 |
| `aa2` | float64 | 11 | 0.46634757630621415 | 9800 |
| `aa4` | float64 | 15 | 0.4470741652380379 | 9428 |
| `aporte_aa` | float64 | 10 | 0.4663475763062144 | 13156 |
| `aporte_tt` | float64 | 4 | 0.15914582372890318 | 14116 |
| `aporte_aa2` | float64 | 10 | 0.4663475763062144 | 13190 |
| `aporte_aa4` | float64 | 14 | 0.447074165238038 | 12702 |
| `total_nivel` | float64 | 0 | 1.5223688215200002 | 2796 |
| `total_aa` | float64 | 10 | 0.46634757630621415 | 2648 |
| `total_tt` | float64 | 4 | 0.15914582372890296 | 2846 |
| `total_aa2` | float64 | 10 | 0.46634757630621415 | 2617 |
| `total_aa4` | float64 | 14 | 0.4470741652380379 | 2471 |

### `cre_serie`

40 filas · 3 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `serie` | str | 0 | Panel | 40 |
| `orden_serie` | int64 | 0 | 0 | 40 |
| `color` | str | 0 | #1F2328 | 19 |

### `cre_tipo`

3 filas · 7 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `tipo_key` | str | 0 | total | 3 |
| `nivel` | str | 0 | Total | 1 |
| `orden_nivel` | int64 | 0 | 1 | 1 |
| `nodo` | str | 0 | Total | 3 |
| `orden_nodo` | int64 | 0 | 0 | 3 |
| `etiqueta` | str | 0 | Total | 3 |
| `orden_etiqueta` | int64 | 0 | 0 | 3 |

### `cre_variacion`

4 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `variacion` | str | 0 | a/a | 4 |
| `orden_variacion` | int64 | 0 | 1 | 4 |

### `cre_variacion_cal`

2 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `variacion_cal` | str | 0 | a/a | 2 |
| `orden_variacion_cal` | int64 | 0 | 1 | 2 |

### `cre_ventana`

4 filas · 3 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `ventana` | str | 0 | 8 trimestres | 4 |
| `trimestres` | int64 | 0 | 8 | 4 |
| `orden_ventana` | int64 | 0 | 1 | 4 |

### `cre_ver`

2 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `ver` | str | 0 | Institución | 2 |
| `orden_ver` | int64 | 0 | 1 | 2 |

### `metricas_bancos`

95,468 filas · 7 columnas · periodo: 201403 → 202606 · 0.94 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `cod_inst` | str | 0 | C0080075 | 34 |
| `nombre_corto` | str | 0 | Bradesco | 34 |
| `categoria` | str | 0 | nucleo | 4 |
| `metrica` | str | 0 | disponibilidades | 73 |
| `valor` | float64 | 0 | 11908888079.77 | 91045 |
