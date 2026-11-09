# Gráficos frecuentes: guía de inspección, diseño y réplica con LLMs

**Entrega:** maqueta-graficos-frecuentes.html  
**Fecha de extracción:** 5 de noviembre de 2026  
**Alcance:** ocho casos reales de cuatro familias. No es una migración de las 97 tarjetas de esas familias.

## 1. Qué contiene y cómo usarlo

Abre **maqueta-graficos-frecuentes.html** directamente en un navegador moderno. No necesita servidor, conexión, instalación ni CDN. El documento contiene fuentes WOFF2, estilos, datos y lógica. El enlace superior abre IMPLEMENTACION_GRAFICOS.md, la guía breve. Este documento conserva las especificaciones y los prompts completos.

La página presenta ocho tarjetas. Pasa el ratón para explorar tooltips por familia; haz clic o toca para conservar la consulta en el panel de valores. Selecciona los filtros disponibles y pulsa **Agrandar**: el detalle conserva el estado del caso. Al cerrar con el botón, Escape o un clic fuera del diálogo, vuelves a la misma tarjeta. Si hay una ayuda abierta, el primer Escape la cierra y el segundo cierra el diálogo. La amplitud abre componentes, el gasto abre subpartidas y la cascada conserva sus cinco ventanas reales.

Las vistas ampliadas no repiten el bloque de ciclo laboral de los relojes: ese bloque pertenecía a aquel caso. Cada familia recibe el detalle que necesita.

### Archivos y responsabilidades

| Archivo | Función |
|---|---|
| maqueta-graficos-frecuentes.html | Entrega principal, editable y autónoma |
| IMPLEMENTACION_GRAFICOS.md | Guía breve para integrar y replicar los ocho ejemplos |
| GUIA_GRAFICOS_FRECUENTES_LLM.md | Diagnóstico, contratos, decisiones y prompts |
| assets/generar_graficos_frecuentes.py | Fuente de construcción y extracción reproducible; requiere Python 3.8 o posterior |
| assets/graficos_frecuentes_extra.js | Adaptadores de interfaz de actividad, brecha de desocupación, gasto y cascada; se incrusta al generar |
| assets/fonts.css | Fuente local reutilizada por el generador; las fuentes quedan incrustadas en el HTML |
| .od-frames/layout.css | Primitivas estructurales existentes que el generador incorpora |

El generador no es necesario para abrir o editar el HTML. Para regenerar desde los JSON del monitor, ejecuta desde el proyecto:

~~~powershell
python assets/generar_graficos_frecuentes.py --html
python assets/generar_graficos_frecuentes.py --guide
~~~

La constante SOURCE del generador apunta al sitio original de este equipo. En otro equipo cambia SOURCE al directorio que contiene assets/js y data. Deben existir los diez JSON enumerados más abajo, assets/fonts.css, assets/graficos_frecuentes_extra.js y .od-frames/layout.css. No sobrescribas una adaptación manual del HTML sin guardar sus cambios en la fuente del generador. El JavaScript adicional queda incrustado: no es una petición externa al abrir el HTML.

## 2. Por qué estos casos

El inventario de INFORME_GRAFICOS.md clasifica **155 tarjetas** por su tarea visual dominante. Las líneas reúnen 53, las tablas analíticas 20 y las columnas 16: las tres familias de la primera entrega suman **89 tarjetas**. Se añade F04, con 8 cascadas: las cuatro familias suman **97 tarjetas**, aproximadamente el 63 % del inventario.

Los recuentos son de tarjetas, no de algoritmos independientes. Tampoco significan que los ocho casos aquí construidos cubran todas las variantes. Se propone reutilizar estructura y controles; las fórmulas y la semántica permanecen en adaptadores separados.

| Familia | Caso | Identificador original | Variante que aporta |
|---|---|---|---|
| F01 · líneas | IPCA y núcleos desde 2008 | AM2-03-1 | Varias series, meta anual y bandas de episodios |
| F01 · líneas | Primario observado contra el que estabiliza la deuda | AM4-02-0 | Dos curvas, negativos, cruces y relleno de brecha |
| F03 · tablas | Cuántos componentes aceleran en cada agregado | AM1-03-0 | Amplitud, denominadores y filas con componentes desplegables |
| F02 · columnas | Aportes al IPCA por grupo | AM2-01-0 | Nueve grupos, apilado de positivos/negativos y línea total |
| F01 · líneas | Índices de actividad, a/a | AM1-01-4 | Cuatro series observadas y cambio entre dos cestas |
| F02 · columnas | Brecha de desocupación | AM3-02-3 | Barras con signo frente a una referencia histórica fija |
| F03 · tablas | Gasto, partida por partida | AM4-07-3 | Jerarquía de 19 filas, peso, cambios y cinco horizontes de comparación |
| F04 · cascadas | De la deuda inicial a la de hoy | AM4-04-0 | Cinco ventanas, pasos acumulados, residuo y conciliación |

### Evidencia examinada y sus límites

- Se consultó el inventario del proyecto, los adaptadores JavaScript originales y las tablas JSON locales.
- Se observaron las referencias AM2_03_1.png, AM4_02_0.png, AM1_03_0.png y AM2_01_0.png de monitor/web/ref.
- Esas imágenes son referencias de diseño. No prueban el estado actual de ejecución: incluyen valores de plantilla y dos estructuras que ya cambiaron.
- La referencia de amplitud muestra seis filas; el código actual define cinco agregados, incluido IBC-Br.
- La referencia de aportes agrupa en tres conjuntos; el código actual exige los nueve grupos. La maqueta conserva nueve.
- La maqueta utiliza una extracción estática de datos locales, no una descarga oficial nueva ni una verificación estadística independiente.
- En la ampliación se leyeron los adaptadores de los cuatro casos nuevos y sus JSON. No se atribuye una inspección visual de nuevas capturas a estos casos.
- No se realizó una renderización, recorrido de navegador ni prueba posterior a la escritura de esta entrega.

## 3. Diagnóstico y propuesta por caso

### 3.1 IPCA y núcleos desde 2008

**Pregunta:** ¿cómo evoluciona la inflación general frente al promedio de núcleos y la meta?

**Problema observado en la referencia:** las bandas tienen gran presencia, faltan valores legibles en el eje vertical y la meta puede confundirse con otra serie observada. Los datos de la captura son de referencia, no valores que deban copiarse.

**Propuesta compacta:** IPCA azul, núcleos petróleo y meta gris discontinua. Bandas tenues sólo para meses en que IPCA supera núcleos. Eje con unidades, calendario visible, selector de mes y lectura numérica de las tres series. Por defecto se conserva la historia completa; ventanas de cinco y diez años permiten acercarse.

