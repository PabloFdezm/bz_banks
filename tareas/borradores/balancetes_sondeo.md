**Sirve acotado.** El masivo «Bancos» (un ZIP por mes, desde 202302) trae balancetes de instituciones individuales; sumarlas por grupo duplica patrimonio y lucro entre entidades del mismo conglomerado. Lo que sirve es el documento 4060, que el BCB publica por conglomerado prudencial (un archivo por líder y mes, con el código C0… de `cod_inst` dentro del archivo): en 1T26 reproduce exactamente activo, patrimonio, cartera neta, depósitos y lucro de `bk_panel` en los seis bancos probados. Quedan abiertos: el 4060 no aparece en la ruta conocida para abr–jun 2026, así que 2T26 no se puede validar a nivel conglomerado; la cuenta de provisiones de crédito en el plan nuevo no cuadra en 2025; y el balancete individual no sirve como serie de grupo sin corregir el perímetro.

# Frente 11 · Sondeo de balancetes COSIF (Fase 1)

Fecha: 9-nov-2026. Solo se escribió este informe. No se tocó pipeline, definiciones, tests, gold, sitio ni `tareas/README.md`. Sin commit ni push. Los datos bajados y los scripts están fuera del repo, en `C:\Users\pablo\AppData\Local\Temp\claude\65f10cd6064c8ce9\f3f1e501-89ac-4345-a73f-8313a4d9ad80\scratchpad\balancetes_sondeo\` (ZIP en `raw\`, parquet derivados en `parq\`).

Convención: «verificado» = URL abierta o cálculo corrido en esta sesión; «no verificado» = lo que no pude comprobar, con el motivo.

## Correcciones al informe previo (`tareas/borradores/capital_mensual_informe.md`, §3.3 y §4)

- **«Bloque B = individual» es incorrecto.** El bloque B de 202606 (PL 181,33 miles de millones de R$ en BB) es el documento **4016**, que solo aparece en junio y diciembre y que ya cerró el resultado dentro del patrimonio. El bloque A es el **4010**, el balancete con las cuentas de resultado abiertas. Verificado: en cada mes y en cada institución, Activo = Pasivo + PL + Resultado (4010) y Activo = Pasivo + PL (4016), con error 0,0 % (ver §1).
- **«En 202606 la identidad no cierra» tampoco es correcto.** Cierra cuando se incluyen las cuentas 7 y 8 (resultado).
- **El 4060 sí existe.** La ruta es por CNPJ8 del líder, no por código C: `.../individualizados/AAAAMM/4060/AAAAMM-4060-<CNPJ8 del líder>.ZIP`. Para Itaú el líder es la holding (60872504), no Itaú Unibanco S.A. (60701190).

## Resumen de lo verificado

- Masivo «Bancos»: 41 meses, 202302 a 202606, sin huecos (202301 da 404). Los 41 ZIP bajados son válidos.
- Individual 4010 (un CNPJ8 por archivo): verificado desde 201801 (BB, 206). Abr–jun 2026 da 404 en la ruta individual, aunque el masivo sí los trae.
- 4060 por líder: verificado 206 para BB en 202302, 202306, 202412, 202501, 202503, 202506, 202512, 202601 y 202603; 404 en 202604–202606. Descargado y leído para BB, Bradesco, Itaú (holding), Santander, BTG y Caixa en 202603 (y 202601).
- Cuadre 1T26 con 4060: exacto en los seis bancos (§6).
- Resultados: el acumulado del año se reinicia en enero y julio; el flujo mensual sale de la diferencia de acumulados (§4).
- Plan de cuentas: el masivo cambia de estructura en **202501**, no en 202503 (§5).

## 1. Segmentos, documentos, historia y tamaño

**Verificado**

- **Masivo «Bancos»**: `https://www.bcb.gov.br/content/estabilidadefinanceira/cosif/Bancos/AAAAMMBANCOS.csv.zip`. Existe desde **202302**; 202301 da 404. Tamaño de un mes:
  - 202302 a 202412 (plan anterior): solo 4010; 16,6–16,7 mil filas; ZIP de ~0,2 MB (CSV de 1,9 MB); 173–175 instituciones; cuentas de 8 dígitos.
  - 202501 a 202606 (meses ordinarios): solo 4010; 49–51 mil filas; ZIP de ~0,9 MB (CSV de 6,2–6,4 MB); 169–176 instituciones; cuentas de 10 dígitos.
  - Junio y diciembre: además el **4016** (desde 202306). 29–30 mil filas en 2023–24 (ZIP de 0,35 MB); 85–89 mil filas en 2025–26 (ZIP de 1,5 MB).
  - Los documentos 4016 aparecen en 202306, 202312, 202406, 202412, 202506, 202512 y 202606. El 4010 aparece en los 41 meses.
