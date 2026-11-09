# Design System de gráficos · Monitor Brasil

Versión 1.2 · 8 de noviembre de 2026 · tema claro.

## Alcance y apertura

Entrada: [graficos/index.html](graficos/index.html). Se abre desde Open Design o un servidor HTTP local. Para verlo sin servidor, abre [graficos/offline/index.html](graficos/offline/index.html) con doble clic: es la edición sin conexión, con datos y código locales. Sin dependencias remotas.

160 tarjetas actuales, 24 familias visuales y 40 nombres de componentes utilizados. Se recorren también las tarjetas dentro de pilas. El inventario anterior del 5 de noviembre tenía 155 tarjetas: no se reutiliza como conteo vigente.

Este sistema documenta y demuestra las familias existentes. Las 160 tarjetas y el catálogo utilizan el mismo contrato UX. Se conservan los datos, las unidades y las fórmulas originales. Los ejemplos conservan los renderizadores del sitio; el contenedor añade consulta accesible, filtros, leyendas y lectura de entradas. Hay diferencias heredadas: los criterios objetivo de una ficha no certifican que cada tarjeta original ya los cumpla. No es una implementación oficial de IBM Carbon Charts.

## Archivos y autoridad

- DESIGN.md: identidad y tokens generales, que este sistema extiende.
- graficos/tokens-graficos.css: roles de visualización, dimensiones y tipografía.
- graficos/contrato.js: utilidades compartidas para ECharts, formato y estilos de series.
- graficos/inventario.js: familias, variantes, tarjetas, estados y dependencias generados desde el código.
- graficos/catalogo.js: navegación, búsqueda, fichas y cobertura.
- graficos/vista.js: adaptación de componentes reales; mantiene el estado al ampliar.
- graficos/monitor/: copia local de fuentes, renderizadores, estilos y datos necesarios. Es un insumo de referencia; la fuente del producto sigue siendo el sitio original.
- graficos/preparar.mjs: regenera el inventario y esta guía desde la copia congelada graficos/monitor; conservar en el generador los cambios a su contenido. graficos/instalar.mjs revisa el enganche con el sistema de diseño y graficos/construir-offline.mjs reconstruye la edición sin conexión. graficos/rutas.mjs resuelve las rutas de los tres desde la ubicación de la carpeta.

## Dirección y fundamentos

Se continúa la identidad existente de Monitor Brasil; no se presenta como una nueva decisión del usuario. IBM Plex Sans para ejes, texto y etiquetas; Plex Mono para cifras tabulares; Bricolage sólo para títulos de la documentación. Fondo blanco, sin sombras decorativas, perspectiva 3D ni suavizado de series que invente extremos.

### Color y redundancia

Categorías, en orden: azul #2E5C8A, petróleo #2F7A86, acero #6C819B, ciruela #7B5E8C y acero claro #A9B8CB. Conservar la identidad de una serie entre vistas. Después de cinco categorías: agrupar en paneles o seleccionar; no generar nuevos colores arbitrarios. Cobre #C2773A = marca de deterioro; #A85E24 para texto asociado; arena #EDC9A6 = brecha o banda. No asignar mejora al signo positivo sin consultar el dominio: subir inflación, mora o deuda puede ser deterioro. El monitor conserva navy como mejora en sus adaptadores económicos.

Referencia #8A8F96 con trazo 6/4 y rótulo, sin color como única señal. Las categorías claras llevan contorno, forma o texto oscuro fuera de la marca. No usar blanco sobre acero claro o arena. Contraste objetivo: texto normal 4,5:1; texto grande y gráficos esenciales 3:1. Una serie que no alcance el contraste con blanco necesita borde más oscuro y una alternativa textual. No se declara verificado el contraste de cada composición heredada.

### Tipografía, anatomía y dimensiones

Cuerpo 16 px; títulos 20 px; ejes y anotaciones nuevos al menos 12 px; valores auxiliares 14 px. Los renderizadores heredados pueden contener textos de 10–11 px: constituyen deuda de migración, no un token recomendado. La capa del catálogo aplica 12 px a los ejes de ECharts sin sustituir sus formateadores. Espaciado 4/8/12/16/24/32 px. Geometría de líneas 2 px; referencia 1,5 px; marcadores de consulta 8 px.

Anatomía: título descriptivo → unidad y período → filtros → leyenda → trama → lectura fijada → nota y fuente. No repetir el último valor como KPI decorativo. Reservar 280–360 px de altura para la trama compacta; tablas crecen en flujo y pueden desplazarse dentro de su región nombrada. En ampliado, la trama dispone de 440–560 px y el detalle crece sin recorte.

### Ejes y formatos

Barras y áreas de magnitud parten de cero; líneas pueden usar dominio ajustado, siempre rotulado. No sincronizar escalas de unidades diferentes. Mantener 4–7 marcas útiles, sin años duplicados ni decimales en ticks cuyo paso es entero. Fechas en español, mes abreviado y año; frecuencia y ventana explícitas. Las ventanas compactas del monitor usan recortarLTM; ampliado conserva la historia completa disponible.

Los adaptadores definen las unidades: una fracción puede requerir ×100, mientras que muchos datos fiscales ya están en puntos. Nunca aplicar una conversión global. Diferenciar %, pp, pb, R$, R$/US$, miles y millones. null significa ausencia; cero sigue siendo un dato. No unir huecos, arrastrar la última observación ni sumar universos o padres e hijos distintos.

## Interacción y accesibilidad

Hover = consulta provisional; clic/toque = consulta fijada en un panel persistente. La leyenda nombra y distingue series también con trazos o formas. Los controles son HTML nativo con nombre visible, foco y área mínima de 44 px. En tramas ECharts, flechas izquierda/derecha e Inicio/Fin recorren observaciones; arriba/abajo cambian de serie; Enter fija y Escape limpia la consulta. Existe una tabla de la entrada transformada para las geometrías complejas: los nombres de campos se conservan y no se agrega una segunda conversión de unidades.

Agrandar mantiene el mismo documento de ejemplo, los filtros y la consulta; Escape cierra el ampliado desde el ejemplo o desde la ficha y restaura el foco. La etiqueta de ventana cambia a Historia completa; un corte transversal no recibe un filtro temporal ficticio. Los estados son: carga anunciada; error recuperable con Reintentar; ausencia con motivo; éxito con fuente. Los FALTA/TERCEROS se muestran como no disponibles, sin inventar datos. DERIVAR indica cálculo local, no ausencia. La cobertura indica estados configurados. La verificación del 8 de noviembre comprobó la carga de las 156 vistas con datos y el motivo de las 4 ausencias; no certifica accesibilidad completa.