**Agrandar:** mismo filtro y mismo mes; gráfico más amplio; lectura numérica; bloque Por periodos con un recorrido mensual y hasta doce observaciones cercanas; definición de las bandas, del promedio y de la meta.

**Lo que no debe cambiar:** la banda no significa recesión, alarma ni incertidumbre. La meta no se extrapola a años sin dato. Los cinco núcleos deben existir en el mismo mes para calcular la media.

### 3.2 Primario observado frente al estabilizador

**Pregunta:** ¿cuánto resultado primario falta para alcanzar el que estabilizaría la deuda según el cálculo del monitor?

**Problema observado en la referencia:** el relleno concentra mucha atención y las anotaciones narrativas quedan desligadas del periodo que se consulta. Sin valores de eje o signos explícitos, es fácil confundir el nivel de primario con la distancia entre ambas curvas.

**Propuesta compacta:** observado azul continuo; estabilizador gris discontinuo; cero visible; relleno arena para falta de primario y azul grisáceo para primario por encima del estabilizador. La lectura separa observado, estabilizador y magnitud de la brecha.

**Agrandar:** comparación con más espacio, tabla mensual y fórmula explícita. Las anotaciones históricas fijas del diseño original se sustituyen en esta propuesta por la consulta del mes y una definición de la brecha. No se generan conclusiones causales nuevas.

**Lo que no debe cambiar:** datos en % del PIB ya escalados; brecha en pp; los rellenos se dividen exactamente en los cruces de las dos líneas. El área no mide probabilidad.

### 3.3 Componentes que aceleran por agregado

**Pregunta:** ¿qué proporción de componentes muestra un ritmo de tres meses mayor que el de doce meses y cuáles son?

**Problema de la referencia y del patrón original:** la tira apilada describe bien la composición, pero el denominador y el detalle quedan demasiado dependientes de ayudas emergentes o del clic en una fila. La estructura de la captura además está desactualizada.

**Propuesta compacta:** cinco agregados reales; tira con tres estados; conteo visible en el orden aceleran / iguales / desaceleran; n de pares válidos y porcentaje que acelera. Cada agregado tiene un botón nativo con flecha y estado desplegado.

**Detalle de componentes:** nombre completo, clasificación textual, círculo vacío en 12m a/a, círculo lleno en 3m a/a, valores numéricos y diferencia. El par de círculos compara dos métricas del mismo mes; no es una serie temporal. La escala es común dentro de cada agregado, no necesariamente entre agregados.

**Agrandar:** misma fecha, orden, búsqueda y agregados abiertos; mayor ancho y explicación completa. El buscador encuentra tanto agregados como componentes. Con una búsqueda activa se muestran los grupos y componentes coincidentes para evitar ocultar el resultado dentro de una fila cerrada.

**Lo que no debe cambiar:** no sumar filas agregadas: Todas las series incluye PMC/PMS/PIM y se superpone con esas tres filas. IBC-Br es otro universo. El denominador excluye componentes sin ambas tasas del mes.

### 3.4 Aportes al IPCA por grupo

**Pregunta:** ¿qué aporta cada grupo a la variación del IPCA elegida?

**Problema observado:** una leyenda simplificada de tres grupos no corresponde al código actual. Nueve colores sin detalle numérico pueden ser difíciles de distinguir, especialmente con barras estrechas o aportes negativos.

**Propuesta compacta:** nueve grupos persistentes, leyenda multilínea, cero claro, positivos arriba y negativos abajo; línea total oscura. Variación, ajuste, ventana y mes son controles funcionales. El eje cubre simultáneamente el total de los positivos, el total de los negativos y la línea del IPCA.

**Agrandar:** conserva los filtros, presenta los nueve aportes del mes, la suma, el total y su diferencia; añade consulta Por periodos y definiciones de unidades.

**Lo que no debe cambiar:** no agrupar categorías arbitrariamente, no normalizar a 100 %, no borrar negativos ni corregir un residuo repartiéndolo entre grupos. Los colores ayudan a localizar, pero el desglose numérico permite leer sin distinguir nueve tonos.

## 4. Especificación visual compartida

Se continúa el lenguaje claro de la maqueta de relojes y del monitor existente. Esta elección conserva la referencia concreta del proyecto; no aplica el fondo oscuro de la descripción genérica del paquete Dashboard.

| Elemento | Regla |
|---|---|
| Fondo | #F6F7F8 |
| Superficie | #FFFFFF |
| Texto | #24324A; secundarios #5B6573 y #606C7A |
| Serie principal | #2E5C8A |
| Segunda serie | #2F7A86 |
| Referencia | #8A8F96, trazo discontinuo |
| Diferencia negativa de ritmo | #A85E24 más etiqueta textual |
| Rellenos fiscales | Arena #EDC9A6 / historia #A9B8CB, con leyenda |
| Titulares | Bricolage Grotesque local |
| Cuerpo y datos | IBM Plex Sans local; números tabulares |
| Texto de interfaz | Base 16 px; auxiliares 14 px; etiquetas numéricas del SVG 13 px |
| Espaciado | Múltiplos de 4/8; sección 48, tarjeta 24, grupos 16/8 px |
| Bordes | 1 px, sin sombra decorativa; radio de tarjeta 12 px |
| Controles | Altura mínima 44 px y foco visible |
| Movimiento | 200 ms para la flecha de despliegue; sin animar datos; reduced-motion desactiva transiciones |

Las etiquetas densas de ejes, tablas y leyendas usan tamaños menores que el texto de cuerpo para conservar la composición de un monitor analítico. Los valores consultados aparecen además en texto HTML. Los tonos claros se reservan a marcas o rellenos; no se usan como texto principal.

### Distribución y adaptación

- A partir de 1024 px: dos casos de líneas en columnas; debajo, tabla y aportes en columnas.
- Por debajo de 1024 px: una columna, sin ocultar acciones.
- Por debajo de 768 px: menos relleno, leyenda de aportes en dos columnas y tabla de periodos convertida en filas de datos apilados.
- El SVG usa el ancho real de su contenedor y no escala una página de escritorio completa.
- El diálogo ocupa casi todo el ancho móvil; cabecera y cuerpo tienen espacio propio, y el cuerpo desplaza su contenido.
- Textos de datos largos envuelven completos; no se truncaron nombres de componentes.

## 5. Contratos de datos y fórmulas

### 5.1 Entrada común del sitio original

Los JSON tienen esta forma, no una lista directa de objetos:

~~~json
{
  "tabla": "nombre",
  "columnas": ["fecha", "categoria_id", "aa"],
  "filas": [["2026-09-30", "t433", 0.045761]]
}
~~~

Conversión: cada fila se convierte en un objeto usando columnas como claves. Los valores null permanecen null. Nunca se sustituyen automáticamente por cero.