- **Individual por CNPJ8 y documento**: `https://www4.bcb.gov.br/fis/cosif/cont/balan/individualizados/AAAAMM/DOC/AAAAMM-DOC-CNPJ8.ZIP`. El 4010 pesa unos 17 KB. El 4060 pesa unos 19 KB (CSV de 115 KB para BB, ~750 filas).
- **Cabecera del masivo**: `#DATA_BASE;DOCUMENTO;CNPJ;AGENCIA;NOME_INSTITUICAO;COD_CONGL;NOME_CONGL;TAXONOMIA;CONTA;NOME_CONTA;SALDO`. Latin-1, separador `;`, coma decimal, tres líneas de título antes del encabezado. `COD_CONGL` y `NOME_CONGL` vacíos en todo el masivo (verificado en 202601 y 202606). El CKAN describe un campo `Atributo` que no existe en el CSV; la clase de institución va en `TAXONOMIA`.
- **Individual 4060**: `COD_CONGL` viene lleno (C0080329, C0080075, C0080099, C0080185, C0080336, C0080738), con `TAXONOMIA` = «CONGLOMERADO PRUDENCIAL».
- **Ejemplo de 4040**: `individualizados/201608/4040/201608-4040-C0049906.ZIP` responde 206. Con el código C aparece el consolidado financeiro (4040); con 202206 da 404. El 4040 no se usa.
- **Otros segmentos**: `.../cosif/Conglomerados/202601CONGLOMERADOS.csv.zip` (y dos variantes de nombre), `.../cosif/Cooperativas/...` y `.../cosif/Consorcios/...`: 404. No hice un listado completo de segmentos; la página de balancetes depende de JavaScript y no pude leer el listado.
- **Calendario**: el CKAN (dataset `ifs-balancetes`) cita el Comunicado 44.132/2025: ene–mar el 31-may, abr–jun el 31-ago, jul–sep el 30-nov, oct–dic el 31-mar. El texto es del CKAN; el comunicado no lo abrí.
- **Reintento de 202603** (que había fallado con un ZIP de 31 KB): bajó bien, 934 KB, ZIP válido.

**No verificado**

- Desde qué mes hay 4060 (solo probé 202302 y desde 202412 para BB; antes no).
- Si existen 4060 para los 33 bancos restantes: el cadastro da el CNPJ líder de los 34 (§3), pero solo probé los seis grandes.
- Por qué abr–jun 2026 está en el masivo y no en la ruta individual (404 para 4010 y 4060). El calendario decía que se publicaban el 31-ago, y ya pasó.
- El masivo de 202603 y 202606 dice «Data de geração dos dados: 2026-11-09» (hoy); el individual de 202603 dice 2026-05-31. El masivo parece regenerado; esto afecta la reproducibilidad.

## 2. Nivel conglomerado prudencial mensual

**Sí existe**: el 4060, por líder. Para 202603 verifiqué los seis archivos (BB, Bradesco, Itaú holding, Santander, BTG, Caixa). Cada archivo trae un solo `COD_CONGL`: el del conglomerado del líder.

**Consolidación frente a suma de individuales (verificado en 1T26, 202603)**. Suma de los miembros del conglomerado (por `CodConglomeradoPrudencial` del cadastro) contra el 4060:

| Grupo | Miembros con 4010 en el masivo | PL de cierre: suma de miembros | PL del 4060 | Diferencia |
|---|---:|---:|---:|---:|
| BB | 2 de 6 | 187,4 | 187,0 | +0,2 % |
| Bradesco | 9 de 19 | 198,0 | 177,2 | +11,7 % |
| Itaú | 7 de 20 | 362,0 | 232,5 | +55,7 % |
| Santander | 4 de 12 | 105,4 | 107,0 | −1,5 % |
| BTG | 6 de 12 | 110,0 | 78,2 | +40,7 % |
| Caixa | 1 de 4 | 114,9 | 115,3 | −0,4 % |

