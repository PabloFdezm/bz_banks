# Tablas de datos (gold e intermedio)

> Generado por `herramientas/generar_spec.py` el 2026-11-05. No editar a mano: se sobrescribe.

Unidades: las tasas y ratios van en **fracción** (0,05 = 5 %); los cambios de tasas, en pp cuando la columna lo dice; los saldos en R$ (IF.Data) o R$ millones (SGS) salvo que la columna diga otra cosa. Ver `spec/04_modelo_de_datos.md`.

## Gold (`datos/gold/`) — lo que exporta el sitio y lee Power BI

Carpeta `datos/gold/`.

### `bank_balances`

1,490 filas · 12 columnas · periodo: 201403 → 202606 · 0.11 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | object | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `cod_inst` | object | 0 | C0080312 | 34 |
| `nombre_corto` | object | 0 | ABC Brasil | 34 |
| `categoria` | object | 0 | fintech_pago, nucleo, publico_listado_regional, publico_no_listado | 4 |
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
| `cuenta_id` | object | 0 | r2_dcf3bde23bd8 | 171 |
| `num_informe` | int64 | 0 | 2 | 3 |
| `informe` | object | 0 | Ativo, Demonstração de Resultado, Passivo | 3 |
| `era` | object | 0 | cosif_2025, cosif_pre2025 | 2 |
| `cod_cuenta` | object | 0 | 140204 | 165 |
| `cuenta` | object | 0 | Ajuste a Valor Justo (e4) | 153 |
| `cuenta_base` | object | 0 | ajuste a valor justo | 125 |
| `grupo` | object | 0 | Operações de Crédito | 22 |
| `grupo_norm` | object | 0 | operacoes de credito | 22 |
| `composicion` | object | 0 | [1611001806] + [1612001805] + [1613001804] + [1630501806] + [1631501805] + [1632501804] +… | 167 |
| `composicion_primera` | object | 0 | [1611001806] + [1612001805] + [1613001804] + [1630501806] + [1631501805] + [1632501804] +… | 167 |
| `n_composiciones` | int64 | 0 | 1 | 2 |
| `concepto_era` | object | 0 | r2_ajuste_a_valor_justo_operacoes_de_credito | 137 |
| `concepto` | object | 73 | ativo_total | 24 |
| `tipo_valor` | object | 0 | flujo, stock | 2 |
| `primer_periodo` | object | 0 | 201403, 201903, 202006, 202309, 202503 | 5 |
| `ultimo_periodo` | object | 0 | 201812, 202003, 202306, 202412, 202606 | 5 |
| `n_bancos` | int64 | 0 | 34 | 4 |

### `bank_hechos`

107,855 filas · 25 columnas · periodo: 201403 → 202606 · 1.80 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | object | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `anio` | int64 | 0 | 2014 | 13 |
| `trimestre` | int64 | 0 | 1 | 4 |
| `escopo` | object | 0 | prudencial | 1 |
| `cod_inst` | object | 0 | C0080075 | 34 |
| `institucion_bcb` | object | 0 | BRADESCO - PRUDENCIAL | 40 |
| `nombre_corto` | object | 0 | Bradesco | 34 |
| `categoria` | object | 0 | fintech_pago, nucleo, publico_listado_regional, publico_no_listado | 4 |
| `num_informe` | int64 | 0 | 2 | 3 |
| `informe` | object | 0 | Ativo, Demonstração de Resultado, Passivo | 3 |
| `era` | object | 0 | cosif_2025, cosif_pre2025 | 2 |
| `cod_cuenta` | object | 0 | 78182 | 165 |
| `cuenta` | object | 0 | Ativo Total (k) = (i) - (j) | 153 |
| `cuenta_base` | object | 0 | ativo total | 125 |
| `grupo` | object | 0 |  | 22 |
| `grupo_norm` | object | 0 |  | 22 |
| `composicion` | object | 0 | [10000007]+[20000004] | 174 |
| `cuenta_id` | object | 0 | r2_fee998449df1 | 171 |
| `concepto_era` | object | 0 | r2_ativo_total | 137 |
| `concepto` | object | 69 | ativo_total | 24 |
| `tipo_valor` | object | 0 | flujo, stock | 2 |
| `es_acumulado` | bool | 0 | False | 2 |
| `valor_publicado` | float64 | 1 | 784373108871.62 | 80906 |
| `valor` | float64 | 1 | 784373108871.62 | 80764 |

### `bank_instituciones`

34 filas · 15 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | object | 0 | C0084710 | 34 |
| `nombre_corto` | object | 0 | Cielo | 34 |
| `categoria` | object | 0 | fintech_pago, nucleo, publico_listado_regional, publico_no_listado | 4 |
| `institucion_bcb_ultima` | object | 0 | CIELO IP - PRUDENCIAL | 34 |
| `tcb` | object | 0 | B1, B4, N1, N4 | 4 |
| `td` | object | 0 | C, I | 2 |
| `tc` | object | 0 | 1, 2, 3 | 3 |
| `sr` | object | 0 | , S1, S2, S3, S4 | 5 |
| `segmento` | object | 0 |  | 1 |
| `actividad` | object | 0 | , Complexo, Crédito Atacado, Crédito Diversificado, Crédito Varejo, Desenvolvimento - BND… | 12 |
| `situacion` | object | 0 | A | 1 |
| `primer_periodo` | object | 0 | 201403, 201712, 201812, 201903, 202106, 202212, 202412 | 7 |
| `ultimo_periodo` | object | 0 | 202606 | 1 |
| `n_filas` | int64 | 0 | 2573 | 7 |
| `nota` | object | 76 | Conglomerado prudencial NU PAGAMENTOS; el conglomerado financiero es C0052058., Grupo fin… | 4 |