La maqueta alinea series mensuales mediante AAAA-MM. Ésta es una decisión de granularidad: el IPCA viene fechado al cierre del mes y los fiscales al inicio. No se unen por posición de fila ni se mezclan ambas familias en un supuesto día común.

### 5.2 Inflación y núcleos

**Tablas:** infj_serie.json, od_bcb.json, od_total.json.

1. IPCA: categoria_id = t433, columna aa.
2. Núcleos: n11427, n27839, n4466, n16122, n28750; columna aa.
3. Para cada mes, promedio aritmético de los cinco aa sólo si los cinco son válidos.
4. IPCA y núcleos pasan de fracción a porcentaje multiplicando por 100.
5. Meta base: meta por anio de od_bcb con datos disponibles.
6. Si od_total contiene metas válidas en un año, su media anual sustituye a od_bcb para ese año, igual que en el adaptador original.
7. Meta × 100; años sin información permanecen null.
8. Banda activa sólo con ambos valores válidos e IPCA > núcleos.
9. Calendario mensual completo desde enero de 2008 hasta el último mes del IPCA. Los meses sin valor interrumpen la línea.

El promedio anual de metas replica el código actual: si un escenario futuro exige cambios de meta dentro del año, adapta explícitamente el contrato; no reutilices esta transformación sin revisarla.

### 5.3 Primario fiscal

**Tabla:** fiscal_mensual.json.

- Observado: primario_observado_pib.
- Referencia: primario_estabilizador_pib.
- Unidad de ambas columnas: puntos de porcentaje del PIB, ya escalados.
- Fórmula: brecha = estabilizador − observado.
- Brecha positiva: falta primario. Brecha negativa: observado por encima del estabilizador.
- Se conserva el signo en la tabla Por periodos; el resumen expresa magnitud absoluta con una etiqueta que explica el signo.
- Desde enero de 2010 al último mes de la tabla; calendario completo y discontinuidades ante null.

**Cruce entre dos meses:** si d0 y d1 son las brechas de extremos y d0 × d1 < 0:

~~~text
t = d0 / (d0 − d1)
x_cruce = x0 + t × (x1 − x0)
y_cruce = observado0 + t × (observado1 − observado0)
~~~

Dibuja dos polígonos, uno a cada lado del cruce. No pintes todo el intervalo con el color del primer mes. Si falta cualquiera de los cuatro valores, no dibujes ese tramo de relleno. La interpolación es geométrica entre observaciones mensuales; no añade un dato observado.

### 5.4 Amplitud

**Tablas:** actv_serie.json y actv_miembro.json.

Universos, en orden del código:

| Agregado | Familias de miembros |
|---|---|
| IBC-Br (sectores) | IBC-Br |
| Todas las series (PMC, PMS, PIM) | Comercio, Servicios, Industria |
| PMC (actividades) | Comercio |
| PMS (actividades) | Servicios |
| PIM (secciones) | Industria |

Filtra miembros con unidad = Volumen y rol = Hijo. Deduplica categoria_id dentro de cada agregado. Para el mes consultado, conserva sólo componentes con m3a y m12 no nulos.

~~~text
d = m3a − m12                 # fracción
si abs(d) <= 0.001: igual     # incluye exactamente el límite de 0,1 pp
si d > 0.001: acelera
si d < -0.001: desacelera

n = aceleran + iguales + desaceleran
porcentaje_acelera = 100 × aceleran / n, si n > 0
diferencia_pp = 100 × d
~~~

No confundas m12 con a12. En este caso se compara m3a con m12. Es una distinción importante del código auditado del 5 de noviembre.

Cada fecha conserva grupos con children, counts y n. Los componentes se ordenan por diferencia descendente. El filtro de búsqueda no recalcula los porcentajes del agregado: filtra la presentación de componentes, manteniendo su universo original.

La maqueta incorpora los últimos 24 meses de actv_serie para explorar fechas, sin ejecutar una consulta remota. No arrastra el dato de un componente rezagado hasta el corte global.

### 5.5 Contribuciones

**Tabla:** grafico_inflacion_v2.json.

| Control | Valores del JSON |
|---|---|
| Mes a mes | periodo = m/m |
| Trimestre a trimestre | periodo = 3m |
| Año a año | periodo = a/a |
| Ajuste | Sin ajuste / Desestacionalizado |

Las seis combinaciones existen en la extracción utilizada. Se incorporan hasta 36 meses de cada combinación. La ventana elige los últimos 12, 24 o 36 registros mensuales disponibles.

| Grupo | serie_id |
|---|---|
| Alimentación y bebidas | ipca\|k7170 |
| Vivienda | ipca\|k7445 |
| Transportes | ipca\|k7625 |
| Salud y cuidados personales | ipca\|k7660 |
| Gastos personales | ipca\|k7712 |
| Educación | ipca\|k7766 |
| Artículos de residencia | ipca\|k7486 |
| Vestuario | ipca\|k7558 |
| Comunicación | ipca\|k7786 |

Para cada mes y grupo, suma aporte × 100 de sus filas válidas. Si falta el grupo o alguno de sus aportes es null, conserva null. Esto hace explícita la falta de información en vez de convertirla en cero, a diferencia del reduce original.

El total toma total_ipca de la primera fila del mes, como el adaptador del monitor, y lo multiplica por 100. El contrato de origen presupone el mismo total repetido para todas las filas del mes. Si se conecta otra fuente, hay que rechazar o resolver totales inconsistentes; esta maqueta no introduce una conciliación nueva.

~~~text
positivo_mes = suma(max(aporte_grupo, 0))
negativo_mes = suma(min(aporte_grupo, 0))
residuo = total_ipca_pct − suma(aportes_pp), sólo con los nueve aportes válidos
dominio_y cubre positivo_mes, negativo_mes, total_ipca_pct y cero
~~~

El residuo se muestra como diferencia, no se etiqueta automáticamente como error ni como décimo grupo. Puede reflejar redondeo o metodología; la maqueta no infiere la causa.

## 6. Arquitectura de la réplica

El HTML tiene tres bloques editables:

1. style: primitivas de layout, fuentes incrustadas y tokens/componentes.
2. script#chart-data: JSON serializado de los ocho adaptadores.
3. script de aplicación: CASES, STATES, vistas, motor SVG, eventos y adaptadores adicionales incrustados.

### Interfaces internas

~~~javascript
// Una observación mensual de líneas; null rompe el trazo.
{ date: "2026-09", values: [4.58, 4.2, 3.0] }

// Una observación de aportes; el orden sigue DATA.groups.
{ date: "2026-09", values: [/* nueve valores o null */], total: 4.58 }

// Una observación de amplitud.
{
  date: "2026-08",
  groups: [{
    id: "pmc",
    name: "PMC (actividades)",
    n: 0,
    counts: { acelera: 0, igual: 0, desacelera: 0 },
    children: [{
      id: "identificador",
      name: "Nombre del componente",
      slow: null, fast: null, gap: null, status: "igual"
    }]
  }]
}
~~~

