# Capital mensual: backtest de B y factibilidad de A — informe del 9-nov-2026

**Recomendación: ninguna de las dos por ahora; no publicar B. Su error típico (mediana del error absoluto) es 0,49 pp en el panel total y 0,66 pp por banco, contra el umbral de 0,3 pp de la tarea.**

Frente 10 (`tareas/10_capital_mensual.md`). Solo escribe este informe; no se tocó pipeline, definiciones, tests, gold, sitio ni `tareas/README.md`. Sin commit ni push.

> **Corregido el 9-nov por el sondeo del frente 11** (`balancetes_sondeo.md`): el 4060 sí existe, nombrado con el CNPJ8 del líder del conglomerado, y calza con IF.Data en 1T26. En 202606 el bloque A es el 4010 y el bloque B es el 4016 (cierre semestral), no el individual. La identidad contable cierra si se incluyen las cuentas 7 y 8. Las afirmaciones contrarias de §1, §3.3 y §4 quedan reemplazadas. Frente 10 cerrado: B descartada, A pasa al frente 11.

## 1. Resumen

- **B no pasa en ningún nivel por el criterio de la tarea.** Ni el panel total (0,49 pp), ni los grupos (0,53 pp), ni los bancos (0,66 pp). Un solo grupo (Medianos y nicho, 0,29 pp, 37 trimestres) queda bajo 0,3 pp, por 0,015 pp y sin margen.
- **El límite no es el crédito.** Aun con la RWA real de q+1 (variante D), el error típico es 0,36 pp en el panel total y 0,51 pp por banco. El error viene de lo que B no observa en el trimestre: la utilidad retenida, dividendos, emisiones y otros movimientos del capital principal (CP).
- **A (balancetes) no es evidencia para elegir ahora.** Los balancetes individuales (4010) sí se publican y se descargan. El documento 4060 del conglomerado no lo encontré en los datos abiertos del BCB. Además el calce contra IF.Data quedó parcial y con una ambigüedad sin resolver (sección 4).

## 2. Parte 1 — Backtest de B

### 2.1 Método

- Estimación de cada par de trimestres consecutivos: `holgura_est(q+1) = CP(q) / [RWA(q) × g] − requerimiento(q)`, en pp, con `g` = crecimiento del saldo de crédito de q a q+1.
- Saldo de crédito: SGS 20539 (crédito total del SFN, R$ mm), leído mensual en el mes de cierre de cada trimestre. Fuente: `datos/crudo/bcb_sgs/bancos_sistema/actual/serie_20539.json`. Serie disponible hasta sep-26.
- Comparado con `holgura_cp_pp` publicada en q+1. **Unidad:** esa columna está guardada como fracción (0,0756 = 7,56 pp); se verificó que `holgura = indice_cp − requerimiento_cp` sin diferencia en todas las filas. El informe la lleva a pp (×100). Así, el umbral de 0,3 pp equivale a 0,003 en la columna.
- **Error = estimado − publicado** (pp). Sesgo positivo = el método sobreestima la holgura.
- **Error típico** = mediana del error absoluto (se usa esta medida porque la tarea la pide así; la media absoluta y la máxima también se reportan).
- **Muestra limpia:** se excluyen pares con `alerta` en q o q+1 (Agibank 2015-T2 a 2016-T2; PagSeguro 2025-T2 y 2025-T4); pares que cruzan el cambio de fuente del requerimiento (2022-T4 → 2023-T1); trimestres con cambio de definición de RWA (2023-T3 por CVA y 2024-T4 por DRC); pares que cruzan la frontera COSIF 2025-T1; y, en grupos, pares donde cambia `n_bancos` (26 → 31 en 2023-T3).
- Variante de utilidad: se suma `lucro_ttm / 4` (run-rate del último año, sin mirar hacia adelante) al CP. Es una cota de lo que aporta el resultado, no un dato del trimestre.

### 2.2 Tabla 1. Bancos individuales (muestra limpia, 1.050–1.051 pares banco × trimestre)

Errores en pp. Máximo: banco y trimestre.

