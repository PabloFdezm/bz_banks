# Dashboard Bancos Brasil — Esqueleto narrativo y especificación de páginas

Versión 0.2 · 3-nov-2026 (v0.1: 2-nov-2026) · Plataforma: sitio HTML estático (después Netlify; réplica parcial en Power BI).
Diseño: Pablo (Principal AM) con Claude.

Este archivo es la **fuente de verdad de la narrativa**: páginas, secciones, preguntas, tarjetas, jerarquía y qué dato alimenta cada tarjeta. El contrato de tablas está en `SPEC_DATOS_BANCOS_v0.1.md`; cómo se construye el sitio, en `SPEC_WEB_BANCOS_00_GENERAL.md`. Si algo de este esqueleto no se puede construir con los datos, se marca FALTA y se avisa; no se reemplaza por otra serie sin decirlo.

---

## Cambios v0.2 (2026-11-03) — mandan sobre el resto de este archivo

Consolidan las decisiones de `PENDIENTES.md` tomadas al ejecutar las olas 1 y 2.

1. **Grupos de pares (S2):** `modelo_negocio` de Pablo (Grandes, Digitales, Medianos y nicho, Pagos, Desarrollo). Banco Pan va dentro de BTG.
2. **B9 · 01:** nombre «Todos los bancos»; pregunta «¿cómo se comparan los 34 bancos en el último trimestre?». **B10:** rótulo «10 · METODOLOGÍA». **B8 · 07:** pregunta «¿cómo lo evalúan sus clientes frente a sus pares?».
3. **Ficha (B8):** con banco activo, el titular es el nombre del banco y el rótulo «8 · FICHA · <GRUPO>». Las demás páginas conservan su título y muestran el banco en la barra.
4. **Último trimestre con huecos:** el total del panel se muestra con los bancos que tienen dato y la nota «n de 34 con dato» (2T26: BRB sin dato).
5. **B4-04 (exposición):** la mora implícita usa `definiciones/bancos__equivalencias_mora.json`; solo se calcula con cobertura ≥ 50 % de la cartera (BNDES, Banco da Amazônia y Cielo quedan vacíos). La tarjeta muestra la cobertura. SGS 21114 es crédito personal **no consignado**.
6. **B6-04 (sensibilidad):** las betas con menos de 24 trimestres llevan la marca «pocos trimestres» y siempre se muestra el IC 90 %. Exclusiones de la regresión: 2024-T4 y, en los 10 bancos con cambio de cobertura en 2025, 2025-T1.
7. **B6-02 / B8-04 (árbol del ROE):** 10 líneas (se agregan «transacciones de pago», desde 2025-T4, y «no operacional», hasta 2024-T4). En Pagos el árbol se compara solo contra su grupo.
8. **Prefijos de universo:** además de los cinco, «BCB ·» para reclamos y tarifas.
9. **Capital (B7) y aperturas (B3-04):** dependen de Olinda (caída desde el 2-nov). Si Olinda no sirve el informe 5 antes de 2020, B7 arranca en 2020-T4.
10. **CVM (B8-06-0):** postergado; la tarjeta queda «en preparación».

## Supuestos de partida (decisiones abiertas de la propuesta v0.1)

Pablo no las ha cerrado todavía. Se adopta la opción recomendada; cambiarlas no obliga a rehacer la estructura.

| # | Decisión | Supuesto adoptado |
|---|---|---|
| S1 | Repo | Todo en `bcb-scraper` (este repo). Specs en `docs/dashboard_bancos/`, sitio en `sitio_bancos/site/`, gold en `pb/Banks/` con prefijo `bk_` |
| S2 | Grupos de pares | Los de `modelo_negocio` que Pablo fijó el 2026-10-08 en `definiciones/bcb_ifdata__bancos_balances.json`: **Grandes, Digitales, Medianos y nicho, Pagos, Desarrollo** |
| S3 | Texto en pantalla | Sin lecturas del analista. Títulos descriptivos, preguntas fijas por sección y una tira «Qué se movió» calculada en Python. Queda un hueco opcional `textos.json` por si Pablo decide escribir |
| S4 | Fichas completas | Los cotizados: Itaú, Bradesco, Banco do Brasil, Santander, BTG Pactual (incluye Pan), Nubank, Inter, XP, ABC Brasil, Banrisul, BMG, Stone, PagSeguro. El resto, ficha «solo panel» |
| S5 | Idioma | Español, igual que el Monitor Brasil |
| S6 | Primera maqueta | Ficha por banco (B8) |

---

## 0. Convenciones transversales

### 0.1 Recorrido

Once páginas, de arriba hacia abajo: B0 Portada → B1 Ciclo y condiciones → B2 Competencia → B3 Crédito → B4 Calidad → B5 Fondeo → B6 Rentabilidad → B7 Capital → B8 Ficha por banco → B9 Comparador → B10 Metodología. Cada página de sistema (B1–B7) termina en «cómo se reparte entre bancos», que es la puerta natural a la Ficha.