A 375 px, una columna y controles que se reorganizan; nombres completos accesibles, consulta táctil y leyendas fuera de sectores pequeños. Las tablas anchas se desplazan dentro de su propia región. A 768 px, lectura apilada con más aire; desde 1024 px, índice lateral; a 1440 px, trama amplia y documentación en dos columnas. Sin scroll horizontal del documento ni bloqueo de zoom. Movimiento sólo de estado, 150–200 ms; respetar prefers-reduced-motion.

## Contrato de implementación

Separar datos crudos → adaptador semántico → entrada del componente → renderizador → estado compartido. El contrato conserva IDs, fuentes, fórmulas, unidades, filtros, orden temporal, referencias y ausencias. No serializar funciones formateadoras como si fueran datos. La API actual es componente(elemento, entrada, { clave, grande, componente }); puede devolver una instancia ECharts o montar HTML. Los componentes de página tienen prioridad sobre el registro general: barras_div no es el mismo dibujante en todas las páginas.

Ejemplo para una nueva visualización:

~~~js
import { opcionesBase, estiloSerie } from './graficos/contrato.js';
const opciones = opcionesBase({
  xAxis: { type: 'time' },
  yAxis: { type: 'value', name: entrada.unidad },
  series: entrada.series.map((s, i) => ({
    ...estiloSerie(i), name: s.nombre, type: 'line',
    data: s.puntos, connectNulls: false, smooth: false
  }))
});
chart.setOption(opciones);
~~~

No añadir un eje secundario, suavizado, normalización o agrupación sin una justificación semántica y un contrato explícito. La API de utilidades no reemplaza los adaptadores económicos actuales.

## Familias

### F01 · Series temporales de líneas

Evolución de una o varias variables en el tiempo. Es la familia de mayor alcance y reúne el dibujante compartido, la variante con leyenda y la variante fiscal.

- **Usar y conservar:** Serie simple; comparación de varias series; observado frente a referencia o contrafactual; trayectoria de expectativas; relleno entre curvas; bandas de incertidumbre; episodios y anotaciones.
- **Compacto:** Mostrar una comparación principal, las referencias necesarias y una jerarquía inequívoca de series. Mantener identificable la última fecha.
- **Ampliado:** Abrir la misma selección con más espacio; permitir consultar fechas y series; mostrar definiciones, referencias y, cuando aporten, paneles separados o valores tabulados.
- **Regla semántica:** No unir por posición de fila datos con fechas distintas. No confundir una banda de percentiles con un intervalo de pronóstico. Los rellenos de brecha requieren probar cruces y valores negativos.
- **Criterios de implementación:** Densidad de series y leyendas; continuidad ante faltantes; calendario y rezagos; referencias de cero/meta; unidades y dominios; diferenciación entre observado, expectativa y contrafactual.
- **Componentes activos:** `lineaL`, `linea`, `tabla`, `serie_tiempo`.
- **Tarjetas actuales:** AM1-01-4, AM1-01-6, AM1-04-0, AM1-04-2, AM1-05-0, AM1-05-2, AM1-06-0, AM1-06-1, AM1-06-3, AM2-00-1, AM2-00-3, AM2-02-1, AM2-03-1, AM2-03-2, AM2-03-3, AM3-01-0, AM3-02-1, AM3-02-2, AM3-05-1, AM3-06-1, AM3-06-2, AM3-06-3, AM3-07-3, AM3-09-7, AM3-09-4, AM3-10-3, AM3-10-1, AM3-11-0, AM4-02-0, AM4-03-1, AM4-04-1, AM4-04-2, AM4-04-3, AM4-05-1, AM4-05-2, AM4-06-0, AM4-08-1, AM4-09-0, AM5-02-0, AM5-03-1, AM5-05-3, AM5-05-5, AM5-06-3, AM5-07-1, AM5-08-1, AM5-08-3, AM6-02-0, AM6-02-2, AM6-04-1, AM6-05-0, AM6-06-1, AM6-06-2, AM6-06-3.

### F02 · Columnas, aportes y combinaciones barra/línea

Magnitudes por fecha o categoría. El mismo componente admite columnas normales, apiladas y una línea adicional.

- **Usar y conservar:** Columna simple; varias series; contribuciones apiladas; valores positivos y negativos; columna con línea superpuesta.
- **Compacto:** Priorizar total y principales componentes. Hacer visibles cero, unidad y fecha; conservar categorías que el negocio exige.
- **Ampliado:** Dar espacio a todos los componentes, consulta por fecha y explicación de aportes. Incluir una tabla de contribuciones y comparación temporal cuando sean útiles.
- **Regla semántica:** No normalizar a 100 % una composición de aportes en pp. No ocultar componentes para que el gráfico se vea limpio sin conservar acceso a ellos.
- **Criterios de implementación:** Número de grupos y colores; ancho de barra; etiquetas de fecha; lectura de negativos; escala que cubra el total apilado y la línea; diferencia entre nivel y contribución.
- **Componentes activos:** `columnas`, `tabla`.
- **Tarjetas actuales:** AM2-01-0, AM2-06-1, AM3-02-3, AM3-04-3, AM3-09-2, AM3-08-3, AM3-09-3, AM3-10-4, AM3-10-0, AM3-11-1, AM4-05-3, AM4-07-2, AM5-04-0, AM5-06-1, AM5-08-2.

### F03 · Tablas analíticas y tablas con micrográficos

Vistas en las que comparar valores y categorías en filas es la tarea principal. Algunas celdas contienen barras, tiras de composición, flechas o miniseries.

