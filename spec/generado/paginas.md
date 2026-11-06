# Páginas, secciones y tarjetas del sitio

> Generado por `herramientas/generar_spec.py` el 2026-11-06. No editar a mano: se sobrescribe.


Datos en `/data/` (relativo a `sitio/`). Páginas con `oculta: true` no salen en el menú pero se abren por URL.

## B0 · Portada — `/`

Archivo: `sitio/assets/js/paginas/b0.js` · rótulo: SISTEMA BCB · PANEL IF.DATA · usaBanco: False

### 01 Crédito · Mensual · Sistema BCB

Crecimiento a/a de la cartera y contribución de cada componente.

- Selector `vista` (COMPONENTES): Libre · Direccionado / Personas · Empresas; por defecto `fuente`
- Selector `modo` (MEDIDA): Nominal / Real (IPCA); por defecto `nominal`
- Fila 1: `B0-01` (ancho 4/9, alto 420) + `B0-02` (ancho 5/9, alto 420)

### 02 Mora · Mensual · Sistema BCB

Mora mayor a 90 días y su cambio en doce meses.

- Fila 1: `B0-03` (ancho 4/9, alto 420) + `B0-04` (ancho 5/9, alto 420)

### 03 Rentabilidad · Trimestral · Panel IF.Data

ROE del sistema y su exceso sobre la tasa libre de riesgo.

- Fila 1: `B0-05` (ancho 4/9, alto 420) + `B0-06` (ancho 5/9, alto 420)

### 04 Estructura · Trimestral · Panel IF.Data

Cuota de cada banco: diez mayores y el resto.

- Selector `vista` (CUOTA EN): Activos totales / Crédito total / Crédito personas / Crédito empresas / Depósitos totales / Depósitos a la vista / Depósitos de ahorro / Depósitos a plazo; por defecto `Activos totales`
- Fila 1: `B0-07` (ancho 9/9, alto 460)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B0-01` | Crecimiento a/a y contribución | `barras_linea` | `bk_portada_credito` | LISTO |  | BCB, SGS 20539, 20542, 20593, 20541, 20540; deflactor IPCA … |
| `B0-02` | Cartera de crédito | `tabla_estandar` | `bk_portada_tablas` | LISTO |  | BCB, SGS |
| `B0-03` | Mora > 90 días y cambio a/a | `barras_linea` | `bk_portada_mora` | LISTO |  | BCB, SGS 21082; desde 2025 rige la Res. 4.966 |
| `B0-04` | Mora por segmento | `tabla_estandar` | `bk_portada_tablas` | LISTO |  | BCB, SGS 21082, 21084, 21112, 21086 y los que el SGS sirva … |
| `B0-05` | ROE y ROE − CDI | `barras_linea` | `bk_portada_roe` | LISTO |  | BCB, IF.Data (conglomerado prudencial); CDI SGS 4389, prome… |
| `B0-06` | Rentabilidad del panel | `tabla_estandar` | `bk_portada_tablas` | LISTO |  | BCB, IF.Data (conglomerado prudencial) |
| `B0-07` | Cuota por banco | `mapa_cuotas` | `bk_portada_cuotas` | LISTO |  | BCB, IF.Data (conglomerado prudencial); informes de pasivo … |

Notas visibles en las tarjetas:

- `B0-02`: Último: saldo nominal en R$ mil millones. Cambios en %. 3m/3m y 12m/12m: promedio de la ventana contra la anterior. Libre y direccionado llegan con un mes de rezago.
- `B0-04`: Último en %. Cambios en pp. 3m/3m y 12m/12m: promedio de la ventana contra la anterior.
- `B0-06`: Último en % (ROE) y pp (ROE − CDI). Cambios en pp. 4T/4T: promedio de cuatro trimestres contra los cuatro anteriores. El ROE no se publica mensual.

## B1 · Ciclo y condiciones — `/ciclo` (oculta)

Archivo: `sitio/assets/js/paginas/b1.js` · rótulo: 1 · CICLO Y CONDICIONES · usaBanco: False

### 01 Tasa · Mensual · Sistema BCB

¿qué tan restrictiva es la política y qué espera el mercado?

- Fila 1: `B1-01-0` (ancho 5/9, alto 372) + `B1-01-1` (ancho 4/9, alto 372)

### 02 Crédito y economía · Mensual · Sistema BCB

¿el crédito crece más o menos que la economía, y está acelerando?

- Fila 1: `B1-02-0` (ancho 5/9, alto 372) + `B1-02-1` (ancho 4/9, alto 372)

### 03 Hogares · Mensual · Sistema BCB

¿los hogares pueden seguir pagando?

- Fila 1: `B1-03-0` (ancho 5/9, alto 372) + `B1-03-1` (ancho 4/9, alto 372)

### 04 Empresas · Mensual · Sistema BCB y SCR

¿las empresas pueden pagar, y qué tamaño de empresa preocupa?

- Fila 1: `B1-04-0` (ancho 5/9, alto 372) + `B1-04-1` (ancho 4/9, alto 372)
- Fila 2: `B1-04-2` (ancho 9/9, alto 372)

### 05 Desintermediación · Semestral · REF

¿cuánto crédito se va del balance de los bancos al mercado de capitales?

- Fila 1: `B1-05-0` (ancho 5/9, alto 372) + `B1-05-1` (ancho 4/9, alto 372)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B1-01-0` | Selic real ex ante | `linea` |  | LISTO |  | BCB, SGS; BCB, Focus; cálculo propio |
| `B1-01-1` | Trayectoria de la Selic: Focus vs. mercado | `linea` |  | LISTO |  | BCB, Focus; B3 |
| `B1-02-0` | Crédito/PIB y su tendencia | `columnas` |  | LISTO |  | BCB, SGS; IBGE, PNAD Contínua; cálculo propio |
| `B1-02-1` | Impulso de crédito | `columnas` |  | DERIVAR |  | BCB, SGS; cálculo propio |
| `B1-03-0` | Comprometimiento de renta: intereses y amortización | `area_apilada` |  | LISTO |  | BCB, SGS |
| `B1-03-1` | Desempleo y mora PF libre | `linea` |  | LISTO |  | IBGE, PNAD Contínua; BCB, SGS |
| `B1-04-0` | Crédito real a/a por porte | `linea` |  | DERIVAR |  | BCB, SGS; cálculo propio |
| `B1-04-1` | Inadimplencia por porte | `linea` |  | DERIVAR |  | BCB, SGS; BCB, SCR.data; cálculo propio |
| `B1-04-2` | Crédito con garantía pública | `columnas` |  | DERIVAR |  | BNDES (FGI); FGO/Pronampe; cálculo propio |
| `B1-05-0` | Crédito amplio por fuente | `columnas` |  | REF |  | BCB, Relatório de Estabilidade Financeira |
| `B1-05-1` | Mercado de capitales por instrumento | `barras_h` |  | REF |  | BCB, Relatório de Estabilidade Financeira |