### 0.2 Anatomía (igual que el Monitor Brasil)

Cabecera → apertura (rótulo, título, intro fija, índice «En esta página») → tira «Qué se movió» → secciones numeradas → cierre (fuentes y cómo leer). Cada sección: **riel** de 452 px (número, nombre, frecuencia · último dato, pregunta, bloque KPI o selector) y **cuerpo** de 1 388 px con tarjetas de ancho 9/6/5/4/3 columnas (1 388/920/764/608/452 px). Alto por defecto de una fila: 372 px; tarjetas dobles: 760 px. Sin doble eje.

### 0.3 Banco activo y grupo

Todo el sitio tiene un **banco activo** (por defecto ninguno) y un **grupo de comparación** (por defecto el `modelo_negocio` del banco activo; sin banco, «Panel»). Con banco activo, cada tarjeta que dibuja bancos lo resalta en navy y deja al resto en acero claro; cada tarjeta que dibuja grupos agrega una línea discontinua `--texto` con el banco. Las tarjetas marcadas **[banco]** cambian con el banco activo; las demás no.

### 0.4 Universos

Cinco universos que nunca comparten eje como si fueran la misma serie (detalle en la propuesta §3.1): **Sistema** (SGS, mensual), **Panel** (IF.Data, 34 conglomerados, trimestral), **Segmentos** (SCR.data), **Publicado** (CVM) y **REF** (semestral). El subtítulo de cada tarjeta empieza con su universo.

### 0.5 Ópticas de grupo

Las mismas cinco de `pb/cre_institucion` (ya calculadas en `cre_panorama`, `cre_calidad`, `cre_contexto`): Total panel; Segmento regulatorio (S1–S4, sin segmento); Propiedad (público, privado nacional, privado extranjero); **Modelo de negocio** (Grandes, Medianos y nicho, Digitales, Pagos, Desarrollo); Tradicional vs Fintech. La óptica por defecto del sitio es **Modelo de negocio**. Las variaciones de grupo se calculan con los mismos bancos en los dos extremos (la entrada de un banco no es crecimiento).

### 0.6 Ventanas y cálculos

- Panel trimestral: ventana de ciclo desde 2014-T1; monitor, 12 trimestres.
- Sistema mensual: ciclo desde 2012; monitor, 36 meses.
- TTM con 4 trimestres consecutivos (NaN si falta uno); ROE y ROA sobre el promedio de t−4 y t.
- Medias móviles de 2 y 4 trimestres disponibles en `cre_panorama` (`aa2`, `aa4`). Por defecto se muestra la a/a de la media de 4T.
- Real = deflactado por IPCA.

### 0.7 Quiebres anotados (siempre visibles donde caigan)

| Fecha | Qué | Dónde se anota |
|---|---|---|
| 2024-T4 | El BCB sirve carteras por modalidad con un salto imposible: el trimestre queda vacío | B2, B3, B4, B8 |
| 2025-T1 | COSIF 2025 (renumeración de cuentas) y migración de los informes de crédito al prudencial | Todas las series del Panel |
| 2025-T1 | Res. 4.966: desaparece la escala AA–H; E–H se reemplaza por activos problemáticos | B4, B8 |
| 2025 | Cambio de política de baja a pérdida (REF oct-26, Boxe 2) | B4 (Sistema) |

### 0.8 Color de signo

Navy = mejora; cobre-texto = deterioro; gris tinta-3 = neutro. Sube ROE, ROA, margen, capital, cobertura o cuota → navy. Sube mora, E–H, activos problemáticos, costo del riesgo, eficiencia (gasto/ingreso) o comprometimiento → cobre. El crecimiento de cartera es neutro. Las categorías nunca van en cobre ni arena.

### 0.9 Claves y estados

Clave de tarjeta `Bp-ss-n` (página-sección-orden). Estados: **LISTO** (la tabla tiene lo que se dibuja), **DERIVAR** (la materia prima está y falta un cálculo en Python), **FALTA** (no hay dato), **REF** (planilla semestral del REF), **FIJO** (valor citado en el spec). En el navegador solo se derivan filtros, re-bases y ordenamientos; todo cálculo DERIVAR se hace en el pipeline (ver spec de datos).

---

## B0 · Portada

Rótulo: `BANCOS BRASIL · MONITOR`. Pregunta de la página: **¿qué cambió en el sistema este trimestre y dónde está el ciclo?**

La portada muestra, uno al lado del otro, el **último corte de cada universo** (Panel 2T26, Sistema ago-26, SCR jun-26, REF oct-26) para que el rezago quede a la vista.

### B0 · 01 · El sistema hoy

Pregunta: ¿cómo está el sistema en las seis cifras que importan, y es mucho o poco contra su historia?
Riel: cortes por universo (texto con fechas, de `bk_manifiesto`).