| Variante | n | Sesgo | Mediana \|e\| | Media \|e\| | % con \|e\| ≤ 0,3 | Máx \|e\| (banco, trimestre) |
|---|---:|---:|---:|---:|---:|---|
| **B**: crédito del sistema (SGS), RWA total | 1.051 | −0,13 | **0,66** | 1,11 | 25,6 % | 31,1 (Inter, 2021-T2→T3) |
| B + utilidad run-rate al 30 % | 1.051 | +0,01 | 0,63 | 1,10 | 27,5 % | 31,1 (Inter) |
| B + utilidad run-rate al 100 % | 1.051 | +0,33 | 0,70 | 1,22 | 24,8 % | 31,0 (Inter) |
| B con RWA de crédito escalada y el resto fijo | 1.051 | +0,34 | 0,65 | 1,47 | 25,9 % | 31,0 (Inter) |
| C: crédito propio del banco (oráculo, bk_panel) | 1.050 | −0,39 | 0,66 | 1,28 | 22,7 % | 67,7 (XP, 2017-T3→T4) |
| D: RWA real de q+1 (sin error de densidad) | 1.051 | −0,32 | 0,51 | 0,97 | 30,4 % | 33,0 (Inter) |
| D + requerimiento real de q+1 | 1.051 | −0,39 | 0,50 | 0,92 | 30,4 % | 33,0 (Inter) |

Lectura:
- Mediana de B: 0,66 pp. Un cuarto de las estimaciones cae dentro de 0,3 pp.
- **Densidad (B frente a D):** la mediana de B − D es 0,36 pp (cuantil 90: 1,42 pp). Suponer que la RWA crece con el crédito del sistema agrega error, pero no es la parte principal.
- **Crédito del banco (C) no mejora a B.** Su mediana es igual (0,66 pp) y su media es peor. La razón es que el crecimiento del crédito propio y el de la RWA se separan tanto como el del sistema: la mediana de |g_RWA − g_banco| es 2,58 pp y la de |g_RWA − g_sistema| es 3,05 pp, por trimestre. Además `bk_panel` tiene quiebres (sección 2.5).
- **Utilidad:** sumar el 100 % del run-rate empeora el sesgo (+0,33). Con el 30 % el sesgo queda en cero, pero la mediana solo baja de 0,66 a 0,63. La utilidad no explica lo que falta.
- La cota de retención que mide el dato es ~0,27–0,35 de la utilidad trimestral (ver 2.4).

### 2.3 Tabla 2. Panel total y grupos (muestra limpia, sin repetir «Todos los grupos» en cada óptica)

| Nivel | n | Sesgo | Mediana \|e\| B | Mediana \|e\| D | % con \|e\| ≤ 0,3 (B) | Máx \|e\| B (grupo, trimestre) |
|---|---:|---:|---:|---:|---:|---|
| **Panel total (26–34 bancos)** | 32 | −0,25 | **0,49** | 0,36 | 34,4 % | 2,1 (Total panel, 2020-T1→T2) |
| Grupos (muestra limpia, 496 pares grupo × trimestre, sin el panel total) | 496 | −0,21 | 0,53 | 0,46 | 28,8 % | 7,9 (Digitales, 2021-T2→T3) |

Por grupo (B; mediana \|e\| y sesgo, muestra limpia):

| Grupo | n | Sesgo | Mediana \|e\| B | Mediana \|e\| D |
|---|---:|---:|---:|---:|
| Medianos y nicho | 37 | −0,12 | 0,29 | 0,29 |
| S3 | 34 | −0,08 | 0,37 | 0,41 |
| Privado nacional | 36 | −0,18 | 0,41 | 0,44 |
| Grandes (= S1) | 40 | −0,16 | 0,41 | 0,37 |
| Tradicionales | 37 | −0,22 | 0,48 | 0,34 |
| Privado extranjero | 39 | −0,07 | 0,53 | 0,38 |
| Público | 37 | −0,36 | 0,59 | 0,43 |
| S2 | 38 | −0,64 | 0,65 | 0,73 |
| Desarrollo | 40 | −0,85 | 1,05 | 1,06 |
| Fintechs (= Digitales) | 35 | +0,24 | 1,10 | 0,78 |
| Digitales | 35 | +0,21 | 1,18 | 0,78 |
| Pagos | 8 | +0,59 | 1,28 | 1,15 |
| S4 | 8 | −1,13 | 2,40 | 2,64 |

