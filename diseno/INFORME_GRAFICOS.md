# Informe de gráficos de Monitor Brasil

**Fecha del inventario:** 5 de noviembre de 2026.  
**Objetivo:** organizar todos los tipos de visualización del sitio original para repetir el proceso de inspección, propuestas, selección, maqueta funcional y guía detallada para LLMs, aprovechando las repeticiones.

## 1. Resultado principal

El sitio referencia **155 tarjetas analíticas en seis páginas**, utilizando **40 nombres técnicos de componentes**. Propongo organizarlas en **24 familias visuales de trabajo**, más los recursos auxiliares de los encabezados de sección y los micrográficos internos.

**No hacen falta 155 maquetas independientes.** Se puede definir un patrón por familia y resolver sus variantes semánticas con datos y configuración. Las 24 familias son una taxonomía de trabajo de este informe, no una decisión ya aprobada de agrupar o sustituir componentes.

Tres familias concentran 89 de las 155 tarjetas: líneas (53), tablas analíticas (20) y columnas (16). Empezaría por líneas, después tablas y columnas. En paralelo, el patrón de relojes ya sirve como precedente de la metodología.

### Qué representa cada cifra

- **Tarjeta:** una instancia identificada por una clave como AM2-04-1 y referenciada por el diseño actual de una página.
- **Componente técnico:** el nombre que la tarjeta pasa al registro del dibujante, como linea, lineaL o serie_tiempo.
- **Familia visual:** agrupación propuesta por geometría dominante y tarea de lectura, no solo por nombre de función.
- **Variante:** cambio de semántica, unidad, interacción, estadístico o composición que merece un caso representativo.
- **Micrográfico:** geometría interna de una tabla, panel o encabezado. No aumenta el número de tarjetas.

Una tarjeta con veinte miniseries sigue contando como una tarjeta. A su vez, una tabla puede contener una matriz que debe revisarse como matriz y no únicamente como texto tabular.

## 2. Alcance y evidencia

Se inventarió el sitio original situado en:

`C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site`

Se cruzaron las claves del diseño actual de las seis páginas con sus definiciones, el registro compartido de componentes y los registros específicos. En AM1–AM5 los títulos proceden de BASE y los adaptadores de derivados; AM6 define sus tarjetas directamente en paginas/am6.js.

Se incluyen las tarjetas que el código actual referencia, también cuando están configuradas como FALTA. Se separan diez definiciones que existen en el código pero no aparecen en el diseño actual. No se cuentan como gráficos analíticos las seis tarjetas de navegación de la portada, la plantilla AM0, las páginas de prueba de componentes ni los prototipos locales de propuestas.

### Cobertura de la inspección

- **Inventario estructural:** las 155 claves quedaron relacionadas con una definición y un componente.
- **Clasificación funcional:** se revisaron registros, adaptadores y dibujantes relevantes para distinguir familias y variantes.
- **Revisión visual previa:** se reutiliza el trabajo realizado para los relojes y sus referencias.
- **Inspección visual de las 155 tarjetas, sus controles y todos sus estados:** pendiente del proceso por familia.

Este documento no asigna puntuaciones estéticas ni declara probados los 155 gráficos. Los apartados de mejora son hipótesis y criterios de inspección, salvo los comportamientos que se identifican expresamente como observados en el código. Tampoco se ejecutaron las derivaciones de datos para certificar disponibilidad en tiempo de ejecución.

Los enlaces de las claves del anexo llevan al adaptador correspondiente en el código original. Las líneas reflejan la copia consultada y pueden desplazarse si el sitio se edita.

## 3. Distribución por página y estado configurado

| Página | Tarjetas | LISTO | DERIVAR | FALTA |
| --- | ---: | ---: | ---: | ---: |
| [Actividad](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am1.js>) | 22 | 8 | 14 | 0 |
| [Inflación](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am2.js>) | 22 | 6 | 16 | 0 |
| [Mercado laboral](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am3.js>) | 49 | 38 | 8 | 3 |
| [Fiscal](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am4.js>) | 23 | 22 | 0 | 1 |
| [Hogares](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am5.js>) | 25 | 25 | 0 | 0 |
| [Expectativas](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js>) | 14 | 12 | 2 | 0 |
| **Total** | **155** | **111** | **40** | **4** |

**Interpretación importante:** DERIVAR no significa “sin implementar”. Son tarjetas cuyo adaptador prepara la entrada con cálculos locales. LISTO tampoco equivale a una prueba satisfactoria: una tabla vacía, una dependencia ausente o una derivación sin resultado pueden llevarla a “en preparación”.

En pagina.js se bloquean explícitamente FALTA y TERCEROS. Entre las tarjetas referenciadas no se encontró ninguna configurada como TERCEROS. El resultado de la carga y del adaptador también puede producir un estado vacío o un error, independientemente de la etiqueta inicial.

## 4. Mapa de las 24 familias

Los conteos son de **asignación principal**, para no sumar una tarjeta dos veces. Las variantes incrustadas se describen después.

