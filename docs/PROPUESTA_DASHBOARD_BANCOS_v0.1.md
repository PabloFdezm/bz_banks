# Dashboard Bancos Brasil — Propuesta v0.1

Versión 0.1 · 2-nov-2026 · Autor: Pablo (Principal AM) con Claude. Plataforma inicial: **HTML estático**; después Netlify; réplica parcial en Power BI como tercera etapa.

Este documento es la propuesta de partida. Cuando se apruebe, se parte en tres piezas, igual que el macro: el **esqueleto narrativo** (fuente de verdad de páginas, secciones y preguntas), el **spec de datos** (contrato de tablas para Claude Code) y los **specs web** por página (para el LLM que construye). Hasta entonces, lo que diga este archivo manda.

---

## 0. Qué es y qué no es

**Para quién.** Analistas buy-side de renta variable y PM que invierten en bancos brasileños. La misma persona lo usa de dos formas: sola, para monitorear qué cambió en el trimestre, y frente a otros, como apoyo visual mientras presenta («PPT con esteroides»).

**Qué cuenta.** De arriba hacia abajo: condiciones macro → sistema → segmentos → banco. Cada página empieza en el driver, sigue con la respuesta del sistema y termina en cómo se reparte entre bancos.

**Qué no es.** No es un informe con tesis: en pantalla no hay conclusiones de inversión, las saca quien presenta. Los títulos afirman hechos verificables («La mora PF de bancos digitales sube por tercer trimestre»), no opiniones. Tampoco reemplaza al Monitor Brasil: lo macro que entra acá es solo lo que mueve a los bancos.

**Relación con lo existente.**

| Pieza | Qué se hace con ella |
|---|---|
| `preparar_bancos_powerbi.py` → `preparar_metricas_bancos.py` → `metricas_bancos.parquet` | Se conserva. Es el núcleo de cálculo por banco (eras COSIF, crédito total auditado, TTM, ROE/ROA, CoR, cobertura, eficiencia, cuotas) |
| `bancos_web/backend/validacion.json`, `tests/auditoria/`, `bancos_web/pipeline/verificar.py` | Se conservan y se extienden a las fuentes nuevas |
| `pb/cre_*` (cartera por tipo, modalidad, calidad) | Se conserva como insumo |
| Tablas macro de `pb/` (`fh_deuda`, `hsf_mensual`, `hogares_modalidades`, `tasa_real_exante`, `cpib_componentes`, `hcs_ahorro`, `tasas_pnad`, `ingreso_pnad`…) | Se leen tal cual. No se copian: si el Monitor Brasil corrige una serie, se corrige acá |
| Front de `bancos_web` (FastAPI + React, v1/v2) | Se archiva. No sigue la arquitectura estática ni el sistema visual del Monitor Brasil |
| Páginas «Banking» del PBIP dual | Siguen siendo macro-crédito y se quedan en el Monitor Brasil |
| FARO (`brazilian-banks-desk`) | Este proyecto es su rediseño desde cero; el repo se decide en §8 |

---

## 1. Decisiones de arquitectura

1. **HTML primero, y construido para aprovechar el HTML.** En el macro el HTML fue maqueta de Power BI. Acá es al revés: el producto es el sitio, y Power BI replica lo que pueda (§7). Eso permite diseñar interacciones que Power BI no tiene (§2).
2. **Mismo sistema de diseño que el Monitor Brasil.** Usa `tokens.json` (navy/cobre, Segoe UI, fondo `#F4F4F4`), la galería de patrones (`INDICE.md`), la anatomía de página AM (cabecera, apertura PG3, secciones con riel de 452 px y cuerpo de 1 388 px, cierre PG4) y las reglas de color de signo. Las piezas que falten se agregan a la galería, no se inventan por página.
3. **Python calcula; el navegador filtra y dibuja.** Toda transformación financiera (TTM, promedios, aportes, percentiles, alineación de frecuencias, grupos de pares) se hace en el pipeline. El JavaScript solo filtra, ordena, re-basa y cambia de banco. Es la misma regla del macro y la que permite replicar en Power BI sin rehacer cálculos.
4. **Stack del sitio.** HTML, CSS y JS sin frameworks ni bundler, módulos ES nativos, ECharts 5.5.1 local con renderizador SVG, datos en JSON exportados desde los Parquet gold. Es el mismo stack de `SPEC_WEB_00_GENERAL.md`, así que los dos sitios comparten componentes.
5. **Un pipeline, dos sitios.** El código de bancos vive en el mismo repo y escribe con `almacen.py` (crudo/derivado con manifiesto). Gold de bancos en `pb/Banks/` (Parquet) y su espejo JSON en el sitio.