- **Usar y conservar:** Tabla simple; agrupaciones; filas desplegables; tablas de amplitud; ranking; gasto con barras de peso; sensibilidad con R²; miniseries dentro de una celda.
- **Compacto:** Conservar las columnas de mayor uso y una jerarquía estable de filas. Resolver categorías largas sin perder el texto completo.
- **Ampliado:** Mostrar detalle de filas, explicaciones, columnas adicionales y controles de consulta realmente útiles. Mantener los estados desplegados y los filtros.
- **Regla semántica:** No tratar todos los usos de tabla_am1 como una tabla idéntica. AM1-03-2 se asigna a F16 y AM2-02-2 a F14 por su geometría dominante.
- **Criterios de implementación:** Ancho de columnas, longitud de nombres, alineación numérica, agrupaciones, acceso a hijos, selección/filtros, unidades y lectura móvil. La geometría incrustada requiere su propia revisión.
- **Componentes activos:** `tabla_am1`, `tabla`, `tabla_gasto`, `sensibilidad_tabla`.
- **Tarjetas actuales:** AM1-01-1, AM1-01-5, AM1-03-0, AM1-03-3, AM1-04-1, AM1-04-3, AM1-06-2, AM2-00-0, AM2-00-2, AM2-02-0, AM2-01-1, AM2-04-0, AM2-04-3, AM2-05-1, AM3-01-2, AM3-03-4, AM3-04-1, AM3-05-6, AM3-07-2, AM4-07-3, AM5-01-2, AM5-09-0.

### F04 · Cascadas o puentes de descomposición

Explican cómo un valor inicial llega a uno final mediante contribuciones intermedias.

- **Usar y conservar:** Puente de desocupación; masa salarial; consumo; servicio de deuda; deuda pública; gasto fiscal. La variante fiscal cambia etiquetas y habilita scroll en móvil.
- **Compacto:** Destacar inicio, final y contribuciones principales, sin romper la suma. Si hay agrupación, conservar un detalle verificable.
- **Ampliado:** Exponer cada paso con nombre completo, valor y explicación. Añadir tabla de conciliación de la suma y períodos inicial/final.
- **Regla semántica:** Inicio + contribuciones = final, con tolerancia declarada. El residuo debe identificarse. La cascada ampliada no puede cambiar la fórmula del compacto.
- **Criterios de implementación:** Cierre aritmético, signos, conexión entre pasos, rótulos largos, totales inicial/final, residuo y tratamiento de contribuciones pequeñas.
- **Componentes activos:** `cascada`, `cascada_scroll`.
- **Tarjetas actuales:** AM3-04-0, AM3-06-0, AM3-10-6, AM4-04-0, AM4-07-1, AM5-02-1, AM5-05-1, AM5-05-4.

### F05 · Dispersión, burbujas y comparaciones sectoriales

Relacionan dos variables por entidad. Las burbujas añaden tamaño; la variante CLU añade distancia a una diagonal y a una referencia.

- **Usar y conservar:** Momentum; relación con rezago; crédito/empleo; empleo/salario; peso/costo de deuda; salario frente a productividad.
- **Compacto:** Mostrar puntos con una jerarquía de etiquetas limitada y referencias explícitas. Reservar espacio para las entidades destacadas.
- **Ampliado:** Permitir inspeccionar entidades, ver nombres completos y acceder a una tabla equivalente. Explicar tamaño, período y referencias sectoriales.
- **Regla semántica:** Área o radio de burbuja deben tener una regla explícita. La variante CLU representa salario menos productividad: no eliminar su diagonal al unificar el componente.
- **Criterios de implementación:** Solapamiento de puntos y rótulos, unidades de X/Y, rezagos, selección de entidades, significado del tamaño, referencias y interpretación de correlación.
- **Componentes activos:** `dispersionL`, `burbujas`, `clu_sectores`.
- **Tarjetas actuales:** AM1-03-1, AM1-05-1, AM1-05-3, AM1-06-4, AM1-06-5, AM3-03-3, AM3-08-0, AM3-08-1, AM3-09-0, AM3-10-2, AM5-05-2.

### F06 · Trayectorias en dos variables y relojes del ciclo

Unen observaciones en orden temporal sobre un plano X/Y. Comparten dibujante, pero no todas las tarjetas son el mismo reloj económico.

- **Usar y conservar:** Reloj del IPCA; reloj laboral; crédito/empleo por intensidad laboral; transferencias/participación; inclusión bancaria/deuda.
- **Compacto:** Usar el reloj depurado ya definido: historia tenue, tres tramos recientes y último punto identificado.
- **Ampliado:** Para los dos relojes ya trabajados, reutilizar la maqueta y guía existentes. Para las otras trayectorias, decidir contexto, períodos y bloque relacionado según su pregunta.
- **Regla semántica:** La secuencia contexto → períodos → reloj laboral es la decisión de la maqueta actual, no una regla para toda trayectoria de la web.
- **Criterios de implementación:** Orden temporal, cruces, último dato, marcas de fecha, referencias de cuadrantes y diferencias de frecuencia. La tarjeta AM3-08-2 está bloqueada por datos.
- **Componentes activos:** `trayectoria`.
- **Tarjetas actuales:** AM2-04-1, AM3-02-0, AM3-08-2, AM4-08-0, AM5-06-2.

### F07 · Barras horizontales de magnitud o divergencia

Comparan valores por categoría. Las divergentes se abren a ambos lados de cero; otras son rankings o barras con un tope.

- **Usar y conservar:** Cambios de ocupación/ingreso; efectos sobre deuda; recaudación; transferencias por programa; crédito por producto.
- **Compacto:** Alinear nombres, pistas y valores. Hacer evidente el cero o el límite de representación.
- **Ampliado:** Dar acceso al ranking completo y a nombres/valores exactos, con explicación de signo y escala. Mostrar sin ambigüedad los datos fuera del tope.
- **Regla semántica:** barras_div tiene implementaciones distintas en Mercado laboral y Fiscal. Un cambio basado solo en el nombre técnico no actualiza automáticamente ambas.
- **Criterios de implementación:** Orden de filas, ancla en cero, valores negativos, nombres largos, unidades y distinción entre barra real y barra recortada.
- **Componentes activos:** `barras_div`, `barras_h`, `barras_fila`.
- **Tarjetas actuales:** AM3-05-0, AM3-05-3, AM3-05-4, AM3-05-5, AM3-09-6, AM3-10-7, AM4-03-2, AM4-06-1, AM4-09-1, AM5-04-1, AM5-06-0.

### F08 · Composición horizontal y barras de 100

Muestran reparto de un total o el peso de partes sobre una base de 100.