Lectura: el doble conteo es el patrimonio de las filiales que la matriz registra como inversión (método de participación); además faltan miembros que no presentan 4010. Para el lucro 2T26 la suma de miembros da Itaú 21,4 contra 12,5 de panel, y BTG 7,2 contra 4,9. **Conclusión: la suma de individuales no sirve para patrimonio ni lucro por grupo.**

## 3. Cruce con `cod_inst`

**Verificado**

- En el 4060, `COD_CONGL` = `cod_inst` en los seis bancos: C0080329 (BB), C0080075 (Bradesco), C0080099 (Itaú), C0080185 (Santander), C0080336 (BTG), C0080738 (Caixa). El nombre (`NOME_CONGL`) es «ITAU - PRUDENCIAL», «BTG PACTUAL - PRUDENCIAL», etc.
- En `datos/crudo/bcb_ifdata/cadastro/actual/cadastro_202606.parquet`, `CodInst` de las entidades individuales es su CNPJ8 (60746948 Bradesco S.A., 60701190 Itaú Unibanco S.A., 00000000 BB, 90400888 Santander, etc.), y `CodConglomeradoPrudencial` da la pertenencia. `CnpjInstituicaoLider` es el CNPJ8 del líder de cada conglomerado.
- Los **34 bancos** de `definiciones/bancos__dashboard.json` tienen `CnpjInstituicaoLider` en el cadastro 202606. Ejemplos: C0080099 → 60872504 (holding), C0080336 → 30306294, C0080738 → 00360305, C0080329 → 00000000, C0080185 → 90400888, C0080075 → 60746948, C0084693 (Nubank) → 18236120.
- Trampa: para Itaú el líder del prudencial es la holding. Con Itaú Unibanco S.A. el balance individual queda muy por debajo del conglomerado (§6).

**No verificado**: que el 4060 exista y tenga `COD_CONGL` igual al `cod_inst` en los 28 bancos restantes.

## 4. Resultados acumulados por semestre

**Verificado** (41 meses, individual 4010 de BB, Caixa, Bradesco, Santander, BTG, Itaú Unibanco S.A. y holding; cuentas 7 y 8 sumadas por `CONTA[:7]`):

- Las cuentas 7 (resultado credor) y 8 (resultado devedor) se acumulan dentro del semestre. BB, 2026 enero a junio: 0,947 → 2,021 → 3,033 → 4,336 → 5,228 → 6,216 (mil mil. de R$).
- Se reinician en enero y en julio: el acumulado de julio es igual al flujo de julio (BB jul-25: 0,764; BB jul-24: 3,073).
- El flujo del mes es el acumulado del mes menos el del mes anterior, salvo enero y julio (donde es el propio acumulado). Se comprobó el reinicio en los 41 meses para BB y Caixa (tabla del cálculo).
- **Junio y diciembre no cierran el resultado en el 4010**: el acumulado de junio de BB (6,216) es el semestre completo. El cierre está en el **4016** (solo jun y dic), que no tiene cuentas 7 y 8 y deja el resultado dentro del PL.
- Suma de los flujos de tres meses contra `lucro_liquido_q` de `bk_panel` (13 trimestres, 2023-1T a 2026-2T; resultados de cada banco):
  - Caixa: −0,02 % a +0,02 %. BTG: −0,02 % a +0,02 %.
  - Bradesco: −0,8 % a +0,4 %.
  - BB: −5,4 % a +3,1 % (mediana −2,6 %).
  - Santander: −11,3 % a +3,0 % (mediana −6,1 %).
  - Itaú holding: −12,6 % a +0,3 % (mediana −4,1 %).
  - La diferencia es de perímetro (individual contra conglomerado); el 4060 de 1T26 cuadra exacto (§6).

**No verificado**: el comportamiento se revisó mes a mes solo en los seis bancos indicados, no en los 34 del panel.

## 5. Plan de cuentas antes y después