---

## 2. Qué aprovechamos del HTML

Lo que justifica partir en HTML y no en Power BI:

| Capacidad | Para qué sirve acá | ¿Replicable en Power BI? |
|---|---|---|
| **Banco activo global** en la URL (`/ficha/?banco=itau`, `?pares=s1`) | Toda página resalta el banco elegido contra su grupo de pares; un link abre exactamente la vista que se presentó | Parcial (slicer sincronizado; sin link profundo) |
| **Modo presentación** (tecla `P`) | Cada sección pasa a lámina 16:9 a pantalla completa, con flechas para avanzar y el banco activo conservado. Es el «PPT con esteroides» sin exportar nada | Parcial (bookmarks + modo pantalla completa) |
| **Pequeños múltiplos de 34 bancos** | Un panel por banco con la misma escala, para ver en una pantalla quién se aparta | Sí, nativo |
| **Dispersión con trayectoria** | Cada banco como un punto con su cola de 8 trimestres (ROE vs. CoR, crecimiento vs. mora) | Solo con Deneb |
| **Quiebres anotados** en los ejes | COSIF 2025, Res. 4966/E–H desde 2025, hueco 2024-T4 del BCB y cambios de perímetro, marcados donde ocurren | Parcial (líneas constantes, sin texto en eje) |
| **Comparar dos cortes** (trimestre actual vs. elegido) | Tabla y gráficos con «antes/ahora» sin duplicar visuales | Sí, con dos slicers |
| **Comparador (screener)** ordenable, con mini-gráficos por fila | Una tabla de 34 bancos × todas las métricas, filtrable por segmento | Sí, nativo (sin sparklines finas) |
| **Definición al pasar el mouse** sobre cada métrica | Cómo se calcula, de qué fuente, en qué universo | Parcial (tooltip de página) |
| **Exportar** PNG de la tarjeta y CSV de sus datos | Llevar una tarjeta a un comité o a un modelo | Sí, nativo para datos |
| **Imprimir a PDF** con hoja de estilo propia | Dejar la presentación a los PM después de la reunión | Sí, nativo |

---

## 3. Convenciones transversales

### 3.1 Cinco universos de datos, siempre rotulados

| Universo | Fuente | Frecuencia y rezago | Cubre | Rótulo en pantalla |
|---|---|---|---|---|
| **Sistema** | BCB-SGS (crédito, mora, tasas, spreads, comprometimiento) | Mensual, ~2 meses | Todo el SFN | «Sistema · BCB» |
| **Panel** | IF.Data, conglomerado prudencial | Trimestral, ~3 meses | 34 conglomerados | «Panel IF.Data · 34 conglomerados» |
| **Segmentos** | SCR.data | Mensual, ~2 meses | Por tipo de institución, modalidad, porte, UF, CNAE; no por banco | «SCR · por segmento» |
| **Publicado** | CVM (ITR/DFP) | Trimestral, al publicar resultados | Cotizados; IFRS o BR GAAP consolidado | «Publicado · CVM» |
| **REF** | Planilla de datos de los gráficos del Relatório de Estabilidade Financeira (confirmar que se sigue publicando) | Semestral (abril y octubre) | Series de supervisión que no se pueden calcular (LCR, PD, estrés) | «BCB · REF [mmm-aa]» |

Reglas:
- Dos universos nunca comparten eje como si fueran la misma serie. Se comparan tendencias, no niveles.
- El universo Sistema hace de **adelanto** del trimestre que IF.Data todavía no publica. En la portada, el último dato del Panel y el del Sistema se muestran con sus fechas, uno al lado del otro.
- El universo Publicado existe para cerrar el rezago en temporada de resultados. Nunca reemplaza al Panel en las páginas de sistema.

### 3.2 Segmentación