| Clave | Tarjeta | Componente (galería) | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B0-01-0 | **Seis cifras del sistema.** Filas: crédito real a/a (Sistema y Panel), mora > 90 días PF libre (Sistema), activos problemáticos/NPL (Panel), ROE TTM (Panel), Basilea (Panel), comprometimiento de renta (Sistema). Columnas: último, fecha, Δ trimestre, Δ año, percentil 10 años, sparkline 12 puntos | `tabla` (T4 + T29) | 9 × 372 | `bk_sistema_q`, `bk_grupo` (Panel), `bk_capital` | LISTO salvo Basilea (FALTA hasta tener `bk_capital`) |

### B0 · 02 · El ciclo

Pregunta: ¿las condiciones empujan o frenan a los bancos?
Riel: KPI K37 «El costo real del crédito» (tasa ICC − IPCA esperado).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B0-02-0 | **Reloj del ciclo financiero.** x = hiato crédito/PIB (BIS), y = Selic real ex ante; trayectoria trimestral desde 2014 con «hoy» marcado | `trayectoria` (G3) | 5 × 372 | `bk_sistema_q`: `bis_hiato_credito_pib`, `selic_real_exante` | DERIVAR (BIS en crudo) |
| B0-02-1 | **Dónde está cada driver en diez años.** Selic real, crédito/PIB, comprometimiento, desempleo, mora PF, spread ICC: percentil y dirección 6m | `tabla` (T29) | 4 × 372 | `bk_sistema_q` | LISTO |

### B0 · 03 · Qué se movió

Pregunta: ¿qué banco o grupo se apartó más en el último trimestre?
Riel: selector de óptica (por defecto Modelo de negocio).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B0-03-0 | **Los cinco mayores movimientos del trimestre** (cuota, ROE, NPL, CoR, crecimiento), con frase plantilla «Nubank: ROE TTM +3,1 pp t/t, a 51,3 %» generada en Python | `tabla` (T24) | 5 × 372 | `bk_qcambio` | DERIVAR |
| B0-03-1 | **ROE TTM por grupo, hace un año y hoy** | `pesas` (G5) | 4 × 372 | `bk_grupo` (roe_ttm) | LISTO |

### B0 · 04 · Puertas

Una tarjeta HTML por página (B1–B9) con su pregunta y el último dato. Sin datos propios.

---

## B1 · Ciclo y condiciones

Rótulo: `1 · CICLO Y CONDICIONES`. Pregunta: **¿el entorno macro empuja o frena a los bancos?** Esta página toma series del Monitor Brasil; no las recalcula.

### B1 · 01 · Tasa

Pregunta: ¿qué tan restrictiva es la política y qué espera el mercado?
Riel: KPI K57 «¿Restrictiva o expansiva?» (tasa real ex ante).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B1-01-0 | **Selic real ex ante**, con la Selic nominal en panel superior | `linea` (G22) | 5 × 372 | `tasa_real_exante` | LISTO. La línea de tasa neutral es FIJO a confirmar por Pablo; sin confirmación, se omite |
| B1-01-1 | **Trayectoria de la Selic: Focus vs. mercado** | `linea` | 4 × 372 | `trayectoria_selic_focus` | LISTO |

### B1 · 02 · Crédito y economía

Pregunta: ¿el crédito crece más o menos que la economía, y está acelerando?
Riel: KPI K58 «El impulso de crédito».

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B1-02-0 | **Crédito/PIB y su tendencia** (SFN, SGS 20622), con aporte PF/PJ | `columnas` + línea (G85) | 5 × 372 | `cpib_componentes` | LISTO |
| B1-02-1 | **Impulso de crédito** (Δ del flujo 12m / PIB 12m) | `columnas` con signo | 4 × 372 | `bk_sistema_m`: `impulso_credito` (SGS 20539 + 4382) | DERIVAR |

### B1 · 03 · Hogares

Pregunta: ¿los hogares pueden seguir pagando?
Riel: «Dato de la sección»: comprometimiento de renta (SGS 29034), último y percentil.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B1-03-0 | **Comprometimiento de renta: intereses y amortización** | `area_apilada` + línea total (T44) | 5 × 372 | `hsf_mensual`, `fh_deuda` | LISTO |
| B1-03-1 | **Desempleo y mora PF libre** en dos paneles con el mismo eje x | `linea` ×2 | 4 × 372 | `tasas_pnad`; `bk_sistema_m`: SGS 21112 | LISTO |

### B1 · 04 · Empresas

Pregunta: ¿las empresas pueden pagar, y qué tamaño de empresa preocupa?
Riel: «Dato de la sección»: activos problemáticos PJ MPME (SCR), último.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B1-04-0 | **Crédito real a/a por porte** (MPME vs. grandes) | `linea` | 5 × 372 | `bk_sistema_m`: SGS 27701, 27702 | DERIVAR (bajar y deflactar) |
| B1-04-1 | **Inadimplencia por porte** | `linea` | 4 × 372 | `bk_sistema_m`: SGS 27703, 27704; `scrdata_pj_agregado` | DERIVAR |
| B1-04-2 | **Crédito con garantía pública** (FGI, Pronampe) como % de las concesiones a MPME | `columnas` | 9 × 372 | crudo `fgo_pronampe`, `bndes_fgi` | DERIVAR |