**Quiebre en el archivo**: el masivo cambia de estructura en **202501**, no en 202503. En 202412 hay 187 bases de siete dígitos (`CONTA[:7]`) y 16,7 mil filas; en 202501 hay 981 bases y 50 mil filas. `QUIEBRE_2025 = 202503` (`pipeline/periodos.py`) es el quiebre de IF.Data. Para los balancetes hace falta otro quiebre en 202501.

**Equivalencia mecánica**: la base de siete dígitos se conserva y cambia el dígito verificador (8 dígitos antes; 10 después, con dos ceros y el verificador). De las 187 bases viejas, 151 existen en el plan nuevo y 36 desaparecen; aparecen 830 bases nuevas (niveles 4 y 5). Entre las 119 bases con nombre en ambas eras, 16 cambian de nombre, y algunas cambian de significado: por ejemplo 4300000 pasa de «Recursos de aceites cambiais, letras imobiliárias…» a «Outros instrumentos de dívida», y 1810000 de «Avais e fianças honrados» a «Operações com características de concessão de crédito». Hay que mapear por concepto, no por código ni por nombre.

**Continuidad BB dic-24 → ene-25 (individual)**: activo 2.304 → 2.274 (−1,3 %); cabecera de operaciones de crédito 866,0 → 857,4 (−1,0 %); depósitos 821,6 → 802,0 (−2,4 %); PL 165,0 → 169,7. Con el conglomerado, el crédito neto de 4060 pasa de 926,8 (dic-24) a 913,1 (ene-25).

**Crédito: la cabecera es neta de provisión en las dos eras** (verificado con el 4060 de BB):
- Plan viejo: `16000001` (operaciones de crédito) = suma de sus hijos + `1690000` (provisión, negativa). En dic-24 la cabecera del 4060 vale 926,77, igual al `credito_liquido` del panel; y la línea 1690000 vale −60,20, igual al `ecl_saldo` del panel.
- Plan nuevo: `1600000` (cabecera) = `credito_liquido` del panel en 202503 (922,08), 202506 (926,72), 202512 (931,95) y 202603 (941,17). Desde 202501 **no hay línea de provisión de nivel ≤ 3** bajo 16: la provisión está dentro de las subcuentas de producto.
- Consecuencia: el saldo bruto (`credito_bruto`) no sale del balancete sin el detalle de nivel 4–5. **No verificado** dónde queda el stock de provisión en el plan nuevo.

**Mapa por concepto** (base de 7 dígitos; BB, en miles de millones de R$ salvo indicación):