Lectura:
- **Nivel en que B pasa:** ninguno con criterio robusto. El panel total, el agregado de grupos y 12 de 13 grupos superan 0,3 pp. Medianos y nicho pasa por 0,015 pp, con 37 trimestres. Los grupos pequeños (Pagos, S4, n = 8) tienen una mediana que no sirve de criterio.
- El sesgo cambia de signo según el grupo (Público y S2 subestiman; Fintechs y Digitales sobreestiman). Un ajuste único no corrige esto.

### 2.4 Retención de utilidad (dato, no supuesto)

Regresión sin constante de ΔCP/CP (trimestre siguiente) sobre (lucro_ttm/4)/CP, bancos con CP mediano < 25 %:

- Muestra: 1.165 pares. Pendiente 0,27. Mediana de ΔCP/CP: 2,4 % por trimestre. Mediana de (lucro_ttm/4)/CP: 4,0 % por trimestre.
- Sin emisiones (|ΔCP/CP| < 15 %): 1.070 pares, pendiente 0,35.

Es decir, cerca de un tercio del run-rate llega al CP. El resto se va en dividendos y JCP, y se mezcla con OCI y ajustes prudenciales. Esto es la razón de la variante con 30 %, y explica por qué esa variante deja el sesgo en cero pero no reduce la mediana.

### 2.5 Quiebres y limitaciones

- **Frontera COSIF 2025-T1:** en `bk_panel`, el crédito total del panel cae de 6,96 billones (2024-T4) a 6,21 (2025-T1), −11 %, mientras el SGS no tiene ese salto. Por eso los pares que cruzan 2025-T1 quedan fuera de la muestra limpia del oráculo. B usa SGS y no depende de bk_panel; la muestra con esos pares incluidos da mediana 0,65 pp por banco (muestra total, sin excluir por frontera: ver tabla de 2.2 «todo»).
- **Requerimiento:** cambia de fuente en 2023-T1 (normas → ACP del BCB). Se excluye el par 2022-T4 → 2023-T1. Usar el requerimiento real de q+1 (D + req.) cambia la mediana solo en 0,01 pp.
- **Outliers:** los errores máximos vienen de emisiones de capital y de bancos con RWA atípica (Inter, C6, XP). Ejemplo verificado: Inter pasa de CP 0,92 mil millones (2019-T2) a 2,13 (2019-T3). No se verificó trimestre a trimestre el origen de cada uno de los 31 pp del máximo.
- **Mediana robusta:** excluir bancos con CP mediano > 25 % (PagSeguro, CloudWalk) deja la mediana de B en 0,65 pp.
- **Panel:** 25 bancos en 2015, 34 desde 2024-T4. `bk_capital_grupo` marca 26 → 31 en 2023-T3.

### 2.6 Veredicto de B

**No se publica.** Error típico 0,49 pp en el panel total y 0,66 pp por banco, contra 0,3 pp. Con RWA real (D) el error sigue por encima de 0,3 pp: el problema está en el CP trimestral, no en el crédito. Una versión con utilidad no se justifica: aporta cero sesgo, pero la mediana no baja de 0,6 pp.

## 3. Parte 2 — Factibilidad de A (balancetes)

### 3.1 Qué publica el BCB (verificado)

| Fuente | Qué contiene | Formato | Verificado en |
|---|---|---|---|
| Datos abiertos, conjunto «Balancetes (IFs e Conglomerados)» | Balancete individual (4010) y consolidado financeiro individual (4040, solo hasta 06/2022). No nombra el 4060 | ZIP con CSV | https://dadosabertos.bcb.gov.br/dataset/ifs-balancetes |
| Archivo individual por institución | 4010, un ZIP por CNPJ8 y mes | CSV, 3 líneas de encabezado, separador `;`, coma decimal | `https://www4.bcb.gov.br/fis/cosif/cont/balan/individualizados/202601/4010/202601-4010-00000000.ZIP` (200, 17.010 bytes, última modificación 31-may-2026) |
| Archivo masivo por mes | Todas las instituciones, documento 4010 (el encabezado dice 4010-4016-4020-4026) | ZIP con un CSV de 0,9 a 1,6 MB | `https://www.bcb.gov.br/content/estabilidadefinanceira/cosif/Bancos/202601BANCOS.csv.zip` (200, 902.299 bytes) |

