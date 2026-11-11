# Frente 13 · Hojas de empresas «MPME» y «Grandes»: datos que faltan, modalidades PJ en el SCR, pipeline y verificaciones

Estado al 10-nov-2026: **en curso**. A y C hechas; B con el sondeo de costo entregado y a la espera del visto bueno
de Pablo; D informada en `borradores/empresas_verificaciones.md`, con decisiones pendientes. Encargo pensado para otra
sesión u otra LLM sin contexto previo.
Leer antes `CLAUDE.md`, `tareas/README.md` y `tareas/12_hoja_tarjeta.md` (mismas fórmulas de aportes y efectos).

## Contexto
- Pablo aprobó el 10-nov separar empresas en dos hojas del canvas de rediseño: `Mpme.dc.html` (micro, pequeña y
  mediana) y `Grandes.dc.html`. Las dos están construidas con un borrador:
  `tareas/borradores/_salida/extraer_empresas.py mpme|grandes` (fuera de git) → `mpme.json` y `grandes.json`.
- Fuentes del borrador: crudo SGS, cubo SCR por producto (cliente PJ: porte, sector CNAE, tipo de institución) y
  `datos/gold/bk_ref.parquet` (REF del BCB: gráficos 1.2.2.1, 1.2.2.2, 1.2.2.7 a 1.2.2.10).

## Estructura aprobada
| Sección | MPME | Grandes |
|---|---|---|
| 1 Volumen | Saldo a/a (SGS 27701 y portes del SCR); peso de cada porte | Saldo a/a (SGS 27702) contra empresas total; peso de grandes en empresas |
| 2 Precio | Tasa de empresas total y libre contra Selic; spread e ICC (el SGS no abre por porte) | Igual |
| 3 Calidad | Mora > 90 MPME (SGS 27703) y por porte; atraso 15–90 por porte | Mora > 90 (SGS 27704) contra empresas total; atraso 15–90 por sector |
| 4 Qué movió la mora | Efecto tasa, mezcla de porte, mezcla de sectores (celdas porte × sector) | Efecto tasa, mezcla de sectores, mezcla de instituciones |
| 5 | Sector: aportes al crecimiento y a la mora | Sector: ídem |
| 6 | Porte: aportes | Emisor: aportes por tipo de institución |
| 7 | Emisor: aportes | Riesgo prospectivo (REF): activos problemáticos y PD por porte |
| 8 | Riesgo prospectivo (REF) | Crédito amplio (REF): banca, mercado de capitales y externo; mercado de capitales por instrumento |
| 9 | Ticket por porte; operaciones a/a | Ticket por sector; operaciones, ticket y saldo a/a |

## Parte A · Datos SGS que faltan (bajar desde el equipo de Pablo)
- `20715` tasa de nuevas operaciones a empresas (total); `20718` ídem recursos libres;
- `20784` spread de empresas; `25352` ICC de empresas;
- `27706` y `27707` cartera en riesgo E–H por porte (MPME y grandes).
Revalidar `27701`–`27704`, `20540`, `21083`, `20632`, que están en el crudo, y llevarlos a `sgs.CODIGOS` y al catálogo
(`herramientas/validar_sgs.py --escribir`; `tests/test_sgs_catalogo.py` debe pasar). Buscar además en el catálogo del
repo macro (`Dashboard/definiciones/bcb_sgs__series/*.json`) las series de empresas por modalidad (capital de giro,
descuento de cuentas por cobrar, cuenta garantizada, comercio exterior, inversión) con saldo, concesiones, tasa y mora.

### Resultado de la Parte A (10-nov, hecha)
- En `sgs.CODIGOS`, en el catálogo (188 series, validado contra el SGS el 10-nov; ningún nombre existente cambió) y en
  el crudo `bancos_sistema` hasta sep-26: las del encargo (20715, 20718, 20784, 25352, 27701–27707, 20540, 21083,
  20632; 21004 ya estaba como `atraso15_90_pj`) y 66 nuevas.