| Concepto | Antes (≤ 202412) | Después (≥ 202501) | Evidencia |
|---|---|---|---|
| Activo total | 1000000 + 2000000 | 1000000 + 2000000 | Identidad A = P + PL + R en todos los meses. Igual a `ativo_total` del panel en 1T26 (6 bancos) |
| PL de cierre | 6000000 + 7000000 + 8000000 | igual | Igual a `patrimonio_liquido` del panel en 1T26 (6 bancos). Sin sumar 7 y 8, el PL del 4010 queda bajo |
| Cartera neta | 1600000 (cabecera, neta) | 1600000 | Igual a `credito_liquido` del panel (§5, crédito) |
| Provisión (stock) | 1690000 (hijo de 16, negativo) | sin línea de nivel ≤ 3 | No verificado en el plan nuevo |
| Depósitos total | 4100000 | 4100000 | Igual a `depositos` del panel en 1T26 (6 bancos) |
| Depósitos vista / ahorro / interfinanceiros / a plazo | 4110000 / 4120000 / 4130000 / 4150000 | igual | BB dic-24 → ene-25: 94,4 → 84,7; 218,4 → 215,1; 11,0 → 10,4; 485,0 → 478,9 |
| Depósitos judiciales | sin línea propia; dentro de 4150000 | 4155000 (hijo de 4150000) | BB jun-26: 281,1 de 588,9 de «a prazo». El total de 415 es continuo (485,0 → 478,9) |
| Lucro del período | 7000000 + 8000000 | igual | Igual a `lucro_liquido_q` del panel en 1T26 (6 bancos) |
| Ingresos de crédito | 7110000 | 7110000 | Continuo |
| Ingresos interfinanceiros | 7140000 | 7140000 | Continuo |
| Ingresos TVM y derivados | 7150000 | 7150000 (+ 7157500) | Continuo |
| Ingresos de cambio | 7130000 (13,5 en dic-24) | **desaparece** en 202501 | Sin equivalente identificado (7191600 «lucro na compra ou venda de moeda estrangeira» es una posibilidad, no verificada) |
| Servicios y tarifas | 7170000 (10,7 en dic-24) | 7170000 + 7170100 (tarifas PN y MEI) + 7170200 (PJ) + 7170500 (pagos) | Cambia el nombre; 7170000 acumulado 1S26 = 10,0 contra 10,8 del panel (1T26 + 2T26, individual contra conglomerado, −7 %) |
| Gasto de captación | 8110000 | 8110000 | Continuo |
| Gasto de obligaciones y repasses | 8120000 | 8120000 | Continuo (−15,6 → −0,8 en ene) |
| Gasto de cambio | 8140000 (−13,3 en dic-24) | **desaparece** en 202501 | Sin equivalente identificado |
| Gasto de TVM y derivados | 8150000 | 8150000 | Continuo |
| Provisiones de crédito (P&L) | 8180000 «Aprovisionamentos e ajustes patrimoniais» (−27,2 en 2024; no separable) | 8199200 (gasto) + 7199200 (reversión), net | Neto 1T26: −16,6 contra −16,5 del panel (+1 %). Neto 1S26: −35,8 contra −35,2 (+1,6 %). 2025 completo: −37,0 contra −66,9 (no calza). Ver §6 y «Lo dudoso» |
| Personal | sin desglose: no hay hijos de 8170000 en 202412 | 8172700 (beneficios) + 8173000 (cargas) + 8173300 (proventos) + 8173600 (capacitación) | 1S26 BB: 13,4 contra 14,5 del panel (−7 %). No calza; no se investigó |
| Administrativos sin personal | 8170000 | 8170000 − personal | No se puede construir antes de 202501 |
| Impuesto y participaciones | 8940000 / 8970000 (nombres distintos) | 7940000, 7941000, 8940000 (cambian nombre, signo y posición) | No usados en los conceptos mínimos |

**Conceptos mínimos del encargo (`tareas/11_fuente_balancetes.md`)**: `despesas_pessoal` y `despesas_administrativas` (separado) no se pueden construir antes de 202501 con el masivo; `provisoes_resultado` tiene una ruptura de definición en 2025. Esto acota la serie histórica que se puede prometer.

## 6. Cuadre de 2T26 (y control de 1T26)

**Control (1T26, con 4060 del conglomerado)**: todas las diferencias son cero (en miles de millones de R$, redondeo a 0,01).

| Banco | Activo | PL de cierre | Cartera neta (16000000) | Depósitos | Lucro 1T26 |
|---|---:|---:|---:|---:|---:|
| BB | 2.605,72 / 2.605,72 | 187,01 / 187,01 | 941,17 / 941,17 | 990,97 / 990,97 | 3,206 / 3,206 |
| Bradesco | 1.990,63 / 1.990,63 | 177,22 / 177,22 | 655,13 / 655,13 | 754,27 / 754,27 | 5,043 / 5,043 |
| Itaú (holding) | 2.834,36 / 2.834,36 | 232,45 / 232,45 | 838,52 / 838,52 | 1.111,78 / 1.111,78 | 12,150 / 12,150 |
| Santander | 1.316,47 / 1.316,47 | 107,05 / 107,05 | 422,09 / 422,09 | 490,27 / 490,27 | 4,081 / 4,081 |
| BTG | 785,84 / 785,84 | 78,17 / 78,17 | 151,11 / 151,11 | 193,06 / 193,06 | 4,570 / 4,570 |
| Caixa | 2.357,61 / 2.357,61 | 115,34 / 115,34 | 1.324,76 / 1.324,76 | 860,31 / 860,31 | 3,094 / 3,094 |

(Cada celda: balancete 4060 / `bk_panel`.)