- **Rezago:** la página del conjunto cita el Comunicado 44.132/2025: base enero–marzo se publica el 31 de mayo; abril–junio, el 31 de agosto; julio–septiembre, el 30 de noviembre; octubre–diciembre, el 31 de marzo del año siguiente. Según la misma página, los archivos se generan mensual o trimestralmente según el caso. No abrí el comunicado.
- **Ruta individual para 202603 (200 en HEAD); para 202604, 202605 y 202606 da 404** («Objeto não encontrado»). Esto no prueba que no existan: la ruta puede moverse o el archivo puede publicarse después.
- **Directorio 4060** (`.../individualizados/202601/4060/`): responde 403. No prueba que no exista; es bloqueo de listado.
- **Conglomerado 4060:** no lo encontré en ninguna fuente abierta del BCB que abrí. Una búsqueda devolvió que el 4060 lo remite a Sisbacen el líder del conglomerado (IN BCB 210); esa referencia viene de un sitio de terceros (okai.com.br) y no la verifiqué en el texto oficial. **Esta es la duda central para A:** si el 4060 no es descargable, A no es lo que dice la tarea (patrimonio de conglomerado).
- **Cambio de leiaute:** un resultado de búsqueda (sitio de terceros) menciona la IN BCB 753 del 1-jul-2026 para 4060 y 4066 (bloque de subconglomerado). No abrí la norma. **No verificado.**

### 3.2 Formato del archivo masivo (202601 y 202606, abiertos)

- Encabezado de tres líneas (título, fecha de generación, fuente) y luego `#DATA_BASE;DOCUMENTO;CNPJ;AGENCIA;NOME_INSTITUICAO;COD_CONGL;NOME_CONGL;TAXONOMIA;CONTA;NOME_CONTA;SALDO`.
- Codificación latin-1 (cp1252). Decimal con coma (`2302611833796,09`).
- CONTA de 10 dígitos con dígito verificador (PL = `6000000004`); en el individual, de 8 dígitos (PL = `60000000`).
- `COD_CONGL` y `NOME_CONGL` vacíos en las 49.364 filas de 202601. Ninguna fila es de conglomerado.
- 202601: 171 instituciones; documento 4010 en todas las filas.

### 3.3 Calce del patrimonio líquido contra IF.Data

| Institución | Fuente | PL 2T26 (R$ mil millones) | Diferencia vs IF.Data prudencial |
|---|---|---:|---:|
| Banco do Brasil | IF.Data prudencial (C0080329) | 181,84 | — |
| Banco do Brasil | 4010 individual, bloque B | 181,33 | −0,3 % |
| Banco do Brasil | 4010 individual, bloque A | 175,42 | −3,5 % |
| Caixa | IF.Data prudencial (C0080738) | 118,80 | — |
| Caixa | 4010 individual, bloque B | 118,37 | −0,4 % |
| Caixa | 4010 individual, bloque A | 111,78 | −5,9 % |
| Bradesco | IF.Data prudencial (C0080075) | 185,19 | — |
| Bradesco S.A. | 4010 individual, bloque B | 175,23 | −5,4 % |
| Bradesco S.A. | 4010 individual, bloque A | 163,15 | −11,9 % |
| Santander | IF.Data prudencial (C0080185) | 106,73 | — |
| Santander (Brasil) S.A. | 4010 individual, bloque B | 98,74 | −7,5 % |
| Santander (Brasil) S.A. | 4010 individual, bloque A | 91,35 | −14,4 % |
| Itaú | IF.Data prudencial (C0080099) | 249,77 | — |
| Itaú Unibanco S.A. | 4010 individual, bloque B | 162,86 | −34,8 % |

Hechos:
- **Calce exacto en 202601:** el único bloque de BB en la `BANCOS` de enero (184.442.015.575,70) es igual al individual 4010 de enero. Eso confirma que la `BANCOS` contiene el 4010 individual.
- **En 202606 hay dos bloques por institución** con PL distintos; no lo resolví. Mi lectura es que el bloque B es el individual, porque para BB y Caixa calza a menos de 0,4 %. No es prueba: el individual de 202606 no se encontró en su ruta (404).
- **Bancos de un solo CNPJ (BB, Caixa):** el 4010 individual calza el PL prudencial a 0,4 % en 2T26. Esto sugiere que, para bancos sin subsidiarias en el conglomerado, el balancete sirve.
- **Bancos con varias entidades (Bradesco, Santander, Itaú):** la diferencia (5 a 35 %) es la del conglomerado frente al individual, no un error del archivo. Un calce útil requeriría el 4060 o sumar el perímetro del conglomerado con IF.Data.
- **Calce de la identidad contable:** en las cuentas que miré no cierra Activo = Pasivo + PL en ninguno de los dos bloques de 202606. No lo resolví.