- **Sucesoras de E–H:** 27706/27707 terminan en dic-24. Desde ene-25 el SGS publica el % del saldo de mayor riesgo de
  la Res. 4.966: `riesgo_4966_pj` 29581, `riesgo_4966_mpme` 29582 y `riesgo_4966_grande` 29583. No empalman.
- **Modalidades PJ del SGS** (saldo, concesiones del mes, tasa y mora > 90; claves `credito_pj_*`, `conc_pj_*`,
  `tasa_pj_*`, `mora90_pj_*`):

  | Modalidad | Saldo | Concesiones | Tasa | Mora > 90 |
  |---|---|---|---|---|
  | Capital de giro total | 20550 | 20642 | 20725 | 21093 |
  | Descuento de duplicatas y recebíveis | 20544 | 20636 | 20719 | 21087 |
  | Anticipo de facturas de tarjeta | 20546 | 20638 | 20721 | 21089 |
  | Cuenta garantizada | 20551 | 20643 | 20726 | 21094 |
  | Cheque especial | 20552 | 20644 | 20727 | 21095 |
  | Tarjeta total | 20564 | 20656 | 22021 | 21106 |
  | ACC | 20565 | 20657 | 20736 | 21107 |
  | Financiación de exportaciones | 20567 | 20659 | 20738 | 21109 |
  | Financiación de importaciones | 20566 | 20658 | 20737 | 21108 |
  | Repasse externo | 20568 | 20660 | 20739 | 21110 |
  | Adquisición de bienes total | 20555 | 20647 | 20730 | 21098 |
  | Otros créditos libres | 20569 | 20661 | — | 21111 |
  | Direccionados total | 20594 | 20686 | 20757 | 21133 |
  | BNDES inversión | 20602 | 20694 | 20765 | 21141 |
  | BNDES total | 20604 | 20696 | 20767 | 21143 |
  | Rural total | 20597 | 20689 | 20760 | 21136 |
  | Inmobiliario total | 20600 | 20692 | 20763 | 21139 |
  | Programas MPME (Pronampe, PEAC; desde nov-25) | 29966 | 29969 | 29975 | 29993 |

  No se agregaron (existen en el SGS): descuento de cheques (20545), leasing (20558), vendor (20559), compror (20560),
  capital de giro por plazo (20547–20549), plazos, atrasos 15–90 y costo del stock por modalidad.
- `tests/test_sgs_catalogo.py`: 2 verdes.

## Parte B · Modalidades PJ en el SCR (trabajo pesado)
El cubo `datos/intermedio/scr_productos/e82fb46f9a/` se armó para personas: en empresas, R$ 2,4 de 3,0 billones caen en
«Otros». Rehacer la agregación desde el crudo del SCR (hoy en el repo macro, ~5 GB) con un mapa de modalidades PJ
(`modalidade`/`submodalidade` del SCR → capital de giro, descuento, cuenta garantizada, comercio exterior, financiamiento
de inversión, rural, inmobiliario, otros). Medir antes el costo (tiempo y disco) y mostrarlo a Pablo. Con eso se agrega
la sección «Producto» a las dos hojas.

### Sondeo de costo (10-nov). Falta el visto bueno de Pablo para construir
- **Crudo:** está en este repo, no en el macro: `datos/crudo/bcb_scr/scrdata/actual/`, 15 ZIP (2012–2026, 2,0 GB
  comprimidos, ~14 GB de CSV). No hay que bajar nada. **Disco C: 15 GB libres (97 % usado).**
- **Tiempo:** agregar un mes con modalidad PJ (sep-26, 314 mil filas del CSV) toma 2,8 s; el agregado actual del cubo
  toma 3,2 s. De ene-18 a sep-26 (105 meses): ~5 min. Desde 2012: ~8–9 min. Después, incremental (un mes).