**Segmentos del BCB** como eje de competencia: S1 privados, Públicos, Digitales, Cooperativas (SNCC) y Demás. Reemplazan las categorías actuales (`nucleo`, `fintech_pago`, `publico_listado_regional`, `publico_no_listado`) para que las cifras sean comparables con el REF. La asignación de cada uno de los 34 conglomerados se escribe en `definiciones/bancos__segmentos.json`, con fuente y fecha.

**Grupos de pares** para las fichas: se usa el `modelo_negocio` que Pablo ya fijó el 2026-10-08 en `definiciones/bcb_ifdata__bancos_balances.json` (corrección del 2-nov: la primera versión de esta propuesta inventaba otros grupos).

| Grupo | Bancos |
|---|---|
| Grandes | Itaú, Bradesco, Banco do Brasil, Santander, Caixa, BTG Pactual |
| Digitales | Nubank, XP, C6, Inter, Agibank, Original, Neon |
| Medianos y nicho | Safra, Votorantim, Daycoval, ABC Brasil, BMG, Mercantil, Pine, Sofisa, Banrisul, Banestes, BRB, Porto Seguro |
| Pagos | Mercado Pago, PagSeguro, Stone, PicPay, Cielo, CloudWalk |
| Desarrollo | BNDES, Banco do Nordeste, Banco da Amazônia |

Banco Pan está dentro del conglomerado prudencial de BTG y no se puede separar en el escopo prudencial.

### 3.3 Definiciones que no se cruzan

| Concepto | Panel IF.Data | Sistema SGS | SCR.data |
|---|---|---|---|
| Mora | Vencido ≥ 15 días por nivel y modalidad (`cre_calidad`) | Atraso > 90 días | Vencido 15–90 y > 90 días; inadimplencia = cartera inadimplente / cartera activa (en R$, no en %) |
| Cartera problemática | Nivel E–H / activos problemáticos desde 2025 (quiebre) | — | Activo problemático |
| Crédito | e+f+g+h (era nueva) / d+e+f (era vieja) | Saldo de la cartera del SFN | Cartera activa |

Cada métrica lleva su definición en el tooltip y en el cierre de la página.

### 3.4 Cálculos

- **TTM**: 4 trimestres consecutivos; si falta uno, NaN. ROE y ROA sobre el promedio de t−4 y t.
- **Cuotas**: el denominador es el Sistema (SGS) cuando existe la serie equivalente; si no, el panel, rotulado como tal.
- **Alineación de frecuencia** (en Python): los saldos se toman a fin de trimestre y los flujos se suman o promedian según corresponda.
- **Deflactor**: IPCA, como en el macro.
- **Ventanas**: 3 años (monitor), ciclo desde 2014 (inicio del panel), máximo.

### 3.5 Color de signo en bancos

Se mantiene la regla del Monitor: color de signo ≠ color de serie. Navy = mejora, cobre-texto = deterioro.

| Sube… | Color |
|---|---|
| ROE, ROA, margen, capital, cobertura, cuota | Navy (mejora) |
| Mora, E–H, costo del riesgo, eficiencia (gasto/ingreso), comprometimiento | Cobre (deterioro) |
| Crecimiento de cartera | Neutro (gris tinta-3): crecer no es bueno ni malo sin contexto |

---

## 4. Estructura del sitio

Cada página sigue la anatomía AM. Cada sección responde una pregunta y declara su driver macro, el universo de datos y el estado del dato:

- **OK**: el dato está en `pb/` o en `metricas_bancos`.
- **DERIVAR**: el crudo existe, falta derivarlo.
- **BAJAR**: falta la extracción.
- **REF**: viene de la planilla semestral del REF.

### B0 · Portada (monitor)

Pregunta: ¿qué cambió en el sistema este trimestre y dónde está el ciclo?

| Sección | Contenido | Estado |
|---|---|---|
| Ahora | 6 cifras del sistema con fecha (crecimiento de crédito, mora PF y PJ, ROE, Basilea, comprometimiento de renta), cada una con el último dato del Panel y del Sistema | OK / DERIVAR (capital) |
| Reloj del ciclo | Selic real ex ante, hiato crédito/PIB (BIS), desempleo y comprometimiento, como posición en su historia | OK (`tasa_real_exante`, `fh_deuda`, `tasas_pnad`) / DERIVAR (BIS credit gap, en crudo) |
| Qué se movió | Tira automática con los 5 mayores cambios trimestrales del panel (cuota, ROE, mora), calculados en Python, sin texto de analista | OK |
| Puertas | Una tarjeta por página con su pregunta y la fecha del último dato | — |