**2T26 (sin 4060 publicado en la ruta conocida)**: el líder individual del masivo 202606 (4010, resultado acumulado abierto) y la suma de miembros con pertenencia del cadastro 2T26, contra `bk_panel` 2T26. Lucro 2T26 = acumulado jun − acumulado mar, con los mismos miembros.

| Grupo | Activo: líder / suma / panel | PL: líder / suma / panel | Cartera neta: líder / suma / panel | Depósitos: líder / suma / panel | Lucro 2T26: líder / suma / panel |
|---|---|---|---|---|---|
| BB | 2.461 (−4,7 %) / 2.467 (−4,5 %) / 2.584 | 181,6 (−0,1 %) / 182,6 (+0,4 %) / 181,8 | 885 (−6,4 %) / 885 (−6,4 %) / 945 | 947 (−7,7 %) / 951 (−7,3 %) / 1.025 | 3,183 (−4,8 %) / 3,306 (−1,2 %) / 3,345 |
| Bradesco | 1.953 (−3,1 %) / 2.125 (+5,4 %) / 2.015 | 175,2 (−5,4 %) / 200,1 (+8,0 %) / 185,2 | 515 (−23,4 %) / 603 (−10,4 %) / 673 | 716 (−8,8 %) / 833 (+6,1 %) / 785 | 7,050 (−0,3 %) / 7,460 (+5,5 %) / 7,070 |
| Itaú (holding) | 493 (−82,7 %) / 2.664 (−6,4 %) / 2.846 | 207,7 (−16,9 %) / 371,0 (+48,5 %) / 249,8 | 61 (−92,8 %) / 582 (−31,5 %) / 849 | 106 (−90,7 %) / 965 (−15,6 %) / 1.144 | 11,551 (−7,7 %) / 21,433 (+71,2 %) / 12,520 |
| Santander | 1.209 (−8,0 %) / 1.241 (−5,6 %) / 1.315 | 98,7 (−7,5 %) / 107,1 (+0,4 %) / 106,7 | 248 (−41,2 %) / 264 (−37,5 %) / 422 | 471 (−6,8 %) / 478 (−5,3 %) / 505 | 3,545 (−2,8 %) / 3,752 (+2,9 %) / 3,646 |
| BTG | 743 (−13,4 %) / 869 (+1,3 %) / 858 | 79,6 (−5,6 %) / 117,4 (+39,3 %) / 84,3 | 24 (−84,5 %) / 58 (−62,6 %) / 155 | 161 (−24,1 %) / 227 (+7,3 %) / 212 | 4,901 (0,0 %) / 7,195 (+46,8 %) / 4,901 |
| Caixa | 2.368 (−0,8 %) / 2.368 (−0,8 %) / 2.386 | 118,4 (−0,4 %) / 118,4 (−0,4 %) / 118,8 | 1.359 (−0,05 %) / 1.359 (−0,05 %) / 1.360 | 875 (0,0 %) / 875 (0,0 %) / 875 | 3,492 (0,0 %) / 3,492 (0,0 %) / 3,492 |

Lectura del cuadre 2T26:
- **Ningún banco cuadra el activo dentro de 0,5 % con el líder individual** (Caixa, el mejor, queda −0,8 %). En PL, cartera y depósitos solo Caixa cuadra dentro de 0,5 %; BB queda a 0,1 % en PL y a 6–8 % en cartera y depósitos.
- **Lucro**: el líder individual sí queda cerca (0 a −8 %), porque el resultado de las filiales entra por método de participación. Sirve como aproximación de lucro, no como cifra.
- **Cartera**: BB −6 %, Bradesco −23 %, Santander −41 %, BTG −85 %; las holdings (Itaú) no tienen la cartera.
- **Suma de miembros**: cuadra el activo de Santander y BTG, pero infla patrimonio y lucro (Itaú y BTG, +39 % a +71 %) por doble conteo.
- Por eso el criterio de la tarea (cuadre de 2T26 dentro de 0,5 % y 1 %) **no se puede cumplir sin el 4060 de 202606**.

## Lo dudoso o no verificado