### B1 · 05 · Desintermediación

Pregunta: ¿cuánto crédito se va del balance de los bancos al mercado de capitales?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B1-05-0 | **Crédito amplio por fuente**: bancario PF, bancario PJ, mercado de capitales, externo; aporte al crecimiento | `columnas` apiladas | 5 × 372 | `bk_ref` (gráfico 1.2.2.1 del REF) | REF |
| B1-05-1 | **Mercado de capitales por instrumento** (debentures, FIDC, CPR, CRI, CRA) | `barras_h` | 4 × 372 | `bk_ref` (tabla 1.2.2.1) | REF |

---

## B2 · Competencia

Rótulo: `2 · ESTRUCTURA Y COMPETENCIA`. Pregunta: **¿quién gana y quién pierde cuota, y en qué cartera?**

### B2 · 01 · Concentración

Pregunta: ¿el sistema se concentra o se abre?
Riel: «Dato de la sección»: cuota de crédito de los cinco mayores.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B2-01-0 | **HHI y cuota top 5** en crédito, depósitos y activo | `linea` | 5 × 372 | `bk_grupo` (hhi_*, top5_*) | DERIVAR |
| B2-01-1 | **Ranking de cuota de crédito con movimiento** (puestos ganados o perdidos en 4T) **[banco]** | `tabla` (T8) | 4 × 372 | `bk_panel`: share_credito | LISTO |

### B2 · 02 · Cuota por grupo

Pregunta: ¿qué tipo de banco gana cuota?
Riel: selector de óptica y de medida (Crédito / Depósitos).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B2-02-0 | **Cuota por grupo, 100 %** (apilado por institución) | `area_apilada` (G8) | 5 × 372 | `cre_panorama` (apilar = Institución, participacion) | LISTO |
| B2-02-1 | **Cuota por banco, hace dos años y hoy** **[banco]** | `pesas` (G9) | 4 × 372 | `bk_panel`: share_credito, share_depositos | LISTO |

### B2 · 03 · Dónde compiten

Pregunta: ¿en qué carteras están ganando los digitales?
Riel: selector Personas / Empresas.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B2-03-0 | **Cuota de cada banco en cada modalidad** (filas = bancos ordenados por tamaño, columnas = modalidades) **[banco]** | `heatmap` secuencial (T3) | 9 × 520 | `bk_cartera`: saldo por banco × modalidad | DERIVAR |
| B2-03-1 | **Cambio de cuota en 4T por modalidad y grupo** | `heatmap` divergente | 9 × 372 | `bk_cartera` | DERIVAR |

### B2 · 04 · Riesgo según el tipo de institución

Pregunta: ¿crecer cuota les está costando mora?
Riel: «Dato de la sección»: inadimplencia de fintechs menos la de bancos (pp, SCR).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B2-04-0 | **Inadimplencia por tipo de institución** (banco, financiera, fintech, cooperativa), PF y PJ en dos paneles | `linea` ×2 | 5 × 372 | `bk_scr` (segmento × mes) | DERIVAR (hoy 6 meses; falta la historia) |
| B2-04-1 | **Crecimiento vs. mora por grupo** con trayectoria de 8 trimestres | `burbujas` con trayectoria (G119) | 4 × 372 | `cre_panorama` (aa4), `cre_calidad` (NPL) | LISTO |

### B2 · 05 · Precio y servicio

Pregunta: ¿compiten en precio o en servicio?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B2-05-0 | **Reclamos por millón de clientes, último trimestre** **[banco]** | `barras_h` | 4 × 372 | `bk_conducta` | DERIVAR (un corte hoy; FALTA la serie) |
| B2-05-1 | **Tarifas de un paquete estándar por grupo** | `tabla` | 5 × 372 | `bk_conducta` (tarifas Olinda) | DERIVAR |
| B2-05-2 | **Pix como % de los pagos minoristas** | `linea` | 9 × 372 | `bk_sistema_m`: meios de pagamento (MPV) | DERIVAR |

---

## B3 · Crédito

Rótulo: `3 · CRÉDITO`. Pregunta: **¿cuánto crece la cartera, en qué y quién la empuja?**

### B3 · 01 · Crecimiento

Pregunta: ¿a qué ritmo crece el crédito, y el sistema adelanta al panel?
Riel: KPI K42 «Crédito nuevo vs. stock» (concesiones PF libres SA, SGS 24444).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B3-01-0 | **Sistema: saldo real a/a, PF y PJ** (mensual) | `linea` (G28) | 5 × 372 | `bk_sistema_m`: SGS 20539/20540/20541, deflactados | LISTO |
| B3-01-1 | **Panel: cartera a/a media 4T por grupo** | `linea` | 4 × 372 | `cre_panorama` (aa4) | LISTO |

### B3 · 02 · Aportes