### B1 · Ciclo y condiciones

Pregunta: ¿las condiciones macro empujan o frenan a los bancos?

| Sección | Pregunta | Driver / datos | Estado |
|---|---|---|---|
| Tasa | ¿Qué tan restrictiva es la política y qué espera el mercado? | Selic, Selic real ex ante, trayectoria Focus vs. mercado | OK |
| Crédito amplio | ¿El crédito crece más o menos que la economía, y quién lo da? | Crédito amplio (bancario, mercado de capitales, externo), crédito/PIB, hiato BIS | OK (`cpib_componentes`) / BAJAR (crédito amplio SGS) |
| Hogares | ¿Los hogares pueden pagar? | Comprometimiento de renta (SGS 29034/29037), deuda/renta, desempleo, renta real | OK |
| Empresas | ¿Las empresas pueden pagar? | Crédito PJ por porte, activos problemáticos por porte (SCR), crédito garantizado (FGI, Pronampe) | OK (`scrdata_pj_*`, FGO/FGI) |
| Desintermediación | ¿Cuánto crédito se va del balance bancario? | Debentures, FIDC, CRI/CRA vs. crédito bancario | BAJAR (CVM/ANBIMA) o REF |

### B2 · Estructura y competencia

Pregunta: ¿quién gana y quién pierde cuota, y en qué cartera?

| Sección | Pregunta | Datos | Estado |
|---|---|---|---|
| Concentración | ¿El sistema se concentra o se abre? | Cuota top 5, HHI en activo, crédito y depósitos | OK (derivar HHI) |
| Cuota por segmento | ¿Qué segmento gana cuota? | Cuota de S1 privados, públicos, digitales y cooperativas, en crédito PF/PJ y depósitos | DERIVAR (segmentación) |
| Cuota por modalidad | ¿Dónde compiten los digitales? | Cuota por modalidad (tarjeta, personal, consignado, vehículos, inmobiliario, PJ) por banco | OK (`cre_panorama`) |
| Riesgo por segmento | ¿Crecer cuota cuesta mora? | Inadimplencia por tipo de institución (banco, financiera, fintech, cooperativa) | OK (SCR agregado) / DERIVAR (historia y PF) |
| Precio y servicio | ¿Compiten en precio o en servicio? | Tarifas por grupo, ranking de reclamos por millón de clientes, Pix | OK (CSV en el catálogo de fuentes) / DERIVAR a serie |

### B3 · Crédito

Pregunta: ¿cuánto crece la cartera, en qué y quién la empuja?

| Sección | Pregunta | Datos | Estado |
|---|---|---|---|
| Crecimiento | ¿A qué ritmo crece, real y nominal? | Sistema mensual (SGS) + panel trimestral | OK |
| Aportes | ¿Qué modalidades y qué bancos explican el crecimiento? | Aportes por tipo y por banco | OK (`cre_panorama`) |
| Mix por banco | ¿Qué tan riesgosa es la cartera de cada banco? | Peso de tarjeta, personal, consignado, PJ e inmobiliario por banco | OK |
| Aperturas | ¿A quién le prestan? | Cartera por porte del tomador, indexador, región, CNAE y plazo, por banco | BAJAR (informes de IF.Data no colectados) |
| Dirigido y rural | ¿Cuánto es crédito con subsidio o garantía? | Rural (SICOR), BNDES, FGI/Pronampe | OK en crudo / DERIVAR |

### B4 · Calidad

Pregunta: ¿se está deteriorando la cartera, dónde y quién está más expuesto?