Estos fragmentos describen la forma, no son registros del archivo real. En la amplitud generada, los hijos sin ambas tasas se excluyen y no quedan como hijos con null.

### Funciones y límites de responsabilidad

| Función / bloque | Responsabilidad |
|---|---|
| build_data en Python | Extraer, alinear y convertir unidades desde los JSON |
| CASES | Títulos, unidades, nombres, colores y notas por caso |
| STATES | Ventana, fecha, búsqueda, orden y grupos abiertos |
| currentRows / selected | Resolver la ventana y el registro consultado |
| caseView | Componer el mismo caso en compacto o ampliado |
| makeControls | Etiquetas y selectores persistentes |
| reading | Dar valores HTML sin depender de leer el SVG |
| amplitudeTable | Mostrar universos, composición y componentes |
| expandedDetails | Desglose del mes, Por periodos y metodología |
| niceDomain | Calcular escala que incluya los valores necesarios |
| linePath | Cortar el trazo ante un null |
| renderChart | Dibujar geometría, ejes, cursor persistente y exploración temporal |
| tooltipContent / tipRow | Contenido semántico por familia; null y unidades explícitas |
| showTip / hideTip / positionTip | Apertura, cierre, ubicación y relación accesible de una ayuda compartida |
| tablePreview / pinTable / tableInspection | Explorar y conservar el detalle de un micrográfico |
| setDate / refresh | Sincronizar todas las representaciones del caso |
| openDetail | Abrir el diálogo sin crear un estado paralelo |

Las vistas compacta y ampliada leen el mismo estado. No dupliques sus cálculos ni mantengas dos fechas independientes. Cuando un filtro deja fuera el mes consultado, se selecciona el último mes de la nueva ventana. La tabla conserva sus grupos abiertos al cambiar de mes.

### Límites deliberados del prototipo

- No conecta en vivo con el monitor ni reemplaza sus renderizadores ECharts.
- No incluye todos los tipos de líneas, tablas o columnas del catálogo.
- No añade un editor de datos, panel de diseño, descarga CSV ni nuevas métricas.
- Los tooltips flotantes son una vista previa con ratón o foco de teclado. En táctil, clic/toque fija la misma información en un panel persistente; el selector de mes y el recorrido mensual siguen disponibles.
- La tabla temporal muestra hasta doce observaciones cercanas al mes consultado; el selector y el recorrido permiten visitar el resto de la ventana.
- El buscador es una ayuda de presentación; los porcentajes mantienen el denominador del agregado.
- Las líneas fiscales son interpolaciones geométricas entre meses, no mediciones diarias.

## 7. Estados, interacción y accesibilidad

| Acción / situación | Comportamiento definido |
|---|---|
| Abrir la página | Ocho casos; último mes en series, corte único de gasto y ventana de tres años en cascada |
| Cambiar ventana | Recalcular vista; conservar mes si sigue dentro, si no elegir último |
| Cambiar variación o ajuste | Usar la combinación local correspondiente; mismo mes si existe |
| Consultar mes | Actualizar cursor, lectura, desglose y tabla temporal |
| Pasar el ratón por un gráfico | Vista previa del mes más cercano; no cambia la consulta persistente |
| Hacer clic o tocar gráfico | Seleccionar el mes más cercano en X y fijar su lectura |
| Ver último mes | Liberar la consulta fijada y volver al corte de la ventana |
| Enfocar gráfico con teclado | Mostrar ayuda del mes seleccionado; flechas recorren, Inicio/Fin van a extremos y Enter fija |
| Escape con ayuda abierta | Cerrar sólo la ayuda; sin ayuda abierta se conserva el cierre normal del diálogo |
| Pasar el ratón o enfocar un micrográfico | Mostrar conteos del agregado o tasas/diferencia del componente |
| Pulsar micrográfico | Conservar su detalle encima de la tabla; Limpiar consulta lo retira |
| Agrandar | Abrir diálogo nativo; mismo caso, estado y datos |
| Cerrar | Botón, Escape o clic exterior; devolver foco al botón Agrandar |
| Navegar por teclado | Selectores, botones, búsqueda y recorrido nativos con foco visible |
| Abrir agregado | Botón con aria-expanded y aria-controls; hijos completos |
| Buscar | Mostrar grupos coincidentes y componentes encontrados; mensaje si no hay resultados |
| Sin ambas tasas | Excluir del denominador de amplitud |
| Sin dato de línea | Mostrar discontinuidad y Sin dato en la consulta |
| Sin combinación de aportes | Mensaje de ausencia y controles para recuperarse |
| Cambiar tamaño | ResizeObserver redibuja sólo la geometría con el ancho del contenedor |
| Movimiento reducido | Sin transiciones ni desplazamiento suave |

El SVG ofrece un nombre accesible; los valores relevantes se leen además en HTML y tablas. El diálogo nativo aporta modalidad y navegación de foco en navegadores modernos. El texto de estado comunica cambios de selección sin depender de color.

### 7.1 Tooltips: vista previa y consulta persistente

**Dos estados distintos:** recorrer un gráfico es explorar; hacer clic, tocar, cambiar el selector o usar flechas es elegir una fecha. La vista previa nunca llama a setDate ni cambia filtros. La consulta elegida se conserva aunque el puntero visite otros meses.

Al fijar una fecha de línea o columnas, el panel inferior muestra Consulta fijada y un botón Ver último mes. Ese botón vuelve al último registro de la ventana actual y retira la marca de fijación. En la tabla, cada micrográfico puede conservar un detalle en un panel encima de las filas; Limpiar consulta retira ese panel sin cambiar el mes ni los agregados abiertos.

| Caso | Jerarquía del tooltip |
|---|---|
| IPCA y núcleos | Mes, IPCA destacado, promedio de núcleos y meta; todos con % a/a |
| Primario fiscal | Mes, brecha con signo en pp, observado y estabilizador en % PIB, significado del signo |
| Aportes | Mes, variación y ajuste; total en % separado de los nueve aportes en pp, en orden estable |
| Amplitud por agregado | Nombre y mes; porcentaje que acelera y conteos de los tres estados con denominador |
| Componente de amplitud | Nombre y mes; diferencia en pp y ambas tasas en %, con explicación del umbral |

**Datos ausentes:** se escribe Sin dato en la fila correspondiente. No se suprime una serie nula del tooltip, no se transforma a cero y no se añade una unidad a un valor inexistente.

**Formato:** el título y los valores usan al menos 16 px; el dato principal, 20 px; rótulos y ayudas, 14 px. Etiquetas largas envuelven dentro de una columna flexible y números con unidades quedan juntos. En aportes se mantienen los nueve grupos: no se acorta la lista en silencio ni se cambia de orden al recorrer meses.