1. **4060 de abr–jun 2026**: 404 en la ruta individual para los seis líderes, aunque el masivo trae esos meses. Hay que volver a probar; sin esto, 2T26 no se valida a nivel conglomerado.
2. **Provisiones de crédito en 2025 (plan nuevo)**: en 3T25, BB registra un gasto de ~93 mil millones (8199200) y una reversión de ~104 mil millones (7199200), que se compensan; el neto acumulado a septiembre (−17,9) no calza con el panel (−47,9), aunque el lucro del trimestre sí (−2,5 %). El neto de 2025 completo (−37,0) tampoco calza con el panel (−66,9). No investigué la causa; puede ser una reclasificación del banco o una mala lectura de las cuentas. Antes de usarla, revisar contra el 4060.
3. **Provisión de crédito en 2024 (plan viejo)**: la cuenta 8180000 (−27,2 en 2024) no calza con el panel de 2024 (−42,1 del conglomerado), pero la comparación es individual contra conglomerado y no la separé. No verificado.
4. **Personal en 1S26 (BB)**: 13,4 de las cuatro líneas contra 14,5 del panel. No se buscaron líneas adicionales.
5. **Diferencia 4016 contra 4010**: en BB jun-26, PL del 4016 (181,33) contra PL del 4010 más resultado (181,63), 0,3 mil millones. El pasivo cambia 0,3 entre los dos documentos; no lo expliqué.
6. **Cuentas de cambio**: 7130000 y 8140000 desaparecen en 202501 sin equivalente identificado. No se buscó en el nivel 4–5.
7. **Nombres y significados cambiados** en 16 de 119 bases comunes (§5); el mapeo debe ser por concepto.
8. **Norma**: no abrí la Res. CMN 4.966 ni la IN BCB 753 (lo que dije en el informe previo sigue sin verificar). Lo que sí está verificado es el cambio de estructura observado en el archivo, en 202501.
9. **Reproducibilidad**: el masivo de 202603 y 202606 tiene fecha de generación de hoy (9-nov-2026); el individual de 202603 tiene la de 31-may. El masivo se regenera sin aviso.
10. **Calendario**: el CKAN cita el Comunicado 44.132/2025 con fechas de publicación por trimestre; no leí el comunicado.
11. **Membresía de conglomerados**: usé el cadastro 2T26 para los dos trimestres. Un miembro que entró o salió en el año cambia la suma; no lo medí.
12. **Cobertura de los 34 bancos**: solo verifiqué seis conglomerados en el 4060 y para 28 falta el mapeo de cuentas y el cuadre.

## Cómo reproducir

Las descargas y los parquet derivados están en la carpeta de scratch. Los scripts leen rutas relativas, así que se corren desde esa carpeta.

```powershell
Set-Location C:\Users\pablo\AppData\Local\Temp\claude\65f10cd6064c8ce9\f3f1e501-89ac-4345-a73f-8313a4d9ad80\scratchpad\balancetes_sondeo
C:\dev\bz_banks\.venv\Scripts\python.exe -X utf8 -I cargar.py raw\bancos_202603\202603BANCOS.csv.zip parq\bancos_202603.parquet
C:\dev\bz_banks\.venv\Scripts\python.exe -X utf8 -I ident8.py parq\202603-4060-00000000.parquet
C:\dev\bz_banks\.venv\Scripts\python.exe -X utf8 -I cuadre.py cong4060 202603 cad202603.parquet
C:\dev\bz_banks\.venv\Scripts\python.exe -X utf8 -I grupos.py
C:\dev\bz_banks\.venv\Scripts\python.exe -X utf8 -I acumulados.py
C:\dev\bz_banks\.venv\Scripts\python.exe -X utf8 -I acum_vs_panel.py
C:\dev\bz_banks\.venv\Scripts\python.exe -X utf8 -I bb_cartera2.py
C:\dev\bz_banks\.venv\Scripts\python.exe -X utf8 -I candidatos.py
```

Nota: `cuadre.py cong4060` lee los parquet de `parq\` con el patrón `AAAAMM-4060-<CNPJ8>.parquet`, que se generó con `cargar.py` a partir de los ZIP individuales. `grupos.py` lee `cad202606.parquet`, copia de `datos/crudo/bcb_ifdata/cadastro/actual/cadastro_202606.parquet`, y los masivos en `parq\masivo\`. Las rutas a `datos/gold/bk_panel.parquet` son absolutas dentro del repo y solo se leen.