- **Usar y conservar:** Distribución de horas; exposición de deuda por moneda/plazo; ingreso, deuda o gasto por cada R$ 100.
- **Compacto:** Usar orden estable y etiquetas únicamente donde caben, con consulta para segmentos pequeños.
- **Ampliado:** Desplegar denominadores, valores absolutos cuando existan y una tabla completa de partes.
- **Regla semántica:** apilada_100 normaliza por la suma de partes. barras_cien puede representar una barra parcial y conservar el resto vacío: no son intercambiables.
- **Criterios de implementación:** Definición del denominador, segmentos pequeños, orden de partes, legibilidad de rótulos y acceso a las cifras.
- **Componentes activos:** `apilada_100`, `barras_cien`.
- **Tarjetas actuales:** AM3-09-5, AM4-05-0, AM5-01-0, AM5-01-1.

### F09 · Paneles múltiples y series sincronizadas

Una tarjeta contiene varias series dibujadas en paneles separados. La unidad de inventario es la tarjeta, no cada minigráfico interno.

- **Usar y conservar:** Paneles por sector; productividad por sector; dos paneles temporales de ahorro/instrumentos; deuda y servicio.
- **Compacto:** Conservar una organización estable y dejar explícito si comparten dominio o solamente calendario.
- **Ampliado:** Dar más altura a los paneles, sincronizar la consulta de fecha y mantener disponible la serie de referencia.
- **Regla semántica:** Misma fecha no obliga a misma escala Y cuando las variables tienen unidades diferentes. Los paneles laborales sí comparan series con un dominio compartido en su grupo.
- **Criterios de implementación:** Qué ejes se comparten, unidades distintas, referencia del total, sincronización temporal, nombres de panel y tamaño mínimo.
- **Componentes activos:** `paneles`, `paneles_tiempo`.
- **Tarjetas actuales:** AM3-07-0, AM3-10-8, AM5-03-0, AM5-05-0.

### F10 · Comparación antes/después o pesas

Dos valores por fila unidos por un tramo, con su diferencia. La escalera de mora es una variante de la misma gramática.

- **Usar y conservar:** Renuncias; salario reciente frente a anual; inflación esperada por componentes; crecimiento por actividad; mora de hace 12 meses y actual.
- **Compacto:** Distinguir antes y ahora con forma/jerarquía, conservar ambos valores y la diferencia.
- **Ampliado:** Mostrar comparación completa por entidad y explicar los períodos exactos. Permitir revisar el efecto de topes y referencias.
- **Regla semántica:** La comparación puede ser 12m frente a 3m anualizado, no solo dos fechas. escalera_mora usa un tope y un umbral propios; no eliminarlos sin decisión explícita.
- **Criterios de implementación:** Cuáles son las dos fechas o transformaciones, distancia visual, signo, colores, referencia y puntos fuera de escala.
- **Componentes activos:** `pesas`, `escalera_mora`.
- **Tarjetas actuales:** AM3-07-4, AM3-07-5, AM3-09-1, AM5-07-0, AM6-02-1, AM6-06-0.

### F11 · Perfiles de desvío y KPI con pistas

El código permite una cifra aislada o perfiles en filas. En las dos tarjetas activas kpi se usa la galería de desvíos; kpi_barras combina cifra y barras.

- **Usar y conservar:** Distancia a meta en σ; desvío frente a normalidad histórica; ahorro/consumo respecto del ingreso.
- **Compacto:** Destacar posición respecto de la referencia y valor exacto. Identificar datos fuera del dominio de la pista.
- **Ampliado:** Explicar media/meta, ventana y desviación estándar, y permitir consultar series o componentes que forman el perfil.
- **Regla semántica:** Distancia a meta y distancia al promedio no son el mismo z-score. No llamar normales a valores solo por entrar en una franja gráfica.
- **Criterios de implementación:** Referencia histórica, unidad, franja normal, saturación de la pista, coherencia entre cifra principal y barras.
- **Componentes activos:** `kpi`, `kpi_barras`.
- **Tarjetas actuales:** AM2-02-3, AM2-05-2, AM5-02-2.

### F12 · Mosaico de unidades federativas

Ubica las 27 UF brasileñas en una disposición de celdas. No es un mapa coroplético con contornos geográficos.

- **Usar y conservar:** Nivel de desocupación por UF; cambio de desocupación en un año.
- **Compacto:** Mantener el mosaico reconocible, una escala clara y cifras legibles.
- **Ampliado:** Añadir ranking/tabulación de UF y selección por entidad, conservando la relación con el mosaico.
- **Regla semántica:** La rampa para niveles no debe reutilizarse sin más para cambios con signo. Una celda ausente no significa cero.
- **Criterios de implementación:** Siglas, leyenda de color, valor real, datos ausentes, signo de mejora y acceso a nombres completos.
- **Componentes activos:** `mosaico_uf`.
- **Tarjetas actuales:** AM3-03-1, AM3-03-2.

### F13 · Bandas de distribución o abanico

Bandas temporales de percentiles de los subítems, con mediana y media ponderada del IPCA.

- **Usar y conservar:** p10–p90, p25–p75, mediana y agregado ponderado en una misma vista.
- **Compacto:** Destacar la banda central y las dos referencias de lectura necesarias, con leyenda inequívoca.
- **Ampliado:** Permitir consultar percentiles por fecha y explicar ponderaciones, cobertura de subítems y cambios de dispersión.
- **Regla semántica:** Es dispersión entre subítems, no incertidumbre de un pronóstico. Incluir valores negativos en la revisión de cómo se apilan las bandas.
- **Criterios de implementación:** Orden de percentiles, bases del apilado, legibilidad de bandas y separación conceptual entre distribución y agregado.
- **Componentes activos:** `abanico`.
- **Tarjetas actuales:** AM2-03-0.

### F14 · Cajas, rangos y distribución por categoría

Agrupa dos variantes visualmente próximas que necesitan contratos estadísticos separados: rango de expectativas y distribución histórica.

- **Usar y conservar:** Focus: mediana, ±1 desvío y mínimo/máximo; IPCA frente a su historia: caja p25–p75, raya de media y posición actual/percentil.
- **Compacto:** Conservar leyenda estadística explícita y resaltar el dato o centro de comparación.
- **Ampliado:** Mostrar estadísticos exactos, fechas, fuente, número de respondientes cuando exista y tabla de referencia.
- **Regla semántica:** No convertir cajas de ±1 desviación en boxplots Q1–Q3. En AM2-02-2 la raya está configurada como media, no como mediana.
- **Criterios de implementación:** Qué representa caja, raya y bigotes; rango comparable por fila; horizonte de pronóstico; cobertura y estadístico central.
- **Componentes activos:** `tabla_am1`, `cajas`.
- **Tarjetas actuales:** AM2-02-2, AM6-01-0.