### `bank_periodos`

50 filas · 6 columnas · periodo: 201403 → 202606 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | object | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `anio` | int64 | 0 | 2014 | 13 |
| `trimestre` | int64 | 0 | 1 | 4 |
| `anio_trimestre` | object | 0 | 2014 T1 | 50 |
| `orden_anio_trimestre` | int64 | 0 | 8057 | 50 |

### `bank_resultados`

1,490 filas · 19 columnas · periodo: 201403 → 202606 · 0.19 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | object | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `cod_inst` | object | 0 | C0080312 | 34 |
| `nombre_corto` | object | 0 | ABC Brasil | 34 |
| `categoria` | object | 0 | fintech_pago, nucleo, publico_listado_regional, publico_no_listado | 4 |
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
| `cod_inst` | object | 0 | C0080312 | 34 |
| `slug` | object | 0 | abc | 34 |
| `nombre_corto` | object | 0 | ABC Brasil | 34 |
| `institucion_bcb` | object | 0 | ABC-BRASIL - PRUDENCIAL | 34 |
| `modelo` | object | 0 | Desarrollo, Digitales, Grandes, Medianos y nicho, Pagos | 5 |
| `segmento_reg` | object | 0 | S1, S2, S3, S4, Sin segmento | 5 |
| `propiedad` | object | 0 | Privado extranjero, Privado nacional, Público | 3 |
| `fintech` | object | 0 | Fintech, Tradicional | 2 |
| `segmento_ref` | object | 0 | Demás, Digitales, Públicos, S1 privados | 4 |
| `cotizado` | bool | 0 | True | 2 |
| `ticker` | object | 62 | ABCB4 | 13 |
| `ticker_estado` | object | 62 | validar | 1 |
| `ficha` | object | 0 | completa, panel | 2 |
| `color` | object | 100 |  | 0 |
| `nota` | object | 76 | Conglomerado prudencial NU PAGAMENTOS; el conglomerado financiero es C0052058. No es Nu H… | 4 |
| `primer_periodo` | object | 0 | 201403, 201712, 201812, 201903, 202106, 202212, 202412 | 7 |
| `ultimo_periodo` | object | 0 | 202606 | 1 |

### `bk_cartera`

22,864 filas · 14 columnas · periodo: 201406 → 202606 · 0.91 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | object | 0 | C0080075 | 34 |
| `periodo` | object | 0 | 201406 | 48 |
| `fecha` | datetime64[us] | 0 | 2014-06-30 00:00:00 | 48 |
| `trimestre` | object | 0 | 2T14 | 48 |
| `tipo` | object | 0 | PF, PJ | 2 |
| `modalidad_id` | object | 0 | pf_consignado | 16 |
| `modalidad` | object | 0 | Consignado | 16 |
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
| `optica` | object | 0 | Modelo de negocio, Total panel | 2 |
| `grupo` | object | 0 | Desarrollo, Digitales, Grandes, Medianos y nicho, Pagos, Total panel | 6 |
| `periodo` | object | 0 | 201406 | 48 |
| `fecha` | datetime64[us] | 0 | 2014-06-30 00:00:00 | 48 |
| `trimestre` | object | 0 | 2T14 | 48 |
| `tipo` | object | 0 | PF, PJ, total | 3 |
| `modalidad_id` | object | 0 | pf_consignado | 19 |
| `modalidad` | object | 0 | Consignado | 19 |
| `saldo` | float64 | 0 | 123938776.39999999 | 4603 |
| `vencido15` | float64 | 0 | 826825.15 | 4414 |
| `npl15` | float64 | 11 | 0.006671238606806192 | 4423 |
| `peso` | float64 | 3 | 0.00040284295104984846 | 4354 |
| `n_bancos` | int64 | 0 | 3 | 15 |
| `mora_sistema` | float64 | 42 | 0.026033333333333335 | 313 |
| `calidad_equivalencia` | object | 16 | exacta, proxy, sin_dato | 3 |
| `dirigido_peso` | float64 | 3 | 0.974861630565386 | 241 |

### `bk_cartera_mix7`