**Ubicación:** la ayuda se coloca junto al puntero o al elemento enfocado, cambia de lado cuando se acerca al borde y se mantiene dentro del viewport con margen. La anchura máxima es de 360 px; en ventanas bajas la ayuda puede desplazarse verticalmente. Cuando el navegador ofrece Popover API, una capa manual permite mostrarla sobre el diálogo sin quedar detrás. La alternativa mantiene el nodo dentro del diálogo abierto o del body.

**Interacción:** apertura inicial tras 120 ms, actualización inmediata mientras la ayuda ya está visible, cierre al salir con un margen de 160 ms para poder entrar al propio tooltip. El puntero puede situarse sobre la ayuda y seleccionar o desplazar su contenido. La ayuda no contiene botones ni enlaces; la acción persistente se hace en el gráfico o micrográfico.

**Teclado:** cada gráfico mensual se expone como un control deslizante horizontal con mínimo, máximo, posición y mes accesible. Las flechas fijan el mes siguiente/anterior, Inicio/Fin seleccionan extremos y Enter o espacio conservan el mes actual. Los micrográficos son botones nativos, accesibles por Tab, Enter y espacio. El selector mensual sigue siendo una alternativa equivalente.

**Escape:** cierra la ayuda y evita que el mismo evento cierre también Agrandar. No borra la consulta persistente. La ayuda no reaparece bajo el mismo puntero hasta salir y volver a entrar; la siguiente interacción de teclado permite abrir otra consulta.

**Táctil:** no se simula hover. Un toque sobre el gráfico fija el mes y un toque sobre una barra de composición o un par de círculos conserva su detalle. La restauración de foco tras el toque no abre una burbuja accidental encima del contenido.

**Limpieza:** al cambiar filtros, redimensionar, desplazar el documento, abrir o cerrar Agrandar o sustituir un gráfico, se retira la vista previa y su relación aria-describedby. El desplazamiento dentro del propio tooltip no lo cierra. Los datos fijados pertenecen a STATES y sobreviven al cambio compacto/ampliado.

**Separación técnica:** tooltipContent sólo formatea; showTip sólo presenta; setDate y pinTable fijan el estado. Los nombres se escapan con E antes de insertarlos en HTML. No se ejecuta HTML procedente de una fuente de datos.

Los datos se cargan de forma síncrona desde el propio HTML: no se simula una espera de red ni se introduce un spinner. Si se conecta una API en una réplica futura, habrá que añadir carga, error recuperable y cancelación sin borrar el estado vigente.

## 8. Cómo extender a las tarjetas repetidas

### Líneas: qué reutilizar y qué adaptar

Reutiliza cabecera, controles, calendario, consulta mensual, ejes, fuentes, diálogo, lectura y tabla temporal.

Adapta unidad, frecuencia, dominio, semántica de series y referencias. Para expectativas por año de referencia, no confundas la fecha de encuesta con el año proyectado. Para índices de actividad, no compares niveles con porcentajes en el mismo eje sin una transformación explícita. Para intervalos de pronóstico, documenta probabilidades y límites; no reutilices las bandas de IPCA > núcleos.

### Tablas: qué reutilizar y qué adaptar

Reutiliza alineación numérica, encabezados, búsquedas, botones desplegables, conservación del estado y presentación móvil.

Adapta las columnas y las filas a su tarea. El gasto con barras de peso necesita una unidad monetaria y su propio total. La sensibilidad con R² necesita horizonte, muestra y modelo. No conviertas todas esas tablas en amplitud. AM1-03-2 y AM2-02-2 siguen siendo excepciones del inventario: su geometría dominante corresponde a otras familias.

### Columnas: qué reutilizar y qué adaptar

Reutiliza cero visible, separación de positivos/negativos, selección mensual, consulta y detalle.

Adapta apilado frente a agrupación, número de componentes y relación entre barra y línea. Una columna de nivel simple no necesita nueve colores. Una descomposición en pp no se convierte a proporción del total. Si cada serie tiene una unidad diferente, resuelve la comparación explícitamente; no añadas un doble eje silencioso.

### Orden sugerido de aplicación

1. Elegir un caso nuevo de cada variante, no todas las repeticiones a la vez.
2. Copiar la estructura de interacción de la familia.
3. Escribir el adaptador y declarar unidades antes de dibujar.
4. Conservar el identificador original para trazabilidad.
5. Comparar requisitos del nuevo caso con las excepciones documentadas.
6. Sólo después extender a las tarjetas equivalentes.

## 9. Prompt maestro para otro LLM

Copia este bloque junto con el HTML, esta guía y las tablas del caso que quieras adaptar:

~~~text
Quiero adaptar un gráfico del monitor usando la maqueta entregada como referencia.

Primero lee la guía y el HTML. Conserva su lenguaje visual, sus controles accesibles
y la separación entre datos, adaptadores y renderizadores.

Caso a adaptar:
- Identificador original: [completar]
- Familia y variante: [línea / tabla / columna y su variante]
- Pregunta que debe responder: [completar]
- Fuente y columnas: [adjuntar o identificar archivos reales]
- Frecuencia y fecha de referencia: [completar]
- Unidad de entrada y de presentación: [completar]
- Fórmulas y referencias que deben conservarse: [completar]

Entregables:
1. HTML funcional y editable que abra sin servidor, con fuentes y datos locales.
2. Guía detallada de las decisiones, adaptador, cálculos y casos límite.

Vista compacta:
- Mantén título, unidad, corte y comparación principal.
- Conserva acceso a todas las series o categorías exigidas.
- Usa un selector de fecha accesible y una lectura numérica en HTML.
- Añade tooltip al pasar el ratón y al enfocar con teclado, con fecha, unidades
  y datos ausentes explícitos. La vista previa no modifica la consulta fijada.
- Clic/toque conserva los datos en el panel; Escape cierra sólo la ayuda.
- Para columnas, separa total en % y componentes en pp; conserva las categorías.
- En micrográficos, usa un botón accesible y detalla sólo la comparación concreta.

Agrandar:
- Debe conservar filtros y fecha del compacto.
- Añade espacio, detalle por periodo y metodología pertinente a la familia.
- Cierra con botón y Escape y devuelve el foco al control que lo abrió.
- No copies secciones de otro caso si no corresponden a su semántica.

Reglas:
- No inventes datos ni sustituyas null por cero.
- No alinees series por posición: une por periodo y declara su granularidad.
- No multipliques por 100 columnas que ya están en porcentaje o pp.
- No normalices contribuciones a 100 %.
- No elimines categorías para simplificar la estética.
- No conviertas un episodio en un intervalo de incertidumbre.
- Conserva las identidades de comentario existentes si editas nodos con UUID.
- Centraliza tokens; evita CDN, fuentes remotas y dependencias ocultas.
- Haz que todos los controles implementen un comportamiento real.
- No modifiques el sitio original cuando se haya pedido una maqueta separada.