## B2 · Estructura y competencia — `/competencia` (oculta)

Archivo: `sitio/assets/js/paginas/b2.js` · rótulo: 2 · ESTRUCTURA Y COMPETENCIA · usaBanco: True

### 01 Concentración · Trimestral · Panel IF.Data

¿el sistema se concentra o se abre?

- Fila 1: `B2-01-0` (ancho 5/9, alto 372) + `B2-01-1` (ancho 4/9, alto 372)

### 02 Cuota por grupo · Trimestral · Panel IF.Data

¿qué tipo de banco gana cuota?

- Fila 1: `B2-02-0` (ancho 5/9, alto 372) + `B2-02-1` (ancho 4/9, alto 372)

### 03 Dónde compiten · Trimestral · Panel IF.Data

¿en qué carteras están ganando los digitales?

- Fila 1: `B2-03-0` (ancho 9/9, alto 520)
- Fila 2: `B2-03-1` (ancho 9/9, alto 372)

### 04 Riesgo según el tipo de institución · Mensual · SCR

¿crecer cuota les está costando mora?

- Fila 1: `B2-04-0` (ancho 5/9, alto 372) + `B2-04-1` (ancho 4/9, alto 372)

### 05 Precio y servicio · Trimestral · Olinda y Sistema BCB

¿compiten en precio o en servicio?