### F15 · Convergencia de expectativas al dato publicado

Varias trayectorias muestran cómo cambió la expectativa de un año antes de conocer su dato final.

- **Usar y conservar:** Horizontes alineados de varios años, con dato publicado final o año todavía sin cierre.
- **Compacto:** Distinguir cada año y el extremo publicado, con calendario de horizontes claro.
- **Ampliado:** Permitir revisar una trayectoria, sus encuestas y su error respecto del publicado, separando años completos e incompletos.
- **Regla semántica:** El nombre embudos no se refiere a un embudo de conversión. No dibujar el dato final de un año en curso como si ya se conociera.
- **Criterios de implementación:** Definición de slots, fecha de encuesta frente a año objetivo, cierre observado y ausencia de dato final.
- **Componentes activos:** `embudos`.
- **Tarjetas actuales:** AM6-03-0.

### F16 · Matrices de calor y matrices de escenarios

Celdas en una retícula que codifican valores por color. Incluye matrices temporales y una matriz fiscal de escenarios.

- **Usar y conservar:** Persistencia de presión inflacionaria; termómetro fiscal; primario estabilizador según i/g; amplitud mensual dibujada mediante tabla_am1.
- **Compacto:** Hacer clara la pregunta de la matriz y mantener leyenda y valor consultable por celda.
- **Ampliado:** Añadir ejes y valores completos, definición de umbrales y consulta por fila/columna. En escenarios, explicar parámetros observados frente a supuestos.
- **Regla semántica:** El termómetro fiscal no es un velocímetro. El mapa de sostenibilidad no es geográfico. No usar una escala numérica única si las filas mezclan unidades.
- **Criterios de implementación:** Significado de filas/columnas, dominio de color, unidades por fila, etiquetas omitidas en móvil, umbrales y tratamiento de faltantes.
- **Componentes activos:** `tabla_am1`, `heatmap`, `termometro`, `mapa_sostenibilidad`.
- **Tarjetas actuales:** AM1-03-2, AM2-04-2, AM4-01-0, AM4-03-0.

### F17 · Calendario de sorpresas

Celdas por período clasificadas como sobre, bajo o en línea con lo esperado, con sus recuentos.

- **Usar y conservar:** Sorpresas de inflación y de crecimiento con semántica de color distinta.
- **Compacto:** Mostrar patrón temporal y categorías con texto o forma además del color.
- **Ampliado:** Consultar por período el esperado, el publicado y la diferencia, con resumen del sesgo de sorpresas.
- **Regla semántica:** Sobre lo esperado no significa mejora en todas las variables. El calendario es categórico; no debe presentarse como un heatmap continuo de magnitudes.
- **Criterios de implementación:** Orden temporal, umbral de en línea, esperado/publicado, cobertura, resultado de cada celda y recuentos.
- **Componentes activos:** `calendario`.
- **Tarjetas actuales:** AM6-03-1.

### F18 · Panel de señales con anticipación

Combina balance de señales, tabla de pares y tiras que indican cuándo podría aparecer su señal.

- **Usar y conservar:** Series de productor frente a subítems de IPCA, relación estimada y rezago.
- **Compacto:** Jerarquizar señal, horizonte y entidad. Evitar que la tira temporal compita con todas las columnas.
- **Ampliado:** Mostrar el conjunto completo de pares y definiciones de relación/rezago; permitir inspeccionar ejemplos de la asociación.
- **Regla semántica:** El adaptador calcula el balance sobre todos los pares, no solo las filas mostradas. Una correlación o un rezago estimado no garantiza un resultado futuro.
- **Criterios de implementación:** Universo del balance frente a filas visibles; significado de poder predictivo; rezago; unidad y fecha de cada dato.
- **Componentes activos:** `senales_am2`.
- **Tarjetas actuales:** AM2-05-0.

### F19 · Área apilada temporal

Muestra cómo cambia la composición de la población de 14 años y más a través del tiempo.

- **Usar y conservar:** Partes apiladas en nivel o al 100 %, según configuración del componente.
- **Compacto:** Mantener orden y colores de categorías, con unidad y total identificables.
- **Ampliado:** Consultar composición por fecha y valores de cada categoría, con una tabla equivalente y explicación del denominador.
- **Regla semántica:** No sumar grupos superpuestos ni cambiar de nivel a porcentaje sin avisarlo. La escala debe cubrir la suma apilada, no solamente la mayor serie.
- **Criterios de implementación:** Total, definiciones de categorías, categorías excluyentes, límite superior del apilado y distinción entre personas y porcentaje.
- **Componentes activos:** `area_apilada`.
- **Tarjetas actuales:** AM3-04-2.

### F20 · Flujos Sankey

Representa los orígenes de los nuevos empleos formales mediante nodos y vínculos.

- **Usar y conservar:** Flujos netos hacia empleo formal, con nodos de origen y destino.
- **Compacto:** Priorizar el flujo principal y rótulos claros, manteniendo el total y su unidad.
- **Ampliado:** Consultar nodos y enlaces con una tabla de origen/destino y explicación de qué significa cada flujo.
- **Regla semántica:** No representar un flujo neto como probabilidades de transición individual. No inventar origen de movimientos para cerrar el dibujo.
- **Criterios de implementación:** Conservación de flujos, definición neto/bruto, magnitudes, nombres de nodos, ancho de enlaces y lectura móvil.
- **Componentes activos:** `sankey`.
- **Tarjetas actuales:** AM3-07-1.

### F21 · Treemap de composición jerárquica

Rectángulos anidados representan el peso de partidas y grupos del gasto fiscal.

- **Usar y conservar:** Grupos y hojas de gasto con colores de categoría.
- **Compacto:** Mostrar grupos y las partidas que tienen superficie suficiente, conservando consulta del resto.
- **Ampliado:** Explorar jerarquía y tabla ordenada de partidas con valores y participaciones.
- **Regla semántica:** No usar magnitudes negativas como área ni sustituir el denominador al abrir el detalle. El color de grupo no equivale a evaluación fiscal.
- **Criterios de implementación:** Área proporcional, denominador, jerarquía, partidas pequeñas, contraste de rótulos y acceso al valor.
- **Componentes activos:** `treemap`.
- **Tarjetas actuales:** AM4-07-0.

