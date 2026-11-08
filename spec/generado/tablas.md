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
| `nota` | str | 76 | Incluye Banco Pan en el conglomerado prudencial; Pan no es separable en escopo prudencial. | 4 |
| `primer_periodo` | str | 0 | 201403 | 7 |
| `ultimo_periodo` | str | 0 | 202606 | 1 |

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

### `bk_grupo`

68,867 filas · 17 columnas · periodo: 201403 → 202606 · 2.91 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `optica` | str | 0 | Total panel | 5 |
| `grupo` | str | 0 | Todos los grupos | 16 |
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | object | 0 | 2014-03-31 | 50 |
| `trimestre` | str | 0 | 1T14 | 50 |
| `metrica` | str | 0 | antes_tributacao_q | 86 |
| `valor` | float64 | 0 | 26472980693.65998 | 47873 |
| `valor_aa` | float64 | 15 | -0.5665442247503278 | 40878 |
| `unidad_aa` | str | 5 | fraccion | 3 |
| `valor_tt` | float64 | 12 | 0.06986940405139297 | 42243 |
| `unidad_tt` | str | 5 | fraccion | 3 |
| `mediana` | float64 | 0 | 107388301.725 | 43493 |
| `p25` | float64 | 0 | 53016640.519999996 | 44939 |
| `p75` | float64 | 0 | 1566001653.8399925 | 46424 |
| `n_bancos` | Int64 | 0 | 24 | 34 |
| `orden_optica` | int64 | 0 | 1 | 5 |
| `orden_grupo` | int64 | 0 | 0 | 16 |

### `bk_manifiesto`

31 filas · 12 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `tipo` | str | 0 | tabla | 2 |
| `tabla` | str | 10 | bk_banco | 28 |
| `archivo` | str | 10 | bk_banco.parquet | 28 |
| `filas` | float64 | 10 | 34.0 | 27 |
| `columnas` | float64 | 10 | 17.0 | 15 |
| `rango` | str | 29 | 2014-06-30 00:00:00–2026-06-30 00:00:00 | 12 |
| `sha256` | str | 10 | 280bfed071740cd2261356e9a39189f1dc83a96750b33a0f234bbb6626b1aa47 | 28 |
| `bytes` | float64 | 10 | 12217.0 | 28 |
| `producido_por` | str | 10 | python -X utf8 preparar_gold_bancos.py base | 11 |
| `universo` | str | 90 | Panel | 3 |
| `ultimo_corte` | str | 90 | 2026-06-30 | 3 |
| `nota` | str | 90 | IF.Data prudencial, trimestral | 3 |

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

106,866 filas · 21 columnas · periodo: 201403 → 202606 · 7.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | str | 0 | C0080075 | 34 |
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | object | 0 | 2014-03-31 | 50 |
| `trimestre` | str | 0 | 1T14 | 50 |
| `metrica` | str | 0 | antes_tributacao_q | 81 |
| `valor` | float64 | 0 | 5091645750.05999 | 102015 |
| `valor_t1` | float64 | 3 | 5091645750.05999 | 99030 |
| `valor_t4` | float64 | 11 | 5091645750.05999 | 91078 |
| `d_tt` | float64 | 6 | 0.10773339709534135 | 99036 |
| `d_aa` | float64 | 14 | -0.904011131580739 | 91140 |
| `valor_tt` | float64 | 10 | 0.10773339709534135 | 94702 |
| `unidad_d` | str | 0 | fraccion | 3 |
| `p10_grupo` | float64 | 1 | 1620620509.499995 | 15745 |
| `p50_grupo` | float64 | 1 | 3059346379.835 | 16191 |
| `p90_grupo` | float64 | 1 | 6406130837.479995 | 16445 |
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

7,762 filas · 14 columnas · fecha: 2012-07-31 → 2026-08-31 · 0.53 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `corte` | str | 0 | porte_pj | 3 |
| `fecha` | datetime64[us] | 0 | 2012-07-31 00:00:00 | 170 |
| `segmento_inst` | str | 69 | Arrendamento | 8 |
| `cliente` | str | 69 | PF | 2 |
| `porte` | str | 90 | Grande | 5 |
| `uf` | str | 41 | AC | 27 |
| `carteira_ativa` | float64 | 0 | 563755769741.65 | 7762 |
| `vencido_15_90` | float64 | 0 | 896951444.74 | 7748 |
| `vencido_90` | float64 | 0 | 1088121084.37 | 7735 |
| `inadimplencia_brl` | float64 | 0 | 2738371289.29 | 7733 |
| `ativo_problematico` | float64 | 0 | 10345113805.74 | 7739 |
| `tasa_inad` | float64 | 0 | 0.00485737164259073 | 7740 |
| `tasa_ap` | float64 | 0 | 0.018350346658945613 | 7745 |
| `porte_es` | str | 90 | Grande | 5 |

### `bk_scr_series`

14,223 filas · 3 columnas · fecha: 2019-01-31 → 2026-08-31 · 0.14 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `serie` | str | 0 | aa\|Tarjeta\|Hasta 1 SM | 326 |
| `fecha` | str | 0 | 2023-01-31 | 92 |
| `valor` | float64 | 0 | 0.43497519745282287 | 13687 |

### `bk_scr_tablas`

