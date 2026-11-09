# Guía de réplica del patrón de relojes con “Agrandar”

Versión 1.0 · Referencia funcional: **maqueta-relojes.html**.

Este documento describe el resultado que debe reproducirse, las reglas que no se deben reinterpretar y los puntos que sí pueden cambiar al llevarlo a otro escenario. Está escrito para servir tanto a una persona que integra la interfaz como a un LLM que recibe los archivos sin conocer la conversación original.

## 1. Qué se entrega y cómo abrirlo

| Archivo | Para qué sirve |
| --- | --- |
| `maqueta-relojes.html` | Maqueta funcional del reloj compacto y de su vista ampliada. Incluye CSS, JavaScript, datos y fuentes tipográficas. Se puede abrir directamente en un navegador moderno. |
| `GUIA_RELOJES_LLM.md` | Especificación, contrato de datos, instrucciones de adaptación, criterios de conformidad y prompt para otro LLM. |
| `index.html` | Comparación anterior de siete propuestas. Se conserva como referencia; no es la entrada de esta maqueta. |

Para usar la maqueta, abre `maqueta-relojes.html`, elige un escenario y una fecha y pulsa **Agrandar**. No necesita instalación, npm, servidor, acceso a la base de datos ni bibliotecas cargadas desde Internet.

El HTML puede trasladarse por sí solo: sus gráficos, datos y fuentes quedan integrados. Para que también funcionen los enlaces de documentación y alternativas del pie, lleva consigo esta guía y, si lo deseas, la comparación anterior.

Los datos son una copia de los disponibles en el proyecto, no una conexión a fuentes en tiempo real. Se conserva su cálculo; no se agregan observaciones nuevas.

## 2. Decisión de producto que se debe preservar

La interfaz tiene dos estados de presentación:

- **Compacto:** un reloj depurado dentro de la tarjeta de la página.
- **Ampliado:** una capa con tres secciones, en este orden vertical:
  1. **Reloj con contexto**.
  2. **Por períodos**.
  3. **Reloj del ciclo laboral**.

“Agrandar” significa ampliar la lectura, no limitarse a escalar el mismo dibujo. El reloj compacto sigue siendo la entrada; el detalle y la comparación histórica aparecen al abrir la capa.

No sustituir este flujo por una galería de propuestas, un cambio de página, tres pestañas o un carrusel. Tampoco reemplazarlo por la lupa, la reproducción temporal, las líneas sincronizadas o la matriz de estados de la comparación anterior.

### Interpretación explícita del tercer bloque

Se ha interpretado “Reloj del ciclo laboral” literalmente: el tercer bloque usa el escenario `laboral`, incluso cuando el reloj principal es inflación.

Por ello:

- Si el principal es IPCA, el tercer bloque es una comparación independiente con el mercado laboral.
- Si el principal es laboral, el tercer bloque vuelve a presentar esa serie como bloque independiente.
- Esta repetición responde al orden solicitado; un LLM no debe suprimirla por su cuenta.
- Para una futura adaptación, el escenario del tercer bloque se configura con `relatedScenarioId`. Cambiarlo es una decisión explícita del producto; no se deduce del título del principal.
- El bloque relacionado conserva fecha, unidades, fuente y escala propias.

## 3. Anatomía visible

### Página y tarjeta sin agrandar

```text
Página
├── Cabecera: Monitor Brasil / Ciclos económicos
├── Título: Relojes del ciclo
├── Filtros
│   ├── Escenario
│   └── Observar hasta
├── Tarjeta compacta
│   ├── Título del indicador y frecuencia
│   ├── Acción Agrandar
│   ├── Nombre del eje Y
│   ├── Reloj depurado
│   ├── Nombre del eje X
│   ├── Leyenda: historia / últimos tres tramos / último dato
│   ├── Fecha y valores del punto consultado
│   └── Fuente
├── Explicación de los dos ejes
└── Enlaces de documentación
```

La explicación lateral ayuda a interpretar los datos. No es un panel de edición ni una colección de controles para presentar el diseño.

### Capa ampliada

```text
Capa casi a pantalla completa
├── Encabezado que conserva su lugar
│   ├── Título del reloj principal
│   ├── Selector de fecha
│   └── Cerrar
└── Un único cuerpo con desplazamiento vertical
    ├── Reloj con contexto
    │   ├── Trayectoria del escenario principal
    │   └── Resumen de la última observación
    ├── Por períodos
    │   ├── Primera etapa
    │   ├── Segunda etapa
    │   └── Tercera etapa
    └── Reloj del ciclo laboral
        ├── Trayectoria laboral hasta el corte
        ├── Explicación de sus ejes
        └── Fecha y fuente propias
```