Pregunta: ¿qué modalidades y qué grupos explican el crecimiento?
Riel: selector Total / Personas / Empresas (igual que el PBIP: sin modalidad suelta).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B3-02-0 | **Aporte por modalidad al crecimiento a/a** | `columnas` apiladas + línea total (C2) | 5 × 372 | `cre_panorama` (apilar = Tipo de crédito, aporte_aa4, total_aa4) | LISTO |
| B3-02-1 | **Aporte por grupo** | `columnas` apiladas + total | 4 × 372 | `cre_panorama` (apilar = Institución) | LISTO |

### B3 · 03 · Mix por banco

Pregunta: ¿qué tan riesgosa es la cartera de cada banco por su composición?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B3-03-0 | **Mix de cartera por banco, 100 %** (tarjeta, personal, consignado, vehículos, hipotecario, rural, PJ) **[banco]** | `apilada_100` (T93) | 9 × 760 | `bk_cartera` | DERIVAR |

### B3 · 04 · Aperturas

Pregunta: ¿a quién le prestan: porte, indexador, región, plazo?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B3-04-0 | **Cartera PJ por porte del tomador, por banco** **[banco]** | `apilada_100` | 5 × 372 | `bk_apertura` | FALTA (informes de IF.Data sin colectar) |
| B3-04-1 | **Cartera por indexador** (prefijado, CDI, IPCA, TR, dólar) **[banco]** | `apilada_100` | 4 × 372 | `bk_apertura` | FALTA |
| B3-04-2 | **Cartera por región, por banco** | `mosaico_uf` (T15) o `heatmap` | 9 × 372 | `bk_apertura` | FALTA |

### B3 · 05 · Dirigido y garantizado

Pregunta: ¿cuánto del crédito tiene subsidio, mandato o garantía pública?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B3-05-0 | **Crédito dirigido real a/a**: rural, inmobiliario, BNDES | `linea` | 5 × 372 | `bk_sistema_m`: SGS 20597+20609, 20600+20612, 20604+20616 | DERIVAR |
| B3-05-1 | **Peso del dirigido en la cartera por grupo** | `columnas` | 4 × 372 | `bk_cartera` (rural, hipotecario, infraestructura) | DERIVAR |

---

## B4 · Calidad

Rótulo: `4 · CALIDAD`. Pregunta: **¿se está deteriorando la cartera, dónde y quién está más expuesto?**

### B4 · 01 · Sistema

Pregunta: ¿la mora sube o baja, y está en máximos?
Riel: KPI K21 «La última vez que estuvo así» (mora PF libre).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B4-01-0 | **Mora > 90 días: PF libre, PJ libre, total**, con bandas p10–p90 de 10 años; nota de la política de baja a pérdida 2025 | `linea` | 5 × 372 | `bk_sistema_m`: SGS 21112, 21086, 21082 | LISTO |
| B4-01-1 | **Atrasos de 15 a 90 días vs. mora > 90 adelantada 3 meses**, PF | `linea` (G31) | 4 × 372 | `bk_sistema_m`: SGS 21005, 21112 (lead 3) | DERIVAR |

### B4 · 02 · Por modalidad

Pregunta: ¿qué cartera se deteriora primero?
Riel: «Dato de la sección»: la modalidad con mayor alza de mora en 12m.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B4-02-0 | **Mora por modalidad PF** (tarjeta rotativo, parcelado, personal, consignado privado/público/INSS, vehículos, inmobiliario), misma escala | `small_multiples` (G1) | 9 × 520 | `hogares_modalidades` (mora90_pct, early_pct) | LISTO |

### B4 · 03 · Por banco

Pregunta: ¿qué banco se deteriora más rápido?
Riel: selector de medida: NPL ≥ 15 días / activos problemáticos / costo del riesgo.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B4-03-0 | **Calidad por grupo** (NPL ≥ 15 días, E–H hasta 2024, activos problemáticos desde 2025, quiebre marcado) | `linea` | 5 × 372 | `cre_calidad` (medida_cal = NPL, npl_def) | LISTO |
| B4-03-1 | **Costo del riesgo TTM y cobertura, por banco** **[banco]** | `barras_h` doble | 4 × 372 | `bk_panel`: costo_riesgo_ttm, cobertura_ecl | LISTO |
| B4-03-2 | **NPL por banco, ocho trimestres** (pequeños múltiplos de los 34, misma escala) **[banco]** | `small_multiples` | 9 × 760 | `bk_cartera` (vencido ≥ 15 / saldo, total) | DERIVAR |

### B4 · 04 · Exposición × driver

Pregunta: ¿qué banco tiene más cartera en los segmentos que se deterioran?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B4-04-0 | **Mora implícita del mix vs. NPL observado.** Mora implícita = Σ peso de la modalidad en el banco × mora del sistema en esa modalidad. Por encima de la diagonal, el banco está peor que su mix; por debajo, mejor **[banco]** | `dispersion` con diagonal (C4) | 5 × 372 | `bk_exposicion` | DERIVAR |
| B4-04-1 | **Cambio de la mora implícita en 12m, por banco**: cuánto empeoró el entorno de cada cartera | `barras_h` | 4 × 372 | `bk_exposicion` | DERIVAR |