- **Disco:** ~3.300 filas y 133 KB de parquet por mes (segmento × porte × CNAE × modalidad PJ): ~14 MB desde 2018.
- **Propuesta:** un cubo aparte, solo PJ (`datos/intermedio/scr_empresas/<versión>/`, con el mismo esquema de versión
  que `scr_productos`). Agregar la dimensión al cubo actual invalida su caché y lo agranda para PF sin ganancia.
- **Mapa propuesto** (`modalidade`/`submodalidade` del SCR; sep-26, R$ mil millones, de 2.970 de PJ):

  | Modalidad | Regla | Saldo | % | Mora > 90 | MPME | Grande |
  |---|---|---|---|---|---|---|
  | Capital de giro | «capital de giro» (hasta y más de 365 días, rotativo) | 801,6 | 27,0 | 5,55 % | 598,5 | 178,7 |
  | Inversión y proyectos | «financiamento de projeto», infraestructura, «aquisição de bens – outros bens», arrendamiento financiero no inmobiliario ni de vehículos, interveniência | 645,0 | 21,7 | 0,67 % | 148,5 | 465,3 |
  | Comercio exterior | financiamientos a la exportación e importación, ACC, cambiais entregues | 316,4 | 10,7 | 0,53 % | 58,0 | 248,9 |
  | Descuento y recebíveis | «direitos creditórios descontados», recebíveis adquiridos, anticipo de factura de tarjeta | 196,1 | 6,6 | 0,88 % | 51,6 | 117,1 |
  | Rural | como hoy | 169,5 | 5,7 | 0,95 % | 25,0 | 142,7 |
  | Vehículos | aquisição de bens – veículos y arrendamiento de vehículos | 164,6 | 5,5 | 4,87 % | 140,2 | 20,1 |
  | Inmobiliario | como hoy | 92,2 | 3,1 | 1,39 % | 54,4 | 30,2 |
  | Cuenta garantizada y sobregiro | conta garantida, cheque especial, adiantamentos a depositantes | 66,6 | 2,2 | 10,44 % | 57,2 | 6,8 |
  | Tarjeta | como hoy (con interés y contado) | 64,5 | 2,2 | 7,46 % | 52,3 | 9,9 |
  | Otros | «outros empréstimos» (227,6), «outros financiamentos» (173,0), compror, vendor, microcrédito, avales honrados… | 453,4 | 15,3 | 3,84 % | 111,1 | 329,9 |

  Hoy «Otros» del cubo es ~2.440 de los 2.970 de PJ; con el mapa baja a 453 (15 %). Ese resto no se puede abrir más
  con el SCR. Límite: el SCR no separa libres de direccionados. El capital de giro del SCR (802) incluye giro del BNDES
  y otros direccionados, así que no se compara con la 20550 del SGS (484, libres).
- **Error del mapa vigente encontrado en el sondeo:** «Arrendamento financeiro exceto veículos automotores e imóveis»
  contiene «veículos automotores» y cae en Vehículos (R$ 21,3 mil millones en PJ, 0,45 en PF). Ver
  `borradores/empresas_verificaciones.md`.

## Parte C · Pipeline
Gold `bk_empresas_m` (SGS) y `bk_empresas_scr_m` (SCR, formato largo `fecha × hoja × dimension × segmento × medida`),
con las fórmulas de `tareas/12_hoja_tarjeta.md` parte B (aportes, efecto tasa y mezcla, tres partes con doble orden).
Tests: aportes y efectos suman el total; pesos suman 100 %.

### Resultado de la Parte C (10-nov, hecha)
- `pipeline/preparar_gold_bancos_empresas.py` publica `bk_empresas_m` (SGS, 31,4 mil filas: empresas total, libres y
  direccionados, MPME, grandes, 17 modalidades, Selic efectiva del mes) y `bk_empresas_scr_m` (SCR desde ene-18, 218
  mil filas; hojas `mpme` y `grandes`). Reutiliza `descomponer_tasa`, `_celdas` y `_efectos` del frente 12. Paso
  `empresas` en `actualizar.py` (después de `producto_pf`) y contrato en `definiciones/contrato_gold.json`. Unidades:
  razones y efectos en fracción.
