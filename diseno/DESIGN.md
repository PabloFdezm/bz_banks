---
name: Monitor Brasil
description: Sistema de diseño para consultar y presentar información macroeconómica de Brasil
colors:
  primary: "#2E5C8A"
  background: "#F6F7F8"
  surface: "#FFFFFF"
  text: "#24324A"
  secondary-text: "#5B6573"
  helper-text: "#606C7A"
  selected: "#E8EEF5"
  positive: "#2F7A86"
  negative: "#A85E24"
  border-strong: "#C9D2DC"
  border-subtle: "#E1E6EC"
  data-steel: "#6C819B"
  data-plum: "#7B5E8C"
  data-steel-light: "#A9B8CB"
  data-worse: "#C2773A"
  data-gap: "#EDC9A6"
  data-reference: "#8A8F96"
typography:
  display:
    fontFamily: "Bricolage Grotesque"
    fontWeight: 600
    fontSize: "clamp(2rem, 4vw, 3rem)"
    lineHeight: 1.15
  body:
    fontFamily: "IBM Plex Sans"
    fontWeight: 400
    fontSize: "1rem"
    lineHeight: 1.6
  label:
    fontFamily: "IBM Plex Sans"
    fontWeight: 500
    fontSize: "0.875rem"
    lineHeight: 1.5
  mono:
    fontFamily: "IBM Plex Mono"
    fontWeight: 500
    fontSize: "1rem"
    lineHeight: 1.5
rounded:
  small: "2px"
  control: "4px"
  dialog: "8px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  section: "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.text}"
    textColor: "{colors.surface}"
---

# Design System: Monitor Brasil

## Overview

Versión 1.0 · 8 de noviembre de 2026 · tema claro.

Un lenguaje analítico y sobrio para profesionales que consultan datos macroeconómicos de Brasil. La identidad combina superficies neutras, azul de navegación, gráficos contenidos y tipografía con números legibles. La prioridad es comparar, entender y consultar; el diseño acompaña la evidencia.

Este es el sistema propio de Monitor Brasil. Carbon aporta la separación entre valores y roles, el vocabulario de estados y las pautas de accesibilidad. La paleta, Bricolage Grotesque, los iconos propios y la retícula histórica son adaptaciones del proyecto; esta versión no declara conformidad completa con IBM Carbon.

**Fuentes de verdad:**

- Valores ejecutables: `monitor/qwen3.8-max/site/assets/css/tokens.css`.
- Primitivas y componentes: `assets/css/sistema.css`, bajo ese mismo `site/`.
- Iconos, anuncios accesibles y utilidades: `assets/js/sistema.js`.
- Composición del producto: `monitor.css`, `experiencia.css` y CSS por página.
- Catálogo: `monitor/qwen3.8-max/site/sistema-diseno/index.html`.
- Datos y contratos: `monitor/spec/` y las guías de `design/`.

Los paths `assets/` de esta guía se refieren a `monitor/qwen3.8-max/site/assets/`. El catálogo entregado en Open Design es una copia portátil de la misma página, con sus propios assets locales. Para continuar desarrollando el monitor, editar los archivos del repositorio `macro_bz`.

## Colors

### Arquitectura

1. **Primitivos `--mb-*`:** valores de la paleta, por ejemplo `--mb-blue`.
2. **Semánticos:** función, por ejemplo `--mb-interactive`, `--mb-layer`, `--mb-text-primary`.
3. **Compatibilidad:** `--navy`, `--texto`, `--tarjeta` y las demás variables históricas apuntan a los roles. Los gráficos existentes conservan sus valores.

Un componente consume el rol; no redefine el hexadecimal. La referencia ejecutable es CSS. El frontmatter de este documento describe la misma identidad para herramientas que leen DESIGN.md.

| Rol | Token | Uso |
| --- | --- | --- |
| Fondo | `--mb-background` | Lienzo de página |
| Superficie | `--mb-layer` | Tarjetas, controles y diálogos |
| Texto | `--mb-text-primary` | Contenido principal |
| Texto secundario | `--mb-text-secondary` | Contexto y descripciones |
| Ayuda | `--mb-text-helper` | Fuentes y notas |
| Acción | `--mb-interactive` | Botón principal y enlaces |
| Hover / activo | `--mb-interactive-hover`, `--mb-interactive-active` | Acción principal oscurecida |
| Selección | `--mb-layer-selected` | Filtro elegido y ubicación actual |
| Foco | `--mb-focus`, `--mb-focus-inset` | Contorno y separación en controles |
| Borde de control | `--mb-border-control` | Contorno identificable de campos |
| Soporte | `--mb-support-success/error/warning` | Estado acompañado por texto e icono |

### Visualización de datos