No asignar un scroll vertical a cada gráfico. No fijar los tres bloques en una altura de pantalla para hacerlos caber a la fuerza: deben conservar legibilidad y recorrer un mismo cuerpo desplazable.

## 4. Estado y transiciones

El estado de datos mínimo es:

```js
{
  scenarioId: "ipca",
  cutoff: "2026-09-01"
}
```

La apertura de la capa se obtiene del estado nativo de `dialog.open`. El foco y la posición de scroll anterior se guardan separadamente.

| Acción | Efecto |
| --- | --- |
| Elegir otro escenario | Cambia el indicador principal y selecciona su última observación disponible. |
| Cambiar “Observar hasta” | Filtra la trayectoria principal y el bloque relacionado usando el mismo corte temporal. |
| Pulsar Agrandar | Abre la capa, dibuja sus tres bloques y coloca el foco en Cerrar. |
| Consultar un punto | Cambia la línea de consulta de ese gráfico; no cambia el corte ni el resumen principal. |
| Cambiar la fecha dentro de la capa | Actualiza las vistas principal, por períodos y relacionada. El selector exterior conserva ese nuevo valor. |
| Cerrar con botón, Escape o fondo | Cierra la capa y devuelve el foco al control que la abrió. |
| Volver a abrir | Mantiene el escenario y el corte; el cuerpo ampliado comienza por su primera sección. |

La inspección temporal de un punto y la fecha de cierre son conceptos diferentes. Nunca convertir un hover en un cambio global de fecha.

## 5. Reloj depurado

El compacto y los relojes de detalle reutilizan el mismo dibujante.

### Capas del dibujo, de atrás hacia delante

1. Un relleno muy tenue para el cuadrante del último punto, si este está estrictamente dentro de un cuadrante.
2. Rejilla de referencia.
3. Cruces de cero discontinuos.
4. Etiquetas de los cuadrantes, en los gráficos de tamaño normal.
5. Trayectoria histórica, en acero claro.
6. Los **últimos tres segmentos**, en azul. Tres segmentos requieren hasta cuatro observaciones.
7. Flecha de dirección en el último segmento, si existe espacio suficiente.
8. Puntos históricos y recientes.
9. Punto terminal.
10. Etiqueta de fecha del punto terminal, en los gráficos de tamaño normal.

La trayectoria es una polilínea en orden cronológico. No usar una curva suavizada: produciría una forma que no está definida por las observaciones. No forzar un recorrido circular ni una rotación horaria.

### Jerarquía de los puntos

- Histórico: radio aproximado de 3,5 px, acero claro.
- Reciente: radio aproximado de 4,5 px, azul.
- Terminal: radio de 7 px.
- Último punto del escenario hasta el corte: oscuro, con contorno blanco.
- Cierre de un período anterior: azul; no debe confundirse con la fecha actual seleccionada.
- Foco de teclado: aro adicional visible de radio 11 px.

No utilizar el área del punto para representar una tercera variable. El tamaño distingue jerarquía y foco.

### Fechas y etiquetas

No rotular todos los puntos en el dibujo. La fecha terminal aparece junto al punto y en la línea de consulta. Los demás puntos revelan fecha y valores mediante cursor, toque o teclado.

La etiqueta terminal debe quedar dentro del área útil. Tiene fondo blanco para no mezclarse con la trayectoria. Su posición se limita según los bordes del gráfico.

## 6. Reloj con contexto

Esta es siempre la primera sección ampliada.

En escritorio usa dos columnas:

- Izquierda: trayectoria principal.
- Derecha: resumen con estado, X, Y y cambios.

El resumen contiene:

1. Fecha a la que corresponde.
2. Estado derivado del signo de las dos coordenadas.
3. Valor del eje X y su unidad.
4. Valor del eje Y y su unidad.
5. Diferencia de cada coordenada respecto de la observación anterior.
6. Nota de período incompleto, cuando corresponde.

El resumen permanece anclado a la última observación visible del corte. Si se consulta un punto antiguo, solo cambia la línea de consulta bajo el gráfico.