11,921 filas · 13 columnas · periodo: 201406 → 202606 · 0.23 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `nivel` | object | 0 | banco, grupo, panel | 3 |
| `optica` | object | 0 | Banco, Modelo de negocio, Total panel | 3 |
| `grupo` | object | 0 | Desarrollo, Digitales, Grandes, Medianos y nicho, Pagos, Total panel | 6 |
| `cod_inst` | object | 16 | C0081249 | 34 |
| `periodo` | object | 0 | 201406 | 48 |
| `fecha` | datetime64[us] | 0 | 2014-06-30 00:00:00 | 48 |
| `trimestre` | object | 0 | 2T14 | 48 |
| `categoria` | object | 0 | PJ, consignado, hipotecario, personal, rural, tarjeta, vehiculos | 7 |
| `categoria_etiqueta` | object | 0 | Consignado, Empresas (todas las modalidades, incluida rural), Hipotecario, Personal (sin … | 7 |
| `saldo` | float64 | 0 | 1992989917.84 | 8600 |
| `peso` | float64 | 6 | 0.7329834386017534 | 8779 |
| `total` | float64 | 0 | 2719010843.74 | 1605 |
| `dirigido_peso` | float64 | 6 | 0.45558254211525007 | 1294 |

### `bk_cartera_totales`

2,858 filas · 6 columnas · periodo: 201406 → 202606 · 0.07 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | object | 0 | C0080075 | 34 |
| `periodo` | object | 0 | 201406 | 48 |
| `tipo` | object | 0 | PF, PJ | 2 |
| `publicado` | float64 | 3 | 132234603100.38 | 2637 |
| `exterior` | float64 | 64 | 293700778.06 | 1037 |
| `brasil` | float64 | 3 | 131940902322.32 | 2637 |

### `bk_cre_calidad`

38,176 filas · 13 columnas · periodo: 201406 → 202606 · 0.49 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | object | 0 | panel\|todos | 20 |
| `tipo_key` | object | 0 | PF, PJ, total | 3 |
| `ver` | object | 0 | Institución, Tipo de crédito | 2 |
| `medida_cal` | object | 0 | NIM, NPL, ROE | 3 |
| `periodo` | object | 0 | 201406 | 49 |
| `trimestre` | object | 0 | 2014 T2 | 49 |
| `orden_trim` | int64 | 0 | 201406 | 49 |
| `pos` | int64 | 0 | 48 | 49 |
| `serie` | object | 0 | Panel | 35 |
| `valor` | float64 | 0 | 0.048779120347128675 | 12762 |
| `d_aa` | float64 | 15 | 0.0012017027420686346 | 10714 |
| `d_tt` | float64 | 4 | 0.00014873270250666953 | 12282 |
| `npl_def` | object | 0 | , Ativos problemáticos, E–H, Vencido ≥15 días | 4 |

### `bk_cre_contexto`

8,252 filas · 8 columnas · periodo: 201406 → 202606 · 0.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | object | 0 | panel\|todos | 20 |
| `medida_cal` | object | 0 | NIM, NPL, ROE | 3 |
| `periodo` | object | 0 | 201506 | 49 |
| `trimestre` | object | 0 | 2015 T2 | 49 |
| `orden_trim` | int64 | 0 | 201506 | 49 |
| `pos` | int64 | 0 | 44 | 49 |
| `serie` | object | 0 | Panel | 20 |
| `valor` | float64 | 0 | 0.06361468359557602 | 1427 |

### `bk_cre_panorama`

26,872 filas · 26 columnas · periodo: 201406 → 202606 · 1.75 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | object | 0 | fintech\|Fintech | 20 |
| `tipo_key` | object | 0 | PF, PJ, total | 3 |
| `apilar` | object | 0 | Institución, Tipo de crédito | 2 |
| `medida` | object | 0 | Crédito, Depósitos | 2 |
| `periodo` | object | 0 | 201406 | 49 |
| `trimestre` | object | 0 | 2014 T2 | 49 |
| `orden_trim` | int64 | 0 | 201406 | 49 |
| `pos` | int64 | 0 | 48 | 49 |
| `serie` | object | 0 | Fintechs | 35 |
| `nivel` | float64 | 0 | 1.5223688215200002 | 11857 |
| `participacion` | float64 | 0 | 1.0 | 13257 |
| `d_participacion` | float64 | 15 | 0.0 | 10997 |
| `n_bancos` | int64 | 0 | 4 | 30 |
| `aa` | float64 | 11 | 0.46634757630621415 | 10543 |
| `tt` | float64 | 4 | 0.15914582372890296 | 11353 |
| `aa2` | float64 | 11 | 0.46634757630621415 | 10561 |
| `aa4` | float64 | 15 | 0.4470741652380379 | 10162 |
| `aporte_aa` | float64 | 10 | 0.4663475763062144 | 14169 |
| `aporte_tt` | float64 | 4 | 0.15914582372890318 | 15195 |
| `aporte_aa2` | float64 | 10 | 0.4663475763062144 | 14203 |
| `aporte_aa4` | float64 | 14 | 0.447074165238038 | 13667 |
| `total_nivel` | float64 | 0 | 1.5223688215200002 | 3029 |
| `total_aa` | float64 | 10 | 0.46634757630621415 | 2880 |
| `total_tt` | float64 | 4 | 0.15914582372890296 | 3085 |
| `total_aa2` | float64 | 10 | 0.46634757630621415 | 2822 |
| `total_aa4` | float64 | 14 | 0.4470741652380379 | 2671 |

### `bk_cred_series`

3,151 filas · 3 columnas · fecha: 2000-03-31 → 2026-09-30 · 0.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `serie` | object | 0 | aa\|Tarjeta | 16 |
| `fecha` | object | 0 | 2011-01-31 | 313 |
| `valor` | float64 | 0 | 0.25606633028220793 | 2839 |

### `bk_cred_tablas`

30 filas · 14 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `bloque` | object | 0 | ciclo, conc, contrib, tipos | 4 |
| `orden` | int64 | 0 | 0 | 13 |
| `fila` | object | 0 | Tarjeta | 19 |
| `grupo` | object | 0 | Ciclo, Concesiones, Empresas, Otros, Personas, Stock, Total | 7 |
| `unidad_ultimo` | object | 0 | brl_mm, pct_nivel, pp | 3 |
| `unidad_cambio` | object | 0 | pct, pp | 2 |
| `trimestral` | bool | 0 | False | 2 |
| `ultimo` | float64 | 0 | 740.378 | 24 |
| `d1` | float64 | 0 | 0.006833452777101678 | 29 |
| `d3` | float64 | 10 | 0.01489286173064941 | 26 |
| `d12` | float64 | 0 | 0.13161619280231585 | 29 |
| `dventana` | float64 | 0 | 0.15728683824600265 | 29 |
| `corte` | object | 0 | 3T26, ago-26, jul-26, sep-26 | 4 |
| `share` | float64 | 23 | 0.09988423391683163 | 17 |

### `bk_exposicion`

1,429 filas · 12 columnas · periodo: 201406 → 202606 · 0.09 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | object | 0 | C0080075 | 34 |
| `periodo` | object | 0 | 201406 | 48 |
| `fecha` | datetime64[us] | 0 | 2014-06-30 00:00:00 | 48 |
| `trimestre` | object | 0 | 2T14 | 48 |
| `cobertura` | float64 | 0 | 0.7087912257886846 | 1145 |
| `mora_implicita` | float64 | 14 | 0.04110942527836453 | 1232 |
| `npl_observado` | float64 | 6 | 0.02879038288379002 | 1316 |
| `brecha_pp` | float64 | 14 | -1.231904239457451 | 1232 |
| `efecto_mix_pp` | float64 | 23 | -0.08550866426012442 | 1104 |
| `efecto_mora_pp` | float64 | 23 | 0.16870595642516403 | 1104 |
| `d_mora_implicita_aa_pp` | float64 | 23 | 0.08319729216503961 | 1104 |
| `quiebre_2025` | bool | 0 | False | 2 |

### `bk_grupo`

68,448 filas · 17 columnas · periodo: 201403 → 202606 · 2.94 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `optica` | object | 0 | Modelo de negocio, Propiedad, Segmento regulatorio, Total panel, Tradicional vs Fintech | 5 |
| `grupo` | object | 0 | Todos los grupos | 16 |
| `periodo` | object | 0 | 201403 | 50 |
| `fecha` | object | 0 | 2014-03-31 | 50 |
| `trimestre` | object | 0 | 1T14 | 50 |
| `metrica` | object | 0 | antes_tributacao_q | 84 |
| `valor` | float64 | 0 | 26472980693.65998 | 48495 |
| `valor_aa` | float64 | 15 | -0.5665442247503278 | 41431 |
| `unidad_aa` | object | 5 | abs, fraccion, pp | 3 |
| `valor_tt` | float64 | 12 | 0.06986940405139297 | 42801 |
| `unidad_tt` | object | 5 | abs, fraccion, pp | 3 |
| `mediana` | float64 | 0 | 107388301.725 | 44230 |
| `p25` | float64 | 0 | 53016640.519999996 | 45593 |
| `p75` | float64 | 0 | 1566001653.8399925 | 47141 |
| `n_bancos` | Int64 | 0 | 24 | 34 |
| `orden_optica` | int64 | 0 | 1 | 5 |
| `orden_grupo` | int64 | 0 | 0 | 16 |

### `bk_manifiesto`

29 filas · 12 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `tipo` | object | 0 | tabla, universo | 2 |
| `tabla` | object | 10 | bk_banco | 26 |
| `archivo` | object | 10 | bk_banco.parquet | 26 |
| `filas` | float64 | 10 | 34.0 | 25 |
| `columnas` | float64 | 10 | 17.0 | 16 |
| `rango` | object | 38 | 34 bancos | 13 |
| `sha256` | object | 10 | 3a5e760a8b31f28b30097b633801255ce2b280bc36c74a87e27deec39b356ef3 | 26 |
| `bytes` | float64 | 10 | 12217.0 | 26 |
| `producido_por` | object | 10 | fuera de preparar_gold_bancos.py base, preparar_gold_bancos_cartera.py, preparar_gold_ban… | 9 |
| `universo` | object | 90 | Panel, SCR, Sistema | 3 |
| `ultimo_corte` | object | 90 | 2026-06-30, 2026-08-31 00:00:00, 2026-09-01 | 3 |
| `nota` | object | 90 | IF.Data prudencial, trimestral, SCR.data, mensual, por segmento de institución (bk_scr, e… | 3 |

### `bk_metrica`

84 filas · 14 columnas · — · 0.02 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `metrica` | object | 0 | aplic_interfinanceiras | 84 |
| `nombre` | object | 0 | Aplicaciones interfinancieras | 84 |
| `nombre_corto` | object | 0 | Aplicaciones interfinancieras | 84 |
| `familia` | object | 0 | calidad, capital, crédito, fondeo, rentabilidad, tamaño | 6 |
| `unidad` | object | 0 | brl, indice, ratio | 3 |
| `formato` | object | 4 | brl_mm, pct1, x1 | 3 |
| `signo` | object | 0 | mejora_baja, mejora_sube, neutro | 3 |
| `signo_fuente` | object | 0 | arquitecto, arquitecto_montos, esqueleto_0.8, neutro_por_defecto | 4 |
| `universo` | object | 0 | panel | 1 |
| `fuente` | object | 0 | BCB IF.Data (prudencial), Derivado de BCB IF.Data (prudencial), preparar_metricas_bancos.… | 2 |
| `definicion` | object | 0 | Saldo al cierre, conglomerado prudencial: COSIF 140199 (desde 2025); COSIF 78189 (hasta 2… | 84 |
| `en_comparador` | boolean | 100 |  | 0 |
| `en_ficha` | bool | 0 | False | 2 |
| `orden` | int64 | 0 | 1 | 84 |

### `bk_panel`

134,300 filas · 21 columnas · periodo: 201403 → 202606 · 6.91 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | object | 0 | C0080075 | 34 |
| `periodo` | object | 0 | 201403 | 50 |
| `fecha` | object | 0 | 2014-03-31 | 50 |
| `trimestre` | object | 0 | 1T14 | 50 |
| `metrica` | object | 0 | antes_tributacao_q | 79 |
| `valor` | float64 | 22 | 5091645750.05999 | 99559 |
| `valor_t1` | float64 | 24 | 5091645750.05999 | 97145 |
| `valor_t4` | float64 | 30 | 5091645750.05999 | 89937 |
| `d_tt` | float64 | 27 | 0.10773339709534135 | 96666 |
| `d_aa` | float64 | 33 | -0.904011131580739 | 88988 |
| `valor_tt` | float64 | 30 | 0.10773339709534135 | 92432 |
| `unidad_d` | object | 0 | abs, fraccion, pp | 3 |
| `p10_grupo` | float64 | 16 | 1620620509.499995 | 15363 |
| `p50_grupo` | float64 | 16 | 3059346379.835 | 15804 |
| `p90_grupo` | float64 | 16 | 6406130837.479995 | 16063 |
| `pct_grupo` | float64 | 23 | 0.8333333333333334 | 52 |
| `pct_panel` | float64 | 22 | 0.9583333333333334 | 385 |
| `rank_panel` | float64 | 92 | 4.0 | 34 |
| `rank_panel_t4` | float64 | 93 | 4.0 | 34 |
| `modelo` | object | 0 | Desarrollo, Digitales, Grandes, Medianos y nicho, Pagos | 5 |
| `n_grupo` | int64 | 0 | 6 | 12 |

### `bk_portada_credito`

1,286 filas · 5 columnas · fecha: 2016-01-31 → 2026-09-30 · 0.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | object | 0 | 2016-01-31 | 129 |
| `modo` | object | 0 | nominal, real | 2 |
| `componente` | object | 0 | direccionado, libre, pf, pj, total | 5 |
| `aa` | float64 | 0 | 0.06132153522752537 | 1286 |
| `contrib_pp` | float64 | 0 | 6.132153522752544 | 1286 |

### `bk_portada_cuotas`

88 filas · 7 columnas · periodo: 202606 → 202606 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `vista` | object | 0 | Activos totales, Crédito empresas, Crédito personas, Crédito total, Depósitos a la vista,… | 8 |
| `orden_vista` | int64 | 0 | 0 | 8 |
| `orden` | int64 | 0 | 0 | 11 |
| `banco` | object | 0 | Itaú Unibanco | 23 |
| `cuota` | float64 | 0 | 0.18133029882058213 | 88 |
| `grupo` | object | 0 | Desarrollo, Digitales, Grandes, Medianos y nicho, Pagos, Resto | 6 |
| `periodo` | object | 0 | 202606 | 1 |

### `bk_portada_mora`

129 filas · 3 columnas · fecha: 2016-01-31 → 2026-09-30 · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | object | 0 | 2016-01-31 | 129 |
| `nivel` | float64 | 0 | 0.0352 | 96 |
| `d_aa_pp` | float64 | 0 | 0.6700000000000002 | 110 |

### `bk_portada_roe`

42 filas · 6 columnas · periodo: 201603 → 202606 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | object | 0 | 201603 | 42 |
| `fecha` | object | 0 | 2016-03-31 | 42 |
| `trimestre` | object | 0 | 1T16 | 42 |
| `roe` | float64 | 0 | 0.17426386966404497 | 42 |
| `cdi_4t` | float64 | 0 | 0.13923333333333335 | 41 |
| `roe_cdi_pp` | float64 | 0 | 3.5030536330711626 | 42 |

### `bk_portada_tablas`

19 filas · 11 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `bloque` | object | 0 | credito_nominal, credito_real, mora, roe | 4 |
| `orden` | int64 | 0 | 0 | 7 |
| `fila` | object | 0 | Direccionado, Empresas, Empresas · libre, Libre, Personas, Personas · libre, ROE 12 meses… | 9 |
| `unidad` | object | 0 | pct, pp | 2 |
| `ultimo` | float64 | 0 | 7444.208 | 14 |
| `d1` | float64 | 0 | 0.004296471798931556 | 19 |
| `d3` | float64 | 11 | 0.013687145039547044 | 17 |
| `d12` | float64 | 0 | 0.08631671726712309 | 19 |
| `dventana` | float64 | 0 | 0.09769985870984277 | 19 |
| `corte` | object | 0 | 2T26, ago-26, jul-26, sep-26 | 4 |
| `share` | float64 | 47 | 1.0 | 5 |

### `bk_puente`

26 filas · 8 columnas · periodo: 202606 → 202606 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `banco` | object | 0 | ABC Brasil, BMG, BNDES, BTG Pactual, Banco do Brasil, Banestes, Bradesco, Caixa, Itaú Uni… | 10 |
| `cod_inst` | object | 0 | C0080075, C0080099, C0080147, C0080178, C0080185, C0080312, C0080329, C0080336, C0080738,… | 10 |
| `linea` | object | 0 | Ativo total, Crédito (nota 8a), Crédito total, Crédito total (e+f+g+h), Depósitos, Depósi… | 8 |
| `periodo` | object | 0 | 202606 | 1 |
| `gaap` | float64 | 0 | 3226.84 | 26 |
| `ifdata` | float64 | 0 | 2846.42 | 26 |
| `dif_pct` | float64 | 0 | -0.11789242726630389 | 23 |
| `nota` | object | 0 | Puente seguros +382,02 → +0,05% | 25 |

### `bk_qcambio`

194 filas · 19 columnas · periodo: 202606 → 202606 · 0.02 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | object | 0 | 202606 | 1 |
| `fecha` | object | 0 | 2026-06-30 | 1 |
| `trimestre` | object | 0 | 2T26 | 1 |
| `cod_inst` | object | 0 | C0086581 | 34 |
| `slug` | object | 0 | cloudwalk | 34 |
| `nombre_corto` | object | 0 | CloudWalk | 34 |
| `modelo` | object | 0 | Desarrollo, Digitales, Grandes, Medianos y nicho, Pagos | 5 |
| `metrica` | object | 0 | costo_riesgo_ttm, credito_aa, eficiencia_ttm, npl15_total, roe_ttm, share_credito | 6 |
| `nombre_metrica` | object | 0 | Costo del riesgo (12 meses), Crecimiento a/a de la cartera, Cuota de crédito, Eficiencia … | 6 |
| `valor_antes` | float64 | 2 | 0.317048998158269 | 191 |
| `valor_ahora` | float64 | 0 | 0.21867007524783716 | 194 |
| `cambio` | float64 | 2 | -9.837892291043183 | 191 |
| `unidad_cambio` | object | 0 | pp | 1 |
| `z` | float64 | 2 | -4.577169176476363 | 191 |
| `sentido` | object | 2 | deterioro, mejora, neutro | 3 |
| `rango` | Int64 | 2 | 1 | 191 |
| `cuota_credito` | float64 | 1 | 0.00013711871001216252 | 33 |
| `relevante` | bool | 0 | False | 2 |
| `rango_relevantes` | Int64 | 47 | 1 | 102 |

### `bk_roe_arbol`

35,100 filas · 10 columnas · periodo: 201403 → 202606 · 0.56 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `entidad` | object | 0 | C0080075 | 54 |
| `periodo` | object | 0 | 201403 | 50 |
| `fecha` | object | 0 | 2014-03-31 | 50 |
| `trimestre` | object | 0 | 1T14 | 50 |
| `linea` | object | 0 | margen_antes_provisiones | 13 |
| `orden` | int64 | 0 | 1 | 13 |
| `unidad` | object | 0 | fraccion, veces | 2 |
| `valor` | float64 | 25 | 0.031493213429097056 | 23054 |
| `mediana_grupo` | float64 | 23 | 0.03119135369352134 | 6454 |
| `brecha` | float64 | 27 | 0.00030185973557571646 | 21623 |

### `bk_scr`

7,762 filas · 15 columnas · fecha: 2012-07-31 → 2026-08-31 · 0.53 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `corte` | object | 0 | porte_pj, segmento_cliente, uf | 3 |
| `fecha` | datetime64[us] | 0 | 2012-07-31 00:00:00 | 170 |
| `segmento_inst` | object | 69 | Arrendamento, Banco, Cooperativa, Desenvolvimento/Fomento, Financeira, Fintech, Instituiç… | 8 |
| `cliente` | object | 69 | PF, PJ | 2 |
| `modalidad` | object | 100 |  | 0 |
| `porte` | object | 90 | Grande, Indisponível, Micro, Médio, Pequeno | 5 |
| `uf` | object | 41 | AC | 27 |
| `carteira_ativa` | float64 | 0 | 563755769741.65 | 7762 |
| `vencido_15_90` | float64 | 0 | 896951444.74 | 7748 |
| `vencido_90` | float64 | 0 | 1088121084.37 | 7735 |
| `inadimplencia_brl` | float64 | 0 | 2738371289.29 | 7733 |
| `ativo_problematico` | float64 | 0 | 10345113805.74 | 7739 |
| `tasa_inad` | float64 | 0 | 0.00485737164259073 | 7740 |
| `tasa_ap` | float64 | 0 | 0.018350346658945613 | 7745 |
| `porte_es` | object | 90 | Grande, Mediana, Micro, Pequeña, Sin dato | 5 |

### `bk_sensibilidad`

34 filas · 8 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `cod_inst` | object | 0 | C0080312 | 34 |
| `modelo` | object | 0 | Desarrollo, Digitales, Grandes, Medianos y nicho, Pagos | 5 |
| `beta_nim_cdi` | float64 | 6 | 0.042848735017183594 | 32 |
| `ic_inf` | float64 | 6 | -0.03212205486732813 | 32 |
| `ic_sup` | float64 | 6 | 0.11781952490169531 | 32 |
| `r2` | float64 | 6 | 0.01020472830374819 | 32 |
| `n_trimestres` | Int64 | 0 | 41 | 12 |
| `excluidos` | object | 0 | , 202412, 202412;202503 | 3 |

### `bk_sistema_m`

8,059 filas · 10 columnas · fecha: 2000-01-01 → 2026-09-01 · 0.23 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[ns] | 0 | 2000-01-01 00:00:00 | 321 |
| `serie_id` | object | 0 | credito_pib | 40 |
| `unidad` | object | 0 | fraccion, pp | 2 |
| `valor` | float64 | 3 | 0.2631 | 4754 |
| `p10` | float64 | 32 | 0.24165000000000003 | 2385 |
| `p50` | float64 | 32 | 0.2551 | 2506 |
| `p90` | float64 | 32 | 0.27044 | 2837 |
| `es_ultimo` | bool | 0 | False | 2 |
| `d_1m` | float64 | 3 | -0.0040999999999999925 | 3829 |
| `d_3m` | float64 | 4 | -0.0021999999999999797 | 4242 |

### `bk_sistema_q`

2,680 filas · 10 columnas · fecha: 2000-03-31 → 2026-09-30 · 0.10 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[ns] | 0 | 2011-06-30 00:00:00 | 107 |
| `serie_id` | object | 0 | atraso15_90_pf | 41 |
| `unidad` | object | 0 | fraccion, pp | 2 |
| `valor` | float64 | 0 | 0.06166666666666667 | 2399 |
| `p10` | float64 | 29 | 0.05390333333333333 | 1026 |
| `p50` | float64 | 29 | 0.05859999999999999 | 1163 |
| `p90` | float64 | 29 | 0.061926666666666665 | 1162 |
| `es_ultimo` | bool | 0 | False | 2 |
| `d_tt` | float64 | 2 | -0.0010333333333333306 | 2144 |
| `d_aa` | float64 | 6 | 0.0008000000000000021 | 2247 |

## Intermedio (`datos/intermedio/`) — entradas del gold

Carpeta `datos/intermedio/`.

### `cre_apilar`

2 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `apilar` | object | 0 | Institución, Tipo de crédito | 2 |
| `orden_apilar` | int64 | 0 | 1 | 2 |

### `cre_calidad`

38,176 filas · 13 columnas · periodo: 201406 → 202606 · 0.49 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | object | 0 | panel\|todos | 20 |
| `tipo_key` | object | 0 | PF, PJ, total | 3 |
| `ver` | object | 0 | Institución, Tipo de crédito | 2 |
| `medida_cal` | object | 0 | NIM, NPL, ROE | 3 |
| `periodo` | object | 0 | 201406 | 49 |
| `trimestre` | object | 0 | 2014 T2 | 49 |
| `orden_trim` | int64 | 0 | 201406 | 49 |
| `pos` | int64 | 0 | 48 | 49 |
| `serie` | object | 0 | Panel | 35 |
| `valor` | float64 | 0 | 0.048779120347128675 | 12762 |
| `d_aa` | float64 | 15 | 0.0012017027420686346 | 10714 |
| `d_tt` | float64 | 4 | 0.00014873270250666953 | 12282 |
| `npl_def` | object | 0 | , Ativos problemáticos, E–H, Vencido ≥15 días | 4 |

### `cre_contexto`

8,252 filas · 8 columnas · periodo: 201406 → 202606 · 0.03 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | object | 0 | panel\|todos | 20 |
| `medida_cal` | object | 0 | NIM, NPL, ROE | 3 |
| `periodo` | object | 0 | 201506 | 49 |
| `trimestre` | object | 0 | 2015 T2 | 49 |
| `orden_trim` | int64 | 0 | 201506 | 49 |
| `pos` | int64 | 0 | 44 | 49 |
| `serie` | object | 0 | Panel | 20 |
| `valor` | float64 | 0 | 0.06361468359557602 | 1427 |

### `cre_institucion`

20 filas · 7 columnas · — · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | object | 0 | panel\|todos | 20 |
| `optica` | object | 0 | Modelo de negocio, Propiedad, Segmento regulatorio, Total panel, Tradicional vs Fintech | 5 |
| `orden_optica` | int64 | 0 | 1 | 5 |
| `grupo` | object | 0 | Todos los grupos | 16 |
| `orden_grupo` | int64 | 0 | 0 | 16 |
| `etiqueta` | object | 0 | Total panel | 20 |
| `orden_etiqueta` | int64 | 0 | 0 | 20 |

### `cre_medida`

2 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `medida` | object | 0 | Crédito, Depósitos | 2 |
| `orden_medida` | int64 | 0 | 1 | 2 |

### `cre_medida_cal`

3 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `medida_cal` | object | 0 | NIM, NPL, ROE | 3 |
| `orden_medida_cal` | int64 | 0 | 1 | 3 |

### `cre_panorama`

26,872 filas · 26 columnas · periodo: 201406 → 202606 · 1.75 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `inst_key` | object | 0 | fintech\|Fintech | 20 |
| `tipo_key` | object | 0 | PF, PJ, total | 3 |
| `apilar` | object | 0 | Institución, Tipo de crédito | 2 |
| `medida` | object | 0 | Crédito, Depósitos | 2 |
| `periodo` | object | 0 | 201406 | 49 |
| `trimestre` | object | 0 | 2014 T2 | 49 |
| `orden_trim` | int64 | 0 | 201406 | 49 |
| `pos` | int64 | 0 | 48 | 49 |
| `serie` | object | 0 | Fintechs | 35 |
| `nivel` | float64 | 0 | 1.5223688215200002 | 11857 |
| `participacion` | float64 | 0 | 1.0 | 13257 |
| `d_participacion` | float64 | 15 | 0.0 | 10997 |
| `n_bancos` | int64 | 0 | 4 | 30 |
| `aa` | float64 | 11 | 0.46634757630621415 | 10543 |
| `tt` | float64 | 4 | 0.15914582372890296 | 11353 |
| `aa2` | float64 | 11 | 0.46634757630621415 | 10561 |
| `aa4` | float64 | 15 | 0.4470741652380379 | 10162 |
| `aporte_aa` | float64 | 10 | 0.4663475763062144 | 14170 |
| `aporte_tt` | float64 | 4 | 0.15914582372890318 | 15196 |
| `aporte_aa2` | float64 | 10 | 0.4663475763062144 | 14204 |
| `aporte_aa4` | float64 | 14 | 0.447074165238038 | 13668 |
| `total_nivel` | float64 | 0 | 1.5223688215200002 | 3029 |
| `total_aa` | float64 | 10 | 0.46634757630621415 | 2881 |
| `total_tt` | float64 | 4 | 0.15914582372890296 | 3086 |
| `total_aa2` | float64 | 10 | 0.46634757630621415 | 2823 |
| `total_aa4` | float64 | 14 | 0.4470741652380379 | 2672 |

### `cre_serie`

40 filas · 3 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `serie` | object | 0 | Panel | 40 |
| `orden_serie` | int64 | 0 | 0 | 40 |
| `color` | object | 0 | #1F2328 | 19 |

### `cre_tipo`

3 filas · 7 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `tipo_key` | object | 0 | PF, PJ, total | 3 |
| `nivel` | object | 0 | Total | 1 |
| `orden_nivel` | int64 | 0 | 1 | 1 |
| `nodo` | object | 0 | Empresas, Personas, Total | 3 |
| `orden_nodo` | int64 | 0 | 0 | 3 |
| `etiqueta` | object | 0 | Total,  Empresas,  Personas | 3 |
| `orden_etiqueta` | int64 | 0 | 0 | 3 |

### `cre_variacion`

4 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `variacion` | object | 0 | Media 2T a/a, Media 4T a/a, a/a, t/t | 4 |
| `orden_variacion` | int64 | 0 | 1 | 4 |

### `cre_variacion_cal`

2 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `variacion_cal` | object | 0 | a/a, t/t | 2 |
| `orden_variacion_cal` | int64 | 0 | 1 | 2 |

### `cre_ventana`

4 filas · 3 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `ventana` | object | 0 | 12 trimestres, 20 trimestres, 8 trimestres, Todo | 4 |
| `trimestres` | int64 | 0 | 8 | 4 |
| `orden_ventana` | int64 | 0 | 1 | 4 |

### `cre_ver`

2 filas · 2 columnas · — · 0.00 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `ver` | object | 0 | Institución, Tipo de crédito | 2 |
| `orden_ver` | int64 | 0 | 1 | 2 |

### `expectativas_focus`

30,029 filas · 16 columnas · — · 0.50 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha_encuesta` | datetime64[us] | 0 | 2021-01-04 00:00:00 | 1430 |
| `indicador` | object | 0 | Câmbio, IPCA, PIB Total, Selic | 4 |
| `tipo_horizonte` | object | 0 | 12 meses, Año calendario | 2 |
| `horizonte` | object | 0 | 12 meses, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030 | 12 |
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
| `unidad` | object | 0 | % a.a., % anual, % crecimiento, R$/US$ | 4 |
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

78,958 filas · 7 columnas · periodo: 201403 → 202606 · 0.78 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `periodo` | object | 0 | 201403 | 50 |
| `fecha` | datetime64[us] | 0 | 2014-03-31 00:00:00 | 50 |
| `cod_inst` | object | 0 | C0080075 | 34 |
| `nombre_corto` | object | 0 | Bradesco | 34 |
| `categoria` | object | 0 | fintech_pago, nucleo, publico_listado_regional, publico_no_listado | 4 |
| `metrica` | object | 0 | disponibilidades | 61 |
| `valor` | float64 | 0 | 11908888079.77 | 75508 |

### `tasa_real_exante`

1,417 filas · 6 columnas · fecha: 2021-01-21 → 2026-09-11 · 0.04 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[us] | 0 | 2021-01-21 00:00:00 | 1417 |
| `selic_nominal` | float64 | 0 | 0.02 | 21 |
| `ipca_esperado_12m` | float64 | 0 | 0.0348 | 1339 |
| `tasa_real_exante` | float64 | 0 | -0.014302280633938902 | 1376 |
| `fuente_tasa_nominal` | object | 0 | Meta Selic BCB/Copom (proxy) | 1 |
| `es_ultimo_dato` | bool | 0 | False | 2 |

### `tasas_pnad`

688 filas · 4 columnas · fecha: 2012-03-31 → 2026-07-31 · 0.01 MB

| Columna | Tipo | % nulos | Ejemplo | Valores distintos |
|---|---|---|---|---|
| `fecha` | datetime64[ns] | 0 | 2012-03-31 00:00:00 | 173 |
| `serie_id` | object | 0 | t6381\|v4099, t6439\|v4114, t6441\|v4118, t6807\|v9869 | 4 |
| `tasa` | float64 | 0 | 0.08 | 224 |
| `cambio_12m` | float64 | 8 | 0.0 | 269 |