Las categorías siguen este orden: azul `#2E5C8A`, petróleo `#2F7A86`, acero `#6C819B`, ciruela `#7B5E8C`, acero claro `#A9B8CB`. Una categoría conserva el mismo color dentro de una comparación. Nunca usar cobre o arena como una categoría neutra.

- Mejora: `--mb-data-better`; deterioro: `--mb-data-worse`; relleno de deterioro: `--mb-data-worse-fill`.
- Brecha o área: `--mb-data-gap`. Explicar el significado según la variable; una subida no siempre es favorable.
- Referencia: `--mb-data-reference`, siempre con trazo discontinuo y nombre explícito.
- Acero claro, arena y gris de referencia son colores de representación, no colores de texto normal. Usar etiqueta, forma, trazo o contorno oscuro cuando el color por sí solo no alcance para distinguir el dato.
- Error de interfaz y deterioro económico tienen roles separados aunque compartan un valor de paleta. Siempre explicarlos con palabras.

Para contenido nuevo: contraste de texto normal al menos 4.5:1; texto grande y elementos esenciales al menos 3:1. El catálogo calcula ratios de pares concretos; eso no certifica el contraste de todas las composiciones del sitio.

## Typography

Fuentes locales con licencia OFL: IBM Plex Sans 400/500/600, IBM Plex Mono 400/500 y Bricolage Grotesque 600/700. No solicitar pesos inexistentes ni fuentes remotas.

| Rol | Token | Aplicación |
| --- | --- | --- |
| Display | `--mb-type-display` | Apertura del catálogo; 32–48 px |
| Encabezado | `--mb-type-heading` | Sección, 24/30 px, Bricolage 600 |
| Título | `--mb-type-title` | Contenido, 20/28 px, Plex 600 |
| Cuerpo | `--mb-type-body` | Lectura, 16 px e interlínea 1.6 |
| Etiqueta | `--mb-type-label` | Control, 14/21 px, Plex 500 |
| Nota | `--mb-type-caption` | Fuente y ayuda breve, 12/18 px |
| Número | `--mb-type-number` | Dato destacado, Plex Mono 500 |

Usar números tabulares en comparaciones. Mantener unidades junto al valor. El español usa coma decimal y punto de miles, según `formato.js`; las fechas y porcentajes del producto se siguen formateando allí.

Las medidas de lectura nuevas no superan 70 caracteres por línea. Los títulos se redactan para su espacio, sin elipsis; los datos largos se muestran completos en el detalle. Las tablas pueden desplazarse dentro de su contenedor cuando una comparación requiere conservar columnas.

**Compatibilidad:** el monitor contiene notas y ejes de 10–11 px y títulos intermedios de 13.5–15 px. Se conservan para evitar alterar la geometría de las tarjetas existentes. Son excepciones heredadas, no ejemplos que replicar en pantallas nuevas. Su migración exige revisar espacio y lectura conjuntamente.

## Layout

La escala compartida es 4, 8, 12, 16, 24, 32, 48, 64 y 96 px. Espacios relacionados: 8–16; entre grupos: 24–32; entre secciones: 48–64. El máximo nuevo es `--mb-content-max: 1440px`.

La retícula nueva `.mb-grid` usa 4 columnas en móvil, 8 desde 768 px y 16 desde 1024 px. Los hijos declaran su extensión por breakpoint mediante `--mb-col-mobile`, `--mb-col-tablet` y `--mb-col-desktop`; por defecto ocupan todo el ancho. Los gutters usan 16 px. El catálogo reorganiza la navegación en 768 px y amplía la composición en 1440 px; soporta anchos menores que 375 px sin bloquear zoom.

**Retícula heredada:** el producto conserva 12 columnas y 18 subdivisiones en el cuerpo, junto con sus cortes de 599/900/1023 px y variantes. Este trabajo comparte fundamentos y componentes; no redistribuye las seis páginas ni cambia alturas configuradas, claves o datos. La retícula nueva es una adaptación local de la idea 2x; los breakpoints oficiales de Carbon son distintos.

Usar flujo normal flex/grid. Las barras pegajosas deben reservar espacio y permitir retorno mediante teclado. Los diálogos y tooltips son las únicas capas de interacción superpuestas; se anclan o restringen al viewport. El catálogo no añade enlaces de herramientas al menú del producto.

## Elevation & Depth

Superficies planas y bordes sutiles. La sombra `--mb-shadow-tooltip` se reserva para ayuda flotante. Los diálogos usan `--mb-overlay` como scrim y un borde discreto; no se apilan tarjetas para simular jerarquía. Las vistas ampliadas del monitor conservan su tratamiento de página de ventana completa.