“Cambio respecto del dato anterior” no equivale siempre a “cambio mensual”. El IPCA de esta maqueta tiene observaciones anuales; el reloj laboral, trimestrales. La etiqueta cita la observación concreta con la que se compara.

Cuando no hay dato anterior, el resumen lo indica y no inventa una variación igual a cero.

## 7. Vista por períodos

La segunda sección reparte el mismo conjunto visible en tres etapas explícitas.

Ejemplos incluidos:

| Escenario | Etapa 1 | Etapa 2 | Etapa 3 |
| --- | --- | --- | --- |
| IPCA | 2017–2019 | 2020–2022 | 2023–2026 |
| Laboral | 2019–2021 | 2022–2023 | 2024–2026 |

Cada panel muestra:

- Nombre del período.
- Número de observaciones incluidas hasta el corte.
- Ejes con nombres y unidades.
- Trayectoria de ese período.
- Punto terminal del período.
- Línea de consulta.

**Regla esencial:** los tres paneles heredan los límites X e Y del reloj principal. No se recalcula el dominio a partir de cada subconjunto.

Los puntos se unen solamente dentro de su propio período. No dibujar una línea entre dos paneles ni repetir datos en períodos superpuestos.

Un período vacío conserva su espacio y explica que no hay observaciones para ese corte. No mostrar una línea plana, una trayectoria ficticia ni el último dato de otro período.

## 8. Reloj laboral y coordinación de fechas

El tercer bloque usa `APP_CONFIG.relatedScenarioId`, cuyo valor inicial es `laboral`.

Su regla de selección es:

```text
observaciones relacionadas cuya fecha sea menor o igual al corte principal
→ orden cronológico
→ última observación disponible
```

No buscar el dato más cercano a ambos lados del corte, porque eso puede introducir una observación futura.

Ejemplo real de la copia incluida:

- Principal IPCA hasta septiembre de 2026.
- Último dato laboral disponible hasta ese corte: segundo trimestre de 2026.
- Mostrar ambas fechas tal como son; no rebautizar el dato laboral como septiembre.

Si el corte principal es anterior al primer dato laboral, el bloque se mantiene y muestra un estado vacío con la primera fecha disponible.

La escala del bloque laboral se calcula con sus propios datos. **No está obligada a coincidir con la escala del IPCA:** representa variables distintas. La comparación de escala común es una regla entre las vistas de un mismo escenario, no entre indicadores diferentes.

## 9. Contrato de datos

Cada observación tiene cuatro campos obligatorios:

```json
{
  "date": "2026-09-01",
  "label": "sep 2026",
  "x": 1.5761,
  "y": 0.3117
}
```

El ejemplo corresponde al IPCA integrado; no es una observación inventada para ilustrar el contrato.

| Campo | Tipo | Significado |
| --- | --- | --- |
| `date` | string ISO `AAAA-MM-DD` | Clave para ordenar y filtrar el período. |
| `label` | string | Nombre visible, por ejemplo `2019`, `sep 2026` o `T2 2026`. |
| `x` | número finito | Coordenada ya transformada, en la unidad declarada por el eje X. |
| `y` | número finito | Coordenada ya transformada, en la unidad declarada por el eje Y. |

En esta copia, las fechas se normalizan al primer día del mes que identifica el período. Son claves temporales, **no fechas de publicación**. Un trimestre se representa por su mes de cierre, y su etiqueta identifica el trimestre.

Reglas de entrada:

- No usar strings como `"1,5"` en los campos numéricos.
- No mezclar porcentajes en fracción y puntos porcentuales.
- No aceptar `NaN`, infinito o valores ausentes.
- No permitir fechas duplicadas.
- No representar datos ausentes mediante cero.
- No redondear antes de construir las trayectorias.
- Ordenar por `date`, sin alterar la asociación entre fecha y coordenadas.
- Las tres etapas deben asignar cada observación a un único período.

El dibujante no vuelve a calcular las fórmulas económicas. Recibe coordenadas preparadas. Así se puede reutilizar con otros indicadores sin esconder transformaciones dentro del código visual.

## 10. Fórmulas de los dos escenarios incluidos

Estas fórmulas provienen de los adaptadores del proyecto de referencia, no de una interpretación visual nueva.

### IPCA