### F22 · Pictograma cuantitativo de bloques

Un bloque representa un año de salario medio requerido para comprar vivienda; el último puede ser parcial.

- **Usar y conservar:** Comparación de vivienda en años de salario mediante bloques discretos.
- **Compacto:** Conservar equivalencia de bloque y cifra exacta, con una lectura inmediata de la unidad.
- **Ampliado:** Explicar precio y salario utilizados, período, fuente y diferencias entre filas.
- **Regla semántica:** No sustituir bloques por iconos decorativos sin mantener equivalencia cuantitativa. Si el valor supera el número de bloques, la limitación debe ser visible.
- **Criterios de implementación:** Unidad por bloque, fracciones, límite de bloques, rótulo exacto, comparabilidad entre filas y valor fuera del máximo.
- **Componentes activos:** `pictograma`.
- **Tarjetas actuales:** AM5-08-0.

### F23 · Dos caminos por tramos y brecha

Dos referencias horizontales por tramo muestran Focus frente a mercado, y la región entre ambas hace visible la brecha.

- **Usar y conservar:** Comparación de caminos para la Selic con tramos de distinto peso.
- **Compacto:** Distinguir los dos caminos y sus tramos, con una única lectura clara de la brecha.
- **Ampliado:** Consultar valores de ambos caminos por tramo y explicar horizonte, fecha de observación y prima por plazo.
- **Regla semántica:** No interpretar la brecha mercado–Focus como desacuerdo puro: puede incluir prima por plazo. No igualar anchos si representan duraciones distintas.
- **Criterios de implementación:** Duración/peso de tramos, alineación de horizontes, esperado frente a implícito, ancho de brecha y valores faltantes.
- **Componentes activos:** `area_entre`.
- **Tarjetas actuales:** AM6-04-0.

### F24 · Escala de posición respecto de zonas

Ubica la tasa real ex ante en una pista con zonas de expansiva a contractiva y marcas de referencia.

- **Usar y conservar:** Zonas de interpretación y posición de la tasa real, con rango neutral configurado.
- **Compacto:** Mostrar posición actual, zona y unidad, conservando una leyenda breve de los extremos.
- **Ampliado:** Explicar construcción de tasa real, zonas y rango neutral con valores explícitos y su fuente.
- **Regla semántica:** La página declara que la tasa neutral no tiene una serie en el modelo y que el rango se fija manualmente. No presentarlo como estimación actualizada automáticamente.
- **Criterios de implementación:** Origen de umbrales, referencia neutral, unidad, posición de marcas, límites y fecha del dato.
- **Componentes activos:** `escala`.
- **Tarjetas actuales:** AM6-05-1.

## Micrográficos y patrones compuestos

| Patrón | Contrato |
| --- | --- |
| Sparkline en tabla | Ventana y fecha explícitas; sin ejes decorativos; lectura del valor y detalle de serie accesibles; no sustituye la tabla. |
| Pista de desvíos σ | Cero central, banda normal identificada, signo e indicador fuera de escala conservados; no confundir con %. |
| Termómetro temporal | Filas por indicador y columnas por período; mínimo de celda legible; no convertir en velocímetro. |
| Flechas de cambios | Períodos 1m/3m/12m y signos explícitos; valor numérico además de dirección; no equivalen a causalidad. |
| Rachas | Número de períodos, condición y ventana; ausencia distinta de incumplimiento. |
| KPI con contexto | Número y unidad unidos; denominador en bloque independiente; nunca cambiar la escala para hacer caber el texto. |
| Minibarras y cajas | Dominio y estadístico declarados; cifra exacta accesible; topes con señal de corte. |

Los 59 bloques de riel inventariados incluyen texto y selectores, además de cifras y gráficos; no se cuentan como nuevas tarjetas ni nuevas familias. Los ejemplos de estas geometrías se consultan dentro de tablas, perfiles y matrices del catálogo.

## Reglas especializadas preservadas

- Relojes: mantener contexto, lectura por períodos y reloj laboral sólo donde corresponde. Las otras trayectorias no heredan fases económicas automáticas. Consultar design/GUIA_RELOJES_LLM.md del repositorio.
- Cascadas: inicio + aportes = final calculado; conservar residuo y mostrar discrepancia con el publicado; tolerancia del caso fiscal 0,0001 pp.
- Cajas Focus: mediana, ±1 desviación y mínimo/máximo; no llamarlas rango intercuartílico. Caja histórica de IPCA: p25–p75, media y posición actual; no cambiar media por mediana.
- Abanico IPCA: dispersión entre subítems, no incertidumbre de una previsión.
- Embudos: convergencia de expectativas, no embudo de conversión comercial.
- Mosaico UF: disposición de celdas, no contornos geográficos precisos.
- Sensibilidad fiscal: retícula de escenarios y supuestos, no mapa geográfico ni pronóstico.
- Sankey: ancho proporcional al flujo, período y universo explícitos; nombres completos en leyenda móvil.
- Treemap: área proporcional, misma jerarquía y universo; no sumar padres e hijos.
- Escala monetaria: rango neutral manual identificado como supuesto, no como serie actualizada.

## Cobertura actual y vistas comprobadas

El recorrido del 8 de noviembre abrió las 160 configuraciones en los cuatro anchos de referencia. Los estados describen la configuración; la columna «Cargan» describe lo que devolvió contenido en la prueba.

| Página | Tarjetas | Cargan | Sin datos |
| --- | ---: | ---: | ---: |
| Actividad (M) | 22 | 22 | 0 |
| Inflación (M) | 22 | 22 | 0 |
| Mercado laboral (M) | 52 | 49 | 3 |
| Fiscal (M) | 23 | 22 | 1 |
| Hogares | 27 | 27 | 0 |
| Expectativas | 14 | 14 | 0 |
| **Total** | **160** | **156** | **4** |

## Mapa de integración