- Fila 1: `B2-05-0` (ancho 4/9, alto 372) + `B2-05-1` (ancho 5/9, alto 372)
- Fila 2: `B2-05-2` (ancho 9/9, alto 372)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B2-01-0` | HHI y cuota top 5 | `linea` |  | DERIVAR |  | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B2-01-1` | Ranking de cuota de crédito con movimiento | `tabla` |  | LISTO | sí | BCB, IF.Data (conglomerado prudencial) |
| `B2-02-0` | Cuota por grupo, 100 % | `area_apilada` |  | LISTO |  | BCB, IF.Data (conglomerado prudencial) |
| `B2-02-1` | Cuota por banco, hace dos años y hoy | `pesas` |  | LISTO | sí | BCB, IF.Data (conglomerado prudencial) |
| `B2-03-0` | Cuota de cada banco en cada modalidad | `heatmap` |  | DERIVAR | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B2-03-1` | Cambio de cuota en 4T por modalidad y grupo | `heatmap` |  | DERIVAR |  | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B2-04-0` | Inadimplencia por tipo de institución | `linea` |  | DERIVAR |  | BCB, SCR.data; cálculo propio |
| `B2-04-1` | Crecimiento vs. mora por grupo | `burbujas_trayectoria` |  | LISTO |  | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B2-05-0` | Reclamos por millón de clientes, último trimestre | `barras_h` |  | DERIVAR | sí | BCB, Olinda |
| `B2-05-1` | Tarifas de un paquete estándar por grupo | `tabla` |  | DERIVAR |  | BCB, Olinda; cálculo propio |
| `B2-05-2` | Pix como % de los pagos minoristas | `linea` |  | DERIVAR |  | BCB, SGS |

## B3 · Crédito — `/credito`

Archivo: `sitio/assets/js/paginas/b3.js` · rótulo: SISTEMA BCB · MENSUAL · usaBanco: False

### 01 Por tipo · Mensual · SGS

Crecimiento a/a del saldo de cada modalidad.

- Selector `grafico` (GRÁFICO): Barras · último / Líneas · historia; por defecto `barras`
- Fila 1: `B3-01` (ancho 4/9, alto 570) + `B3-02` (ancho 5/9, alto 570)

### 02 Qué lo movió · Mensual · SGS

Contribución de cada modalidad al crecimiento del total en el último mes.

- Fila 1: `B3-03` (ancho 4/9, alto 590) + `B3-04` (ancho 5/9, alto 590)

### 03 Crédito nuevo · Mensual · SGS

Concesiones contra stock: si lo que se presta crece más que el saldo, el saldo tiende a acelerar.

- Fila 1: `B3-05` (ancho 4/9, alto 420) + `B3-06` (ancho 5/9, alto 420)

### 04 Ciclo · Trimestral · SGS 20622

Crédito/PIB contra su tendencia: la brecha dice si el crédito está sobre o bajo lo sostenible.

- Fila 1: `B3-07` (ancho 4/9, alto 420) + `B3-08` (ancho 5/9, alto 420)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B3-01` | Crecimiento a/a por tipo | `barras_signo` | `bk_cred_tablas`, `bk_cred_series` | LISTO |  | BCB, SGS; consignado = privado + público + INSS |
| `B3-02` | Cartera por tipo | `tabla_estandar` | `bk_cred_tablas` | LISTO |  | BCB, SGS |
| `B3-03` | Contribución al crecimiento m/m | `barras_signo` | `bk_cred_tablas` | LISTO |  | BCB, SGS; Otros = resto de libre y direccionado |
| `B3-04` | Contribución por tipo | `tabla_estandar` | `bk_cred_tablas` | LISTO |  | BCB, SGS |
| `B3-05` | Concesiones contra saldo, a/a | `barras_linea` | `bk_cred_series` | LISTO |  | BCB, SGS 20631, 20539 |
| `B3-06` | Concesiones y saldo | `tabla_estandar` | `bk_cred_tablas` | LISTO |  | BCB, SGS 20631, 20633, 20632, 20539 |
| `B3-07` | Crédito/PIB, tendencia y brecha | `barras_linea` | `bk_cred_series` | LISTO |  | BCB, SGS 20622; HP unilateral, λ = 400.000 |
| `B3-08` | Ciclo del crédito | `tabla_estandar` | `bk_cred_tablas` | LISTO |  | BCB, SGS |

Notas visibles en las tarjetas:

- `B3-02`: Último: saldo en R$ mil millones. Share: peso en la cartera total. Cambios en %. 3m/3m y 12m/12m: promedio de la ventana contra la anterior.
- `B3-04`: Último: saldo en R$ mil millones. Share: peso en la cartera total. Cambios: contribución al crecimiento del total, en pp; suman el total.
- `B3-06`: Último: flujo del mes (concesiones) o saldo, en R$ mil millones. Cambios en %; 12m/12m de concesiones compara sumas de doce meses.
- `B3-08`: Último en % (crédito/PIB, tendencia) y pp (brecha). Cambios en pp. El BIS mide crédito total al sector privado y su brecha difiere.