| Sección | Pregunta | Datos | Estado |
|---|---|---|---|
| Sistema | ¿La mora sube o baja, y está en máximos? | Mora > 90 días PF/PJ (SGS) con bandas históricas; nota sobre la política de baja a pérdida de 2025 (Boxe 2 del REF) | OK |
| Adelanto | ¿Qué anticipa la mora de los próximos trimestres? | Mora temprana 15–90 días por modalidad (SCR, `hogares_modalidades`) contra desempleo y comprometimiento | OK / DERIVAR (SCR PF) |
| Por banco | ¿Qué banco se deteriora más rápido? | NPL ≥ 15 días, E–H, costo del riesgo TTM, cobertura | OK |
| Exposición × driver | ¿Qué cartera de qué banco está en el segmento que más se deteriora? | Mix de IF.Data × mora por modalidad del Sistema (cálculo en Python) | DERIVAR |
| Empresas | ¿Qué porte y qué sector se deterioran? | Activos problemáticos por porte y CNAE (SCR) | OK (PJ) |

### B5 · Fondeo y liquidez

Pregunta: ¿cómo se fondean los bancos y cuánto les cuesta?

| Sección | Pregunta | Datos | Estado |
|---|---|---|---|
| Mix | ¿Depósitos, compromissadas o emisiones? | Pasivo por instrumento y banco | OK (`panel_bancos_wide`) |
| Ahorro | ¿El ahorro va a depósitos bancarios o sale del balance? | CDB vs. poupança vs. Selic | OK (`hcs_ahorro`) |
| Calce | ¿Cuánto del crédito está financiado con depósitos? | Crédito/depósitos por banco | OK |
| Costo | ¿Quién paga más por fondearse? | Gasto de captación / pasivo con costo (aproximación implícita); tasas en % del DI por segmento | DERIVAR / REF |
| Liquidez | ¿Hay holgura? | LCR, NSFR agregados y dispersión | REF |

### B6 · Rentabilidad

Pregunta: ¿quién gana dinero, por qué y qué tan sostenible es?

| Sección | Pregunta | Datos | Estado |
|---|---|---|---|
| Sistema y segmentos | ¿La rentabilidad sube o baja, y en qué segmento? | ROE/ROA TTM por segmento | OK |
| Descomposición del ROE | ¿Qué explica la diferencia de ROE entre bancos? | Margen financiero, tarifas, costo del riesgo, gasto, impuestos y apalancamiento, en % del activo promedio, por banco contra su grupo | DERIVAR (sobre `metricas_bancos`) |
| ROE vs. riesgo | ¿Rentabilidad comprada con riesgo? | Dispersión ROE vs. costo del riesgo con trayectoria de 8 trimestres | OK |
| Sensibilidad a la Selic | ¿A quién le favorece una Selic alta? | Margen trimestral vs. Selic promedio por banco (beta en Python) | DERIVAR |
| Eficiencia | ¿Quién gana escala? | Eficiencia TTM y crecimiento de gastos vs. ingresos | OK |

### B7 · Capital

Pregunta: ¿cuánto capital sobra para crecer o repartir?

| Sección | Pregunta | Datos | Estado |
|---|---|---|---|
| Niveles | ¿Dónde está cada banco contra su mínimo? | Basilea, nivel 1, capital principal vs. requerimiento | BAJAR (serie completa del informe de capital; hoy hay 5 cortes sueltos) |
| Generación | ¿El capital crece por resultados o por emisión? | Variación del capital principal: resultado − dividendos ± otros | DERIVAR |
| Consumo | ¿Cuánto RWA consume cada real de crédito? | Densidad de RWA, RWA por tipo de riesgo | BAJAR |
| Holgura de crecimiento | ¿Cuánto puede crecer la cartera sin capital nuevo? | Exceso sobre el mínimo / densidad de RWA (cálculo propio) | DERIVAR |
| Estrés | ¿Aguanta un escenario adverso? | Resultado agregado del test de estrés | REF |

### B8 · Ficha por banco (plantilla única)

Pregunta: ¿cómo está este banco frente a sus pares en todo lo anterior?

Una sola plantilla para los 34; se publica completa para los cotizados (Itaú, Bradesco, BB, Santander, BTG, Nubank, Inter, ABC, Banrisul, BMG, XP, Stone, PagSeguro) y en versión «solo panel» para el resto.