- La descomposición de la tasa media de las modalidades libres pondera por **saldo**, no por concesiones. Con
  concesiones, el cheque especial lleva la media a 52,8 % contra 24,4 % de la 20718; con saldo, la diferencia queda
  entre −0,4 y +2,1 pp en toda la historia.
- `tests/test_empresas.py`: 7 pruebas (unitarias con cubo y SGS sintéticos e integración): aportes = total, efecto tasa
  + mezcla = total, tres partes = variación en los dos órdenes, pesos = 1 por dimensión, ticket total = cart_ops / ops,
  pesos MPME + grandes = 1, descomposición SGS = Δ tasa media, libres + direccionados = total, E–H hasta dic-24 y 4.966
  desde ene-25.
- **Falta:** correr `manifiesto_gold.py` y `generar_spec.py` (no los corrí: hay otras sesiones en paralelo). Hasta
  entonces `test_gold_reales_sin_errores` falla porque `bk_empresas_*` no tiene fila en `bk_manifiesto` (lo mismo
  pasa con fondeo y pyb).
- `extraer_empresas.py` (fuera de git) lee solo de gold (`bk_empresas_m`, `bk_empresas_scr_m`, `bk_ref` y
  `bk_cartera_mix7`). Contra los JSON previos, sin diferencias de más de 0,01, salvo:
  - P2: tasa total, tasa libre, spread e ICC con dato (antes «en preparación»). La referencia pasa a la Selic efectiva
    del mes (4189, criterio del frente 12).
  - P3: el bloque de riesgo muestra E–H hasta dic-24 y la 4.966 desde ene-25 (MPME o grandes, y PJ total), con nota.
  - P1: el a/a del SGS tiene dato en 2014 (antes vacío por calcularse sobre la serie recortada).
  - P4: sin dato en 2018 (antes 0 por sumar vacíos).
  - Notas del desfase del REF en sus secciones; el bloque REF de P1 dice «hasta jun-26».

## Parte D · Verificaciones abiertas
1. **Micro:** el SCR muestra saldo −17,6 % a/a y número de operaciones +87,5 % a/a a sep-26. Probable reclasificación
   de porte o entrada masiva de operaciones chicas (instituciones de pago, microcrédito). Cuantificar y explicar.
2. **MPME SGS contra SCR:** el SGS da +5,3 % a/a y el SCR (micro + pequeña + mediana) +1,8 %. Explicar la diferencia
   (definición de porte, «sin dato» excluido, cobertura).
3. **«Servicios financieros» en MPME** resta −1,9 pp al crecimiento: revisar si son entidades financieras chicas
   registradas como PJ no financiera o un cambio de CNAE.
4. **Ticket de grandes por sector:** «Administración pública» y «Electricidad y gas» tienen tickets de decenas de
   millones; confirmar que no sea un error de unidad.
5. **REF:** las series son de la última edición (oct-26) y llegan a jun-26; dejar explícito en la hoja el desfase.

### Resultado de la Parte D (10-nov): informe en `borradores/empresas_verificaciones.md`
1. Micro: el −17,6 % del saldo es un bloque de R$ 38–47 mil millones de «Servicios financieros» que entra en micro en
   sep-25 y sale a pequeña en jul-26. Sin ese sector, micro crece +11,7 %. El +87,5 % de las operaciones es un cambio
   de porte (pequeña → micro) de ~3,8 millones de operaciones de tarjeta PJ de financieras e instituciones de pago en
   nov-25. Sin esas tres instituciones (con fintechs), +0,9 %.