## B11 · Personas — `/personas`

Archivo: `sitio/assets/js/paginas/b11.js` · rótulo: SCR.DATA · MENSUAL · usaBanco: False

### 01 Cartera por renta · Mensual · SCR.data

Cuánto crece la cartera en cada tramo de renta del deudor, en salarios mínimos (SM).

- Selector `producto` (PRODUCTO): Tarjeta / Personal / Consignado / Vehículos / Inmobiliario / Rural / Cheque esp. / Total; por defecto `Tarjeta`
- Fila 1: `B11-01` (ancho 4/9, alto 640) + `B11-02` (ancho 5/9, alto 640)

### 02 Exposición a renta baja · Mensual · SCR.data

Qué parte de la cartera está en deudores de hasta 3 SM, en total y por tipo de institución.

- Selector `producto` (PRODUCTO): Tarjeta / Personal / Consignado / Vehículos / Inmobiliario / Rural / Cheque esp. / Total; por defecto `Tarjeta`
- Fila 1: `B11-03` (ancho 4/9, alto 470) + `B11-04` (ancho 5/9, alto 470)

### 03 Mora por renta · Mensual · SCR.data

Mora de más de 90 días en cada tramo, y cuánto crédito tiene cada operación.

- Selector `producto` (PRODUCTO): Tarjeta / Personal / Consignado / Vehículos / Inmobiliario / Rural / Cheque esp. / Total; por defecto `Tarjeta`
- Fila 1: `B11-05` (ancho 4/9, alto 640) + `B11-06` (ancho 5/9, alto 640)

### 04 Mora temprana · Mensual · SCR.data

El atraso de 15 a 90 días se adelanta unos 3 meses a la mora de más de 90.