- X = IPCA a/a menos la meta del año.
- Y = IPCA a/a menos IPCA a/a de diciembre anterior.
- Un punto por año desde 2017.
- Años cerrados: observación de diciembre.
- Año 2026: observación disponible de septiembre.
- Meta: tabla anual `od_bcb`, complementada por `od_total`, como en el código original.
- Las series de origen están en fracción y se multiplicaron por 100 una sola vez para obtener pp.

El punto de 2026 es parcial. No tratarlo como si cubriera doce meses completos ni ocultar esa diferencia al compararlo con 2025.

### Laboral

- X = mediana 2012–2019 de la desocupación SA menos la desocupación SA observada.
- Y = crecimiento a/a del salario real menos ese mismo crecimiento a/a seis meses antes.
- Frecuencia de puntos: cierre trimestral.
- Ventana visible: desde 2019.
- La mediana de referencia se calcula sobre las observaciones mensuales disponibles de 2012–2019 en `empleo_pagina`.
- Mediana incluida en la copia: 10,00595 %.
- La inversión de X es intencional: a la derecha significa mercado más apretado.

No confundir la coordenada Y con el crecimiento salarial en nivel o con el aumento del salario en seis meses. Es un **cambio de la tasa de crecimiento a/a**.

### Fechas y últimos valores de la copia

| Escenario | Última observación | X, pp | Y, pp |
| --- | --- | ---: | ---: |
| IPCA | sep 2026 | 1,5761 | 0,3117 |
| Laboral | T2 2026 | 4,53215 | −2,1691 |

Estos valores documentan la copia integrada. No son una promesa de actualización ni un reemplazo de la fuente de datos del sistema real.

## 11. Configuración que un LLM debe localizar

En el HTML hay un bloque delimitado por:

```text
BEGIN_REUSABLE_CONFIG
...
END_REUSABLE_CONFIG
```

Contiene:

### APP_CONFIG

```js
{
  version: "1.0",
  initialScenario: "ipca",
  relatedScenarioId: "laboral",
  recentSegments: 3,
  expandedOrder: ["context", "periods", "related"]
}
```

El orden de los bloques también está escrito explícitamente en el HTML. No basta con cambiar `expandedOrder` para reordenar la interfaz: en esta versión documenta un requisito invariable.

### SCENARIOS

Cada escenario declara:

| Campo | Responsabilidad |
| --- | --- |
| `id` | Identificador estable. |
| `dataKey` | Clave de su lista de observaciones dentro de `source-data`. Debe ser propia del escenario. |
| `name` | Nombre del selector. |
| `title` | Título de la tarjeta y del detalle. |
| `frequency` | Frecuencia breve. |
| `frequencyDescription` | Descripción de la ventana y la observación más reciente. |
| `x`, `y` | Etiqueta, unidad, textos negativo/positivo/cero y explicación del eje. |
| `periods` | Tres objetos con `label`, `from` y `to`. |
| `source` | Fuente que realmente respalda los datos. |
| `method` | Fórmula o transformación de las coordenadas. |
| `partialDate` | Fecha de un punto incompleto, o `null`. |
| `partialNote` | Explicación visible de esa condición. |

La elección de textos de cuadrantes es semántica. Para otro indicador no debe copiarse “Apretado” ni “Sobre la meta” si no significan lo mismo.

Los datos están en el elemento `<script type="application/json" id="source-data">`. Separar ese elemento de los descriptores permite reemplazar una serie sin reescribir la estructura del componente.

## 12. Reglas de escala y formato

Los límites se calculan una vez para cada escenario a partir de su conjunto completo integrado:

1. Tomar el máximo valor absoluto de cada eje.
2. Aplicar un margen del 20 %.
3. Redondear hacia arriba con un paso legible.
4. Usar dominio simétrico alrededor de cero.
5. Mantener esos límites al cambiar la fecha y al separar períodos.

Por eso el cero permanece en el centro y un mismo desplazamiento conserva su significado dentro del escenario.

Los datos futuros al corte no aparecen como puntos. El dominio se mantiene referido a la copia completa para evitar saltos de escala al explorar la historia; no se recalcula con cada corte.

El valor se presenta normalmente con un decimal y coma decimal. Cuando un valor pequeño no nulo quedaría redondeado a cero, el formateador aumenta la precisión necesaria, hasta seis decimales. Así un cambio pequeño no se etiqueta arbitrariamente como ausencia de cambio.

Los valores conservan su signo y unidad. No permitir que un precio, número, signo o unidad se parta entre líneas.