| Familia | Tipo de visualización | Tarjetas | Páginas | Prioridad propuesta |
| --- | --- | ---: | --- | --- |
| [F01](#f01) | Series temporales de líneas | 53 | AM1, AM2, AM3, AM4, AM5, AM6 | P1 |
| [F02](#f02) | Columnas, aportes y combinaciones barra/línea | 16 | AM2, AM3, AM4, AM5 | P1 |
| [F03](#f03) | Tablas analíticas y tablas con micrográficos | 20 | AM1, AM2, AM3, AM4, AM5 | P1 |
| [F04](#f04) | Cascadas o puentes de descomposición | 8 | AM3, AM4, AM5 | P1 |
| [F05](#f05) | Dispersión, burbujas y comparaciones sectoriales | 10 | AM1, AM3, AM5 | P1 |
| [F06](#f06) | Trayectorias en dos variables y relojes del ciclo | 5 | AM2, AM3, AM4, AM5 | P0 · base ya definida |
| [F07](#f07) | Barras horizontales de magnitud o divergencia | 9 | AM3, AM4, AM5 | P1 |
| [F08](#f08) | Composición horizontal y barras de 100 | 3 | AM3, AM4, AM5 | P2 |
| [F09](#f09) | Paneles múltiples y series sincronizadas | 4 | AM3, AM5 | P2 |
| [F10](#f10) | Comparación antes/después o pesas | 6 | AM3, AM5, AM6 | P2 |
| [F11](#f11) | Perfiles de desvío y KPI con pistas | 3 | AM2, AM5 | P2 |
| [F12](#f12) | Mosaico de unidades federativas | 2 | AM3 | P2 |
| [F13](#f13) | Bandas de distribución o abanico | 1 | AM2 | P2 |
| [F14](#f14) | Cajas, rangos y distribución por categoría | 2 | AM2, AM6 | P2 |
| [F15](#f15) | Convergencia de expectativas al dato publicado | 1 | AM6 | P2 |
| [F16](#f16) | Matrices de calor y matrices de escenarios | 4 | AM1, AM2, AM4 | P2 |
| [F17](#f17) | Calendario de sorpresas | 1 | AM6 | P2 |
| [F18](#f18) | Panel de señales con anticipación | 1 | AM2 | P2 |
| [F19](#f19) | Área apilada temporal | 1 | AM3 | P3 |
| [F20](#f20) | Flujos Sankey | 1 | AM3 | P3 |
| [F21](#f21) | Treemap de composición jerárquica | 1 | AM4 | P3 |
| [F22](#f22) | Pictograma cuantitativo de bloques | 1 | AM5 | P3 |
| [F23](#f23) | Dos caminos por tramos y brecha | 1 | AM6 | P3 |
| [F24](#f24) | Escala de posición respecto de zonas | 1 | AM6 | P3 |

P0 indica un precedente ya definido, no una revisión pendiente de todas sus instancias. P1 prioriza alcance y reutilización; P2, variantes y riesgos de interpretación; P3, tipos especializados. **No son niveles de error visual comprobado.**

### Dos asignaciones que evitan una clasificación engañosa

- AM1-03-2 usa tabla_am1, pero su lectura dominante es una matriz mensual de amplitud: se asigna a F16.
- AM2-02-2 usa tabla_am1, pero su lectura dominante es la distribución histórica por fila: se asigna a F14.

Las otras doce tarjetas que nombran tabla_am1 quedan en F03. Esta separación permite diseñar por tarea visual y seguir compartiendo primitivas de código.

## 5. Fichas por familia: qué revisar y qué prototipar

Cada ficha separa descripción, variantes, criterios de inspección y una dirección de exploración. Las ideas de compacto y ampliado son propuestas para la siguiente etapa; no se han implementado por anticipado.

<a id="f01"></a>

### F01 · Series temporales de líneas

**Alcance:** 53 tarjetas; componentes `linea`, `lineaL`, `serie_tiempo`. Incluye 1 tarjeta(s) configurada(s) como FALTA.

Evolución de una o varias variables en el tiempo. Es la familia de mayor alcance y reúne el dibujante compartido, la variante con leyenda y la variante fiscal.

**Variantes que conservar:** Serie simple; comparación de varias series; observado frente a referencia o contrafactual; trayectoria de expectativas; relleno entre curvas; bandas de incertidumbre; episodios y anotaciones.

**Casos piloto:**

- [AM2-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:886>) — IPCA y núcleos desde 2008
- [AM1-01-4](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1010>) — Índices de actividad, a/a
- [AM4-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:449>) — Primario observado contra el que estabiliza la deuda
- [AM5-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:479>) — Consumo, ingreso y el consumo que habría sido
- [AM6-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:149>) — La expectativa de cada año, encuesta tras encuesta

**Inspección dirigida:** Densidad de series y leyendas; continuidad ante faltantes; calendario y rezagos; referencias de cero/meta; unidades y dominios; diferenciación entre observado, expectativa y contrafactual.

**Propuesta para el compacto:** Mostrar una comparación principal, las referencias necesarias y una jerarquía inequívoca de series. Mantener identificable la última fecha.

**Propuesta para Agrandar:** Abrir la misma selección con más espacio; permitir consultar fechas y series; mostrar definiciones, referencias y, cuando aporten, paneles separados o valores tabulados.

**Invariantes y precauciones semánticas:** No unir por posición de fila datos con fechas distintas. No confundir una banda de percentiles con un intervalo de pronóstico. Los rellenos de brecha requieren probar cruces y valores negativos.

**Todas las instancias de esta familia:** `AM1-01-4`, `AM1-01-6`, `AM1-04-0`, `AM1-04-2`, `AM1-06-0`, `AM1-06-1`, `AM1-06-3`, `AM1-05-0`, `AM1-05-2`, `AM2-00-1`, `AM2-00-3`, `AM2-02-1`, `AM2-03-1`, `AM2-03-2`, `AM2-03-3`, `AM3-01-0`, `AM3-02-1`, `AM3-02-2`, `AM3-05-1`, `AM3-06-1`, `AM3-06-2`, `AM3-06-3`, `AM3-07-3`, `AM3-09-4`, `AM3-09-7`, `AM3-10-1`, `AM3-10-3`, `AM3-11-0`, `AM4-02-0`, `AM4-03-1`, `AM4-04-1`, `AM4-04-2`, `AM4-04-3`, `AM4-05-1`, `AM4-05-2`, `AM4-06-0`, `AM4-08-1`, `AM4-09-0`, `AM5-02-0`, `AM5-03-1`, `AM5-05-3`, `AM5-05-5`, `AM5-06-3`, `AM5-07-1`, `AM5-08-1`, `AM5-08-3`, `AM6-02-0`, `AM6-02-2`, `AM6-04-1`, `AM6-05-0`, `AM6-06-1`, `AM6-06-2`, `AM6-06-3`.

<a id="f02"></a>

### F02 · Columnas, aportes y combinaciones barra/línea

**Alcance:** 16 tarjetas; componentes `columnas`. 

Magnitudes por fecha o categoría. El mismo componente admite columnas normales, apiladas y una línea adicional.

**Variantes que conservar:** Columna simple; varias series; contribuciones apiladas; valores positivos y negativos; columna con línea superpuesta.

**Casos piloto:**

- [AM2-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:634>) — Aportes al IPCA por grupo
- [AM2-06-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1320>) — Exceso sobre la meta: descomposición del BCB
- [AM3-02-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:459>) — Brecha de desocupación
- [AM4-07-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:817>) — Impulso del gasto

**Inspección dirigida:** Número de grupos y colores; ancho de barra; etiquetas de fecha; lectura de negativos; escala que cubra el total apilado y la línea; diferencia entre nivel y contribución.

**Propuesta para el compacto:** Priorizar total y principales componentes. Hacer visibles cero, unidad y fecha; conservar categorías que el negocio exige.

**Propuesta para Agrandar:** Dar espacio a todos los componentes, consulta por fecha y explicación de aportes. Incluir una tabla de contribuciones y comparación temporal cuando sean útiles.

**Invariantes y precauciones semánticas:** No normalizar a 100 % una composición de aportes en pp. No ocultar componentes para que el gráfico se vea limpio sin conservar acceso a ellos.

**Todas las instancias de esta familia:** `AM2-01-0`, `AM2-06-1`, `AM3-02-3`, `AM3-04-3`, `AM3-05-2`, `AM3-08-3`, `AM3-09-2`, `AM3-09-3`, `AM3-10-0`, `AM3-10-4`, `AM3-11-1`, `AM4-05-3`, `AM4-07-2`, `AM5-04-0`, `AM5-06-1`, `AM5-08-2`.

<a id="f03"></a>

### F03 · Tablas analíticas y tablas con micrográficos

**Alcance:** 20 tarjetas; componentes `tabla`, `tabla_am1`, `tabla_gasto`, `sensibilidad_tabla`. 

Vistas en las que comparar valores y categorías en filas es la tarea principal. Algunas celdas contienen barras, tiras de composición, flechas o miniseries.

**Variantes que conservar:** Tabla simple; agrupaciones; filas desplegables; tablas de amplitud; ranking; gasto con barras de peso; sensibilidad con R²; miniseries dentro de una celda.

**Casos piloto:**

- [AM1-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1124>) — Cuántos componentes aceleran en cada agregado
- [AM2-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:719>) — IPCA y sus agregados: cómo vienen y cuán lejos están de la meta
- [AM4-07-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:857>) — El gasto, partida por partida
- [AM5-09-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:951>) — Sensibilidad del consumo al crédito

**Inspección dirigida:** Ancho de columnas, longitud de nombres, alineación numérica, agrupaciones, acceso a hijos, selección/filtros, unidades y lectura móvil. La geometría incrustada requiere su propia revisión.

**Propuesta para el compacto:** Conservar las columnas de mayor uso y una jerarquía estable de filas. Resolver categorías largas sin perder el texto completo.

**Propuesta para Agrandar:** Mostrar detalle de filas, explicaciones, columnas adicionales y controles de consulta realmente útiles. Mantener los estados desplegados y los filtros.

**Invariantes y precauciones semánticas:** No tratar todos los usos de tabla_am1 como una tabla idéntica. AM1-03-2 se asigna a F16 y AM2-02-2 a F14 por su geometría dominante.

**Todas las instancias de esta familia:** `AM1-01-1`, `AM1-01-5`, `AM1-03-0`, `AM1-03-3`, `AM1-04-1`, `AM1-04-3`, `AM1-06-2`, `AM2-00-0`, `AM2-00-2`, `AM2-01-1`, `AM2-02-0`, `AM2-04-0`, `AM2-04-3`, `AM2-05-1`, `AM3-01-2`, `AM3-01-1`, `AM3-04-1`, `AM3-07-2`, `AM4-07-3`, `AM5-09-0`.

<a id="f04"></a>

### F04 · Cascadas o puentes de descomposición

**Alcance:** 8 tarjetas; componentes `cascada`, `cascada_scroll`. 

Explican cómo un valor inicial llega a uno final mediante contribuciones intermedias.

**Variantes que conservar:** Puente de desocupación; masa salarial; consumo; servicio de deuda; deuda pública; gasto fiscal. La variante fiscal cambia etiquetas y habilita scroll en móvil.

**Casos piloto:**

- [AM3-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:522>) — De la desocupación de hace 3 años a la de hoy
- [AM5-02-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:502>) — Del consumo de 2019 al de hoy
- [AM4-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:556>) — De la deuda de hace 3 años a la de hoy
- [AM4-07-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:793>) — Del gasto de 2021 al de hoy

**Inspección dirigida:** Cierre aritmético, signos, conexión entre pasos, rótulos largos, totales inicial/final, residuo y tratamiento de contribuciones pequeñas.

**Propuesta para el compacto:** Destacar inicio, final y contribuciones principales, sin romper la suma. Si hay agrupación, conservar un detalle verificable.

**Propuesta para Agrandar:** Exponer cada paso con nombre completo, valor y explicación. Añadir tabla de conciliación de la suma y períodos inicial/final.

**Invariantes y precauciones semánticas:** Inicio + contribuciones = final, con tolerancia declarada. El residuo debe identificarse. La cascada ampliada no puede cambiar la fórmula del compacto.

**Todas las instancias de esta familia:** `AM3-04-0`, `AM3-06-0`, `AM3-10-6`, `AM4-04-0`, `AM4-07-1`, `AM5-02-1`, `AM5-05-1`, `AM5-05-4`.

<a id="f05"></a>

### F05 · Dispersión, burbujas y comparaciones sectoriales

**Alcance:** 10 tarjetas; componentes `dispersionL`, `burbujas`, `clu_sectores`. Incluye 1 tarjeta(s) configurada(s) como FALTA.

Relacionan dos variables por entidad. Las burbujas añaden tamaño; la variante CLU añade distancia a una diagonal y a una referencia.

**Variantes que conservar:** Momentum; relación con rezago; crédito/empleo; empleo/salario; peso/costo de deuda; salario frente a productividad.

**Casos piloto:**

- [AM1-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1130>) — Momentum de los agregados
- [AM1-05-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1422>) — Brecha e IPCA menos meta 18 meses después
- [AM3-08-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:803>) — Crédito pyme y empleo formal por sector
- [AM3-10-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:987>) — Salario contra productividad, por sector
- [AM5-05-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:666>) — Mapa de la deuda: cuánto pesa y cuánto cuesta

**Inspección dirigida:** Solapamiento de puntos y rótulos, unidades de X/Y, rezagos, selección de entidades, significado del tamaño, referencias y interpretación de correlación.

**Propuesta para el compacto:** Mostrar puntos con una jerarquía de etiquetas limitada y referencias explícitas. Reservar espacio para las entidades destacadas.

**Propuesta para Agrandar:** Permitir inspeccionar entidades, ver nombres completos y acceder a una tabla equivalente. Explicar tamaño, período y referencias sectoriales.

**Invariantes y precauciones semánticas:** Área o radio de burbuja deben tener una regla explícita. La variante CLU representa salario menos productividad: no eliminar su diagonal al unificar el componente.

**Todas las instancias de esta familia:** `AM1-03-1`, `AM1-06-4`, `AM1-06-5`, `AM1-05-1`, `AM1-05-3`, `AM3-08-0`, `AM3-08-1`, `AM3-09-0`, `AM3-10-2`, `AM5-05-2`.

<a id="f06"></a>

### F06 · Trayectorias en dos variables y relojes del ciclo

**Alcance:** 5 tarjetas; componentes `trayectoria`. Incluye 1 tarjeta(s) configurada(s) como FALTA.

Unen observaciones en orden temporal sobre un plano X/Y. Comparten dibujante, pero no todas las tarjetas son el mismo reloj económico.

**Variantes que conservar:** Reloj del IPCA; reloj laboral; crédito/empleo por intensidad laboral; transferencias/participación; inclusión bancaria/deuda.

**Casos piloto:**

- [AM2-04-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1043>) — Reloj del ciclo del IPCA, año a año
- [AM3-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:419>) — Reloj del ciclo laboral
- [AM4-08-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:875>) — Transferencias y participación, año a año
- [AM5-06-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:776>) — Más gente con banco, más deuda

**Inspección dirigida:** Orden temporal, cruces, último dato, marcas de fecha, referencias de cuadrantes y diferencias de frecuencia. La tarjeta AM3-08-2 está bloqueada por datos.

**Propuesta para el compacto:** Usar el reloj depurado ya definido: historia tenue, tres tramos recientes y último punto identificado.

**Propuesta para Agrandar:** Para los dos relojes ya trabajados, reutilizar la maqueta y guía existentes. Para las otras trayectorias, decidir contexto, períodos y bloque relacionado según su pregunta.

**Invariantes y precauciones semánticas:** La secuencia contexto → períodos → reloj laboral es la decisión de la maqueta actual, no una regla para toda trayectoria de la web.

**Todas las instancias de esta familia:** `AM2-04-1`, `AM3-02-0`, `AM3-08-2`, `AM4-08-0`, `AM5-06-2`.

<a id="f07"></a>

### F07 · Barras horizontales de magnitud o divergencia

**Alcance:** 9 tarjetas; componentes `barras_div`, `barras_h`, `barras_fila`. Incluye 1 tarjeta(s) configurada(s) como FALTA.

Comparan valores por categoría. Las divergentes se abren a ambos lados de cero; otras son rankings o barras con un tope.

**Variantes que conservar:** Cambios de ocupación/ingreso; efectos sobre deuda; recaudación; transferencias por programa; crédito por producto.

**Casos piloto:**

- [AM3-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:603>) — Quién trabaja hoy que no trabajaba en 2019
- [AM4-03-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:534>) — Qué mueve la deuda en 12 meses
- [AM4-09-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:939>) — Recaudación real por impuesto
- [AM5-06-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:725>) — Crédito nuevo por producto

**Inspección dirigida:** Orden de filas, ancla en cero, valores negativos, nombres largos, unidades y distinción entre barra real y barra recortada.

**Propuesta para el compacto:** Alinear nombres, pistas y valores. Hacer evidente el cero o el límite de representación.

**Propuesta para Agrandar:** Dar acceso al ranking completo y a nombres/valores exactos, con explicación de signo y escala. Mostrar sin ambigüedad los datos fuera del tope.

**Invariantes y precauciones semánticas:** barras_div tiene implementaciones distintas en Mercado laboral y Fiscal. Un cambio basado solo en el nombre técnico no actualiza automáticamente ambas.

**Todas las instancias de esta familia:** `AM3-05-0`, `AM3-05-3`, `AM3-09-6`, `AM3-10-7`, `AM4-03-2`, `AM4-06-1`, `AM4-09-1`, `AM5-04-1`, `AM5-06-0`.

<a id="f08"></a>

### F08 · Composición horizontal y barras de 100

**Alcance:** 3 tarjetas; componentes `apilada_100`, `barras_cien`. 

Muestran reparto de un total o el peso de partes sobre una base de 100.

**Variantes que conservar:** Distribución de horas; exposición de deuda por moneda/plazo; ingreso, deuda o gasto por cada R$ 100.

**Casos piloto:**

- [AM3-09-5](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:908>) — Horas trabajadas por semana
- [AM4-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:643>) — Deuda por moneda y plazo de repreciación
- [AM5-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:468>) — De cada R$ 100 de ingreso

**Inspección dirigida:** Definición del denominador, segmentos pequeños, orden de partes, legibilidad de rótulos y acceso a las cifras.

**Propuesta para el compacto:** Usar orden estable y etiquetas únicamente donde caben, con consulta para segmentos pequeños.

**Propuesta para Agrandar:** Desplegar denominadores, valores absolutos cuando existan y una tabla completa de partes.

**Invariantes y precauciones semánticas:** apilada_100 normaliza por la suma de partes. barras_cien puede representar una barra parcial y conservar el resto vacío: no son intercambiables.

**Todas las instancias de esta familia:** `AM3-09-5`, `AM4-05-0`, `AM5-01-0`.

<a id="f09"></a>

### F09 · Paneles múltiples y series sincronizadas

**Alcance:** 4 tarjetas; componentes `paneles`, `paneles_tiempo`. 

Una tarjeta contiene varias series dibujadas en paneles separados. La unidad de inventario es la tarjeta, no cada minigráfico interno.

**Variantes que conservar:** Paneles por sector; productividad por sector; dos paneles temporales de ahorro/instrumentos; deuda y servicio.

**Casos piloto:**

- [AM3-07-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:721>) — Empleo formal por sector
- [AM3-10-8](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:1062>) — Productividad por sector
- [AM5-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:532>) — El CDB supera a la poupança
- [AM5-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:631>) — Deuda plana, servicio récord

**Inspección dirigida:** Qué ejes se comparten, unidades distintas, referencia del total, sincronización temporal, nombres de panel y tamaño mínimo.

**Propuesta para el compacto:** Conservar una organización estable y dejar explícito si comparten dominio o solamente calendario.

**Propuesta para Agrandar:** Dar más altura a los paneles, sincronizar la consulta de fecha y mantener disponible la serie de referencia.

**Invariantes y precauciones semánticas:** Misma fecha no obliga a misma escala Y cuando las variables tienen unidades diferentes. Los paneles laborales sí comparan series con un dominio compartido en su grupo.

**Todas las instancias de esta familia:** `AM3-07-0`, `AM3-10-8`, `AM5-03-0`, `AM5-05-0`.

<a id="f10"></a>

### F10 · Comparación antes/después o pesas

**Alcance:** 6 tarjetas; componentes `pesas`, `escalera_mora`. 

Dos valores por fila unidos por un tramo, con su diferencia. La escalera de mora es una variante de la misma gramática.

**Variantes que conservar:** Renuncias; salario reciente frente a anual; inflación esperada por componentes; crecimiento por actividad; mora de hace 12 meses y actual.

**Casos piloto:**

- [AM3-07-4](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:793>) — Renuncias por sector
- [AM3-09-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:860>) — Salario real por sector: 12 meses contra 3 meses
- [AM6-02-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:172>) — Qué parte del IPCA se espera que ceda
- [AM5-07-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:814>) — La escalera de la mora

**Inspección dirigida:** Cuáles son las dos fechas o transformaciones, distancia visual, signo, colores, referencia y puntos fuera de escala.

**Propuesta para el compacto:** Distinguir antes y ahora con forma/jerarquía, conservar ambos valores y la diferencia.

**Propuesta para Agrandar:** Mostrar comparación completa por entidad y explicar los períodos exactos. Permitir revisar el efecto de topes y referencias.

**Invariantes y precauciones semánticas:** La comparación puede ser 12m frente a 3m anualizado, no solo dos fechas. escalera_mora usa un tope y un umbral propios; no eliminarlos sin decisión explícita.

**Todas las instancias de esta familia:** `AM3-07-4`, `AM3-07-5`, `AM3-09-1`, `AM5-07-0`, `AM6-02-1`, `AM6-06-0`.

<a id="f11"></a>

### F11 · Perfiles de desvío y KPI con pistas

**Alcance:** 3 tarjetas; componentes `kpi`, `kpi_barras`. 

El código permite una cifra aislada o perfiles en filas. En las dos tarjetas activas kpi se usa la galería de desvíos; kpi_barras combina cifra y barras.

**Variantes que conservar:** Distancia a meta en σ; desvío frente a normalidad histórica; ahorro/consumo respecto del ingreso.

**Casos piloto:**

- [AM2-02-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:834>) — Qué tan lejos de la meta
- [AM2-05-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1265>) — Productor: qué tan lejos de lo normal
- [AM5-02-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:511>) — Ahorro y consumo contra el ingreso

**Inspección dirigida:** Referencia histórica, unidad, franja normal, saturación de la pista, coherencia entre cifra principal y barras.

**Propuesta para el compacto:** Destacar posición respecto de la referencia y valor exacto. Identificar datos fuera del dominio de la pista.

**Propuesta para Agrandar:** Explicar media/meta, ventana y desviación estándar, y permitir consultar series o componentes que forman el perfil.

**Invariantes y precauciones semánticas:** Distancia a meta y distancia al promedio no son el mismo z-score. No llamar normales a valores solo por entrar en una franja gráfica.

**Todas las instancias de esta familia:** `AM2-02-3`, `AM2-05-2`, `AM5-02-2`.

<a id="f12"></a>

### F12 · Mosaico de unidades federativas

**Alcance:** 2 tarjetas; componentes `mosaico_uf`. 

Ubica las 27 UF brasileñas en una disposición de celdas. No es un mapa coroplético con contornos geográficos.

**Variantes que conservar:** Nivel de desocupación por UF; cambio de desocupación en un año.

**Casos piloto:**

- [AM3-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:479>) — Desocupación por estado
- [AM3-03-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:500>) — Cambio de la desocupación en un año

**Inspección dirigida:** Siglas, leyenda de color, valor real, datos ausentes, signo de mejora y acceso a nombres completos.

**Propuesta para el compacto:** Mantener el mosaico reconocible, una escala clara y cifras legibles.

**Propuesta para Agrandar:** Añadir ranking/tabulación de UF y selección por entidad, conservando la relación con el mosaico.

**Invariantes y precauciones semánticas:** La rampa para niveles no debe reutilizarse sin más para cambios con signo. Una celda ausente no significa cero.

**Todas las instancias de esta familia:** `AM3-03-1`, `AM3-03-2`.

<a id="f13"></a>

### F13 · Bandas de distribución o abanico

**Alcance:** 1 tarjetas; componentes `abanico`. 

Bandas temporales de percentiles de los subítems, con mediana y media ponderada del IPCA.

**Variantes que conservar:** p10–p90, p25–p75, mediana y agregado ponderado en una misma vista.

**Casos piloto:**

- [AM2-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:851>) — Cuánto se generaliza la inflación: la distribución de los subítems

**Inspección dirigida:** Orden de percentiles, bases del apilado, legibilidad de bandas y separación conceptual entre distribución y agregado.

**Propuesta para el compacto:** Destacar la banda central y las dos referencias de lectura necesarias, con leyenda inequívoca.

**Propuesta para Agrandar:** Permitir consultar percentiles por fecha y explicar ponderaciones, cobertura de subítems y cambios de dispersión.

**Invariantes y precauciones semánticas:** Es dispersión entre subítems, no incertidumbre de un pronóstico. Incluir valores negativos en la revisión de cómo se apilan las bandas.

**Todas las instancias de esta familia:** `AM2-03-0`.

<a id="f14"></a>

### F14 · Cajas, rangos y distribución por categoría

**Alcance:** 2 tarjetas; componentes `cajas`, `tabla_am1`. 

Agrupa dos variantes visualmente próximas que necesitan contratos estadísticos separados: rango de expectativas y distribución histórica.

**Variantes que conservar:** Focus: mediana, ±1 desvío y mínimo/máximo; IPCA frente a su historia: caja p25–p75, raya de media y posición actual/percentil.

**Casos piloto:**

- [AM6-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:117>) — Lo que espera el mercado, de 2026 a 2030
- [AM2-02-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:810>) — La distancia a la meta de hoy contra su historia

**Inspección dirigida:** Qué representa caja, raya y bigotes; rango comparable por fila; horizonte de pronóstico; cobertura y estadístico central.

**Propuesta para el compacto:** Conservar leyenda estadística explícita y resaltar el dato o centro de comparación.

**Propuesta para Agrandar:** Mostrar estadísticos exactos, fechas, fuente, número de respondientes cuando exista y tabla de referencia.

**Invariantes y precauciones semánticas:** No convertir cajas de ±1 desviación en boxplots Q1–Q3. En AM2-02-2 la raya está configurada como media, no como mediana.

**Todas las instancias de esta familia:** `AM2-02-2`, `AM6-01-0`.

<a id="f15"></a>

### F15 · Convergencia de expectativas al dato publicado

**Alcance:** 1 tarjetas; componentes `embudos`. 

Varias trayectorias muestran cómo cambió la expectativa de un año antes de conocer su dato final.

**Variantes que conservar:** Horizontes alineados de varios años, con dato publicado final o año todavía sin cierre.

**Casos piloto:**

- [AM6-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:212>) — Cinco años, cinco embudos

**Inspección dirigida:** Definición de slots, fecha de encuesta frente a año objetivo, cierre observado y ausencia de dato final.

**Propuesta para el compacto:** Distinguir cada año y el extremo publicado, con calendario de horizontes claro.

**Propuesta para Agrandar:** Permitir revisar una trayectoria, sus encuestas y su error respecto del publicado, separando años completos e incompletos.

**Invariantes y precauciones semánticas:** El nombre embudos no se refiere a un embudo de conversión. No dibujar el dato final de un año en curso como si ya se conociera.

**Todas las instancias de esta familia:** `AM6-03-0`.

<a id="f16"></a>

### F16 · Matrices de calor y matrices de escenarios

**Alcance:** 4 tarjetas; componentes `heatmap`, `termometro`, `mapa_sostenibilidad`, `tabla_am1`. 

Celdas en una retícula que codifican valores por color. Incluye matrices temporales y una matriz fiscal de escenarios.

**Variantes que conservar:** Persistencia de presión inflacionaria; termómetro fiscal; primario estabilizador según i/g; amplitud mensual dibujada mediante tabla_am1.

**Casos piloto:**

- [AM2-04-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1076>) — Desde cuándo presiona y en cuántos frentes
- [AM4-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:420>) — Termómetro fiscal
- [AM4-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:480>) — Mapa de sostenibilidad
- [AM1-03-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1167>) — Cuántos componentes aceleran, mes a mes

**Inspección dirigida:** Significado de filas/columnas, dominio de color, unidades por fila, etiquetas omitidas en móvil, umbrales y tratamiento de faltantes.

**Propuesta para el compacto:** Hacer clara la pregunta de la matriz y mantener leyenda y valor consultable por celda.

**Propuesta para Agrandar:** Añadir ejes y valores completos, definición de umbrales y consulta por fila/columna. En escenarios, explicar parámetros observados frente a supuestos.

**Invariantes y precauciones semánticas:** El termómetro fiscal no es un velocímetro. El mapa de sostenibilidad no es geográfico. No usar una escala numérica única si las filas mezclan unidades.

**Todas las instancias de esta familia:** `AM1-03-2`, `AM2-04-2`, `AM4-01-0`, `AM4-03-0`.

<a id="f17"></a>

### F17 · Calendario de sorpresas

**Alcance:** 1 tarjetas; componentes `calendario`. 

Celdas por período clasificadas como sobre, bajo o en línea con lo esperado, con sus recuentos.

**Variantes que conservar:** Sorpresas de inflación y de crecimiento con semántica de color distinta.

**Casos piloto:**

- [AM6-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:225>) — Calendario de sorpresas

**Inspección dirigida:** Orden temporal, umbral de en línea, esperado/publicado, cobertura, resultado de cada celda y recuentos.

**Propuesta para el compacto:** Mostrar patrón temporal y categorías con texto o forma además del color.

**Propuesta para Agrandar:** Consultar por período el esperado, el publicado y la diferencia, con resumen del sesgo de sorpresas.

**Invariantes y precauciones semánticas:** Sobre lo esperado no significa mejora en todas las variables. El calendario es categórico; no debe presentarse como un heatmap continuo de magnitudes.

**Todas las instancias de esta familia:** `AM6-03-1`.

<a id="f18"></a>

### F18 · Panel de señales con anticipación

**Alcance:** 1 tarjetas; componentes `senales_am2`. 

Combina balance de señales, tabla de pares y tiras que indican cuándo podría aparecer su señal.

**Variantes que conservar:** Series de productor frente a subítems de IPCA, relación estimada y rezago.

**Casos piloto:**

- [AM2-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1150>) — Qué precios al productor adelantan a los subítems de más peso del IPCA

**Inspección dirigida:** Universo del balance frente a filas visibles; significado de poder predictivo; rezago; unidad y fecha de cada dato.

**Propuesta para el compacto:** Jerarquizar señal, horizonte y entidad. Evitar que la tira temporal compita con todas las columnas.

**Propuesta para Agrandar:** Mostrar el conjunto completo de pares y definiciones de relación/rezago; permitir inspeccionar ejemplos de la asociación.

**Invariantes y precauciones semánticas:** El adaptador calcula el balance sobre todos los pares, no solo las filas mostradas. Una correlación o un rezago estimado no garantiza un resultado futuro.

**Todas las instancias de esta familia:** `AM2-05-0`.

<a id="f19"></a>

### F19 · Área apilada temporal

**Alcance:** 1 tarjetas; componentes `area_apilada`. 

Muestra cómo cambia la composición de la población de 14 años y más a través del tiempo.

**Variantes que conservar:** Partes apiladas en nivel o al 100 %, según configuración del componente.

**Casos piloto:**

- [AM3-04-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:564>) — Cómo se reparte la población de 14 años y más

**Inspección dirigida:** Total, definiciones de categorías, categorías excluyentes, límite superior del apilado y distinción entre personas y porcentaje.

**Propuesta para el compacto:** Mantener orden y colores de categorías, con unidad y total identificables.

**Propuesta para Agrandar:** Consultar composición por fecha y valores de cada categoría, con una tabla equivalente y explicación del denominador.

**Invariantes y precauciones semánticas:** No sumar grupos superpuestos ni cambiar de nivel a porcentaje sin avisarlo. La escala debe cubrir la suma apilada, no solamente la mayor serie.

**Todas las instancias de esta familia:** `AM3-04-2`.

<a id="f20"></a>

### F20 · Flujos Sankey

**Alcance:** 1 tarjetas; componentes `sankey`. 

Representa los orígenes de los nuevos empleos formales mediante nodos y vínculos.

**Variantes que conservar:** Flujos netos hacia empleo formal, con nodos de origen y destino.

**Casos piloto:**

- [AM3-07-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:742>) — De dónde vienen los nuevos formales

**Inspección dirigida:** Conservación de flujos, definición neto/bruto, magnitudes, nombres de nodos, ancho de enlaces y lectura móvil.

**Propuesta para el compacto:** Priorizar el flujo principal y rótulos claros, manteniendo el total y su unidad.

**Propuesta para Agrandar:** Consultar nodos y enlaces con una tabla de origen/destino y explicación de qué significa cada flujo.

**Invariantes y precauciones semánticas:** No representar un flujo neto como probabilidades de transición individual. No inventar origen de movimientos para cerrar el dibujo.

**Todas las instancias de esta familia:** `AM3-07-1`.

<a id="f21"></a>

### F21 · Treemap de composición jerárquica

**Alcance:** 1 tarjetas; componentes `treemap`. 

Rectángulos anidados representan el peso de partidas y grupos del gasto fiscal.

**Variantes que conservar:** Grupos y hojas de gasto con colores de categoría.

**Casos piloto:**

- [AM4-07-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:765>) — Mapa del gasto del gobierno central

**Inspección dirigida:** Área proporcional, denominador, jerarquía, partidas pequeñas, contraste de rótulos y acceso al valor.

**Propuesta para el compacto:** Mostrar grupos y las partidas que tienen superficie suficiente, conservando consulta del resto.

**Propuesta para Agrandar:** Explorar jerarquía y tabla ordenada de partidas con valores y participaciones.

**Invariantes y precauciones semánticas:** No usar magnitudes negativas como área ni sustituir el denominador al abrir el detalle. El color de grupo no equivale a evaluación fiscal.

**Todas las instancias de esta familia:** `AM4-07-0`.

<a id="f22"></a>

### F22 · Pictograma cuantitativo de bloques

**Alcance:** 1 tarjetas; componentes `pictograma`. 

Un bloque representa un año de salario medio requerido para comprar vivienda; el último puede ser parcial.

**Variantes que conservar:** Comparación de vivienda en años de salario mediante bloques discretos.

**Casos piloto:**

- [AM5-08-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:859>) — La vivienda en años de salario

**Inspección dirigida:** Unidad por bloque, fracciones, límite de bloques, rótulo exacto, comparabilidad entre filas y valor fuera del máximo.

**Propuesta para el compacto:** Conservar equivalencia de bloque y cifra exacta, con una lectura inmediata de la unidad.

**Propuesta para Agrandar:** Explicar precio y salario utilizados, período, fuente y diferencias entre filas.

**Invariantes y precauciones semánticas:** No sustituir bloques por iconos decorativos sin mantener equivalencia cuantitativa. Si el valor supera el número de bloques, la limitación debe ser visible.

**Todas las instancias de esta familia:** `AM5-08-0`.

<a id="f23"></a>

### F23 · Dos caminos por tramos y brecha

**Alcance:** 1 tarjetas; componentes `area_entre`. 

Dos referencias horizontales por tramo muestran Focus frente a mercado, y la región entre ambas hace visible la brecha.

**Variantes que conservar:** Comparación de caminos para la Selic con tramos de distinto peso.

**Casos piloto:**

- [AM6-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:243>) — Dos caminos para la Selic

**Inspección dirigida:** Duración/peso de tramos, alineación de horizontes, esperado frente a implícito, ancho de brecha y valores faltantes.

**Propuesta para el compacto:** Distinguir los dos caminos y sus tramos, con una única lectura clara de la brecha.

**Propuesta para Agrandar:** Consultar valores de ambos caminos por tramo y explicar horizonte, fecha de observación y prima por plazo.

**Invariantes y precauciones semánticas:** No interpretar la brecha mercado–Focus como desacuerdo puro: puede incluir prima por plazo. No igualar anchos si representan duraciones distintas.

**Todas las instancias de esta familia:** `AM6-04-0`.

<a id="f24"></a>

### F24 · Escala de posición respecto de zonas

**Alcance:** 1 tarjetas; componentes `escala`. 

Ubica la tasa real ex ante en una pista con zonas de expansiva a contractiva y marcas de referencia.

**Variantes que conservar:** Zonas de interpretación y posición de la tasa real, con rango neutral configurado.

**Casos piloto:**

- [AM6-05-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:302>) — La tasa real en la escala de la política monetaria

**Inspección dirigida:** Origen de umbrales, referencia neutral, unidad, posición de marcas, límites y fecha del dato.

**Propuesta para el compacto:** Mostrar posición actual, zona y unidad, conservando una leyenda breve de los extremos.

**Propuesta para Agrandar:** Explicar construcción de tasa real, zonas y rango neutral con valores explícitos y su fuente.

**Invariantes y precauciones semánticas:** La página declara que la tasa neutral no tiene una serie en el modelo y que el rango se fija manualmente. No presentarlo como estimación actualizada automáticamente.

**Todas las instancias de esta familia:** `AM6-05-1`.

## 6. Repeticiones reales y falsas equivalencias

### 6.1 Misma gramática, diferentes implementaciones

| Grupo | Qué se puede compartir | Qué necesita un adaptador |
| --- | --- | --- |
| linea / lineaL / serie_tiempo | Ejes, consulta, jerarquía de series, leyenda y comportamiento del detalle | Rellenos, episodios, referencias fiscales, leyenda dinámica y unidades |
| tabla / tabla_am1 / tabla_gasto / sensibilidad_tabla | Filas, columnas, alineación, foco, desplegables y lectura móvil | Celdas de dominio, agrupaciones, micrográficos y columnas específicas |
| cascada / cascada_scroll | Modelo de pasos, totales y conexión entre contribuciones | Nombres, formato fiscal y estrategia para móvil |
| pesas / escalera_mora | Antes/después, tramo, diferencia y consulta | Topes, períodos comparados, umbral de cambio y semántica del color |
| paneles / paneles_tiempo | Contenedor de múltiples paneles y coordinación temporal | Ejes compartidos o independientes y referencias del total |
| apilada_100 / barras_cien | Segmentos, leyenda y acceso a partes pequeñas | Normalización por suma frente a una base monetaria que puede quedar parcialmente vacía |

La mejora reutilizable debería vivir en la primitiva o el contenedor compartido. El adaptador conserva las fórmulas, unidades y textos específicos. Repetir un diseño en varias páginas no implica que deba copiarse el código completo varias veces.

### 6.2 Mismo nombre, distinto código efectivo

- barras_div se registra con una función de Mercado laboral y con otra de Fiscal. La revisión tiene que localizar ambos registros.
- tabla usa el dibujante común en Mercado laboral y un envoltorio con consultas adicionales en Inflación.
- tabla_am1 de Inflación reutiliza el componente exportado por Actividad.
- lineaL también se reutiliza de Actividad en Inflación.
- AM5 conserva funciones antiguas de líneas, columnas y trayectorias que ya no registra; un inventario de todas las funciones del archivo las contaría por error como componentes activos.

### 6.3 Nombre parecido, significado diferente

| Nombre de la interfaz/código | Qué representa realmente | Error que debe evitarse |
| --- | --- | --- |
| Termómetro fiscal | Matriz de indicadores por período | Rediseñarlo como velocímetro |
| Mapa de sostenibilidad | Retícula de escenarios de tasa/costo y crecimiento | Tratarlo como mapa geográfico |
| Mosaico UF | Disposición de celdas por unidad federativa | Atribuir precisión de contornos geográficos |
| Embudos | Convergencia de expectativas hacia un dato observado | Usar un embudo de conversión comercial |
| Cajas de Focus | Mediana, ±1 desviación y mínimo/máximo | Etiquetar la caja como rango intercuartílico |
| Caja histórica de IPCA | p25–p75, media y posición/percentil actual | Cambiar la raya por mediana sin modificar la definición |
| Abanico de subítems | Dispersión de subítems en cada fecha | Presentarlo como incertidumbre de un pronóstico |
| Trayectoria | Plano X/Y unido en el tiempo | Añadir automáticamente fases o un bloque laboral |
| Señales | Relaciones y rezagos estimados, con balance de un universo | Interpretarlas como garantías de resultados futuros |

### 6.4 Primitivas visuales internas que también necesitan revisión

El número de familias de tarjeta no agota los elementos visuales internos.

| Primitiva | Dónde aparece / función identificada | Familia o revisión relacionada |
| --- | --- | --- |
| Sparkline de 36 meses | Tablas de índices y agregados; sparkSVG en AM1 | F01 dentro de F03 |
| Miniserie SVG | Función sparkSVG en AM2 | F01 dentro de la tabla que la use |
| Barra de cambios con cero | barraCentro y celdas de amplitud | F07 / F03 |
| Tira de composición | Tablas de amplitud; partes que aceleran o desaceleran | F08 / F03 |
| Matriz de celdas mensual | AM1-03-2 mediante tabla_am1 | F16 |
| Caja y percentil histórico | cajaVentana, AM2-02-2 | F14 |
| Posición actual sobre rango histórico | rielRango: min, p25–p75, mediana, max y hace 12 meses | F14 / F24 |
| Cambios y flechas a 1m, 3m y 12m | rielFlechas | Perfil auxiliar de cambios; F11 |
| Tira de rachas | rielRacha | Secuencia temporal categórica auxiliar |
| Pistas de R² o peso | Tabla de sensibilidad y tabla de gasto | F03 / F07 |

Estas primitivas deben tener reglas propias de escala, faltantes, foco, consulta y unidades. Una maqueta representativa de la tabla debe incluir las celdas visuales, no únicamente texto de ejemplo.

## 7. Encabezados de sección: inventario complementario

Además de las 155 tarjetas, las configuraciones contienen **65 bloques de encabezado de sección**:

| Tipo declarado | Cantidad | Tratamiento |
| --- | ---: | --- |
| dato | 24 | Cifra y nota de contexto; puede ocultarse si no hay dato |
| texto | 23 | Texto explicativo, no gráfico adicional |
| kpi_galeria | 14 | Bloque libre que puede contener perfiles, pistas, cambios o tiras |
| selector | 4 | Controles y contenido de selección |

Estos 65 bloques no son 65 gráficos adicionales ni 65 instancias necesariamente visibles. La publicación depende de que el cálculo devuelva contenido. Tampoco se suman a las 155 tarjetas.

Las catorce galerías se revisarán junto a las primitivas que utilizan. Los selectores deben formar parte de la prueba de estado de cada familia porque pueden redibujar varias tarjetas.

### Distribución de bloques auxiliares por página

| Página | dato | texto | kpi_galeria | selector | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Actividad | 0 | 0 | 1 | 1 | 2 |
| Inflación | 1 | 0 | 1 | 0 | 2 |
| Mercado laboral | 7 | 14 | 5 | 0 | 26 |
| Fiscal | 4 | 6 | 5 | 1 | 16 |
| Hogares | 6 | 2 | 2 | 2 | 12 |
| Expectativas | 6 | 1 | 0 | 0 | 7 |

## 8. Hallazgos de código que orientan la inspección

Estos puntos provienen de la implementación leída. Se distinguen de un problema observado en una captura actual.

### H01 · Filas desplegables con activación por clic

tablaAM1 construye filas expandibles con aria-expanded y un manejador de click. En esa función no se incorpora un botón nativo ni un manejador de teclado para abrirlas.

**Acción propuesta:** revisar las tarjetas que realmente devuelven hijos y darles un disparador semántico operable por teclado, con foco visible y estado persistente. No afirmar que las catorce tarjetas despliegan hijos: eso depende de sus entradas.

### H02 · Topes que limitan la geometría

La galería kpi fija la posición del punto dentro de un dominio; barras_fila, escalera_mora y kpi_barras también limitan sus pistas. Algunas variantes muestran una marca de corte.

**Acción propuesta:** unificar cómo se señala “fuera de escala”, conservar siempre la cifra completa y revisar qué ocurre cuando el dato previo también supera el máximo. No ampliar arbitrariamente la escala si el tope tiene significado analítico.

### H03 · Nombres abreviados en cascadas fiscales

cascada_scroll sustituye varios nombres por abreviaturas y, bajo 600 px, crea un gráfico de 640 px con scroll horizontal interno.

**Acción propuesta:** comprobar acceso a nombres completos, claridad de las abreviaturas y ergonomía del scroll. Comparar esa solución con una composición móvil distinta antes de trasladarla al resto de cascadas.

### H04 · Los faltantes se filtran en varias series

El dibujante de líneas elimina puntos nulos antes de pasarlos a la serie. Eso no define por sí solo cómo debe expresarse un hueco temporal.

**Acción propuesta:** acordar por variante si la ausencia debe cortar el trazo o si es válido unir observaciones disponibles. La decisión depende de frecuencia y fuente; el informe no declara incorrecta toda conexión entre datos disponibles.

### H05 · Hay varios mecanismos de relleno entre curvas

La línea base soporta e.area y sus envoltorios añaden otros rellenos; el componente fiscal calcula dos regiones de color. No son implementaciones idénticas.

**Acción propuesta:** usar casos con cruces, datos negativos y fechas no coincidentes para decidir un contrato común. Si el significado requiere distinguir encima/debajo, conservar ambos sentidos.

### H06 · Los balances no siempre se refieren a lo que se ve

senales_am2 ajusta el balance con todos los pares del universo, mientras la tabla puede mostrar solo un subconjunto.

**Acción propuesta:** rotular el universo del balance y el alcance de la tabla para que el usuario no intente reconciliarlos como si fueran la misma selección.

### H07 · Agrandar depende de una gestión común

pagina.js crea la tarjeta ampliada y dibuja su componente con el indicador grande. También gestiona cierre, foco, inercia del fondo, controles, liberación y redimensionamiento.

**Acción propuesta:** mantener esa infraestructura y cambiar el cuerpo de detalle según la familia. No construir veinticuatro gestores de modales ni alterar por accidente la ampliación de los demás gráficos.

### H08 · Hay dos motivos diferentes para “no disponible”

Una tarjeta puede estar bloqueada por su estado configurado, o puede alcanzar un estado en preparación/error después de cargar o derivar.

**Acción propuesta:** separar dependencia ausente, resultado vacío, filtro sin coincidencias y error de carga. Una maqueta necesita esos estados; una captura del caso feliz no los describe.

## 9. Orden de trabajo recomendado

El orden se basa en reutilización y complejidad semántica, no en un ranking estético.

| Etapa | Familias | Alcance de tarjetas configuradas | Qué se define |
| --- | --- | ---: | --- |
| Base existente | F06 | 5 | Aprovechar reloj depurado, detalle y guía; revisar aparte otras trayectorias |
| Ola 1 | F01 → F03 → F02 | 89 | Ejes, leyendas, consulta, tablas, datos largos y variantes de aportes |
| Ola 2 | F07 → F04 → F05 | 27 | Rankings/divergencia, conciliación de puentes y relaciones entre entidades |
| Ola 3 | F10 → F08 → F09 → F11 → F14 → F16 | 22 | Antes/después, composición, paneles y referencias estadísticas |
| Ola 4 | F12 → F13 → F15 → F17 → F18 | 6 | Geografía en mosaico, distribuciones, expectativas y señales |
| Ola 5 | F19 → F20 → F21 → F22 → F23 → F24 | 6 | Especializados: composición temporal, flujos, jerarquía, bloques, caminos y zonas |

Los alcances suman 155 e incluyen las cuatro tarjetas FALTA como dependencias a resolver, no como gráficos ya disponibles. Las olas 1 y 2 reúnen 116 tarjetas; pueden compartir gran parte de la infraestructura sin perder sus adaptadores.

**Siguiente familia sugerida: F01, líneas.** Es la más repetida y fija patrones que después reutilizan paneles, bandas y gráficos incrustados.

No haría un único ejemplo de línea para todas: al menos una serie simple, una multiserie con leyenda, una con relleno/cruce y una de expectativas o referencias.

## 10. Proceso de mejora por familia

### Paso A · Inspección del original

Seleccionar los casos piloto de la ficha e inspeccionar:

1. Tarjeta compacta.
2. Agrandar.
3. Filtros y selectores que la afectan.
4. Consulta de punto/fila/celda.
5. Fecha, unidad, referencia y significado de signos.
6. Reflujo en móvil y escritorio.
7. Un caso vacío o faltante y un caso de nombres/valores extremos.

Registrar cada observación con clave de tarjeta, estado, tamaño y evidencia. No convertir un hallazgo de una variante en un diagnóstico de todas.

### Paso B · Propuestas y selección

Preparar dos o tres alternativas funcionalmente distintas dentro de la identidad visual existente. Compararlas con los mismos datos y sin cambiar fórmulas para que una opción parezca más limpia.

La propuesta debe resolver una pregunta concreta: localizar el último dato, comparar entidades, explicar aportes, reconocer dispersión o seguir un cambio de fase.

### Paso C · Maqueta funcional de la familia

Una entrada por familia que cubra sus variantes críticas y el flujo compacto → Agrandar. Mantener configuración, datos, dibujante y estado separados.

La ampliación puede ofrecer mayor detalle, tablas, paneles o definiciones según la familia. El bloque laboral acordado para los relojes no se agrega automáticamente al resto.

### Paso D · Guía para LLMs

Documentar:

- Anatomía y orden de componentes.
- Modelo de datos, fórmulas, unidades y frecuencia.
- Variantes admitidas y diferencias obligatorias.
- Dominios, signos, estadísticos y faltantes.
- Interacciones, foco, estado y cierre.
- Reflujo, tipografía, contraste e iconos.
- Qué puede cambiar por configuración y qué es invariante.
- Prompt de réplica y matriz de casos.

### Paso E · Adaptación a las repeticiones

Elegido el patrón, aplicar el cambio en el nivel correcto del código. Cada tarjeta conserva su adaptador y sus datos, salvo que se autorice una corrección semántica.

Entregar una matriz de cobertura: implementado por componente, revisado en cada variante y pendiente por datos. No confundir reutilización del dibujante con inspección individual completada.

### Entregables orientativos por familia

Para una familia `F01`, por ejemplo:

- `maqueta-f01-lineas.html`: entrada funcional y variantes representativas.
- `GUIA_F01_LINEAS_LLM.md`: reglas y prompt de réplica.
- Matriz de tarjetas cubiertas y pendientes dentro de la guía o informe de la familia.

Son nombres orientativos para trabajo posterior, no archivos creados en esta entrega.

### Precedente ya disponible

- [Maqueta de relojes](maqueta-relojes.html).
- [Guía detallada de relojes](GUIA_RELOJES_LLM.md).
- [Comparación de siete propuestas](exploracion-relojes.html).

Ese precedente define el proceso y dos escenarios de ejemplo. No significa que las otras tres tarjetas que nombran trayectoria estén ya adaptadas.

## 11. Reglas comunes para todas las futuras maquetas

1. Datos originales y transformaciones explícitas; ninguna cifra inventada.
2. Fechas reales de la observación, con períodos parciales indicados.
3. Identidad visual de Monitor Brasil y tokens compartidos.
4. Mismos datos entre alternativas de una comparación.
5. Escalas consistentes donde se comparan magnitudes equivalentes; unidades distintas se declaran.
6. Referencias de cero, meta, media y contrafactual identificables.
7. Color de categoría separado del color de evaluación.
8. Estado del usuario preservado al agrandar y cerrar.
9. Consulta por toque y teclado, además del ratón.
10. Un camino accesible a datos/etiquetas que no caben en el dibujo.
11. Mensajes útiles para filtro vacío, ausencia de datos y error.
12. Configuración reutilizable para títulos, ejes, períodos, referencias y fuentes.
13. Reglas de tamaño y dominio para casos extremos.
14. Cambios en componentes compartidos con sus variantes representadas.
15. Distinción entre realizado, revisado visualmente y pendiente.

## 12. Tarjetas bloqueadas por datos

Estas cuatro tarjetas sí aparecen en el diseño, pero pagina.js no ejecuta su dibujante mientras sigan configuradas como FALTA.

| Clave | Familia | Título | Motivo declarado |
| --- | --- | --- | --- |
| [AM3-08-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:823>) | F05 | Crédito a medianas y grandes y empleo formal por sector | crédito a medianas y grandes por sector (SCR.data por porte) en preparación |
| [AM3-08-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:824>) | F06 | Por intensidad laboral: crédito y empleo, trimestre a trimestre | crédito pyme trimestral por grupo de intensidad laboral en preparación |
| [AM3-09-7](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:937>) | F01 | Salario de admisión: efecto salarial y de composición | descomposición por celdas del CAGED en preparación |
| [AM4-06-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:758>) | F07 | Cuánto puede crecer el gasto | falta el límite de gasto del año (RTN tabla 1.6), que no está en los datos exportados |

La mejora del patrón de su familia puede avanzar con otros casos reales. Su adaptación específica necesita resolver la dependencia o documentar el estado vacío; no debe llenarse con números plausibles.

## 13. Definiciones existentes que no se montan en el diseño actual

Se encontraron diez definiciones de tarjetas sin referencia en las filas de las seis páginas actuales. Son potenciales antecedentes o variantes, no diez gráficos adicionales publicados.

| Clave | Componente | Estado declarado |
| --- | --- | --- |
| [AM1-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:946>) | `tabla_am1` | DERIVAR |
| [AM1-01-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:972>) | `columnas` | LISTO |
| [AM1-01-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:989>) | `barras_doble` | LISTO |
| [AM1-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1089>) | `tabla_am1` | DERIVAR |
| [AM1-02-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1095>) | `lineaL` | LISTO |
| [AM1-02-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1105>) | `senales_am1` | DERIVAR |
| [AM1-02-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1118>) | `tabla_am1` | FALTA |
| [AM2-06-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1290>) | `columnas` | LISTO |
| [AM3-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:475>) | `heatmap` | DERIVAR |
| [AM3-10-5](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:1017>) | `flechas` | LISTO |

barras_doble, senales_am1 y flechas aparecen en estas definiciones o registros, pero no son nombres de componentes usados por las 155 tarjetas actuales. Conviene conservarlos como antecedentes y no construir maquetas de ellos por el solo hecho de existir en un archivo.

El registro compartido contiene diecinueve componentes base. dispersion y senales no se nombran directamente en las 155 tarjetas, pero sus envoltorios dispersionL y senales_am2 sí los utilizan. Por tanto, ausencia de uso directo no implica código muerto.

## 14. Mapa de los 40 componentes técnicos

Esta tabla permite pasar del catálogo visual al dibujante. Una función puede reutilizar otra internamente. Los registros específicos de página tienen prioridad sobre el nombre del registro compartido.

| Componente declarado | Tarjetas | Familias principales | Páginas | Dibujante / envoltorio |
| --- | ---: | --- | --- | --- |
| `linea` | 32 | F01 | AM2, AM3, AM5, AM6 | [linea](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:155>) |
| `columnas` | 16 | F02 | AM2, AM3, AM4, AM5 | [columnas](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:236>) |
| `tabla_am1` | 14 | F03, F14, F16 | AM1, AM2 | [tablaAM1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:99>) |
| `lineaL` | 11 | F01 | AM1, AM2 | [lineaL](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:264>) |
| `serie_tiempo` | 10 | F01 | AM4 | [serieTiempo](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:65>) |
| `cascada` | 6 | F04 | AM3, AM5 | [cascada](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:543>) |
| `tabla` | 6 | F03 | AM2, AM3 | [tabla](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:291>); [tablaConTooltip](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:186>) |
| `barras_div` | 5 | F07 | AM3, AM4 | [barrasDiv](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:45>); [barrasDiv](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:273>) |
| `dispersionL` | 5 | F05 | AM1 | [dispersionL](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:279>) |
| `pesas` | 5 | F10 | AM3, AM6 | [pesas](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:308>) |
| `trayectoria` | 5 | F06 | AM2, AM3, AM4, AM5 | [trayectoria](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:777>) |
| `burbujas` | 4 | F05 | AM3, AM5 | [burbujas](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:772>) |
| `apilada_100` | 2 | F08 | AM3, AM4 | [apilada100](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:848>) |
| `barras_fila` | 2 | F07 | AM5 | [barrasFila](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:125>) |
| `barras_h` | 2 | F07 | AM4 | [barras_h](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:272>) |
| `cascada_scroll` | 2 | F04 | AM4 | [cascadaScroll](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:379>) |
| `kpi` | 2 | F11 | AM2 | [kpi](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:964>) |
| `mosaico_uf` | 2 | F12 | AM3 | [mosaicoUf](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:79>) |
| `paneles` | 2 | F09 | AM3 | [paneles](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:108>) |
| `paneles_tiempo` | 2 | F09 | AM5 | [panelesTiempo](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:81>) |
| `abanico` | 1 | F13 | AM2 | [abanico](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:206>) |
| `area_apilada` | 1 | F19 | AM3 | [areaApilada](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:884>) |
| `area_entre` | 1 | F23 | AM6 | [areaEntre](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:503>) |
| `barras_cien` | 1 | F08 | AM5 | [barrasCien](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:99>) |
| `cajas` | 1 | F14 | AM6 | [cajas](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:346>) |
| `calendario` | 1 | F17 | AM6 | [calendario](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:445>) |
| `clu_sectores` | 1 | F05 | AM3 | [cluSectores](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:193>) |
| `embudos` | 1 | F15 | AM6 | [embudos](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:393>) |
| `escala` | 1 | F24 | AM6 | [escala](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:472>) |
| `escalera_mora` | 1 | F10 | AM5 | [escalera](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:148>) |
| `heatmap` | 1 | F16 | AM2 | [heatmap](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:611>) |
| `kpi_barras` | 1 | F11 | AM5 | [kpiBarras](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:209>) |
| `mapa_sostenibilidad` | 1 | F16 | AM4 | [mapaSostenibilidad](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:227>) |
| `pictograma` | 1 | F22 | AM5 | [pictograma](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:183>) |
| `sankey` | 1 | F20 | AM3 | [sankeyEC](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:283>) |
| `senales_am2` | 1 | F18 | AM2 | [senalesAM2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:247>) |
| `sensibilidad_tabla` | 1 | F03 | AM5 | [sensibilidad](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:233>) |
| `tabla_gasto` | 1 | F03 | AM4 | [tablaGasto](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:299>) |
| `termometro` | 1 | F16 | AM4 | [termometro](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:187>) |
| `treemap` | 1 | F21 | AM4 | [treemap](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:329>) |

### Puntos comunes de integración

- [config.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/config.js>): páginas del sitio y rutas.
- [pagina.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/pagina.js:192>): estados bloqueados y construcción de tarjetas.
- [Agrandar y cerrar](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/pagina.js:219>): gestor compartido de la capa, foco y fondo.
- [dibujar](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/pagina.js:337>): preparación de datos, controles y llamada al componente.
- [charts.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/charts.js:1200>): registro base y reglas de componentes HTML.
- [excel.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/excel.js>): exportación existente que debe conservarse cuando se cambie un componente.
- [destacar.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/destacar.js>): selección y resaltado cruzado que una maqueta aislada no debe borrar al integrarse.

## 15. Inventario completo de tarjetas referenciadas

Las claves enlazan a su definición de componente/datos. Se conserva el título base de configuración, que puede estar acompañado por un subtítulo dinámico en la página. Los estados son los declarados en el código.

### AM1 · Actividad — 22 tarjetas

Diseño y posiciones: [paginas/am1.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am1.js>).

| Clave y adaptador | Título base | Familia | Componente | Estado |
| --- | --- | --- | --- | --- |
| [AM1-01-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:957>) | Qué sabemos ya del trimestre en curso | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM1-01-4](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1010>) | Índices de actividad, a/a | [F01](#f01) | `lineaL` | DERIVAR |
| [AM1-01-5](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1083>) | Cuánto cambió el ritmo anual de cada sector | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM1-01-6](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1024>) | IBC-Br contra lo esperado del PIB | [F01](#f01) | `lineaL` | DERIVAR |
| [AM1-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1124>) | Cuántos componentes aceleran en cada agregado | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM1-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1130>) | Momentum de los agregados | [F05](#f05) | `dispersionL` | LISTO |
| [AM1-03-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1167>) | Cuántos componentes aceleran, mes a mes | [F16](#f16) | `tabla_am1` | DERIVAR |
| [AM1-03-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1196>) | Las que más aceleran y desaceleran | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM1-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1210>) | Consumo: por grupo y por ciclo | [F01](#f01) | `lineaL` | DERIVAR |
| [AM1-04-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1214>) | Consumo: variaciones del último mes | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM1-04-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1218>) | Industria: por uso y por sensibilidad | [F01](#f01) | `lineaL` | DERIVAR |
| [AM1-04-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1222>) | Industria: variaciones del último mes | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM1-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1362>) | Uso de capacidad, industria de transformación | [F01](#f01) | `lineaL` | LISTO |
| [AM1-05-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1377>) | Uso de capacidad y desocupación 12 meses después | [F05](#f05) | `dispersionL` | LISTO |
| [AM1-05-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1398>) | Brecha de actividad | [F01](#f01) | `lineaL` | LISTO |
| [AM1-05-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1422>) | Brecha e IPCA menos meta 18 meses después | [F05](#f05) | `dispersionL` | LISTO |
| [AM1-06-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1228>) | Nivel | [F01](#f01) | `lineaL` | LISTO |
| [AM1-06-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1247>) | Variación | [F01](#f01) | `lineaL` | LISTO |
| [AM1-06-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1332>) | Último dato de la selección | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM1-06-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1264>) | Base 100 al inicio de la ventana | [F01](#f01) | `lineaL` | LISTO |
| [AM1-06-4](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1285>) | Momentum de las series elegidas | [F05](#f05) | `dispersionL` | DERIVAR |
| [AM1-06-5](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am1.js:1302>) | Una serie contra otra | [F05](#f05) | `dispersionL` | DERIVAR |

### AM2 · Inflación — 22 tarjetas

Diseño y posiciones: [paginas/am2.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am2.js>).

| Clave y adaptador | Título base | Familia | Componente | Estado |
| --- | --- | --- | --- | --- |
| [AM2-00-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:519>) | Qué sabemos ya del trimestre en curso | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM2-00-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:551>) | IPCA y sus agregados, 12 meses | [F01](#f01) | `lineaL` | DERIVAR |
| [AM2-00-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:568>) | Cuánto cambió la inflación de cada agregado | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM2-00-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:588>) | IPCA 12 meses contra lo esperado | [F01](#f01) | `lineaL` | DERIVAR |
| [AM2-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:634>) | Aportes al IPCA por grupo | [F02](#f02) | `columnas` | LISTO |
| [AM2-01-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:666>) | Último dato por grupo | [F03](#f03) | `tabla` | LISTO |
| [AM2-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:719>) | IPCA y sus agregados: cómo vienen y cuán lejos están de la meta | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM2-02-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:745>) | Acumulado en el año contra la meta | [F01](#f01) | `linea` | DERIVAR |
| [AM2-02-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:810>) | La distancia a la meta de hoy contra su historia | [F14](#f14) | `tabla_am1` | DERIVAR |
| [AM2-02-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:834>) | Qué tan lejos de la meta | [F11](#f11) | `kpi` | DERIVAR |
| [AM2-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:851>) | Cuánto se generaliza la inflación: la distribución de los subítems | [F13](#f13) | `abanico` | DERIVAR |
| [AM2-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:886>) | IPCA y núcleos desde 2008 | [F01](#f01) | `linea` | DERIVAR |
| [AM2-03-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:918>) | Servicios subyacentes e industriales desde 2008 | [F01](#f01) | `linea` | LISTO |
| [AM2-03-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:942>) | Libres y administrados desde 2008 | [F01](#f01) | `linea` | LISTO |
| [AM2-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:968>) | Cuántos componentes aceleran en cada agregado | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM2-04-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1043>) | Reloj del ciclo del IPCA, año a año | [F06](#f06) | `trayectoria` | DERIVAR |
| [AM2-04-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1076>) | Desde cuándo presiona y en cuántos frentes | [F16](#f16) | `heatmap` | LISTO |
| [AM2-04-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1111>) | Los ítems que más empujan | [F03](#f03) | `tabla` | DERIVAR |
| [AM2-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1150>) | Qué precios al productor adelantan a los subítems de más peso del IPCA | [F18](#f18) | `senales_am2` | DERIVAR |
| [AM2-05-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1198>) | Cuántas series del productor aceleran, por familia | [F03](#f03) | `tabla_am1` | DERIVAR |
| [AM2-05-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1265>) | Productor: qué tan lejos de lo normal | [F11](#f11) | `kpi` | DERIVAR |
| [AM2-06-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am2.js:1320>) | Exceso sobre la meta: descomposición del BCB | [F02](#f02) | `columnas` | LISTO |

### AM3 · Mercado laboral — 49 tarjetas

Diseño y posiciones: [paginas/am3.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am3.js>).

| Clave y adaptador | Título base | Familia | Componente | Estado |
| --- | --- | --- | --- | --- |
| [AM3-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:333>) | La desocupación se despegó de la actividad | [F01](#f01) | `linea` | LISTO |
| [AM3-01-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:381>) | La desocupación contra su historia | [F03](#f03) | `tabla` | DERIVAR |
| [AM3-01-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:353>) | La población y la fuerza laboral | [F03](#f03) | `tabla` | LISTO |
| [AM3-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:419>) | Reloj del ciclo laboral | [F06](#f06) | `trayectoria` | DERIVAR |
| [AM3-02-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:445>) | Desocupación contra su mediana 2012-19 | [F01](#f01) | `linea` | DERIVAR |
| [AM3-02-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:454>) | Salario real | [F01](#f01) | `linea` | LISTO |
| [AM3-02-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:459>) | Brecha de desocupación | [F02](#f02) | `columnas` | DERIVAR |
| [AM3-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:479>) | Desocupación por estado | [F12](#f12) | `mosaico_uf` | LISTO |
| [AM3-03-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:500>) | Cambio de la desocupación en un año | [F12](#f12) | `mosaico_uf` | LISTO |
| [AM3-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:522>) | De la desocupación de hace 3 años a la de hoy | [F04](#f04) | `cascada` | LISTO |
| [AM3-04-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:538>) | Desocupación con otra participación | [F03](#f03) | `tabla` | LISTO |
| [AM3-04-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:564>) | Cómo se reparte la población de 14 años y más | [F19](#f19) | `area_apilada` | DERIVAR |
| [AM3-04-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:583>) | Efecto empleo y efecto participación | [F02](#f02) | `columnas` | LISTO |
| [AM3-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:603>) | Quién trabaja hoy que no trabajaba en 2019 | [F07](#f07) | `barras_div` | LISTO |
| [AM3-05-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:624>) | Informalidad | [F01](#f01) | `linea` | LISTO |
| [AM3-05-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:637>) | Asalariados privados con contrato, por tamaño de la empresa | [F02](#f02) | `columnas` | LISTO |
| [AM3-05-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:656>) | Ingreso real por tipo de ocupación | [F07](#f07) | `barras_div` | LISTO |
| [AM3-06-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:676>) | De la masa salarial de hace 3 años a la de hoy | [F04](#f04) | `cascada` | LISTO |
| [AM3-06-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:691>) | Masa salarial contra consumo | [F01](#f01) | `linea` | DERIVAR |
| [AM3-06-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:702>) | Salario nominal contra IPCA | [F01](#f01) | `linea` | LISTO |
| [AM3-06-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:710>) | Ingreso real medio y personas con ingreso | [F01](#f01) | `linea` | LISTO |
| [AM3-07-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:721>) | Empleo formal por sector | [F09](#f09) | `paneles` | LISTO |
| [AM3-07-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:742>) | De dónde vienen los nuevos formales | [F20](#f20) | `sankey` | LISTO |
| [AM3-07-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:768>) | Qué sectores crean más empleo formal | [F03](#f03) | `tabla` | LISTO |
| [AM3-07-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:784>) | CAGED y PNAD formal | [F01](#f01) | `linea` | LISTO |
| [AM3-07-4](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:793>) | Renuncias por sector | [F10](#f10) | `pesas` | LISTO |
| [AM3-07-5](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:797>) | Renuncias por tamaño de la firma | [F10](#f10) | `pesas` | LISTO |
| [AM3-08-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:803>) | Crédito pyme y empleo formal por sector | [F05](#f05) | `burbujas` | LISTO |
| [AM3-08-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:823>) | Crédito a medianas y grandes y empleo formal por sector | [F05](#f05) | `burbujas` | FALTA |
| [AM3-08-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:824>) | Por intensidad laboral: crédito y empleo, trimestre a trimestre | [F06](#f06) | `trayectoria` | FALTA |
| [AM3-08-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:825>) | Empleo formal neto por tamaño de la firma | [F02](#f02) | `columnas` | LISTO |
| [AM3-09-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:844>) | Sectores: empleo y salario real | [F05](#f05) | `burbujas` | LISTO |
| [AM3-09-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:860>) | Salario real por sector: 12 meses contra 3 meses | [F10](#f10) | `pesas` | LISTO |
| [AM3-09-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:870>) | Salario de admisión en salarios mínimos | [F02](#f02) | `columnas` | LISTO |
| [AM3-09-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:884>) | El salario mínimo | [F02](#f02) | `columnas` | LISTO |
| [AM3-09-4](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:898>) | Salario real: por mes y por hora | [F01](#f01) | `linea` | LISTO |
| [AM3-09-5](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:908>) | Horas trabajadas por semana | [F08](#f08) | `apilada_100` | LISTO |
| [AM3-09-6](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:926>) | Salario de admisión por tamaño de la firma | [F07](#f07) | `barras_div` | LISTO |
| [AM3-09-7](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:937>) | Salario de admisión: efecto salarial y de composición | [F01](#f01) | `linea` | FALTA |
| [AM3-10-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:940>) | Crecimiento: más gente o más productiva | [F02](#f02) | `columnas` | DERIVAR |
| [AM3-10-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:956>) | Productividad por ocupado y por hora | [F01](#f01) | `linea` | DERIVAR |
| [AM3-10-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:987>) | Salario contra productividad, por sector | [F05](#f05) | `clu_sectores` | LISTO |
| [AM3-10-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:998>) | Salario nominal, CLU y productividad | [F01](#f01) | `linea` | LISTO |
| [AM3-10-4](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:1009>) | CLU contra la meta | [F02](#f02) | `columnas` | LISTO |
| [AM3-10-6](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:1037>) | De dónde vino la productividad desde 2019 | [F04](#f04) | `cascada` | LISTO |
| [AM3-10-7](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:1050>) | Productividad por sector | [F07](#f07) | `barras_div` | LISTO |
| [AM3-10-8](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:1062>) | Productividad por sector | [F09](#f09) | `paneles` | LISTO |
| [AM3-11-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:1084>) | Salario nominal y servicios subyacentes, rezagados | [F01](#f01) | `linea` | LISTO |
| [AM3-11-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am3.js:1094>) | Diferencia: salario menos servicios | [F02](#f02) | `columnas` | LISTO |

### AM4 · Fiscal — 23 tarjetas

Diseño y posiciones: [paginas/am4.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am4.js>).

| Clave y adaptador | Título base | Familia | Componente | Estado |
| --- | --- | --- | --- | --- |
| [AM4-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:420>) | Termómetro fiscal | [F16](#f16) | `termometro` | LISTO |
| [AM4-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:449>) | Primario observado contra el que estabiliza la deuda | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:480>) | Mapa de sostenibilidad | [F16](#f16) | `mapa_sostenibilidad` | LISTO |
| [AM4-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:510>) | Costo de la deuda contra crecimiento del PIB | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-03-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:534>) | Qué mueve la deuda en 12 meses | [F07](#f07) | `barras_div` | LISTO |
| [AM4-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:556>) | De la deuda de hace 3 años a la de hoy | [F04](#f04) | `cascada_scroll` | LISTO |
| [AM4-04-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:581>) | Qué movió la deuda cada año | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-04-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:603>) | Deuda bruta del gobierno general | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-04-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:620>) | Deuda neta: interna y externa | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:643>) | Deuda por moneda y plazo de repreciación | [F08](#f08) | `apilada_100` | LISTO |
| [AM4-05-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:664>) | La Selic y lo que la deuda realmente paga | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-05-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:683>) | La U de la indexación | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-05-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:705>) | Intereses nominales | [F02](#f02) | `columnas` | LISTO |
| [AM4-06-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:722>) | Primario del gobierno central contra la meta | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-06-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:758>) | Cuánto puede crecer el gasto | [F07](#f07) | `barras_h` | FALTA |
| [AM4-07-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:765>) | Mapa del gasto del gobierno central | [F21](#f21) | `treemap` | LISTO |
| [AM4-07-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:793>) | Del gasto de 2021 al de hoy | [F04](#f04) | `cascada_scroll` | LISTO |
| [AM4-07-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:817>) | Impulso del gasto | [F02](#f02) | `columnas` | LISTO |
| [AM4-07-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:857>) | El gasto, partida por partida | [F03](#f03) | `tabla_gasto` | LISTO |
| [AM4-08-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:875>) | Transferencias y participación, año a año | [F06](#f06) | `trayectoria` | LISTO |
| [AM4-08-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:896>) | Transferencias a hogares | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-09-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:917>) | Ingresos contra gasto: la tijera | [F01](#f01) | `serie_tiempo` | LISTO |
| [AM4-09-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am4.js:939>) | Recaudación real por impuesto | [F07](#f07) | `barras_h` | LISTO |

### AM5 · Hogares — 25 tarjetas

Diseño y posiciones: [paginas/am5.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am5.js>).

| Clave y adaptador | Título base | Familia | Componente | Estado |
| --- | --- | --- | --- | --- |
| [AM5-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:468>) | De cada R$ 100 de ingreso | [F08](#f08) | `barras_cien` | LISTO |
| [AM5-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:479>) | Consumo, ingreso y el consumo que habría sido | [F01](#f01) | `linea` | LISTO |
| [AM5-02-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:502>) | Del consumo de 2019 al de hoy | [F04](#f04) | `cascada` | LISTO |
| [AM5-02-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:511>) | Ahorro y consumo contra el ingreso | [F11](#f11) | `kpi_barras` | LISTO |
| [AM5-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:532>) | El CDB supera a la poupança | [F09](#f09) | `paneles_tiempo` | LISTO |
| [AM5-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:566>) | Tasa de ahorro de los hogares | [F01](#f01) | `linea` | LISTO |
| [AM5-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:583>) | Aportes al crecimiento del ingreso | [F02](#f02) | `columnas` | LISTO |
| [AM5-04-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:610>) | Transferencias federales, por programa | [F07](#f07) | `barras_fila` | LISTO |
| [AM5-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:631>) | Deuda plana, servicio récord | [F09](#f09) | `paneles_tiempo` | LISTO |
| [AM5-05-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:657>) | Por qué sube el servicio | [F04](#f04) | `cascada` | LISTO |
| [AM5-05-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:666>) | Mapa de la deuda: cuánto pesa y cuánto cuesta | [F05](#f05) | `burbujas` | LISTO |
| [AM5-05-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:680>) | Lo que paga la deuda contra la Selic | [F01](#f01) | `linea` | LISTO |
| [AM5-05-4](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:700>) | El crédito nuevo: tasa y composición | [F04](#f04) | `cascada` | LISTO |
| [AM5-05-5](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:709>) | Plazo del crédito libre nuevo | [F01](#f01) | `linea` | LISTO |
| [AM5-06-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:725>) | Crédito nuevo por producto | [F07](#f07) | `barras_fila` | LISTO |
| [AM5-06-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:746>) | Quién mueve el saldo | [F02](#f02) | `columnas` | LISTO |
| [AM5-06-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:776>) | Más gente con banco, más deuda | [F06](#f06) | `trayectoria` | LISTO |
| [AM5-06-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:792>) | Deuda / ingreso: libre y dirigido | [F01](#f01) | `linea` | LISTO |
| [AM5-07-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:814>) | La escalera de la mora | [F10](#f10) | `escalera_mora` | LISTO |
| [AM5-07-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:835>) | Mora por segmento | [F01](#f01) | `linea` | LISTO |
| [AM5-08-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:859>) | La vivienda en años de salario | [F22](#f22) | `pictograma` | LISTO |
| [AM5-08-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:879>) | Tres tasas para comprar una casa | [F01](#f01) | `linea` | LISTO |
| [AM5-08-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:901>) | Quién financia la vivienda | [F02](#f02) | `columnas` | LISTO |
| [AM5-08-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:927>) | Precio, alquiler y salario | [F01](#f01) | `linea` | LISTO |
| [AM5-09-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/derivados/am5.js:951>) | Sensibilidad del consumo al crédito | [F03](#f03) | `sensibilidad_tabla` | LISTO |

### AM6 · Expectativas — 14 tarjetas

Diseño y posiciones: [paginas/am6.js](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js>).

| Clave y adaptador | Título base | Familia | Componente | Estado |
| --- | --- | --- | --- | --- |
| [AM6-01-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:117>) | Lo que espera el mercado, de 2026 a 2030 | [F14](#f14) | `cajas` | LISTO |
| [AM6-02-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:149>) | La expectativa de cada año, encuesta tras encuesta | [F01](#f01) | `linea` | LISTO |
| [AM6-02-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:172>) | Qué parte del IPCA se espera que ceda | [F10](#f10) | `pesas` | LISTO |
| [AM6-02-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:185>) | Cuánto discrepan los analistas | [F01](#f01) | `linea` | LISTO |
| [AM6-03-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:212>) | Cinco años, cinco embudos | [F15](#f15) | `embudos` | DERIVAR |
| [AM6-03-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:225>) | Calendario de sorpresas | [F17](#f17) | `calendario` | LISTO |
| [AM6-04-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:243>) | Dos caminos para la Selic | [F23](#f23) | `area_entre` | LISTO |
| [AM6-04-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:272>) | Selic esperada para fin de 2026 y de 2027 | [F01](#f01) | `linea` | LISTO |
| [AM6-05-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:285>) | Tasa real ex-ante | [F01](#f01) | `linea` | LISTO |
| [AM6-05-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:302>) | La tasa real en la escala de la política monetaria | [F24](#f24) | `escala` | DERIVAR |
| [AM6-06-0](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:315>) | Quién frena en 2027 | [F10](#f10) | `pesas` | LISTO |
| [AM6-06-1](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:329>) | Revisiones del PIB | [F01](#f01) | `linea` | LISTO |
| [AM6-06-2](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:342>) | Tipo de cambio esperado | [F01](#f01) | `linea` | LISTO |
| [AM6-06-3](<C:/Users/pablo/OneDrive/Documentos/macro_bz/monitor/qwen3.8-max/site/assets/js/paginas/am6.js:355>) | IPCA esperado 12 meses adelante | [F01](#f01) | `linea` | LISTO |

## 16. Cómo continuar con otro LLM sin repetir la investigación

Entregar este informe, la maqueta/guía de relojes como precedente y las definiciones de la familia elegida. Usar las claves del inventario como alcance explícito, no una instrucción vaga del tipo “arregla todos los gráficos”.

Prompt de inicio:

```text
Trabaja sobre la familia [ID y nombre] del INFORME_GRAFICOS.md.
El objetivo es repetir el proceso de los relojes, manteniendo los datos
y la semántica de cada tarjeta.

1. Usa el informe para localizar el componente efectivo y sus variantes.
2. Inspecciona primero los casos piloto y sus vistas compacta y Agrandar.
3. Distingue observaciones visuales, comportamiento del código y supuestos.
4. Propón alternativas comparables con los mismos datos.
5. Tras la selección, prepara una maqueta funcional reutilizable.
6. Entrega una guía detallada para LLMs con configuración, datos,
   interacciones, estados, reflujo e invariantes.
7. Relaciona cada tarjeta de esta familia con la variante que la cubre.
8. Mantén separadas las tarjetas bloqueadas por datos.
9. Conserva los controles de selección, la exportación y el foco al integrar.
10. No copies el bloque laboral a familias donde no fue solicitado.
11. No afirmes que revisaste tarjetas o estados que no inspeccionaste.

Alcance de código autorizado: [archivos o componentes].
Casos piloto: [claves del informe].
Salida esperada: [propuestas / maqueta seleccionada / integración].
```

Este informe deja preparado el catálogo y el orden de revisión. La siguiente actividad recomendada es inspeccionar visualmente los pilotos de F01 y definir las variantes de línea que deben aparecer en su maqueta funcional.