Movimiento: entrada 240 ms, salida 160 ms, feedback 180 ms. Animar opacidad y transformaciones para expresar cambios de estado. `movimientoReducido()` omite animaciones no necesarias; el contenido y la respuesta de estado siguen disponibles. No usar animación continua para comunicar carga: texto y `aria-busy` bastan.

## Shapes

Radios: 2 px para piezas compactas, 4 px en controles, 8 px en diálogos nuevos. Objetivo táctil nuevo: 44 × 44 px. Variante compacta de escritorio: 36 px de alto, expandida a 44 px en pantallas pequeñas. Un radio no define por sí solo la jerarquía.

Los iconos funcionales vienen de `icono()` en `sistema.js`: viewBox 24 × 24, trazo 1.6, extremos redondos, `aria-hidden` y `.od-icon`. El tamaño pertenece al icono, mediante `--od-icon-size`, no a selectores de padres. Son iconos propios; no se presentan como iconos oficiales de Carbon.

## Components

### Consumo y carga

```html
<link rel="stylesheet" href="assets/css/tokens.css">
<link rel="stylesheet" href="assets/css/sistema.css">
<script type="module">
  import { activarComponentes, icono, anunciar } from './assets/js/sistema.js';
  activarComponentes(document);
</script>
```

En el monitor actual, `experiencia.css` importa `sistema.css` y `experiencia.js` reexporta las utilidades compartidas. Se conservan los imports existentes de `pagina.js`. No inicializar dos veces una interacción ya controlada por el producto.

### Botones

`.mb-button` es la base; `.mb-button--primary` indica la acción principal, `.mb-button--ghost` la acción contextual y `.mb-button--compact` la variante de escritorio. El botón base sin modificador es secundario. `.mb-icon-button` tiene nombre accesible aunque no tenga texto visible.

- Una acción principal por grupo de decisiones; `<button type="button">` salvo envío de formulario.
- Hover oscurece la acción; `:focus-visible` dibuja el contorno; `:active` conserva contraste.
- `disabled` es nativo. Una espera temporal usa `aria-busy="true"` y `estadoBoton()`, que restaura el estado previo.
- Los botones históricos `.barra-presentar`, `.accion-secundaria` y `.tarjeta-agrandar` consumen las mismas reglas base; sus variantes de composición siguen en `experiencia.css`.

### Campos y filtros

`.mb-field` reúne etiqueta visible, `.mb-input`/`.mb-select`, ayuda y error. El error usa `aria-invalid="true"`, un mensaje asociado por `aria-describedby` y una instrucción para corregirlo. Validar al salir y al enviar; no en cada tecla. El borde de campos usa `--mb-border-control`.

`.mb-segmented[data-mb-segment]` agrupa botones con `data-value` y `aria-pressed`. Debe tener nombre con `aria-label` o `aria-labelledby`. `activarComponentes()` actualiza selección y emite `mb:seleccion` con `detail.value`. El consumidor actualiza los datos. Son botones, no pestañas: se recorren con Tab y se activan con Enter/Espacio.

`<details class="mb-multi">` permite selección múltiple con checkboxes etiquetados. Su resumen mantiene un nombre estable y muestra cantidad seleccionada mediante el consumidor. Los filtros existentes conservan los controladores de `charts.js`.

### Navegación

`.mb-nav-link` indica ubicación con `aria-current="page"`, texto y superficie seleccionada. Usar `<nav aria-label="…">`. Los enlaces conservan destino real; para cambiar estado dentro de una vista usar botones. El menú móvil del monitor mantiene su cierre con Escape y retorno del foco.

### Tarjeta analítica y KPI

`.mb-card` organiza cabecera, contexto, controles, representación, lectura persistente y fuente. `.mb-kpi.od-stat` separa valor y caption en bloques. Cada valor ilustrativo debe estar marcado como ejemplo; el producto toma las cifras de sus tablas reales.

La selección de serie se muestra tanto en la leyenda como en el gráfico. Una vista ampliada debe contener nombre completo, fecha elegida, unidades, gráfico/tabla, lectura y metodología, con cierre y retorno al control que la abrió. El catálogo demuestra un diálogo nativo; el monitor mantiene `abrirGrande()` y su navegación existente.

### Tablas, leyendas y tooltips

`.mb-table` usa caption, encabezados `scope`, alineación numérica y cifras tabulares. El contenedor `.mb-table-scroll` admite desplazamiento local con nombre accesible y foco. Una fila no simula ser botón: incluir un control explícito cuando haya acción.

`.mb-legend` contiene botones con texto, muestra de color/trazo y `aria-pressed`. La referencia usa trazo discontinuo. `.mb-tooltip` acompaña un control de ayuda con `aria-expanded`, `aria-controls` y panel con id; Escape, segundo clic y clic fuera cierran. La ayuda está disponible por toque y teclado, no solo hover.