Un valor exactamente sobre un eje se describe con el texto `zero` de ese eje. No adjudicarle una fase positiva o negativa por conveniencia gráfica.

## 13. Sistema visual y dimensiones

La identidad visual continúa la página de Monitor Brasil encontrada en el proyecto: fondo claro, azul moderado y tipografía local. No se adoptó el tema oscuro de la ficha genérica de Dashboard porque no corresponde al artefacto existente.

| Elemento | Valor |
| --- | --- |
| Fondo de página | `#F6F7F8` |
| Superficie | `#FFFFFF` |
| Texto principal | `#24324A` |
| Texto secundario | `#5B6573` |
| Texto de anotación | `#606C7A` |
| Azul de recorrido reciente | `#2E5C8A` |
| Historia | `#A9B8CB` |
| Referencias de cero | `#8A8F96` |
| Bordes | `#E1E6EC` |
| Rejilla | `#E6EAEF` |
| Relleno del estado actual | `#E8EEF5`, tenue |
| Tipografía de contenido | IBM Plex Sans |
| Tipografía de títulos de página/sección | Bricolage Grotesque |
| Texto de interfaz | 16 px |
| Etiquetas secundarias | 12–14 px |
| Datos principales del resumen | 28 px, 26 px en móvil |
| Radio de superficie | 8 px |
| Radio de controles | 4 px |
| Altura mínima de controles | 44 px |
| Retícula de espaciado | Múltiplos de 4 y 8 px |
| Contenedor de página | Máximo 1160 px |
| Capa ampliada | Máximo 1400 px; 94 vw de ancho y 92 dvh de alto |
| Escritorio: separación contexto/resumen | 32 px |
| Columna del resumen | 256 px; 224 px en anchos intermedios |

Las anotaciones de datos del gráfico conservan tamaños menores que el texto general de interfaz, como en la visualización de referencia. No reducir las etiquetas de formulario a esos tamaños.

No introducir gradientes, efectos de vidrio, brillos, decoración figurativa ni colores rojo/verde para “mejora” o “empeora”. El signo por sí solo no define una valoración económica.

Los iconos de ampliar y cerrar son SVG funcionales con clase `od-icon`, geometría declarada y un único estilo de trazo.

## 14. Geometría del gráfico y adaptación

El gráfico se dibuja con el ancho real de su contenedor. No se escala una captura ni se fija una imagen a proporciones distintas.

Valores de referencia del dibujante:

- Tarjeta compacta: 292 px de alto en anchos amplios; 320 px en contenedores estrechos.
- Gráfico ampliado: 400 px; 360 px si el contenedor es estrecho.
- Gráfico por período: 288 px.
- Margen izquierdo: 52 px; 44 px en períodos.
- Margen derecho: 20 px.
- Margen superior: 44 px; 20 px en períodos.
- Margen inferior: 36 px.

El tamaño mayor no agrega observaciones ni altera los dominios. Agrega espacio, legibilidad y contexto.

### Anchos principales

- **1440 px o más:** capa amplia; bloques con 40 px de padding.
- **1024 px o más:** tarjeta y explicación lateral; contexto y resumen en dos columnas.
- **768–1023 px:** página en una columna; se reduce la separación del detalle, sin eliminar sus bloques.
- **375–767 px:** capa a pantalla completa; contexto y resumen se apilan; los tres períodos se apilan.
- **Menos de 375 px:** se reduce el margen y el texto visible de Agrandar puede ceder al icono, conservando su nombre accesible.

La página y la capa no deben requerir desplazamiento horizontal. No comprimir los tres períodos en columnas diminutas en un teléfono.

## 15. Apertura, cierre y accesibilidad

La maqueta utiliza un elemento nativo `<dialog>` abierto con `showModal()`.

Comportamiento implementado:

1. Guardar el elemento que tiene foco y el scroll de la página.
2. Abrir el diálogo.
3. Bloquear el scroll de la página de fondo.
4. Dibujar el detalle después de abrirlo, cuando ya tiene dimensiones útiles.
5. Empezar por la primera sección.
6. Poner el foco en Cerrar.
7. Conservar el encabezado fuera del cuerpo desplazable.

El diálogo nativo deja inerte el fondo mientras está abierto y delimita la interacción modal.

El cierre admite:

- Botón Cerrar.
- Escape.
- Pulsar y soltar fuera del rectángulo del diálogo, en el fondo de escritorio.