| ID | Familia | Componente | Estado configurado |
| --- | --- | --- | --- |
| AM1-01-4 | F01 | lineaL | DERIVAR |
| AM1-01-1 | F03 | tabla_am1 | DERIVAR |
| AM1-01-6 | F01 | lineaL | DERIVAR |
| AM1-01-5 | F03 | tabla_am1 | DERIVAR |
| AM1-03-0 | F03 | tabla_am1 | DERIVAR |
| AM1-03-1 | F05 | dispersionL | LISTO |
| AM1-03-2 | F16 | tabla_am1 | DERIVAR |
| AM1-03-3 | F03 | tabla_am1 | DERIVAR |
| AM1-04-0 | F01 | lineaL | DERIVAR |
| AM1-04-1 | F03 | tabla_am1 | DERIVAR |
| AM1-04-2 | F01 | lineaL | DERIVAR |
| AM1-04-3 | F03 | tabla_am1 | DERIVAR |
| AM1-05-0 | F01 | lineaL | LISTO |
| AM1-05-1 | F05 | dispersionL | LISTO |
| AM1-05-2 | F01 | lineaL | LISTO |
| AM1-05-3 | F05 | dispersionL | LISTO |
| AM1-06-0 | F01 | lineaL | LISTO |
| AM1-06-1 | F01 | lineaL | LISTO |
| AM1-06-2 | F03 | tabla_am1 | DERIVAR |
| AM1-06-3 | F01 | lineaL | LISTO |
| AM1-06-4 | F05 | dispersionL | DERIVAR |
| AM1-06-5 | F05 | dispersionL | DERIVAR |
| AM2-00-0 | F03 | tabla_am1 | DERIVAR |
| AM2-00-1 | F01 | lineaL | DERIVAR |
| AM2-00-2 | F03 | tabla_am1 | DERIVAR |
| AM2-00-3 | F01 | lineaL | DERIVAR |
| AM2-02-0 | F03 | tabla_am1 | DERIVAR |
| AM2-02-1 | F01 | linea | DERIVAR |
| AM2-02-2 | F14 | tabla_am1 | DERIVAR |
| AM2-02-3 | F11 | kpi | DERIVAR |
| AM2-01-0 | F02 | columnas | LISTO |
| AM2-01-1 | F03 | tabla | LISTO |
| AM2-03-0 | F13 | abanico | DERIVAR |
| AM2-03-1 | F01 | linea | DERIVAR |
| AM2-03-2 | F01 | linea | LISTO |
| AM2-03-3 | F01 | linea | LISTO |
| AM2-04-0 | F03 | tabla_am1 | DERIVAR |
| AM2-04-1 | F06 | trayectoria | DERIVAR |
| AM2-04-2 | F16 | heatmap | LISTO |
| AM2-04-3 | F03 | tabla | DERIVAR |
| AM2-05-0 | F18 | senales_am2 | DERIVAR |
| AM2-05-1 | F03 | tabla_am1 | DERIVAR |
| AM2-05-2 | F11 | kpi | DERIVAR |
| AM2-06-1 | F02 | columnas | LISTO |
| AM3-01-0 | F01 | linea | LISTO |
| AM3-01-2 | F03 | tabla | LISTO |
| AM3-02-0 | F06 | trayectoria | DERIVAR |
| AM3-02-1 | F01 | linea | DERIVAR |
| AM3-02-2 | F01 | linea | LISTO |
| AM3-02-3 | F02 | tabla | LISTO |
| AM3-03-1 | F12 | mosaico_uf | LISTO |
| AM3-03-2 | F12 | mosaico_uf | LISTO |
| AM3-03-3 | F05 | burbujas | LISTO |
| AM3-03-4 | F03 | tabla | LISTO |
| AM3-04-0 | F04 | cascada | LISTO |
| AM3-04-3 | F02 | columnas | LISTO |
| AM3-04-2 | F19 | area_apilada | DERIVAR |
| AM3-04-1 | F03 | tabla | LISTO |
| AM3-05-0 | F07 | barras_div | LISTO |
| AM3-05-3 | F07 | barras_div | LISTO |
| AM3-05-4 | F07 | barras_div | LISTO |
| AM3-05-5 | F07 | barras_div | LISTO |
| AM3-05-6 | F03 | tabla | LISTO |
| AM3-05-1 | F01 | linea | LISTO |
| AM3-06-0 | F04 | cascada | LISTO |
| AM3-06-1 | F01 | linea | DERIVAR |
| AM3-06-2 | F01 | linea | LISTO |
| AM3-06-3 | F01 | tabla | LISTO |
| AM3-07-0 | F09 | paneles | LISTO |
| AM3-07-1 | F20 | sankey | LISTO |
| AM3-07-2 | F03 | tabla | LISTO |
| AM3-07-3 | F01 | linea | LISTO |
| AM3-07-4 | F10 | pesas | LISTO |
| AM3-07-5 | F10 | pesas | LISTO |
| AM3-09-2 | F02 | columnas | LISTO |
| AM3-09-6 | F07 | barras_div | LISTO |
| AM3-09-7 | F01 | linea | FALTA |
| AM3-08-0 | F05 | burbujas | LISTO |
| AM3-08-1 | F05 | burbujas | FALTA |
| AM3-08-2 | F06 | trayectoria | FALTA |
| AM3-08-3 | F02 | columnas | LISTO |
| AM3-09-0 | F05 | burbujas | LISTO |
| AM3-09-1 | F10 | pesas | LISTO |
| AM3-09-4 | F01 | linea | LISTO |
| AM3-09-5 | F08 | apilada_100 | LISTO |
| AM3-09-3 | F02 | columnas | LISTO |
| AM3-10-3 | F01 | linea | LISTO |
| AM3-10-4 | F02 | columnas | LISTO |
| AM3-10-2 | F05 | clu_sectores | LISTO |
| AM3-10-7 | F07 | barras_div | LISTO |
| AM3-10-6 | F04 | cascada | LISTO |
| AM3-10-0 | F02 | columnas | DERIVAR |
| AM3-10-8 | F09 | paneles | LISTO |
| AM3-10-1 | F01 | linea | DERIVAR |
| AM3-11-0 | F01 | linea | LISTO |
| AM3-11-1 | F02 | columnas | LISTO |
| AM4-01-0 | F16 | termometro | LISTO |
| AM4-02-0 | F01 | serie_tiempo | LISTO |
| AM4-03-0 | F16 | mapa_sostenibilidad | LISTO |
| AM4-03-1 | F01 | serie_tiempo | LISTO |
| AM4-03-2 | F07 | barras_div | LISTO |
| AM4-04-0 | F04 | cascada_scroll | LISTO |
| AM4-04-1 | F01 | serie_tiempo | LISTO |
| AM4-04-2 | F01 | serie_tiempo | LISTO |
| AM4-04-3 | F01 | serie_tiempo | LISTO |
| AM4-05-0 | F08 | apilada_100 | LISTO |
| AM4-05-1 | F01 | serie_tiempo | LISTO |
| AM4-05-2 | F01 | serie_tiempo | LISTO |
| AM4-05-3 | F02 | columnas | LISTO |
| AM4-06-0 | F01 | serie_tiempo | LISTO |
| AM4-06-1 | F07 | barras_h | FALTA |
| AM4-07-0 | F21 | treemap | LISTO |
| AM4-07-1 | F04 | cascada_scroll | LISTO |
| AM4-07-2 | F02 | columnas | LISTO |
| AM4-07-3 | F03 | tabla_gasto | LISTO |
| AM4-08-0 | F06 | trayectoria | LISTO |
| AM4-08-1 | F01 | serie_tiempo | LISTO |
| AM4-09-0 | F01 | serie_tiempo | LISTO |
| AM4-09-1 | F07 | barras_h | LISTO |
| AM5-01-0 | F08 | barras_cien | LISTO |
| AM5-01-1 | F08 | barras_cien | LISTO |
| AM5-01-2 | F03 | tabla | LISTO |
| AM5-02-0 | F01 | linea | LISTO |
| AM5-02-1 | F04 | cascada | LISTO |
| AM5-02-2 | F11 | kpi_barras | LISTO |
| AM5-03-0 | F09 | paneles_tiempo | LISTO |
| AM5-03-1 | F01 | linea | LISTO |
| AM5-04-0 | F02 | columnas | LISTO |
| AM5-04-1 | F07 | barras_fila | LISTO |
| AM5-05-0 | F09 | paneles_tiempo | LISTO |
| AM5-05-1 | F04 | cascada | LISTO |
| AM5-05-2 | F05 | burbujas | LISTO |
| AM5-05-3 | F01 | linea | LISTO |
| AM5-05-4 | F04 | cascada | LISTO |
| AM5-05-5 | F01 | linea | LISTO |
| AM5-06-0 | F07 | barras_fila | LISTO |
| AM5-06-1 | F02 | columnas | LISTO |
| AM5-06-2 | F06 | trayectoria | LISTO |
| AM5-06-3 | F01 | linea | LISTO |
| AM5-07-0 | F10 | escalera_mora | LISTO |
| AM5-07-1 | F01 | linea | LISTO |
| AM5-08-0 | F22 | pictograma | LISTO |
| AM5-08-1 | F01 | linea | LISTO |
| AM5-08-2 | F02 | columnas | LISTO |
| AM5-08-3 | F01 | linea | LISTO |
| AM5-09-0 | F03 | sensibilidad_tabla | LISTO |
| AM6-01-0 | F14 | cajas | LISTO |
| AM6-02-0 | F01 | linea | LISTO |
| AM6-02-1 | F10 | pesas | LISTO |
| AM6-02-2 | F01 | linea | LISTO |
| AM6-03-0 | F15 | embudos | DERIVAR |
| AM6-03-1 | F17 | calendario | LISTO |
| AM6-04-0 | F23 | area_entre | LISTO |
| AM6-04-1 | F01 | linea | LISTO |
| AM6-05-0 | F01 | linea | LISTO |
| AM6-05-1 | F24 | escala | DERIVAR |
| AM6-06-0 | F10 | pesas | LISTO |
| AM6-06-1 | F01 | linea | LISTO |
| AM6-06-2 | F01 | linea | LISTO |
| AM6-06-3 | F01 | linea | LISTO |

