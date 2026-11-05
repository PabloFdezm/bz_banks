# 06 · Páginas

Detalle autogenerado (secciones, selectores, filas, cada tarjeta con componente, datos y nota):
`generado/paginas.md`. Aquí: qué responde cada página y en qué estado está.

## Estados

- **v3 construida:** estructura aprobada por Pablo (gráfico izquierda 4/9, `tabla_estandar` derecha 5/9,
  una lámina por sección, posiciones idénticas en Presentar). Hoy: **Portada (B0)** y **Crédito (B3)**.
- **Estructura antigua visible:** en el menú y con datos, pero con tarjetas de la versión anterior (sin el
  par gráfico/tabla estándar): **Calidad (B4)**, **Rentabilidad (B6)**, **Ficha por banco (B8)**.
  Pendientes de rehacer con el proceso canvas → aprobación → construcción.
- **Ocultas:** existen y se abren por URL, fuera del menú (`oculta: true` en `config.js`): B1, B2, B5, B7,
  B9, B10. Varias tarjetas en «en preparación».

## B0 · Portada (`/`) — v3

Pregunta: ¿cómo está el sistema hoy?

| Sección | Gráfico (izq.) | Tabla (der.) | Selectores |
|---|---|---|---|
| 01 Crédito (mensual, SGS) | B0-01 `barras_linea`: total a/a (línea) y contribución de componentes (barras) | B0-02 cartera: Total, Libre, Direccionado, Personas, Empresas | Componentes: Libre·Direccionado / Personas·Empresas; Medida: Nominal / Real (IPCA) |
| 02 Mora (mensual, SGS) | B0-03 nivel de mora > 90 días y cambio a/a | B0-04 mora por segmento (7 filas) | — |
| 03 Rentabilidad (trimestral, IF.Data) | B0-05 ROE del panel y ROE − CDI | B0-06 ROE y ROE − CDI | — |
| 04 Estructura (trimestral, IF.Data) | B0-07 `mapa_cuotas` (treemap a todo el ancho): diez mayores + Resto | — | Cuota en: activos, crédito total/PF/PJ, depósitos totales/vista/ahorro/plazo |

Datos: `bk_portada_*`.

## B3 · Crédito (`/credito`) — v3

Pregunta: ¿qué tipo de crédito crece, qué lo movió, cómo viene el crédito nuevo y dónde está el ciclo?

| Sección | Gráfico | Tabla |
|---|---|---|
| 01 Por tipo | B3-01: selector **Barras · último** (a/a por modalidad, Total primero en cobre, Personas navy, Empresas acero) / **Líneas · historia** (a/a de 36 meses por modalidad + Total grueso en cobre; leyenda clicable) | B3-02 cartera por tipo con Share y fila Total |
| 02 Qué lo movió | B3-03 `barras_signo`: contribución m/m en pp (suma navy, resta cobre) | B3-04 contribución por tipo (incluye Otros y Total) |
| 03 Crédito nuevo | B3-05 concesiones libres 12m a/a contra saldo total a/a | B3-06 concesiones libres/PF/PJ y saldo total |
| 04 Ciclo | B3-07 crédito/PIB, tendencia HP (discontinua) y brecha (barras, eje derecho simétrico) | B3-08 ciclo (trimestral) |

Datos: `bk_cred_tablas`, `bk_cred_series`. Alto de las secciones 01 y 02: 570 y 590 px (tablas de 11–12 filas).

## B4 · Calidad (`/calidad`) — estructura antigua

Franja: mora sistema, PF libre, PJ libre (de `bk_sistema_q`), NPL ≥ 15 d y costo del riesgo del panel.
Secciones: 01 Sistema (B4-01-0 mora > 90 d PF libre, PJ libre, total) · 02 Por grupo y por banco (B4-03-0
calidad por grupo; B4-03-1 costo del riesgo TTM y cobertura por banco) · 03 Exposición (B4-04-0 mora
implícita del mix vs NPL observado; B4-04-1 cambio de la mora implícita en 12m).

## B6 · Rentabilidad (`/rentabilidad`) — estructura antigua

Franja: ROE, ROA, margen de intermediación, costo del riesgo y eficiencia del panel. Secciones: 01 ROE por
grupo · 02 Del margen al ROA (cascada banco vs mediana del grupo, requiere banco) · 03 ROE vs costo del
riesgo con trayectoria de 8 trimestres · 04 Beta del margen a la Selic · 05 Eficiencia hace un año y hoy.
Plan de Pablo: rehacer como **cascada desde el NIM hasta el ROE**.

## B8 · Ficha por banco (`/ficha?banco=<slug>`) — estructura antigua

Requiere banco. Franja: ROE, NPL ≥ 15 d, cuota de crédito, costo del riesgo, eficiencia del banco.
Secciones: 01 contra su grupo (12 métricas con percentiles) · 02 tamaño y cartera (cuotas, mix vs grupo y
panel) · 03 rentabilidad (árbol del ROE vs mediana del grupo, ROE 12 trimestres vs grupo y CDI) · 04 fondeo
(mix vs grupo) · 05 identidad y puente IF.Data ↔ publicado. Lee las particiones `banco/<slug>/`.

## Ocultas

B1 Ciclo y condiciones · B2 Estructura y competencia · B5 Fondeo y liquidez · B7 Capital · B9 Comparador ·
B10 Metodología y fuentes (sin secciones). Contenido en `generado/paginas.md`.

## Estructura objetivo (pedida por Pablo, 3-nov)

Portada (hecha) → Crédito (hecha) → **Mora** → **Rentabilidad** (cascada NIM → ROE) → **Márgenes**
(rendimiento del crédito menos costo de captación; IF.Data informe 4 para gasto de captación e informe 3
para captaciones) → **Por banco** (crédito/depósitos en la historia) → **Productos** (tasas, crecimiento y
endeudamiento por producto). Cada una: canvas → aprobación → construcción, con las reglas de `01`.