### Feedback

`.mb-notice` comunica soporte con título, explicación y acción cuando corresponde. Añadir `role="status"` para cambios no urgentes y `role="alert"` solo para errores que requieren atención inmediata. Nunca usar el color como única explicación.

Loading: mantener el espacio, marcar `aria-busy` y explicar qué se carga. Vacío: explicar por qué y cómo avanzar. Error: causa comprensible y reintento. Éxito: confirmar el resultado. El catálogo incluye simulación explícita de estos estados, sin solicitudes ni cambios de datos del monitor.

### Contrato de gráficos

- Líneas: selección persistente de fecha, valores legibles y referencia discontinua; no depender solo del tooltip.
- Columnas: cero visible cuando corresponda; signo y unidad explícitos.
- Tablas: números comparables, nombres íntegros en detalle y notas separadas de los datos.
- Cascadas: distinguir totales de deltas y conservar la conciliación.
- Relojes: fecha y trayectoria visibles, punto actual identificable por forma/tamaño y lectura de ambos ejes.

Referencias locales: [gráficos frecuentes](design/GUIA_GRAFICOS_FRECUENTES_LLM.md), [integración](design/IMPLEMENTACION_GRAFICOS.md) y [relojes](design/GUIA_RELOJES_LLM.md). Estas guías mantienen el contrato especializado; esta base no regenera sus datos ni sustituye sus fórmulas.

### Integración y alcance

Los siete puntos de entrada principales ya cargan `tokens.css` y `experiencia.css`; reciben los nuevos aliases y las bases compartidas mediante esa cadena. Los módulos continúan importando `experiencia.js`, que delega iconos y feedback a `sistema.js`. El catálogo anterior `_componentes/` incorpora la misma capa de experiencia.

Los estilos particulares de gráficos, el responsive heredado, los controladores por página y la lógica de datos permanecen en sus módulos. Esta primera versión no convierte todas las reglas históricas a clases `.mb-*`; la compatibilidad permite migración gradual. La publicación no forma parte de esta entrega.

## Do's and Don'ts

### Do

- Consumir tokens semánticos y componentes compartidos; extender un rol existente antes de añadir otra variante.
- Acompañar estados, signos y selección con texto, forma o trazo.
- Mantener datos, unidades, períodos, fórmulas y nombres de fuente del monitor.
- Documentar una variante nueva con ejemplo funcional y estados antes de replicarla.
- Revisar visualmente componentes y páginas afectadas antes de publicar; esta entrega no incluye una revisión renderizada.

### Don't

- No confundir una adaptación de Carbon con una implementación oficial completa.
- No usar los cinco colores categóricos como significado favorable/desfavorable sin explicación.
- No copiar los tamaños heredados de 10–11 px a interfaces nuevas.
- No recortar cifras, errores, unidades ni etiquetas de acciones.
- No añadir números ficticios a una pantalla de producto. Los ejemplos del catálogo están identificados como ilustrativos.

Referencias oficiales: [tokens de color Carbon](https://www.carbondesignsystem.com/building-blocks/foundations/color/tokens), [tipografía](https://www.carbondesignsystem.com/building-blocks/foundations/typography/type-sets), [retícula](https://www.carbondesignsystem.com/building-blocks/foundations/2x-grid/overview) y [botones](https://www.carbondesignsystem.com/building-blocks/core/components/button/specifications).

### Ajustes de lectura responsive · noviembre 2026

- Termómetro fiscal: historia debajo de cada indicador en móvil, con sus celdas completas y el último valor visible.
- KPI con denominador: `cifraContexto` permite separar «R$ 28,7» y «de cada R$ 100» en bloques, manteniendo el texto completo para Presentar.
- Barras de ingreso: leyenda exterior en móvil con todas las categorías y sus valores; las cifras conservan sus unidades.
- Flujos laborales: las tarjetas estrechas trasladan nombres y valores a una lectura exterior para evitar recortes en el diagrama.
- Gráfico del catálogo: coordenadas adaptadas al ancho real; las etiquetas mantienen 12 px y la lectura por mes conserva teclado y selección.
- Muestras en columnas: sin el margen adicional reservado para bloques consecutivos verticales.


### Sistema especializado de gráficos · noviembre 2026

El [catálogo de gráficos](monitor/qwen3.8-max/site/sistema-diseno/graficos/index.html) documenta 24 familias y las variantes de las 160 tarjetas actuales. La [guía editable](DESIGN_GRAFICOS.md) conserva los contratos económicos y define el estándar de visualización. No migra las tarjetas del monitor.