Al cerrar:

- Restituir el scroll de la página.
- Devolver el foco al control de origen si sigue presente.
- Conservar escenario y fecha.
- No recrear silenciosamente la selección inicial.

En móvil no hay un área exterior útil: Cerrar y Escape siguen disponibles.

### Teclado del gráfico

Cada gráfico tiene un punto dentro del orden de tabulación. Las flechas recorren los puntos; Inicio y Fin llevan al primero y al último. Enter o Espacio confirman la consulta.

No añadir todos los puntos al recorrido de Tab. Con treinta observaciones y varios gráficos se volvería una navegación innecesariamente larga.

Cada punto tiene un nombre accesible con fecha y coordenadas. La consulta se anuncia de forma controlada para teclado o toque; el movimiento del ratón no produce anuncios constantes.

La entrada tiene una transición de 200 ms basada en opacidad y desplazamiento corto. No hay reproducción automática de los datos. Con `prefers-reduced-motion`, se eliminan las animaciones.

## 16. Estados de datos

| Situación | Resultado |
| --- | --- |
| Datos válidos | Reloj y consulta operativos. |
| Una observación | Mostrar el punto; omitir segmentos inexistentes y comparación anterior. |
| Ningún dato hasta el corte | Explicar que no hay observaciones y ofrecer la primera fecha disponible. |
| Período todavía vacío | Conservar su panel con explicación. |
| Coordenadas inválidas | Mostrar un error local de datos; no dibujar una serie parcialmente corrupta. |
| Fecha duplicada | Informar del problema; no escoger una fila arbitrariamente. |
| Último año parcial | Mostrar la nota de período incompleto. |
| Fechas principal/relacionada distintas | Mostrar las dos fechas y explicar la diferencia. |
| Escenario sin datos utilizables | Desactivar Agrandar en la tarjeta principal y explicar el estado. |

Esta maqueta tiene datos locales síncronos y por ello no muestra una carga de red ficticia. Si se integra con un servicio, agregar carga y error de red preservando el espacio del gráfico y manteniendo un camino de recuperación. No mostrar un reloj falso mientras llega la respuesta.

## 17. API para otros escenarios

El HTML expone una interfaz acotada:

```js
ClockPrototype.registerScenario(configuracion, observaciones);
ClockPrototype.selectScenario(id);
ClockPrototype.selectCutoff(fechaISO);
ClockPrototype.open();
ClockPrototype.close();
ClockPrototype.getState();
```

`getState()` devuelve una copia del estado, incluyendo `expanded`; no entrega una referencia mutable al estado interno.

`registerScenario` valida campos, ejes, fechas y pertenencia a períodos. Si el registro falla, restaura la configuración y los datos anteriores. No debe quedar un escenario incompleto en el selector.

### Plantilla de adaptación

Este es un molde de configuración, **no un escenario con datos ficticios listo para presentar**. Completa los textos y proporciona observaciones reales transformadas antes de usarlo:

```js
const configuracion = {
  id: "mi_escenario",
  dataKey: "mi_serie",
  name: "Nombre para el selector",
  title: "Reloj del indicador",
  frequency: "Frecuencia real de la fuente",
  frequencyDescription: "Ventana y último período disponible",
  x: {
    label: "Nombre de X",
    unit: "Unidad de X",
    negative: "Lectura con X bajo cero",
    positive: "Lectura con X sobre cero",
    zero: "Lectura en la referencia",
    explanation: "Definición de X y sentido de sus movimientos"
  },
  y: {
    label: "Nombre de Y",
    unit: "Unidad de Y",
    negative: "Lectura con Y bajo cero",
    positive: "Lectura con Y sobre cero",
    zero: "Lectura en la referencia",
    explanation: "Definición de Y y sentido de sus movimientos"
  },
  periods: [
    { label: "Etapa 1", from: "2017-01-01", to: "2019-12-31" },
    { label: "Etapa 2", from: "2020-01-01", to: "2022-12-31" },
    { label: "Etapa 3", from: "2023-01-01", to: "2026-12-31" }
  ],
  source: "Fuente verificable de las observaciones suministradas",
  method: "Fórmulas exactas que producen X e Y",
  partialDate: null,
  partialNote: ""
};

// observaciones debe existir y cumplir el contrato de datos.
// Ajustar los períodos a la ventana real antes del registro.
ClockPrototype.registerScenario(configuracion, observaciones);
ClockPrototype.selectScenario("mi_escenario");
```