### B4 · 05 · Empresas

Pregunta: ¿qué porte y qué región se deterioran?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B4-05-0 | **Activos problemáticos PJ por porte** | `linea` | 5 × 372 | `scrdata_pj_agregado` → `bk_scr` | DERIVAR |
| B4-05-1 | **Inadimplencia por estado** | `mosaico_uf` (T15) | 4 × 372 | `bk_scr` (por UF) | DERIVAR |

---

## B5 · Fondeo y liquidez

Rótulo: `5 · FONDEO`. Pregunta: **¿cómo se fondean los bancos y cuánto les cuesta?**

### B5 · 01 · Mix de fondeo

Pregunta: ¿depósitos, compromissadas o emisiones?
Riel: selector de óptica.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B5-01-0 | **Pasivo + PL por instrumento, por grupo, 100 %** (depósitos, interfinancieros, compromissadas, instrumentos de deuda, préstamos y repases, otros, PL) | `apilada_100` | 5 × 372 | `bk_grupo` (componentes del pasivo) | DERIVAR (suma por grupo) |
| B5-01-1 | **Depósitos a/a por grupo** | `linea` | 4 × 372 | `bk_grupo`: depositos_aa | DERIVAR |

### B5 · 02 · El ahorro

Pregunta: ¿el ahorro se queda en el balance bancario?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B5-02-0 | **CDB vs. poupança vs. Selic** | `linea` | 9 × 372 | `hcs_ahorro` | LISTO |

### B5 · 03 · Calce y costo

Pregunta: ¿quién depende más del mayorista y quién paga más por fondearse?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B5-03-0 | **Crédito / depósitos por banco** **[banco]** | `barras_h` | 4 × 372 | `bk_panel`: credito_depositos | DERIVAR (cociente simple) |
| B5-03-1 | **Costo implícito de captación vs. CDI** (gasto de captación TTM / pasivo con costo promedio) **[banco]** | `dispersion` | 5 × 372 | `bk_panel`: costo_captacion_ttm | FALTA (el DRE del panel no separa gasto de captación; validar en `bank_cuentas`) |

### B5 · 04 · Liquidez

Pregunta: ¿hay holgura de liquidez?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B5-04-0 | **LCR y NSFR: agregado, máximo y mínimo** (S1) | `linea` | 9 × 372 | `bk_ref` (gráficos 1.2.1.15, 1.2.1.18) | REF |

---

## B6 · Rentabilidad

Rótulo: `6 · RENTABILIDAD`. Pregunta: **¿quién gana dinero, por qué y qué tan sostenible es?**

### B6 · 01 · Sistema y grupos

Pregunta: ¿la rentabilidad sube o baja, y en qué grupo?
Riel: KPI K3 «Firma de momentum» del ROE del panel.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B6-01-0 | **ROE TTM por grupo** | `linea` | 5 × 372 | `cre_contexto` / `cre_calidad` (medida_cal = ROE) | LISTO |
| B6-01-1 | **ROE menos CDI medio 4T, por grupo** | `columnas` agrupadas | 4 × 372 | `cre_contexto` (ROE, CDI (media 4T)) | LISTO |

### B6 · 02 · Descomposición del ROE

Pregunta: ¿qué explica la diferencia de ROE entre un banco y su grupo?
Riel: selector de banco (si no hay banco activo, muestra el grupo contra el panel).

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B6-02-0 | **Del margen al ROE, en % del activo promedio**: margen antes de provisiones, provisiones, tarifas y servicios, personal, administrativos, tributarios, otros, impuesto y participaciones → ROA → × apalancamiento → ROE. Banco vs. mediana del grupo **[banco]** | `cascada` doble (G4) | 9 × 520 | `bk_roe_arbol` | DERIVAR |
| B6-02-1 | **Brecha de cada línea contra el grupo** (pp del activo) **[banco]** | `barras_h` con signo | 9 × 372 | `bk_roe_arbol` | DERIVAR |

### B6 · 03 · Rentabilidad y riesgo

Pregunta: ¿la rentabilidad se compra con riesgo?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B6-03-0 | **ROE TTM vs. costo del riesgo TTM, por banco, con trayectoria de 8 trimestres** **[banco]** | `burbujas` con trayectoria (G119), tamaño = activo | 9 × 760 | `bk_panel`: roe_ttm, costo_riesgo_ttm, ativo_total | LISTO (la trayectoria solo para el banco activo y los Grandes, para no saturar) |

### B6 · 04 · Sensibilidad a la Selic

Pregunta: ¿a quién le conviene una Selic alta?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B6-04-0 | **Beta del margen a la Selic**: pendiente de la regresión del NIM trimestral contra el CDI medio, desde 2016, por banco, con intervalo **[banco]** | `barras_h` con intervalo | 5 × 372 | `bk_sensibilidad` | DERIVAR |
| B6-04-1 | **NIM vs. CDI por grupo** | `linea` ×2 paneles | 4 × 372 | `cre_contexto` (NIM, CDI) | LISTO |