2. SGS +5,35 % contra SCR +1,78 %: el SCR incluye el sector financiero (el SGS es de sociedades no financieras) y deja
   fuera «Sin dato». Sin servicios financieros y con «Sin dato», el SCR da +5,17 %.
3. «Servicios financieros» en MPME: el mismo bloque del punto 1, de pocos deudores, con saltos de un mes de porte y de
   tipo de institución. No son entidades financieras chicas.
4. Tickets de Administración pública (R$ 65 millones) y Electricidad y gas (R$ 10 millones): no es un error de unidad.
   Son préstamos a entes públicos y project finance (BNDES), medidos sobre el 68–69 % del saldo; en extractivas la
   cobertura es 23 %.
5. REF: edición oct-26, datos hasta jun-26 (3 meses de desfase). Nota agregada en la hoja.

**Decisiones de Pablo:** tratamiento de «Servicios financieros» (sacarlo o segmento aparte) y bandas (sep-25,
mar–abr-26, jul-26, nov-25); SCR sin servicios financieros en P1 de MPME; ticket en escala logarítmica y con umbral de
cobertura; corregir el error del arrendamiento en `scr_productos.json` (reprocesa el cubo); visto bueno de la parte B.

## Terminado cuando
- A: códigos en `sgs.CODIGOS`, catálogo y crudo; lista de modalidades PJ del SGS identificadas.
- B: sondeo de costo entregado a Pablo; con su visto bueno, cubo PJ por modalidad.
- C: gold y tests.
- D: informe corto en `tareas/borradores/empresas_verificaciones.md`.
- Nada se commitea sin pedirlo a Pablo.

## Decisiones de Pablo del 10-nov (tarde) y pendientes de pipeline
Aplicado en la hoja (borrador `extraer_empresas.py`; copia previa en `extraer_empresas_previo_sf.py`):
- MPME sin «Servicios financieros» (el SCR se recalcula en memoria con `construir_hoja_scr` sobre el cubo sin ese
  sector); línea gris «Micro con servicios financieros (SCR publicado)» en P1 y nota sobre el porte «Sin dato».
- Grandes: «Servicios financieros» en gris y punteado, y líneas «sin servicios financieros» en P5.
- Bandas sep-25, mar-26, jul-26 (saldo) y nov-25 (operaciones) en P1, P3, P5, P6 y P9; nota de operaciones en P9 de MPME.
- P9 de Grandes en R$ millones con escala logarítmica (`Grafico.dc.html` acepta `log`) y sectores con cobertura < 50 % en gris.
Para hacer en pipeline:
1. Llevar la exclusión de «Servicios financieros» al gold: `bk_empresas_scr_m` con hoja `mpme` sin el sector y una
   variante `grandes_sin_sf` (o columna), para que el borrador deje de recalcular.
2. Corregir el mapa de `definiciones/scr_productos.json`: «Arrendamento financeiro exceto veículos automotores e
   imóveis» cae en Vehículos por coincidencia de texto (R$ 21,3 mil millones PJ y 0,45 PF a sep-26). Reprocesar el
   cubo y verificar que Personas y Mora (`bk_scr_tablas`, `bk_scr_series`) cambien solo en Vehículos y Otros.
3. Cubo de modalidades PJ (Parte B): Pablo aprueba el costo estimado en el sondeo; ejecutarlo.

## Decisiones de Pablo (11-nov, desde el celular)
- Parte B: **autorizado** el cubo PJ por modalidad (~9 min, ~14 MB).
- «Servicios financieros»: **fuera de MPME**; en Grandes, **segmento aparte en gris** con línea «Total sin servicios
  financieros».
- `scr_productos.json`: **corregir** «Arrendamento financeiro exceto veículos» (sale de Vehículos) y reprocesar el cubo,
  Personas y Mora.
- Aplicar: bandas en sep-25, mar–abr-26 y jul-26 (saldo) y nov-25 (operaciones); ticket de Grandes en escala
  logarítmica; tasa libre ponderada por saldo.