- Selector `producto` (PRODUCTO): Tarjeta / Personal / Consignado / Vehículos / Inmobiliario / Rural / Cheque esp. / Total; por defecto `Tarjeta`
- Fila 1: `B11-07` (ancho 4/9, alto 640) + `B11-08` (ancho 5/9, alto 640)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B11-01` | Crecimiento a/a de la cartera por tramo | `barras_signo` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data; tramos según la renta declarada del deudor |
| `B11-02` | Cartera por tramo de renta | `tabla_estandar` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data |
| `B11-03` | Mix de la cartera por tramo de renta, % | `barras_linea` | `bk_scr_series` | LISTO |  | BCB, SCR.data; sin «N.D.» ni «sin renta»; jul-25: reclasifi… |
| `B11-04` | Exposición hasta 3 SM por tipo de institución | `tabla_estandar` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data |
| `B11-05` | Mora >90 días por tramo, % | `barras_linea` | `bk_scr_series` | LISTO |  | BCB, SCR.data; carteira_inadimplência / carteira ativa; Res… |
| `B11-06` | Ticket por tramo (saldo por operación) | `tabla_estandar` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data |
| `B11-07` | Atraso de 15 a 90 días por tramo, % | `barras_linea` | `bk_scr_series` | LISTO |  | BCB, SCR.data; vencido de 15 a 90 días / carteira ativa |
| `B11-08` | Mora >90 días por tramo | `tabla_estandar` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data |

Notas visibles en las tarjetas:

- `B11-02`: Último: R$ mil millones. Share: peso del tramo en el producto. Cambios en %. Ago-26: ~R$ 15 mil millones de tarjeta pasan de «más de 20 SM» a «N.D.» por reclasificación de la fuente.
- `B11-04`: Último: % de la cartera del tipo en deudores de hasta 3 SM. Share: peso del tipo en el producto. Cambios en pp. Las fintech grandes aparecen según su licencia (financiera o institución de pago). SCR.data no trae S1–S5.
- `B11-06`: Último: R$ por operación, en celdas con 15 o más operaciones. Cambios en %. En personal, el ticket de los tramos altos se multiplica en 2025 por un cambio de la fuente: su 12m/12m no es comparable.
- `B11-08`: Último: % de la cartera del tramo. Share: peso del tramo en el producto. Cambios en pp; 12m/12m: promedio de 12 meses contra los 12 previos. El SCR incluye todas las instituciones: el nivel difiere de la serie del SGS.

## B4 · Calidad — `/calidad`

Archivo: `sitio/assets/js/paginas/b4.js` · rótulo: 4 · CALIDAD · usaBanco: True

**Franja de indicadores (arriba):** Mora > 90 días · Sistema ← `bk_sistema_q`; Mora > 90 · PF libre ← `bk_sistema_q`; Mora > 90 · PJ libre ← `bk_sistema_q`; NPL ≥ 15 días · Panel ← `optica/panel/bk_grupo`; Costo del riesgo · Panel ← `optica/panel/bk_grupo`

### 01 Sistema · Mensual · Sistema BCB

Mora mayor a 90 días: personas, empresas y total.

- Fila 1: `B4-01-0` (ancho 9/9, alto 320)

### 02 Por grupo y por banco · Trimestral · Panel IF.Data

NPL por grupo y costo del riesgo con cobertura en el grupo del banco activo.

- Fila 1: `B4-03-0` (ancho 5/9, alto 380) + `B4-03-1` (ancho 4/9, alto 380)

### 03 Exposición · Trimestral · Panel IF.Data

Cuánto NPL predice el mix de cartera de cada banco y cuánto tiene.

- Fila 1: `B4-04-0` (ancho 5/9, alto 640) + `B4-04-1` (ancho 4/9, alto 640)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B4-01-0` | Mora > 90 días: PF libre, PJ libre, total | `linea` | `bk_sistema_m` | LISTO |  | BCB, SGS |
| `B4-03-0` | Calidad por grupo | `linea` | `bk_cre_calidad` | LISTO |  | BCB, IF.Data (conglomerado prudencial) |
| `B4-03-1` | Costo del riesgo TTM y cobertura, por banco | `barras_h_doble` | `metrica/costo_riesgo_ttm/bk_panel`, `metrica/cobertura_ecl/bk_panel`, `bk_banco` | LISTO | sí | BCB, IF.Data (conglomerado prudencial) |
| `B4-04-0` | Mora implícita del mix vs. NPL observado | `dispersion` | `bk_exposicion`, `bk_banco` | DERIVAR | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B4-04-1` | Cambio de la mora implícita en 12m, por banco | `barras_h` | `bk_exposicion`, `bk_banco` | DERIVAR |  | BCB, IF.Data (conglomerado prudencial); cálculo propio |

Notas visibles en las tarjetas:

- `B4-01-0`: Desde 2025, con la Res. 4.966 y el cambio de política de baja a pérdida, la mora > 90 días puede no ser comparable con años anteriores.
- `B4-03-0`: Hasta 2024-T3 la medida es la escala E–H; desde 2025-T1 (Res. 4.966) son los activos problemáticos. La línea cambia de definición en 2025-T1. 2024-T4 sin dato en todo el panel.
- `B4-03-1`: Con banco activo: los bancos de su grupo, el activo en negrita. Sin banco: los 15 de mayor costo del riesgo. Último trimestre con dato (2T26): 32 de 34 bancos; sin dato BRB y Cielo.
- `B4-04-0`: Por encima de la diagonal, el banco tiene más NPL del que su mix predice; por debajo, menos. Solo bancos con cobertura de al menos 50 % de la cartera; los demás no tienen punto.
- `B4-04-1`: * Cambio de cobertura en 2025. Mora implícita solo con cobertura de al menos 50 %: BNDES, Banco da Amazônia y Cielo sin dato.

## B12 · Mora — `/mora`

Archivo: `sitio/assets/js/paginas/b12.js` · rótulo: SCR.DATA · MENSUAL · usaBanco: False

### 01 Activos problemáticos por modalidad · Mensual · SCR.data

Qué parte de cada modalidad de personas está en atraso de 90 días o reestructurada con deterioro. Réplica del gráfico 1.2.2.16 del REF.

- Fila 1: `B12-01` (ancho 4/9, alto 610) + `B12-02` (ancho 5/9, alto 610)

### 02 Mora temprana por modalidad · Mensual · SCR.data

El atraso de 15 a 90 días anticipa la mora de más de 90 en unos 3 meses.

- Fila 1: `B12-03` (ancho 4/9, alto 610) + `B12-04` (ancho 5/9, alto 610)

### 03 Crédito de mayor riesgo · Mensual · SCR.data

Si el crédito más riesgoso crece más que el resto, la mora futura sube. Réplica del gráfico 1.2.2.15 del REF.

- Fila 1: `B12-05` (ancho 4/9, alto 610) + `B12-06` (ancho 5/9, alto 610)

### 04 Empresas por sector · Mensual · SCR.data

Activos problemáticos de la cartera de empresas por sector de actividad (sección CNAE).

- Fila 1: `B12-07` (ancho 4/9, alto 700) + `B12-08` (ancho 5/9, alto 700)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B12-01` | Activos problemáticos / cartera, % | `barras_linea` | `bk_scr_series` | LISTO |  | BCB, SCR.data; personas; Res. 4.966 desde ene-25 (otra defi… |
| `B12-02` | Stock de activos problemáticos por modalidad | `tabla_estandar` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data |
| `B12-03` | Atraso de 15 a 90 días / cartera, % | `barras_linea` | `bk_scr_series` | LISTO |  | BCB, SCR.data; personas |
| `B12-04` | Mora >90 días por modalidad | `tabla_estandar` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data |
| `B12-05` | Crecimiento a/a de la cartera de personas, % | `barras_linea` | `bk_scr_series` | LISTO |  | BCB, SCR.data; menor riesgo = inmobiliario, consignado, veh… |
| `B12-06` | Cartera de personas por modalidad | `tabla_estandar` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data |
| `B12-07` | Activos problemáticos / cartera por sector, último mes | `barras_simple` | `bk_scr_tablas`, `bk_scr_series` | LISTO |  | BCB, SCR.data; 10 mayores sectores por cartera |
| `B12-08` | Cartera de empresas por sector | `tabla_estandar` | `bk_scr_tablas` | LISTO |  | BCB, SCR.data |

Notas visibles en las tarjetas:

- `B12-02`: Último: R$ mil millones. Share: peso en el total de personas. Cambios en %. A jun-26 calza con el REF: total 9,2 %, tarjeta 12,7 %, no consignado 14,9 %.
- `B12-04`: Último: % de la cartera. Share: peso de la modalidad en la cartera de personas. Cambios en pp; 12m/12m: promedio de 12 meses contra los 12 previos.
- `B12-06`: Último: R$ mil millones. Share: peso en la cartera de personas. Cambios en %.
- `B12-08`: Último: R$ mil millones. Cambios en %. El nivel total queda bajo el del REF por diferencia de universo: sirve para comparar sectores. Financieras +38 % a/a: revisar reclasificación.

## B5 · Fondeo y liquidez — `/fondeo` (oculta)

Archivo: `sitio/assets/js/paginas/b5.js` · rótulo: 5 · FONDEO · usaBanco: True

### 01 Mix de fondeo · Trimestral · Panel IF.Data

¿depósitos, compromissadas o emisiones?

- Fila 1: `B5-01-0` (ancho 5/9, alto 372) + `B5-01-1` (ancho 4/9, alto 372)

### 02 El ahorro · Mensual · Sistema BCB

¿el ahorro se queda en el balance bancario?

- Fila 1: `B5-02-0` (ancho 9/9, alto 372)

### 03 Calce y costo · Trimestral · Panel IF.Data

¿quién depende más del mayorista y quién paga más por fondearse?

- Fila 1: `B5-03-0` (ancho 4/9, alto 372) + `B5-03-1` (ancho 5/9, alto 372)

### 04 Liquidez · Semestral · REF

¿hay holgura de liquidez?

- Fila 1: `B5-04-0` (ancho 9/9, alto 372)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B5-01-0` | Pasivo + PL por instrumento, por grupo, 100 % | `apilada_100` |  | DERIVAR |  | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B5-01-1` | Depósitos a/a por grupo | `linea` |  | DERIVAR |  | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B5-02-0` | CDB vs. poupança vs. Selic | `linea` |  | LISTO |  | BCB, SGS |
| `B5-03-0` | Crédito / depósitos por banco | `barras_h` |  | DERIVAR | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B5-03-1` | Costo implícito de captación vs. CDI | `dispersion` |  | FALTA | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B5-04-0` | LCR y NSFR: agregado, máximo y mínimo | `linea` |  | REF |  | BCB, Relatório de Estabilidade Financeira |

## B6 · Rentabilidad — `/rentabilidad`

Archivo: `sitio/assets/js/paginas/b6.js` · rótulo: 6 · RENTABILIDAD · usaBanco: True

**Franja de indicadores (arriba):** ROE 12 meses · Panel ← `optica/panel/bk_grupo`; ROA 12 meses · Panel ← `optica/panel/bk_grupo`; Margen de intermediación ← `optica/panel/bk_grupo`; Costo del riesgo · Panel ← `optica/panel/bk_grupo`; Eficiencia · Panel ← `optica/panel/bk_grupo`

### 01 ROE por grupo · Trimestral · Panel IF.Data

ROE de 12 meses por modelo de negocio.

- Fila 1: `B6-01-0` (ancho 9/9, alto 320)

### 02 De dónde sale el ROA · Trimestral · Panel IF.Data

Árbol del ROA del banco activo contra la mediana de su grupo.

- Fila 1: `B6-02-0` (ancho 9/9, alto 540)

### 03 Riesgo y Selic · Trimestral · Panel IF.Data

Rentabilidad contra costo del riesgo, y sensibilidad del margen a la tasa.

- Fila 1: `B6-03-0` (ancho 5/9, alto 440) + `B6-04-0` (ancho 4/9, alto 440)

### 04 Eficiencia · Trimestral · Panel IF.Data

Gasto sobre ingreso, hace un año y hoy.

- Fila 1: `B6-05-0` (ancho 9/9, alto 380)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B6-01-0` | ROE TTM por grupo | `linea` | `optica/modelo/bk_grupo` | LISTO |  | BCB, IF.Data (conglomerado prudencial) |
| `B6-02-0` | Del margen al ROA, en % del activo promedio | `cascada_doble` | `bk_banco`, `bk_roe_arbol` | LISTO | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B6-03-0` | ROE TTM vs. costo del riesgo TTM, por banco, con trayectori… | `burbujas_trayectoria` | `bk_banco`, `metrica/roe_ttm/bk_panel`, `metrica/costo_riesgo_ttm/bk_panel`, `metrica/ativo_total/bk_panel` | LISTO | sí | BCB, IF.Data (conglomerado prudencial) |
| `B6-04-0` | Beta del margen a la Selic | `barras_ic` | `bk_banco`, `bk_sensibilidad` | LISTO | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B6-05-0` | Eficiencia TTM por banco, hace un año y hoy | `pesas` | `bk_banco`, `bk_metrica`, `metrica/eficiencia_ttm/bk_panel` | LISTO | sí | BCB, IF.Data (conglomerado prudencial) |

Notas visibles en las tarjetas:

- `B6-02-0`: Las medianas de cada línea no suman exactamente a la mediana del ROA del grupo.

## B7 · Capital — `/capital` (oculta)

Archivo: `sitio/assets/js/paginas/b7.js` · rótulo: 7 · CAPITAL · usaBanco: True

### 01 Niveles · Trimestral · Panel IF.Data

¿dónde está cada banco contra su mínimo?

- Fila 1: `B7-01-0` (ancho 5/9, alto 520) + `B7-01-1` (ancho 4/9, alto 520)

### 02 Generación y consumo · Trimestral · Panel IF.Data

¿el capital crece por resultados y cuánto consume cada real de crédito?

- Fila 1: `B7-02-0` (ancho 5/9, alto 372) + `B7-02-1` (ancho 4/9, alto 372)

### 03 Holgura y estrés · Trimestral y semestral · Panel y REF

¿cuánto puede crecer la cartera sin capital nuevo, y aguanta un escenario adverso?

- Fila 1: `B7-03-0` (ancho 5/9, alto 372) + `B7-03-1` (ancho 4/9, alto 372)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B7-01-0` | Basilea, nivel 1 y capital principal por banco, contra el m… | `barras_h` |  | FALTA | sí | BCB, IF.Data (conglomerado prudencial); BCB, mínimos regula… |
| `B7-01-1` | Capital principal por grupo | `linea` |  | FALTA |  | BCB, IF.Data (conglomerado prudencial) |
| `B7-02-0` | Variación del capital principal en 4T: resultado, dividendo… | `cascada` |  | FALTA | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B7-02-1` | Densidad de RWA | `apilada_100` |  | FALTA | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B7-03-0` | Holgura de crecimiento | `barras_h` |  | FALTA | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B7-03-1` | Resultado del test de estrés del BCB | `tabla` |  | REF |  | BCB, Relatório de Estabilidade Financeira |

## B8 · Ficha por banco — `/ficha`

Archivo: `sitio/assets/js/paginas/b8.js` · rótulo: 8 · FICHA · usaBanco: True

**Franja de indicadores (arriba):** ROE 12 meses ← `metrica/roe_ttm/bk_panel` (banco); NPL ≥ 15 días ← `metrica/npl15_total/bk_panel` (banco); Cuota de crédito ← `metrica/share_credito/bk_panel` (banco); Costo del riesgo ← `metrica/costo_riesgo_ttm/bk_panel` (banco); Eficiencia ← `metrica/eficiencia_ttm/bk_panel` (banco)

### 01 Contra su grupo · Trimestral · Panel IF.Data

Doce métricas del banco contra el rango de su grupo.

- Fila 1: `B8-02-0` (ancho 9/9, alto 540)

### 02 Tamaño y cartera · Trimestral · Panel IF.Data

Balance y mix de cartera contra grupo y panel.

- Fila 1: `B8-01-1` (ancho 4/9, alto 340) + `B8-03-0` (ancho 5/9, alto 340)

### 03 Rentabilidad · Trimestral · Panel IF.Data

Árbol del ROA y ROE contra grupo y CDI.

- Fila 1: `B8-04-0` (ancho 5/9, alto 460) + `B8-04-1` (ancho 4/9, alto 460)

### 04 Fondeo · Trimestral · Panel IF.Data

Mix de fondeo contra el grupo.

- Fila 1: `B8-05-0` (ancho 9/9, alto 260)

### 05 Identidad y puente · Trimestral · IF.Data y publicado

Ficha técnica y diferencias contra lo publicado.

- Fila 1: `B8-01-0` (ancho 4/9, alto 400) + `B8-06-1` (ancho 5/9, alto 400)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B8-01-0` | Ficha técnica | `tabla` | `bk_banco`, `bk_manifiesto` | LISTO | sí | BCB, IF.Data (conglomerado prudencial); CVM |
| `B8-01-1` | Tamaño y cuotas | `tabla` | `bk_banco`, `bk_manifiesto`, `bk_metrica` | LISTO | sí | BCB, IF.Data (conglomerado prudencial) |
| `B8-02-0` | Doce métricas, una fila cada una | `percentiles` | `bk_banco`, `bk_manifiesto`, `bk_metrica` | DERIVAR | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B8-03-0` | Mix de cartera: banco vs. grupo vs. panel | `apilada_100` | `bk_banco`, `bk_manifiesto`, `bk_cartera_grupo` | DERIVAR | sí | BCB, IF.Data (conglomerado prudencial) |
| `B8-04-0` | Árbol del ROE: banco vs. mediana del grupo | `cascada_doble` | `bk_banco`, `bk_manifiesto` | DERIVAR | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B8-04-1` | ROE TTM, 12 trimestres, banco vs. grupo y vs. CDI | `linea_banco` | `bk_banco`, `bk_manifiesto` | LISTO | sí | BCB, IF.Data (conglomerado prudencial); BCB, SGS |
| `B8-05-0` | Mix de fondeo, banco vs. grupo | `apilada_100` | `bk_banco`, `bk_manifiesto`, `bk_metrica` | DERIVAR | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |
| `B8-06-1` | Puente IF.Data ↔ publicado | `tabla` | `bk_banco`, `bk_manifiesto`, `bk_puente` | LISTO | sí | BCB, IF.Data (conglomerado prudencial); CVM; cálculo propio |

Notas visibles en las tarjetas:

- `B8-02-0`: Grupo de comparación: el modelo del banco. Doce métricas; Basilea queda fuera hasta que exista bk_capital.
- `B8-03-0`: Un segmento por modalidad de cartera; el grupo y el panel usan las mismas modalidades. Rótulo solo si el segmento pesa 8 % o más.
- `B8-04-1`: Sin línea del CDI: la serie no está exportada.
- `B8-05-0`: La mediana de cada línea del grupo no suma 100 %: la barra del grupo se escala a su suma.

## B9 · Comparador — `/comparador` (oculta)

Archivo: `sitio/assets/js/paginas/b9.js` · rótulo: 9 · COMPARADOR · usaBanco: True

### 01 Todos los bancos · Trimestral · Panel IF.Data

¿cómo se comparan los 34 bancos en el último trimestre?

- Fila 1: `B9-01-0` (ancho 9/9, alto auto)

| Tarjeta | Título | Componente | Datos | Estado | Banco | Fuente |
|---|---|---|---|---|---|---|
| `B9-01-0` | Los 34 bancos × ~20 métricas | `comparador` |  | LISTO | sí | BCB, IF.Data (conglomerado prudencial); cálculo propio |

## B10 · Metodología y fuentes — `/metodologia` (oculta)

Archivo: `sitio/assets/js/paginas/b10.js` · rótulo: 10 · METODOLOGÍA · usaBanco: False