### B6 · 05 · Eficiencia

Pregunta: ¿quién gana escala?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B6-05-0 | **Eficiencia TTM por banco, hace un año y hoy** **[banco]** | `pesas` (G114) | 5 × 372 | `bk_panel`: eficiencia_ttm | LISTO |
| B6-05-1 | **Crecimiento de gastos vs. ingresos, a/a TTM, por grupo** | `dispersion` con diagonal | 4 × 372 | `bk_grupo` | DERIVAR |

---

## B7 · Capital

Rótulo: `7 · CAPITAL`. Pregunta: **¿cuánto capital sobra para crecer o repartir?** Toda la página depende de colectar el informe de capital de IF.Data (hoy solo hay cinco cortes sueltos en `datos/derivado/bcb_ifdata/valores/ifdata_capital_*.csv`).

### B7 · 01 · Niveles

Pregunta: ¿dónde está cada banco contra su mínimo?
Riel: «Dato de la sección»: Basilea del panel.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B7-01-0 | **Basilea, nivel 1 y capital principal por banco, contra el mínimo con colchones** **[banco]** | `barras_h` con marcas (escala) | 5 × 520 | `bk_capital` + FIJO de mínimos regulatorios (`manual/minimos_regulatorios.csv`) | FALTA |
| B7-01-1 | **Capital principal por grupo** | `linea` | 4 × 520 | `bk_capital` | FALTA |

### B7 · 02 · Generación y consumo

Pregunta: ¿el capital crece por resultados y cuánto consume cada real de crédito?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B7-02-0 | **Variación del capital principal en 4T: resultado, dividendos, otros** **[banco]** | `cascada` | 5 × 372 | `bk_capital`, `bk_panel` (lucro) | FALTA |
| B7-02-1 | **Densidad de RWA** (RWA / activo) y RWA por tipo de riesgo **[banco]** | `apilada_100` | 4 × 372 | `bk_capital` | FALTA |

### B7 · 03 · Holgura y estrés

Pregunta: ¿cuánto puede crecer la cartera sin capital nuevo, y aguanta un escenario adverso?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B7-03-0 | **Holgura de crecimiento**: (capital principal − mínimo con colchones) / (densidad de RWA × mínimo), en % de la cartera actual **[banco]** | `barras_h` | 5 × 372 | `bk_capital` | FALTA |
| B7-03-1 | **Resultado del test de estrés del BCB** (agregado) | `tabla` | 4 × 372 | `bk_ref` | REF |

---

## B8 · Ficha por banco

Rótulo: `8 · FICHA · [Banco]`. Pregunta: **¿cómo está este banco frente a sus pares en todo lo anterior?** Ruta `/ficha/?banco=<slug>`. Sin banco en la URL, muestra el selector y nada más. Todas las tarjetas son **[banco]**.

Grupo de pares = `modelo_negocio` del banco. Un selector en la cabecera permite cambiar a otra óptica (Segmento regulatorio, Propiedad) o a «Panel».

### B8 · 01 · Identidad

Pregunta: ¿qué banco es y qué tan reciente es la información?
Riel: selector de banco (lista agrupada por modelo) y selector de grupo de comparación.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B8-01-0 | **Ficha técnica**: nombre BCB, conglomerado, modelo, segmento, propiedad, ticker, nota (por ejemplo «incluye Banco Pan»), último corte Panel y Publicado | `tabla` | 4 × 372 | `bk_banco`, `bk_manifiesto` | LISTO (salvo Publicado) |
| B8-01-1 | **Tamaño y cuotas**: activo, crédito, depósitos, PL, con cuota y Δ cuota en 4T | `tabla` con barras (T4) | 5 × 372 | `bk_panel` | LISTO |

### B8 · 02 · Posición contra los pares

Pregunta: ¿en qué es mejor y en qué es peor que su grupo?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B8-02-0 | **Doce métricas, una fila cada una**: el rango p10–p90 del grupo como barra gris, la mediana como marca, el banco como punto (navy si está del lado bueno según el signo de la métrica, cobre si no) y el punto de hace un año en acero claro. Métricas: crecimiento de crédito a/a, % PF, NPL, costo del riesgo, cobertura, margen, tarifas/activo, eficiencia, ROA, ROE, apalancamiento, crédito/depósitos (Basilea cuando exista) | `percentiles` (nuevo; pariente de K1/T12) | 9 × 760 | `bk_panel` (valor, p10_grupo, p50_grupo, p90_grupo, valor_t4) | DERIVAR |

### B8 · 03 · Cartera

Pregunta: ¿de qué está hecha su cartera y cómo se porta cada pedazo contra el sistema?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B8-03-0 | **Mix de cartera: banco vs. grupo vs. panel** | `apilada_100` (3 barras) | 5 × 372 | `bk_cartera` | DERIVAR |
| B8-03-1 | **NPL por modalidad: banco vs. su grupo vs. mora del sistema** | `tabla` (T41) | 4 × 372 | `bk_cartera`, `bk_sistema_q` | DERIVAR |
| B8-03-2 | **Crecimiento de cartera y NPL, 12 trimestres, banco vs. mediana del grupo** | `linea` ×2 paneles | 9 × 372 | `bk_panel`, `bk_grupo` | LISTO |