Antes de crear una nueva entrega, describe el alcance y las diferencias del caso.
Si sólo faltan decisiones pequeñas y reversibles, decláralas como supuestos.
Si faltan datos esenciales, identifica exactamente el archivo o campo requerido.
No afirmes que probaste o renderizaste algo si no lo hiciste.
~~~

## 10. Prompts específicos

### Nueva línea

~~~text
Usa el caso IPCA como estructura de una serie temporal y el caso fiscal sólo si
necesitas un relleno de brecha. Declara cada serie como observada, referencia,
expectativa o contrafactual. Conserva null, las fechas y las unidades.
Si hay cruces, calcula su intersección antes de colorear el área.
Añade el caso a CASES y STATES sin duplicar el motor.
~~~

### Nueva tabla

~~~text
Usa el caso de amplitud para las interacciones, no para copiar sus fórmulas.
Define el significado y la unidad de cada columna, el universo de cada fila,
la regla de agrupación y si los grupos se superponen.
La búsqueda no debe cambiar un denominador estadístico.
Los detalles deben poder abrirse con teclado y conservarse al Agrandar.
~~~

### Nuevas columnas

~~~text
Usa el caso de aportes como estructura de selección y consulta.
Decide explícitamente si las barras son simples, agrupadas o apiladas.
Declara la unidad de cada barra y de la línea, si existe.
Calcula el dominio con positivos, negativos y línea, y conserva cero.
Si hay suma y total, muestra su diferencia sin modificar los componentes.
~~~

## 11. Criterios de revisión para una futura integración

Esta sección es una pauta para quien integre la propuesta; no documenta pruebas ejecutadas en esta entrega.

1. Elegir último mes, un mes intermedio y un mes sin referencia.
2. Comprobar un null y una discontinuidad sin interpolación inventada.
3. Comparar contra los JSON un valor y una transformación por familia.
4. Revisar la brecha fiscal positiva, negativa, exactamente cero y con cruce entre meses.
5. Comprobar que la escala contiene apilados y línea.
6. Revisar que los nueve grupos siguen presentes y no se normalizaron.
7. Verificar el límite de amplitud ±0,001 en fracción y n = 0.
8. Abrir componentes, cambiar fecha y Agrandar: no debe perderse el estado.
9. Buscar un hijo, borrar búsqueda y recuperar la lista completa.
10. Recorrer con teclado, cerrar con Escape y confirmar retorno de foco.
11. Revisar 375, 768, 1024 y 1440 px con nombres largos y zoom.
12. Comprobar que la tabla móvil conserva unidades y todos sus valores.
13. Si se modifica el adaptador de origen, actualizar la guía junto al código.
14. Recorrer varios meses con el ratón sin que cambie la fecha fijada en el panel.
15. Conservar una consulta, abrir Agrandar y cerrar: mismo mes y mismo detalle.
16. Revisar tooltip cerca de cada borde, con nueve grupos y con un valor null.
17. Pulsar Escape sobre una ayuda dentro del diálogo: primero cierra la ayuda, después el diálogo.
18. Recorrer con flechas, Inicio/Fin y selector mensual; fijar micrográficos con Enter y espacio.
19. En táctil, confirmar consulta persistente sin burbuja de hover ni pérdida de desplazamiento vertical.

## 12. Trazabilidad y decisiones pendientes

La extracción se basa en:

- assets/js/derivados/am2.js: AM2-03-1, nucleoAA, GRUPOS_APORTE y AM2-01-0.
- assets/js/derivados/am4.js: AM4-02-0.
- assets/js/derivados/am1.js: AGREG_03, conteo, tablaAmplitud e idsDe.
- data/infj_serie.json, od_bcb.json, od_total.json, fiscal_mensual.json, grafico_inflacion_v2.json, actv_serie.json y actv_miembro.json.
- Ampliación: data/empleo_pagina.json, fis_gasto.json y fiscal_cascada.json.
- Adaptadores nuevos: AM1-01-4 e ids de actividad; AM3-02-3 y medianaDesoc; AM4-07-3 y tablaGasto; AM4-04-0 y selector ventana04.

Directorio de referencia original:
C:\Users\pablo\OneDrive\Documentos\macro_bz\monitor\qwen3.8-max\site

El monitor original, index.html, maqueta-relojes.html e INFORME_GRAFICOS.md no se modifican con esta entrega. La guía conserva el trabajo previo y documenta ocho ejemplos de cuatro familias.

Queda pendiente elegir qué propuestas se trasladan al monitor y revisar las variantes no representadas antes de aplicarlas de forma masiva. No hay una dependencia pendiente para abrir la maqueta autónoma.

## 13. Especificación detallada de los cuatro ejemplos añadidos

La ampliación conserva los cuatro ejemplos iniciales y sus tooltips. No se cambian sus universos, fórmulas ni fuentes. Se suman cuatro adaptadores y se mantiene un solo diálogo de Agrandar para los ocho casos.

### 13.1 Líneas: índices de actividad, a/a

**Caso original:** AM1-01-4.  
**Tabla:** actv_serie.json.  
**Pregunta:** ¿cómo cambia la actividad del conjunto y de sus sectores en el mismo periodo?

La tarjeta añade el selector Series con dos cestas completas:

| Cesta | Serie 1 | Serie 2 | Serie 3 | Serie 4 |
|---|---|---|---|---|
| PIM, PMC y PMS | IBC-Br (v001) | Industria PIM-PF (v006) | Comercio ampliado PMC (v003) | Servicios PMS (v005) |
| IBC-Br y sectores | IBC-Br (v001) | IBC-Br agropecuario (v007) | IBC-Br industria (v008) | IBC-Br servicios (v009) |

**Contrato:** fecha mensual y a12 × 100. No se utiliza m12, que en otros ejemplos representa otra comparación. Todas las series son observadas y sus trazos son continuos cuando hay datos. No se marca la cuarta como referencia discontinua sólo por ser la última de la lista.

El calendario toma los últimos 48 meses disponibles del conjunto actv_serie. Cada cesta contiene el mismo calendario; un mes sin valor para una serie permanece null. La ventana de 24 meses recorta ese calendario sin modificar los valores ni arrastrar una tasa anterior.

**Compacto:** cuatro líneas, leyenda completa, cesta, ventana y consulta mensual. El panel muestra los cuatro valores del mes.

**Tooltip:** mes y las cuatro variaciones en % a/a, con IBC-Br como lectura principal y el mismo orden de la leyenda. Una serie ausente se identifica como Sin dato.