398 filas · 16 columnas · — · 0.03 MB

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
| `share` | float64 | 20 | 0.08988570188517031 | 131 |
| `ultimo` | float64 | 0 | 68.37278767381001 | 382 |
| `d1` | float64 | 0 | 0.026981913868585172 | 382 |
| `d3` | float64 | 0 | -0.041158873580104616 | 382 |
| `d12` | float64 | 0 | 0.1578941942226415 | 382 |
| `dventana` | float64 | 0 | 0.03396254917323316 | 382 |
| `corte` | str | 0 | ago-26 | 1 |

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

### `bk_sistema_m`

8,813 filas · 10 columnas · fecha: 2000-01-01 → 2026-09-01 · 0.24 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[us] | 0 | 2000-01-01 00:00:00 | 321 |
| `serie_id` | str | 0 | credito_pib | 44 |
| `unidad` | str | 0 | fraccion | 2 |
| `valor` | float64 | 3 | 0.2631 | 4760 |
| `p10` | float64 | 32 | 0.24165000000000003 | 2606 |
| `p50` | float64 | 32 | 0.2551 | 2634 |
| `p90` | float64 | 32 | 0.27044 | 3050 |
| `es_ultimo` | bool | 0 | False | 2 |
| `d_1m` | float64 | 3 | -0.0040999999999999925 | 3845 |
| `d_3m` | float64 | 4 | -0.0021999999999999797 | 4269 |

### `bk_sistema_q`

2,930 filas · 10 columnas · fecha: 2000-03-31 → 2026-09-30 · 0.11 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[us] | 0 | 2011-06-30 00:00:00 | 107 |
| `serie_id` | str | 0 | atraso15_90_pf | 45 |
| `unidad` | str | 0 | fraccion | 2 |
| `valor` | float64 | 0 | 0.06166666666666667 | 2562 |
| `p10` | float64 | 29 | 0.05390333333333333 | 1129 |
| `p50` | float64 | 29 | 0.05859999999999999 | 1269 |
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

### `expectativas_focus`

30,029 filas · 16 columnas · — · 0.50 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha_encuesta` | datetime64[us] | 0 | 2021-01-04 00:00:00 | 1430 |
| `indicador` | str | 0 | Câmbio | 4 |
| `tipo_horizonte` | str | 0 | Año calendario | 2 |
| `horizonte` | str | 0 | 2021 | 12 |
| `anio_referencia` | Int64 | 5 | 2021 | 11 |
| `fecha_objetivo` | datetime64[us] | 0 | 2021-12-31 00:00:00 | 1437 |
| `orden_horizonte` | int64 | 0 | 2021 | 12 |
| `mediana` | float64 | 0 | 5.0 | 4756 |
| `media` | float64 | 0 | 5.02 | 19156 |
| `desvio_padrao` | float64 | 5 | 0.27 | 10533 |
| `minimo` | float64 | 5 | 4.5 | 666 |
| `maximo` | float64 | 5 | 6.0 | 767 |
| `numero_respondentes` | Int64 | 0 | 92 | 160 |
| `es_porcentaje` | bool | 0 | False | 2 |
| `unidad` | str | 0 | R$/US$ | 4 |
| `es_ultima_encuesta` | bool | 0 | False | 2 |

### `fh_deuda`

257 filas · 8 columnas · fecha: 2005-03-01 → 2026-07-01 · 0.02 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[us] | 0 | 2005-03-01 00:00:00 | 257 |
| `deuda_ingreso` | float64 | 0 | 0.172 | 231 |
| `deuda_ingreso_sin_hip` | float64 | 0 | 0.1456 | 226 |
| `servicio` | float64 | 0 | 0.17 | 215 |
| `servicio_intereses` | float64 | 0 | 0.0507 | 190 |
| `servicio_amortizacion` | float64 | 0 | 0.1193 | 200 |
| `servicio_sin_hip` | float64 | 0 | 0.1661 | 221 |
| `ingreso_real_aa` | float64 | 0 | 0.035560275659242135 | 257 |

### `metricas_bancos`

95,861 filas · 7 columnas · periodo: 201403 → 202606 · 0.94 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | str | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `cod_inst` | str | 0 | C0080075 | 34 |
| `nombre_corto` | str | 0 | Bradesco | 34 |
| `categoria` | str | 0 | nucleo | 4 |
| `metrica` | str | 0 | disponibilidades | 73 |
| `valor` | float64 | 0 | 11908888079.77 | 91433 |

### `tasa_real_exante`

1,417 filas · 6 columnas · fecha: 2021-01-21 → 2026-09-11 · 0.04 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[us] | 0 | 2021-01-21 00:00:00 | 1417 |
| `selic_nominal` | float64 | 0 | 0.02 | 21 |
| `ipca_esperado_12m` | float64 | 0 | 0.0348 | 1339 |
| `tasa_real_exante` | float64 | 0 | -0.014302280633938902 | 1376 |
| `fuente_tasa_nominal` | str | 0 | Meta Selic BCB/Copom (proxy) | 1 |
| `es_ultimo_dato` | bool | 0 | False | 2 |

### `tasas_pnad`

688 filas · 4 columnas · fecha: 2012-03-31 → 2026-07-31 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[ns] | 0 | 2012-03-31 00:00:00 | 173 |
| `serie_id` | str | 0 | t6381\|v4099 | 4 |
| `tasa` | float64 | 0 | 0.08 | 224 |
| `cambio_12m` | float64 | 8 | 0.0 | 269 |