### B8 · 04 · Rentabilidad

Pregunta: ¿por qué su ROE es el que es?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B8-04-0 | **Árbol del ROE: banco vs. mediana del grupo** (la misma pieza que B6-02-0) | `cascada` doble | 5 × 520 | `bk_roe_arbol` | DERIVAR |
| B8-04-1 | **ROE TTM, 12 trimestres, banco vs. grupo y vs. CDI** | `linea` | 4 × 520 | `bk_panel`, `bk_grupo`, `cre_contexto` | LISTO |

### B8 · 05 · Fondeo y capital

Pregunta: ¿cómo se financia y cuánto espacio tiene para crecer?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B8-05-0 | **Mix de fondeo, banco vs. grupo** | `apilada_100` | 5 × 372 | `bk_panel` | DERIVAR |
| B8-05-1 | **Basilea y holgura de crecimiento** | `escala` | 4 × 372 | `bk_capital` | FALTA |

### B8 · 06 · Último publicado

Pregunta: ¿qué dijo el banco en su último resultado y cómo calza con IF.Data?

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B8-06-0 | **Último trimestre publicado (CVM)**: activo, cartera, depósitos, PL, lucro, ROE anualizado, con la base contable rotulada | `tabla` | 5 × 372 | `bk_publicado` | FALTA |
| B8-06-1 | **Puente IF.Data ↔ publicado**: diferencia por línea en el último trimestre auditado | `tabla` (T25) | 4 × 372 | `validacion.json` → `bk_puente` | LISTO para los bancos auditados |

### B8 · 07 · Conducta

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B8-07-0 | **Reclamos por millón de clientes: banco vs. grupo, histórico** | `linea` | 9 × 372 | `bk_conducta` | FALTA la serie (hay un corte) |

---

## B9 · Comparador

Rótulo: `9 · COMPARADOR`. Sin narrativa: es la herramienta de consulta.

| Clave | Tarjeta | Componente | Ancho × alto | Datos | Estado |
|---|---|---|---|---|---|
| B9-01-0 | **Los 34 bancos × ~20 métricas**, ordenable por cualquier columna, filtrable por modelo, segmento y propiedad; sparkline de 8 trimestres en ROE, NPL, crecimiento y cuota; descarga CSV del corte visible; clic en un banco → su ficha **[banco]** | `tabla` (T4 + T8) | 9 × auto | `bk_panel` | LISTO (columnas de capital FALTA) |

Riel: selector de trimestre y de grupo.

---

## B10 · Metodología y fuentes

Texto fijo, sin tarjetas de datos: los cinco universos y su rezago; definiciones de cada métrica (desde `bk_metrica`); quiebres de §0.7; ópticas y grupos de §0.5 con la lista de bancos; el puente IF.Data ↔ publicado; las fuentes públicas (BCB IF.Data, SGS, SCR.data, Olinda; IBGE; CVM; BIS) y la fecha de corte de cada una.

---

## Anexo A · Recuento de tarjetas por estado

| Página | LISTO | DERIVAR | FALTA | REF |
|---|---|---|---|---|
| B0 | 3 | 2 | (Basilea dentro de B0-01-0) | — |
| B1 | 5 | 4 | — | 2 |
| B2 | 4 | 7 | — | — |
| B3 | 4 | 3 | 3 | — |
| B4 | 4 | 6 | — | — |
| B5 | 1 | 3 | 1 | 1 |
| B6 | 5 | 4 | — | — |
| B7 | — | — | 5 | 1 |
| B8 | 5 | 5 | 3 | — |
| B9 | 1 | — | — | — |

Lectura: con lo que ya existe se puede construir el esqueleto de todas las páginas salvo Capital. La Ficha (B8), primera maqueta, depende sobre todo de cuatro derivaciones nuevas (`bk_cartera`, percentiles por grupo, `bk_roe_arbol`, `bk_exposicion`) y de dos extracciones (capital y CVM).

## Anexo B · Piezas nuevas para la galería

Se agregan a `pb/pbip/diseno/patrones/` con el procedimiento de `AGENTS.md` antes de construirlas en el sitio:

| Pieza | Qué es | Dónde se usa |
|---|---|---|
| `percentiles` | Una fila por métrica: barra p10–p90 del grupo, marca de mediana, punto del banco (hoy y hace un año) | B8-02-0 |
| `cascada doble` | Dos cascadas paralelas (banco y grupo) con las mismas líneas | B6-02-0, B8-04-0 |
| `burbujas` con trayectoria filtrada | G119 limitado al banco activo y a un grupo | B6-03-0, B2-04-1 |
| `small_multiples` de bancos | 34 paneles con la misma escala y el banco activo resaltado | B4-03-2 |