**Agrandar:** conserva cesta, ventana y mes. Añade el recorrido mensual y una tabla de hasta doce observaciones cercanas, con una columna por serie. Cambiar la cesta conserva el mes cuando existe.

**Reglas de réplica:**

- Declarar todos los identificadores y sus nombres en el adaptador.
- No aplicar un trazo de meta a una serie observada.
- No sumar índices ni tasas de series distintas para inventar un agregado.
- Mantener el calendario completo y no unir datos por posición.
- El corte global y el último dato de una serie concreta pueden diferir: no se inventa el dato del mes global.

### 13.2 Columnas: brecha de desocupación

**Caso original:** AM3-02-3.  
**Tabla:** empleo_pagina.json.  
**Pregunta:** ¿la desocupación desestacionalizada del mes está por encima o por debajo de su referencia histórica?

~~~text
historia = desocupacion_sa válida entre 2012-01-01 y 2019-12-31
referencia = mediana(historia)
tasa_porcentaje = desocupacion_sa × 100
referencia_porcentaje = referencia × 100
brecha_pp = (desocupacion_sa − referencia) × 100
~~~

La columna brecha_pp existente en empleo_pagina pertenece a una comparación distinta y NO se utiliza para este gráfico. Reutilizarla por su nombre sería un error semántico.

La referencia permanece fija al cambiar de ventana. Se representa la historia desde enero de 2016 y se ofrecen los últimos cinco o tres años. Las fechas faltantes se conservan como huecos mensuales.

**Compacto:** barras desde cero, acero para valores positivos y cobre para negativos. Las etiquetas dicen Por encima / Por debajo de la mediana: el color no se interpreta como bueno o malo sin contexto.

**Consulta persistente:** brecha en pp, tasa SA en % y mediana histórica en %. No son tres magnitudes intercambiables.

**Tooltip:** los mismos tres valores y una frase que explica el signo. No se coloca % a una brecha en puntos porcentuales.

**Agrandar:** mismo mes y ventana, gráfico mayor y tabla temporal. El eje contiene positivos, negativos y cero.

**Reglas de réplica:**

- Calcular la mediana con todos los datos válidos del intervalo base, no con el tramo visible.
- No recalcular la referencia al cambiar de ventana o al consultar un mes.
- No convertir null en cero.
- Si se adopta otro intervalo histórico en un escenario nuevo, cambiar la etiqueta, el cálculo y la guía juntos.
- Si faltara toda la historia base, no inventar una mediana: mostrar el caso como no disponible y explicar la dependencia.

### 13.3 Tabla: gasto, partida por partida

**Caso original:** AM4-07-3.  
**Tabla:** fis_gasto.json.  
**Corte disponible:** julio de 2026 en esta extracción.  
**Estructura:** 19 filas ordenadas por orden, con partidas principales, subpartidas y Gasto total.

La fuente es una foto del último corte, no una serie por mes. Por eso la interfaz no añade un selector temporal ficticio. Usa:

1. Comparar en tarjeta: elige Cambio 1 año, Cambio 3 años o crecimiento Real a 1, 2 o 5 años.
2. Consultar partida: permite seleccionar cualquiera de las 19 filas, incluidas las subpartidas plegadas.
3. Botón de grupo: despliega o pliega los hijos en la tarjeta compacta.
4. Barra/valor de peso: vista previa al pasar el ratón o enfocar; clic/toque fija la partida.

Seleccionar una subpartida abre automáticamente su padre en compacto. Cambiar la métrica conserva esa selección. La vista ampliada muestra todas las filas y todos los horizontes, manteniendo el estado de los grupos que se usará al volver al compacto.

#### Unidades: entrada y salida

| Campo de entrada | Transformación | Presentación |
|---|---|---|
| pct_pib | × 100 | Peso en % del PIB |
| d_pct_1a | × 100 | Cambio de peso a 1 año en pp |
| d_pct_3a | × 100 | Cambio de peso a 3 años en pp |
| real_1a | × 100 | Crecimiento real acumulado a 1 año en % |
| real_2a | × 100 | Crecimiento real acumulado a 2 años en % |
| real_5a | × 100 | Crecimiento real acumulado a 5 años en % |

Estas columnas entran como fracciones. Es distinto de fiscal_mensual y fiscal_cascada, que ya contienen niveles en porcentaje y cambios en pp. No aplique una conversión uniforme a todos los archivos fiscales.

Los crecimientos reales multianuales no se anualizan. La maqueta mantiene la magnitud acumulada de origen.

#### Geometría de las barras de peso

~~~text
ancho relativo = peso_partida_en_PIB / peso_gasto_total_en_PIB × 100
~~~

La cifra visible sigue siendo el peso en el PIB. La leyenda explica que la barra compara contra el gasto total. La escala es común para todos los padres e hijos; no se recalcula para magnificar cada fila.

**Jerarquía:** nivel = 1 identifica subpartidas de la partida principal anterior. Gasto total es la referencia de las barras, no una fila que se sume a las demás.

**Tooltip:** nombre completo, corte, tipo de fila, peso, ambos cambios y los tres crecimientos reales, todos con unidad. La consulta fija muestra el peso, el cambio a 1 año y el crecimiento real a 1 año. El detalle completo permanece en Agrandar y en el tooltip.

**Móvil:** la tabla convierte cada fila en un bloque de datos con rótulos explícitos. No se ocultan métricas de la tabla ampliada. Los nombres envuelven completos.

**Reglas de réplica:**

- No sumar partidas principales y subpartidas: hay doble conteo.
- No derivar tasas de crecimiento del gasto total como media de las tasas de los hijos.
- No llamar variación real a un cambio de participación en el PIB.
- No usar el signo de una variación como diagnóstico económico automático.
- Si se cambia el denominador de la barra, cambiar su explicación visible.
- No fabricar una fecha seleccionable para un archivo que sólo tiene un corte.

### 13.4 Cascada: de la deuda inicial a la de hoy

**Caso original:** AM4-04-0.  
**Tabla:** fiscal_cascada.json.  
**Ventanas reales:** 1, 2, 3, 5 y 10 años. La selección inicial es tres años.

Cada ventana tiene deuda_inicial, deuda_final, mes_base, mes_fin y cuatro componentes ordenados: Intereses, Déficit primario, Crecimiento y Residuo.

**Contrato de unidades:** los niveles están en % del PIB y valor de cada componente, en pp. Ya están escalados; no se multiplican por 100.

~~~text
acumulado_0 = deuda_inicial
acumulado_i = acumulado_(i−1) + valor_componente_i
cierre_calculado = acumulado_último
diferencia = deuda_final_informada − cierre_calculado
tolerancia = 0.0001 pp
~~~

La fuente define un residuo como componente. No se elimina por considerarlo ruido, ni se sustituye por la diferencia calculada por la interfaz. Si el cierre supera la tolerancia, la maqueta lo informa y mantiene todas las cifras originales.