### 3.4 Plan de cuentas (Res. 4.966)

- La tarea dice que la Res. 4.966 cambia el COSIF desde ene-25. **No lo verifiqué en fuente oficial.** En el repo, `pipeline/diccionario_ifdata.py` (línea 377) y `pipeline/periodos.py` (QUIEBRE_2025) hablan de un «nuevo estándar contable COSIF 2025» con renumeración de cuentas, y `spec/08_estado_pendientes_y_riesgos.md` lo documenta como trampa verificada de los datos de IF.Data, no como cita normativa.
- Lo que sí se verificó en los datos: el PL de BB y Caixa calza con IF.Data en 2T26 con el código 6000000004 de la `BANCOS`. No calcé cuentas de la era 2024 para comparar la renumeración.

### 3.5 Costo estimado de `pipeline/balancetes.py` (estimación, no medida)

| Tarea | Horas |
|---|---:|
| Descarga: mes a mes, reintentos, ruta individual y masiva, registro de procedencia, fallback | 6 |
| Parser: encabezado, latin-1, coma decimal, dígito verificador, validación de bloques duplicados | 8 |
| Mapeo de cuentas por época (COSIF 2024 y 2025), PL, Activo, cartera de crédito, resultado del mes | 12–16 |
| Calce contra IF.Data en 5 bancos y en el sistema, con tests | 6–8 |
| Integración: `actualizar.py`, contrato gold, verificador, spec | 4 |
| **Total** | **36–42** |

Esta cifra asume que el 4060 es descargable. Si no lo es, A se limita a bancos individuales y el costo baja, pero la métrica no es la de conglomerado que pide la tarea.

## 4. Lo dudoso

1. **¿Existe el 4060 descargable?** No lo encontré. Es lo que decide A. Hace falta confirmar en el portal de estadísticas del BCB o con el DOU.
2. **Bloques duplicados en 202606:** no sé cuál es el balancete oficial. El calce con BB y Caixa favorece el bloque B, pero no es concluyente.
3. **Res. 4.966 y leiaute IN 753:** no verificados en fuente oficial.
4. **Rutas 404 para 202604–202606 en la ruta individual** pueden ser rezago de publicación, no ausencia. Hay que volver a probar después del 31-ago-2026.
5. **Red:** las descargas de 202603 (BANCOS e individuales) fallaron: el ZIP de 202603 quedó en 31 KB y no es un archivo válido. No se completó el calce de 1T26 (cierre trimestral). Queda pendiente.
6. **Backtest:** B usa un crecimiento de crédito SGS que también incluye cuentas no comparables con la RWA. Las cotas de utilidad (run-rate y 30 %) son ajustes posteriores, no un método de nowcast.

## 5. Cómo reproducir (scripts de análisis en el scratchpad, sin tocar el repo)

```powershell
Set-Location C:\dev\bz_banks
.venv\Scripts\python.exe -X utf8 -I C:\Users\pablo\AppData\Local\Temp\claude\65f10cd6064c8ce9\f3f1e501-89ac-4345-a73f-8313a4d9ad80\scratchpad\capital_mensual\backtest.py
.venv\Scripts\python.exe -X utf8 -I C:\Users\pablo\AppData\Local\Temp\claude\65f10cd6064c8ce9\f3f1e501-89ac-4345-a73f-8313a4d9ad80\scratchpad\capital_mensual\final.py
```

Archivos generados:
- Filas del backtest: `C:\Users\pablo\AppData\Local\Temp\claude\65f10cd6064c8ce9\f3f1e501-89ac-4345-a73f-8313a4d9ad80\scratchpad\capital_mensual\backtest_filas_final.csv`
- Muestra descargada (BANCOS 202601, 202606; individual 4010 de 202601): `C:\Users\pablo\AppData\Local\Temp\claude\65f10cd6064c8ce9\f3f1e501-89ac-4345-a73f-8313a4d9ad80\scratchpad\balancetes_muestra\`