| Sección | Contenido |
|---|---|
| Identidad | Segmento, grupo de pares, tamaño, cuotas y último trimestre disponible por universo (Panel y Publicado) |
| Posición | Percentil del banco dentro de su grupo en ~12 métricas (crecimiento, mix, NPL, CoR, cobertura, margen, eficiencia, ROE, Basilea, crédito/depósitos) |
| Crédito y calidad | Mix de cartera, aportes al crecimiento, NPL por modalidad contra la mora del Sistema en esa modalidad |
| Rentabilidad | Descomposición del ROE del banco vs. la mediana del grupo |
| Capital | Basilea y holgura de crecimiento |
| Último publicado | Cifras del ITR (CVM) cuando sean más recientes que IF.Data, rotuladas como base distinta, con el puente de `validacion.json` |
| Conducta | Reclamos y tarifas |

### B9 · Comparador

Tabla de los 34 bancos × métricas, ordenable y filtrable por segmento y grupo, con mini-gráfico de 8 trimestres por celda clave y descarga CSV. No tiene narrativa; es la herramienta de consulta que hoy hace `bancos_web`.

### B10 · Metodología y fuentes

Universos, definiciones, quiebres (COSIF 2025, Res. 4966, hueco 2024-T4), segmentación, el puente IF.Data ↔ publicado y la fecha de corte de cada fuente.

### Fuera de la v1: valuación

P/VL vs. ROE sostenible y P/U vs. crecimiento con datos del pipeline de Bloomberg. Queda para después por una razón de licencia: los datos de Bloomberg no se pueden publicar en un sitio abierto. Si se agrega, va solo en la versión local o detrás de acceso restringido, nunca en el JSON público.

---

## 5. Datos: inventario y extracciones nuevas

### 5.1 Lo que ya está y entra tal cual

`metricas_bancos.parquet` y `panel_bancos_wide.csv` (34 × 50 trimestres, 2014Q1–2026Q2); `pb/Banks/*`; `pb/cre_*`; tablas macro de `pb/` listadas en §0; `scrdata_pj_agregado` y `scrdata_pj_submodalidad`; crudo de BIS credit gap, SICOR, FGO/Pronampe y BNDES-FGI; CSV del catálogo de fuentes (reclamos 2T26, tarifas, medios de pago, SCR agregado por segmento y UF).

### 5.2 Extracciones nuevas, en orden

| # | Qué | Fuente | Para qué páginas | Esfuerzo |
|---|---|---|---|---|
| 1 | Serie trimestral completa del informe de capital | IF.Data (`ifdata.py colectar`) | B7, B8 | Bajo |
| 2 | Aperturas de cartera por banco: nivel de riesgo, indexador, región, porte, CNAE, plazo | IF.Data | B3, B4, B8 | Bajo–medio |
| 3 | SCR.data PF derivado e historia desde 2012 | SCR.data ZIP anuales | B2, B4 | Medio (archivos de cientos de MB) |
| 4 | Crédito amplio y series de spread/ICC del SGS que falten | SGS | B1, B6 | Bajo |
| 5 | ITR y DFP de los cotizados | CVM | B8 | Medio (mapear plan de cuentas por banco) |
| 6 | Planilla de datos de los gráficos del REF, semestral | BCB | B5, B7 | Bajo, si sigue publicándose |
| 7 | Reclamos y tarifas como serie histórica (hoy un solo corte) | BCB REST / Olinda | B2, B8 | Bajo |
| 8 | Mercado de capitales (debentures, FIDC, CRI/CRA) | CVM o REF | B1 | Medio; se puede cubrir con el REF al inicio |

### 5.3 Contrato de datos (resumen; el detalle va en el spec de datos)

| Tabla gold | Grano | Uso |
|---|---|---|
| `dim_banco` | cod_inst | Nombre, segmento BCB, grupo de pares, cotizado (sí/no), ticker, color fijo |
| `dim_metrica` | metrica | Nombre, unidad, definición, universo, fuente, signo (mejora/deterioro/neutro), formato |
| `fact_panel` | banco × trimestre × métrica | Todo lo de IF.Data, ya calculado, con percentil dentro del grupo y del sistema |
| `fact_sistema` | serie × mes | SGS y tablas macro, alineado; versión trimestral derivada |
| `fact_scr` | segmento × modalidad × porte × mes | SCR agregado con la tasa oficial |
| `fact_publicado` | banco × trimestre × línea | CVM, con su puente al panel |
| `fact_ref` | serie × semestre | Planilla del REF |
| `qcambio` | página × orden | La tira «Qué se movió», generada en Python |
| `manifiesto` | — | Fecha de corte por universo, versión del pipeline y hash de cada tabla |