## Verificación funcional y responsive · 8 de noviembre de 2026

Se recorrieron las 160 tarjetas y las 24 familias, y se repitieron las seis páginas del monitor a 375, 768, 1024 y 1440 px. La prueba usó el catálogo servido por HTTP y el mismo contrato de lectura que el producto.

| Prueba | Alcance | Resultado |
| --- | --- | --- |
| Recorrido de carga | 160 ejemplos a 1200 × 900 px | 156 vistas; 4 ausencias explicadas; 0 tiempos agotados |
| Familias en móvil | 24 familias a 375 × 900 px | 0 desbordes; trama mínima de 148 px |
| Catálogo responsive | 375, 768, 1024 y 1440 px | 0 desbordes; controles de 44 px; foco visible |
| Seis páginas | 160 tarjetas en cada ancho | 0 excepciones; 0 desbordes; tablas con datos |
| Toque | F01 a 375 px con emulación táctil | Consulta fijada: mar-26 y sus cuatro series |
| Teclado y foco | Flechas, Enter, Escape y cambio de familia | Consulta fijada, ampliado cerrado y foco devuelto |

Correcciones comprobadas en el documento del ejemplo:

- F10: las 18 filas de «Renuncias por sector» miden 69 px a 375 px y 40 px a 1440 px; los nombres completos no se recortan.
- F23: la trama de «Dos caminos para la Selic» mide 280 px y sus cinco SVG 254 px en ambos anchos.
- F08: a 375 px la leyenda exterior muestra las cuatro categorías y sus porcentajes; las barras no dependen de rótulos internos.
- F01: el toque fija mar-26 y las cuatro series; el panel conserva la lectura y la ventana declara los últimos 12 meses.

Las capturas y el registro completo se conservan en `graficos/verificacion/` y en `reportes/INFORME.md`. La verificación no certifica accesibilidad completa, exactitud estadística ni el comportamiento de otros motores de navegador.

## Actualización y límites

Los generadores viven en `graficos/` y resuelven sus rutas desde su propia ubicación, así que la carpeta funciona sin OpenDesign y sin servidor: `node graficos/preparar.mjs` regenera el inventario y esta guía desde la copia congelada `graficos/monitor`; `node graficos/instalar.mjs` republica el catálogo en el sistema de diseño; `node graficos/construir-offline.mjs` reconstruye `graficos/offline/`. Añadir `--verificar` a la preparación compara sin escribir y sale con código 1 si algo difiere. La copia de referencia queda congelada en esta preparación: no sincroniza automáticamente futuras descargas de datos.

Las dependencias declaradas se copiaron desde el proyecto durante la preparación.

La evidencia de la verificación 1.2 se documenta en reportes/INFORME.md. Los estados configurados no certifican accesibilidad o exactitud estadística; se conservan los motivos de los cuatro casos sin datos.