#### Por qué la cascada es horizontal

Los pasos se leen de arriba hacia abajo y el eje horizontal mide la posición acumulada en % del PIB. La orientación permite leer nombres completos en tarjetas estrechas y en móvil sin una tira que exija desplazamiento horizontal.

- Nivel inicial: barra desde cero a deuda_inicial.
- Contribución positiva: desde acumulado anterior hasta un nivel mayor, en cobre.
- Contribución negativa: desde acumulado anterior hasta un nivel menor, en azul.
- Conexión entre pasos: guía discontinua en el cierre del paso anterior.
- Nivel final: barra desde cero a deuda_final informada.
- Residuo: tiene el mismo tratamiento geométrico que los demás componentes y una etiqueta explícita.

El selector Consultar paso, clic/toque o las flechas permiten conservar la lectura de una etapa. Las flechas arriba/abajo siguen el orden de la cascada; Inicio/Fin seleccionan niveles inicial/final. El tooltip describe el componente, su contribución y el acumulado antes/después.

**Compacto:** ventana, paso consultado, cascada completa, lectura y conciliación visible. No se esconde una discrepancia hasta que el usuario abra Agrandar.

**Agrandar:** conserva ventana y paso; añade una tabla con tipo, nivel anterior, aporte y cierre de cada etapa. En los niveles, el campo de aporte se marca No aplica, no cero ni Sin dato.

El panel de conciliación presenta nivel inicial, cierre calculado, final informado y diferencia con cuatro decimales. El mensaje distingue un cierre dentro de tolerancia de una discrepancia.

**Reglas de réplica:**

- Mantener orden_componente: reordenar por tamaño cambia la lectura acumulada.
- Usar mes_base y mes_fin reales, no sólo etiquetas relativas como Hoy.
- Mostrar total inicial y final desde cero; las contribuciones son barras flotantes.
- Separar % del PIB de pp en tablas y tooltips.
- Si falta una contribución, no completar silenciosamente el acumulado.
- No introducir una corrección de conciliación inventada.
- Conservar el residuo de origen aunque el cierre aritmético ya parezca correcto.

### 13.5 Arquitectura de extensión sin duplicar la aplicación

El archivo assets/graficos_frecuentes_extra.js se incorpora en el marcador EXTRA_ADAPTERS del script principal antes de montar los casos. Sus funciones no requieren otra página ni un segundo diálogo.

| Pieza adicional | Responsabilidad |
|---|---|
| EXTRA_CASES | Identificar los cuatro adaptadores nuevos |
| DATA.activityBaskets | Dos cestas con el mismo calendario de actividad |
| METRICS | Nombre y unidad de cada horizonte del gasto |
| bridge | Resolver la ventana vigente de cascada |
| extraControls | Controles propios de cada variante |
| extraReading | Consulta persistente con unidades del caso |
| extraTip | Tooltip semántico de las cuatro variantes |
| spendingTable | Jerarquía compacta y detalle completo del gasto |
| bridgeReconciliation | Cierre calculado, final informado y diferencia |
| renderExtraChart | Barras con signo y cascada horizontal |
| selectExtra | Fijar partida, paso o mes sin modificar el resto |
| extraDetails | Tabla temporal o conciliación según la variante |

La extensión delega las líneas al motor existente y reutiliza el gestor de tooltips y el diálogo. Los renderizadores de barras y cascada comparten formato, dominio, selección y estilos. Los eventos de controles propios se resuelven antes del manejador genérico para no tratar una partida como si fuera una fecha.

Al integrar en otro proyecto, puede reorganizarse este código en módulos. Lo que debe conservarse es el contrato de cada adaptador y un solo estado por caso, compartido entre compacto y Agrandar. No copie dos motores de selección independientes.

### 13.6 Prompts específicos de las variantes nuevas

~~~text
ACTIVIDAD
Añade un caso de cuatro líneas observadas con dos cestas seleccionables.
Usa a12 × 100 de actv_serie, el mismo calendario mensual y hasta 48 meses.
Conserva el mes al cambiar de cesta. No dibujes ninguna serie como meta.
Replica tooltips, consulta persistente, tabla por periodos y Agrandar.

BRECHA DE DESOCUPACIÓN
Calcula la mediana de desocupacion_sa válida entre 2012 y 2019.
Representa (tasa SA − mediana) × 100 en pp desde 2016.
No uses el campo brecha_pp del archivo: pertenece a otra comparación.
La referencia no cambia con la ventana visible. Distingue tasa y brecha.

GASTO
Conserva las 19 filas, su jerarquía y el corte real de fis_gasto.
Convierte cada campo según la tabla de unidades, una sola vez.
No sumes padres e hijos. Declara el denominador de las barras.
Muestra todos los horizontes en Agrandar y permite desplegar hijos en compacto.
No inventes una serie temporal para un archivo de corte único.

CASCADA
Usa las cinco ventanas de fiscal_cascada y conserva el orden de sus componentes.
Los niveles ya están en % del PIB; las contribuciones ya están en pp.
Dibuja barras flotantes, conserva el residuo y muestra la conciliación.
No redistribuyas la diferencia de cierre. Usa una tolerancia de 0,0001 pp.
Mantén ventana y paso entre compacto y Agrandar, con consulta por teclado.
~~~

### 13.7 Casos que debe revisar quien integre

Esta lista no afirma pruebas ejecutadas en esta entrega.

1. Cambiar entre las dos cestas de actividad y conservar la fecha.
2. Comparar un valor a12 con la fila original y distinguirlo de m12.
3. Revisar un mes de actividad sin alguna serie: Sin dato, sin arrastre.
4. Cambiar la ventana de desocupación y confirmar que la mediana no se mueve.
5. Contrastar tasa, mediana y resta en pp con los JSON.
6. Ver el cero y los dos signos de las columnas sin recorte.
7. Abrir una partida de gasto y seleccionar un hijo desde el desplegable.
8. Revisar que cambiar la métrica no cambia el universo ni la partida fijada.
9. Comprobar una fila de cada tipo: padre, hijo y total.
10. Comparar d_pct_1a, d_pct_3a y real_2a: una sola conversión × 100.
11. Recorrer las cinco ventanas de cascada y sus seis pasos.
12. Contrastar inicio + cuatro contribuciones con el final informado.
13. Conservar el residuo aunque sea negativo y aunque el cierre sea exacto.
14. Revisar una discrepancia y un valor nulo sin corrección automática.
15. Abrir Agrandar con una partida o paso fijado y regresar sin perderlo.
16. Usar ratón, teclado y toque, incluyendo Escape sobre el tooltip.
17. Revisar 375, 768, 1024 y 1440 px, nombres largos y zoom.