Para que el escenario permanezca al volver a abrir el archivo, incorporarlo a `SCENARIOS` y a `source-data`. El registro por API modifica la sesión en memoria, no escribe el HTML ni guarda datos en una base de datos.

## 18. Cómo llevarlo al sitio original

Los puntos identificados en el código de referencia son:

- `assets/js/pagina.js`: construcción de la tarjeta en `tarjetaShell`.
- La acción de ampliación llama a `abrirGrande(clave, cfgTar)`.
- `cerrarGrande` restaura foco, inercia y scroll del fondo.
- `dibujar(..., grande)` recibe si se trata del estado ampliado.
- El componente compartido actual está en `assets/js/charts.js`, función `trayectoria`.
- Los adaptadores económicos están en `assets/js/derivados/am2.js` y `am3.js`.

La maqueta **no modifica esos archivos**. Para integrarla:

1. Identificar las tarjetas de tipo reloj por su clave o componente, no por comparar texto de títulos.
2. En estado normal, montar solamente el reloj depurado.
3. En estado `grande`, montar el contenedor de tres secciones.
4. Pasar al compacto y al detalle el mismo modelo preparado de datos.
5. Reutilizar el estado de corte y los dominios del escenario.
6. Mantener el bloque laboral con su propio adaptador.
7. Preservar las acciones existentes del resto de tarjetas, como descargar Excel.
8. Aplicar la nueva estructura de scroll solo al detalle de relojes, sin alterar todas las tarjetas ampliadas.

No copiar sin más el diálogo completo si la aplicación ya posee un gestor de capas. En ese caso se reutiliza la gestión existente de apertura, cierre, foco e inercia, y se adapta el cuerpo visual de la maqueta.

La altura actual de una tarjeta agrandada no debe obligar a comprimir tres bloques en el espacio que antes ocupaba un solo gráfico. Debe existir un cuerpo interno flexible con scroll vertical.

## 19. Criterios de conformidad para la réplica

Esta lista describe qué debe cumplir una implementación. No constituye un registro de pruebas ejecutadas.

- [ ] La tarjeta cerrada muestra el reloj depurado.
- [ ] Agrandar abre un detalle dentro de la página.
- [ ] La primera sección es Reloj con contexto.
- [ ] La segunda sección es Por períodos.
- [ ] La tercera sección es el reloj laboral configurado.
- [ ] Las secciones aparecen una debajo de otra.
- [ ] Solo el cuerpo del detalle tiene scroll vertical.
- [ ] El cierre permanece accesible durante el scroll.
- [ ] Cambiar de fecha mantiene la coordinación entre vistas.
- [ ] Consultar un punto no cambia el corte global.
- [ ] Los tres períodos heredan la escala del principal.
- [ ] El bloque laboral no hereda por error la escala del IPCA.
- [ ] Una fecha relacionada atrasada aparece con su etiqueta real.
- [ ] No se usan observaciones posteriores al corte.
- [ ] Un año incompleto conserva su advertencia.
- [ ] Un período vacío explica su condición.
- [ ] Los ceros no se inventan para completar faltantes.
- [ ] Se puede abrir y cerrar mediante teclado.
- [ ] El foco vuelve al botón Agrandar.
- [ ] La vista de 375 px no necesita scroll horizontal.
- [ ] Todos los iconos funcionales tienen tamaño y nombre accesible.
- [ ] El HTML se puede abrir con los datos integrados sin conexión.
- [ ] El resto de tarjetas de la aplicación conserva su funcionamiento.
- [ ] Se documenta cualquier diferencia respecto de esta referencia.

## 20. Prompt listo para otro LLM

Adjunta `maqueta-relojes.html`, esta guía y, si corresponde, los archivos de la aplicación de destino. El siguiente texto puede copiarse como encargo:

```text
Implementa el patrón de relojes descrito en GUIA_RELOJES_LLM.md.
Usa maqueta-relojes.html como referencia funcional y visual.

Objetivo
Una tarjeta compacta debe mostrar un reloj depurado. Al pulsar Agrandar,
debe abrirse una capa con estas secciones, apiladas en este orden exacto:
1. Reloj con contexto.
2. Por períodos.
3. Reloj del ciclo laboral.

No entregues una galería de alternativas ni reemplaces el flujo por pestañas.
No añadas lupa, reproducción temporal o matriz de estados.
No cambies el indicador principal al pasar de compacto a ampliado.

Alcance
Adapta este patrón a los archivos y escenarios que te proporcione.
Conserva la identidad visual y los comportamientos existentes que no
sean necesarios para esta integración.
Si la aplicación ya tiene Agrandar, reutiliza su gestor de capas.
No reconstruyas la aplicación completa.

Datos y semántica
Los puntos tienen date, label, x e y.
Las coordenadas llegan transformadas y con sus unidades declaradas.
Usa datos suministrados; no inventes valores ni completes faltantes con cero.
Ordena por fecha y rechaza duplicados o coordenadas no finitas.
Describe las fórmulas de X e Y antes de alterar cualquier cálculo.
No cambies la inversión del eje laboral.
Distingue la variación de una tasa respecto de su nivel.
No clasifiques un signo positivo como bueno o malo sin una definición.
No conviertas los cuadrantes en auge/recesión por similitud visual.

Escalas
El compacto, el contexto y los tres períodos del mismo escenario
comparten dominios simétricos de referencia, fijos al cambiar el corte.
El bloque laboral conserva dominio, unidades y fecha propios.
Nunca uses datos posteriores al corte para completar el bloque relacionado.
Indica años parciales y diferencias de fecha entre bloques.

Comportamiento
Al abrir: conserva escenario y corte, bloquea el fondo, muestra primero
Reloj con contexto y pone el foco en Cerrar.
El detalle tiene un solo cuerpo con desplazamiento vertical y un
encabezado accesible.
Permite cerrar con botón, Escape y fondo exterior cuando exista.
Al cerrar: restaura scroll y foco, conservando las selecciones.
Cambiar la fecha actualiza todas las vistas.
Consultar un punto solo actualiza su línea de consulta.

Visualización
Historia tenue, últimos tres segmentos azules y último punto destacado.
No suavices curvas ni fuerces recorridos circulares.
No etiquetes todos los puntos a la vez.
Dibuja la flecha solo si el segmento tiene espacio.
Explica ambos ejes con nombres y unidades.
La vista por períodos usa tres etapas configurables sin solapamiento.
No comprimas los tres paneles en un teléfono: apílalos.

Reutilización
Separa configuración, datos, dibujante y estado.
Los textos de ejes y cuadrantes provienen de la configuración.
El orden contexto → períodos → relacionado es una regla del producto.
El tercer bloque se resuelve desde relatedScenarioId, inicialmente laboral.
Si el principal también es laboral, conserva el tercer bloque salvo
que te autorice expresamente a cambiar esa decisión.

Accesibilidad
Controles de al menos 44 px, foco visible y etiquetas persistentes.
No dependas solo del color.
Recorre los puntos con flechas; no conviertas todos en paradas de Tab.
Respeta movimiento reducido y reflujo a 375 px.
Muestra mensajes útiles para datos vacíos, inválidos y períodos sin datos.

Entrega
Entrega código editable y una entrada funcional.
Documenta la configuración de cada escenario, fórmulas, fechas,
fuentes y cualquier diferencia frente a la referencia.
Distingue lo implementado de lo realmente comprobado.
No afirmes que ejecutaste pruebas, capturas o validaciones si no lo hiciste.
```

Para una integración concreta, añade al prompt los nombres de las tarjetas afectadas y los archivos que sí puede modificar el LLM. No debe adivinar el alcance a partir de un nombre de carpeta.

## 21. Qué puede variar y qué debe permanecer

| Puede variar mediante configuración | Debe permanecer mientras no cambie el encargo |
| --- | --- |
| Indicador principal | Reloj depurado en la tarjeta compacta |
| Texto de los ejes y cuadrantes | Entrada mediante Agrandar |
| Unidades y frecuencias | Orden de las tres secciones |
| Fuente y método | Separación entre consulta y corte |
| Fechas y observaciones | Preservación de datos y fórmulas |
| Límites calculados para cada escenario | Escala común dentro del mismo escenario |
| Etiquetas y fechas de los tres períodos | Fecha propia del bloque relacionado |
| Condición de período incompleto | Foco, cierre y reflujo accesibles |

La estructura fue elegida por el usuario. Las dimensiones concretas, la implementación con diálogo nativo, el cálculo de límites y la separación de configuración son decisiones de esta maqueta para que el patrón sea consistente y replicable.