`exportar_datos_web_bancos.py` convierte gold a JSON por página. El verificador (`verificar.py`) se extiende con: segmentos que suman el sistema, no regresión de períodos por universo, y coherencia de las fechas de corte de la portada.

---

## 6. Plan por fases

| Fase | Entregable | Criterio de salida |
|---|---|---|
| **F0 · Definiciones** | Esqueleto narrativo v0.1 (páginas, secciones, preguntas, jerarquía) + `bancos__segmentos.json` + inventario de datos con estado | Pablo aprueba estructura y segmentación |
| **F1 · Maquetas** | Tres páginas en HTML con el sistema del Monitor: Portada (B0), Rentabilidad (B6) y Ficha (B8), con cifras en corchetes, más el modo presentación funcionando | Se ven bien en 1 920 px y en lámina 16:9; las piezas nuevas entran a la galería |
| **F2 · Datos** | Extracciones 1–4 de §5.2 + gold + JSON + verificador extendido | Verificador sin errores; cada tarjeta de las maquetas tiene su columna mapeada |
| **F3 · Sitio v1** | B0–B10 con datos reales, sin `[` publicado | Checklist de publicación del macro (§12 del spec web) aplicado a bancos |
| **F4 · Netlify** | Deploy, rutina de refresco trimestral (IF.Data) y mensual (SGS/SCR), y acceso definido | Una actualización completa corrida de punta a punta |
| **F5 · Power BI** | Réplica de las páginas de sistema (B1–B7) y la ficha vía drill-through, leyendo los mismos Parquet gold | Cifras idénticas a las del sitio en el mismo corte |

Extracciones 5–8 se suman entre F3 y F4. La CVM (5) es la prioridad antes de la primera temporada de resultados que se presente con el tablero.

---

## 7. Netlify y Power BI: lo que hay que tener en cuenta desde ahora

**Netlify.** El sitio es estático y los datos son públicos (BCB, IBGE, CVM). Lo que no es público es el encuadre (grupos de pares, selección, marca). Antes de publicar hay que decidir el acceso: link abierto sin indexar, contraseña del sitio (revisar si el plan de Netlify la incluye) o un acceso corporativo delante. Bloomberg queda fuera de cualquier versión publicada.

**Power BI.** La réplica es viable porque nada se calcula en el navegador: Power BI lee los mismos Parquet gold. No se replican el link profundo por banco, el modo presentación tal cual (se aproxima con bookmarks) ni las dispersiones con trayectoria (requieren Deneb). Por eso F5 replica primero las páginas de sistema, donde Power BI no pierde nada, y deja la ficha como drill-through.

---

## 8. Decisiones abiertas para Pablo

1. **Repo.** ¿Vive en este repo (`bcb-scraper`, con su pipeline) y el sitio en `pb/pbip/diseno/bancos/`, o en `brazilian-banks-desk` (FARO) consumiendo los JSON exportados? La recomendación es un solo repo para los datos y el sitio en una carpeta propia.
2. **Grupos de pares** de §3.2 (tu `modelo_negocio`): ¿lo mantienes para las fichas? Puntos a revisar: XP en Digitales, BTG en Grandes y PicPay en Pagos.
3. **Texto en pantalla.** La propuesta es títulos que afirman hechos y una tira «Qué se movió» automática, sin lecturas del analista. ¿O quieres el espacio de «Qué cambió» con texto propio, como en el Monitor Brasil?
4. **Cotizados con ficha completa.** ¿La lista de §B8 está bien? ¿Agregar Banco Pan (dentro de BTG en el panel) o los bancos listados en EE.UU. que no son bancos en Brasil?
5. **Idioma.** ¿Español, como el Monitor, o inglés para usarlo con PM de otras regiones?
6. **Primera maqueta.** La propuesta es partir por la Ficha (B8), porque es la página que más se usa al presentar y obliga a resolver la segmentación, los grupos de pares y el modo presentación de una vez.
