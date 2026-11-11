---
name: Bancos Brasil
description: Dashboard del sistema bancario de Brasil. Pares gráfico-tabla para consultar y presentar.
colors:
  navy-dato: "#2E5C8A"
  navy-profundo: "#1F3F60"
  seleccion: "#E8EEF5"
  cobre-total: "#A85E24"
  petroleo: "#2F7A86"
  acero: "#6C819B"
  celeste-acero: "#8FB0D0"
  gris-referencia: "#8A8F96"
  tinta: "#24324A"
  texto-suave: "#5B6573"
  rotulo: "#6B7684"
  gris-apagado: "#8A93A0"
  banda-periodo: "#E8ECF1"
  borde-control: "#C9D2DC"
  borde-tarjeta: "#E1E6EC"
  linea-tabla: "#E6EAEF"
  hover-suave: "#EEF1F5"
  fondo: "#F6F7F8"
  superficie: "#FFFFFF"
typography:
  display:
    fontFamily: "Bricolage Grotesque, sans-serif"
    fontSize: "32px"
    fontWeight: 700
  headline:
    fontFamily: "Bricolage Grotesque, sans-serif"
    fontSize: "26px"
    fontWeight: 700
  title:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: "24px"
  body:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "20px"
  label:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 500
  caption:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: "18px"
  numero:
    fontFamily: "IBM Plex Mono, monospace"
    fontSize: "13px"
    fontWeight: 400
  eje:
    fontFamily: "IBM Plex Mono, monospace"
    fontSize: "12px"
    fontWeight: 400
  grupo-menu:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    letterSpacing: "0.06em"
rounded:
  control: "4px"
  panel: "6px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  xxl: "32px"
components:
  boton:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "0 16px"
    height: "44px"
    typography: "{typography.body}"
  boton-hover:
    textColor: "{colors.navy-dato}"
  boton-barra:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "36px"
    typography: "{typography.label}"
  boton-excel:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    size: "44px"
  selector:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "0 10px"
    height: "44px"
    typography: "{typography.body}"
  chip-leyenda:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "0 10px"
    height: "36px"
    typography: "{typography.caption}"
  tarjeta:
    backgroundColor: "{colors.superficie}"
    rounded: "{rounded.control}"
    padding: "16px 24px 12px"
  dialogo:
    backgroundColor: "{colors.superficie}"
    rounded: "{rounded.control}"
    padding: "20px 28px 24px"
  menu-enlace:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "7px 12px"
    typography: "{typography.body}"
  menu-enlace-actual:
    backgroundColor: "{colors.seleccion}"
    textColor: "{colors.navy-profundo}"
---

# Design System: Bancos Brasil

## Overview

**Creative North Star: "El cuaderno del analista"**

Un instrumento de trabajo, no una vitrina. El sitio es la libreta donde un analista buy-side ordena el crédito, el
fondeo y la rentabilidad del sistema bancario brasileño. Cada cifra tiene que poder auditarse y nada está ahí por
adorno. La unidad es el **par gráfico-tabla**: el gráfico a la izquierda muestra la trayectoria y la tabla a la
derecha da el último dato y sus variaciones. La página entera se arma con esos pares, uno por fila, y cada par es
también una lámina de Presentar.

La densidad es alta pero ordenada. Las superficies son blancas y planas sobre un fondo gris muy claro, con bordes de
1 px. El color se guarda para los datos y para la ubicación; los controles casi no lo usan. La tipografía separa tres
voces: Bricolage Grotesque para títulos de página y de sección, IBM Plex Sans para rótulos y texto, e IBM Plex Mono
para toda cifra.

La dirección para lo que viene es **firme y precisa**: igual de sobria que hoy, pero con más contraste en los estados.
Lo seleccionado, resaltado o activo se tiene que leer de un vistazo. Más color decorativo no es el camino.

**Key Characteristics:**
- Un par gráfico-tabla por fila; el gráfico ocupa 1,5 partes y la tabla 1 parte (mínimo 440 px).
- Superficies planas, bordes finos, sin sombras salvo en capas flotantes.
- Navy para datos y ubicación; el Total en cobre.
- Toda cifra en Plex Mono, alineada a la derecha.
- Controles de 44 px de alto (36 px en la barra superior y en los chips de leyenda).

## Colors

Una paleta fría y suavizada (sin negro ni azul saturado) donde el único color cálido es el del Total.

### Primary
- **Navy dato** (`navy-dato`): la primera serie de cada gráfico, los títulos de sección, el hover de controles, el foco
  y la barra de ubicación del menú. Es el color que más se repite y el que da identidad al sitio.
- **Navy profundo** (`navy-profundo`): el texto del enlace actual del menú, sobre el fondo de selección.
- **Selección** (`seleccion`): el fondo del estado elegido (página actual, opción activa).

### Secondary
- **Cobre total** (`cobre-total`): solo el Total, cuando un gráfico abre un total en partes (trazo de 3 px). Nunca va
  como una categoría más.

### Tertiary
- **Petróleo** (`petroleo`), **Acero** (`acero`) y **Celeste acero** (`celeste-acero`): las series que siguen a la
  primera.
- **Gris referencia** (`gris-referencia`): las referencias (Selic, mediana del grupo, panel), siempre con trazo
  punteado y su rótulo al final de la línea.

Pendiente de construir (decidido el 11-nov en `diseno/DECISIONES_UX_2026-11.md` §4): la paleta de 8 categorías con
contraste entre vecinas, y gris claro punteado para «sin dato / otros». Hasta que esté en el código, no se toma como
token.

### Neutral
- **Tinta** (`tinta`): texto principal, cifras y la línea bajo el encabezado de la tabla.
- **Texto suave** (`texto-suave`): subtítulos de ejes y unidades, fuente, corte de los datos.
- **Rótulo** (`rotulo`): encabezados de grupo del menú, números de sección del menú, texto deshabilitado y texto de
  las series atenuadas (4,7:1 sobre blanco).
- **Gris apagado** (`gris-apagado`): el filete de 2 px sobre la fila Total. No sirve para texto: da 3,1:1 sobre blanco.
- **Banda de período** (`banda-periodo`): fondo de las bandas que marcan un quiebre de método en el gráfico
  (Res. 4.966), con su rótulo en `#4F5B6B`. Neutra a propósito: nada cálido compite con el cobre del Total.
- **Borde control** (`borde-control`): el contorno de botones y selectores.
- **Borde tarjeta** (`borde-tarjeta`): el contorno de tarjetas, del menú y de la barra superior.
- **Línea tabla** (`linea-tabla`): el separador entre filas.
- **Hover suave** (`hover-suave`): el fondo al pasar el mouse por el menú y por los botones de ícono.
- **Fondo** (`fondo`): el lienzo de la página y el hover de las filas de tabla.
- **Superficie** (`superficie`): tarjetas, menú, diálogos y controles.

### Named Rules
**La regla del Total en cobre.** Cuando un gráfico abre un total en partes, el Total va en cobre y siempre visible. El
cobre no se usa para nada más.

**La regla de la tabla sin color.** La tabla estándar no lleva colores por fila ni por signo. La fila Total va en
negrita, con un filete superior gris de 2 px, nunca en cobre.

**La regla de la referencia rotulada.** Toda línea de referencia es gris referencia punteada y lleva su nombre al
final, sobre el último punto (12 px, texto suave). El gráfico lo hace solo para cualquier serie punteada en ese gris.

## Typography

**Display Font:** Bricolage Grotesque (con sans-serif)
**Body Font:** IBM Plex Sans (con system-ui)
**Label/Mono Font:** IBM Plex Mono (con monospace)

**Character:** Bricolage pone un acento editorial solo en los títulos. Plex Sans y Plex Mono hacen el trabajo:
técnicas y neutras, con cifras que se alinean columna por columna.

### Hierarchy
- **Display** (Bricolage 700, 32 px): título de la página.
- **Headline** (Bricolage 700, 26 px, en navy): título de sección, que es también el de la lámina en Presentar.
- **Title** (Plex Sans 600, 18/24 px): título de tarjeta. Es descriptivo: dice qué muestra el gráfico.
- **Body** (Plex Sans 400, 14/20 px): indicador de tabla, enlaces del menú y controles.
- **Label** (Plex Sans 500, 14 px): botones de la barra superior.
- **Caption** (Plex Sans 400, 13/18 px): subtítulo de ejes y unidades, corte, chips de leyenda.
- **Número** (Plex Mono 400, 13 px): cifras de tabla, alineadas a la derecha. Los encabezados de tabla van en Plex Sans
  600 de 13 px.
- **Eje** (Plex Mono 400, 12 px): ejes y fuente.
- **Número de sección** (Plex Mono 400, 15 px, texto suave): el «01» junto al título de sección.
- **Título de Agrandar** (Plex Sans 600, 20 px): el título del diálogo de detalle.
- **Grupo de menú** (Plex Sans 600, 11 px, mayúsculas, espaciado 0,06em): Sistema, Personas, Empresas, etc.

### Named Rules
**La regla de los 12 px.** Nada de contenido bajo 12 px en pantalla. El grupo del menú (11 px en mayúsculas) es la
única excepción y no se replica.

**La regla de la cifra en mono.** Todo número que se compara va en Plex Mono. Coma decimal y punto de miles.

## Layout

- **Fluido, sin escalar.** El contenido usa el ancho disponible, hasta un máximo de 1.760 px. Los gráficos se dibujan
  al ancho real de su contenedor. No hay lienzo fijo achicado con `zoom`.
- **Un par por fila.** Gráfico a la izquierda (1,5 fr) y tabla a la derecha (1 fr, mínimo 440 px). Nunca dos pares por
  fila; nunca gráfico y tabla de la misma serie.
- **Marco.** Menú lateral fijo de 248 px, que se puede plegar y viene plegado bajo 1.400 px si no hay preferencia
  guardada. Barra superior pegajosa con el título, el corte de los datos y las acciones (Excel de la página,
  Presentar). Contenido con 24 px de margen.
- **Bajo 1.100 px** el par se apila (gráfico arriba, tabla abajo) y el menú se abre por encima. **Bajo 640 px** se
  ocultan el corte y Presentar. En celular no hay diseño propio: una columna y nada se sale de la pantalla. Las filas
  de controles, leyendas y selectores saltan de línea; las tarjetas bajan su margen lateral a 16 px y las celdas a
  4 px, de modo que la tabla corta cabe entera. Solo las tablas completas (P&L, balance) se desplazan dentro de su
  tarjeta.
- **Eje X:** los rótulos miden 60 px y el gráfico deja al menos 64 px entre ellos, raleando parejo (uno de cada k)
  según el ancho real.
- **Ritmo:** 4 · 8 · 12 · 16 · 24 · 32 px. Dentro de la tarjeta, 6 px entre bloques. Entre hojas, 8 px.
- **Presentar.** Cada sección es una lámina a pantalla completa: título de sección y par gráfico-tabla, ajustados al
  alto de la pantalla. Título, selectores, gráfico y tabla ocupan la misma posición en todas las láminas.

## Elevation & Depth

Plano por defecto: la profundidad la marcan el fondo gris frente a la superficie blanca y los bordes de 1 px. Solo
las capas que flotan sobre la página llevan sombra.

### Shadow Vocabulary
- **Botón flotante** (`box-shadow: 0 1px 2px rgba(27,36,51,0.08)`): el botón «Menú» con el menú plegado.
- **Barra de Presentar** (`box-shadow: 0 4px 16px rgba(27,36,51,0.12)`): los controles de lámina, abajo a la derecha.
- **Menú sobre el contenido** (`box-shadow: 4px 0 16px rgba(27,36,51,0.12)`): el menú abierto bajo 1.100 px.
- **Diálogo Agrandar** (`box-shadow: 0 12px 40px rgba(27,36,51,0.25)`): la ventana de detalle, centrada y fija.

La barra superior usa el fondo al 94 % con un desenfoque de 4 px para que el contenido no se confunda al pasar por
debajo.

### Named Rules
**La regla de lo plano en reposo.** Tarjetas, tablas y controles no llevan sombra. Una sombra significa que algo
flota sobre la página.

## Shapes

Ángulos casi rectos: 4 px de radio en controles, tarjetas, diálogos y enlaces del menú; 6 px solo en la barra
flotante de Presentar. Las etiquetas pequeñas del gráfico (último valor, chips ▲▼) también van con 4 px. Bordes de 1 px en todas partes. El grosor marca jerarquía en dos casos: el filete de 2 px
sobre el Total y la barra interior de 3 px del enlace actual. Los íconos son trazos propios de 1,6 px en cajas de 16
o 18 px.

## Components

### Buttons
Firmes y callados: blancos con borde, sin relleno de color.
- **Shape:** ángulo suave (4 px).
- **Base:** fondo de superficie, borde de control, texto en tinta, 44 px de alto, 16 px de padding lateral. Texto e
  ícono separados por 8 px.
- **Hover / Focus:** el borde y el texto pasan a navy. El foco es un contorno navy de 2 px, separado 2 px del botón.
- **Disabled:** texto en rótulo, sin cambio en hover.
- **Barra superior:** la misma pieza a 36 px de alto, en Plex 500.
- **Excel:** cuadrado de 44 × 44 px, solo ícono, con nombre accesible.
- **Ícono del menú:** 32 × 32 px, sin borde, con fondo hover suave.

### Chips (leyenda)
- **Style:** sin fondo ni borde en reposo, 36 px de alto, Plex 13 px. A la izquierda, un trazo corto con la forma
  de la serie: línea sólida de 3 px y 22 px de largo, o punteada de 2 px y 20 px si es una referencia.
- **Hover:** aparece el borde de control.
- **Resaltada:** borde navy con fondo de selección. Mientras haya una serie resaltada, los demás chips y filas pasan
  su texto a rótulo (`#6B7684`) y solo la muestra de color baja al 45 %; las líneas del gráfico se atenúan. Nunca se
  atenúa el texto con opacidad (quedaba en 2,3:1).
- **Interacción:** clic resalta la serie; otro clic en la misma la suelta; Ctrl + clic suma series. «Ajustar eje» va
  al final de la fila con el mismo tamaño y queda deshabilitado mientras no haya una serie resaltada. Es un botón de
  dos estados: el texto no cambia y el estado lo dan `aria-pressed` y el estilo de presionado.

### Cards / Containers
- **Corner Style:** 4 px.
- **Background:** superficie.
- **Shadow Strategy:** ninguna (ver Elevation & Depth).
- **Border:** 1 px en borde tarjeta.
- **Internal Padding:** 16 px arriba, 24 px a los lados, 12 px abajo. La fuente cierra la tarjeta pegada al borde
  inferior.
- **Cabecera:** el título y el subtítulo a la izquierda, los controles a la derecha. Si no caben, los controles bajan
  a una segunda línea en vez de salirse.

### Inputs / Fields
- **Selector:** select nativo de 44 px, borde de control, 4 px de radio, Plex 14 px, con `aria-label`. Sirve para
  corte, agrupación y período.
- **Focus:** contorno navy de 2 px.

### Navigation
- **Menú lateral:** blanco, borde derecho de 1 px. Los grupos (Sistema, Personas, Empresas, Fondeo, Bancos) llevan
  rótulos en mayúsculas de 11 px. Los enlaces son de 14 px con 4 px de radio. En hover, fondo hover suave y texto
  navy.
- **Página actual:** fondo de selección, texto navy profundo en 600 y una barra interior navy de 3 px a la izquierda.
- **Secciones de la página:** lista numerada bajo el enlace actual, con números en Plex Mono de 12 px. La sección
  visible se marca con un borde izquierdo navy de 2 px.
- **Saltar al contenido:** primer elemento enfocable.

### Tabla estándar (signature)
La misma tabla en todo el sitio. Columnas: `Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m`; en
series trimestrales, `t/t · — · a/a · 4T/4T`. La versión corta de la página es `Indicador · Corte · Share · a/a`, con
`Último` en vez de `Share` donde el share no aplica, o `Último · Share` cuando ambos aportan (el monto y su peso).
Aprobado el 11-nov-2026.
- **Variaciones:** `a/a` es crecimiento en % (con signo y «%»); `Δ a/a` es cambio de una tasa o ratio en pp (con
  signo, sin sufijo; la unidad va en el subtítulo, «Δ a/a en pp»).
- **Decimales por tipo de dato:** crecimientos y shares, 1; tasas, spreads, mora y sus cambios en pp, 2; montos, 1;
  índices, 1.
- **Unidades:** los niveles en % llevan «%»; los niveles en pp (spread) no llevan sufijo ni en la celda ni en el eje.
- Cifras en Plex Mono de 13 px, a la derecha. El indicador va en Plex Sans, a la izquierda, y puede ocupar varias
  líneas.
- Encabezado en Plex Sans 600 sobre una línea de 1 px en tinta. Filas separadas por la línea de tabla y con 9 px de
  padding vertical.
- Total en negrita con un filete gris de 2 px encima. Los grupos se separan con el mismo filete.
- Cada fila es una serie del gráfico: clic en la fila resalta la serie y viceversa. Hover con fondo gris.
- Si no cabe, la tabla se desplaza dentro de su tarjeta.

### Gráfico de líneas (signature)
- Trazo redondeado. El Total en cobre de 3 px; las referencias en gris punteado, con su nombre al final.
- Cada período es un botón con la fecha y los valores visibles («sep-26: Personas 9,3 %, …»); las flechas, Inicio y
  Fin mueven el período fijado y el foco.
- Al pasar el mouse, un recuadro con la fecha y el valor de cada serie visible en el orden de la leyenda, con el Total
  en negrita, del lado contrario al cursor.
- El último valor se rotula solo en las series resaltadas. Los valores fuera de escala se marcan con chips ▲▼.
- La página muestra los últimos 24 meses (8 trimestres en series trimestrales).

### Agrandar (diálogo)
Ventana centrada y fija, de hasta 1.552 px, con su propio scroll; se cierra con Esc o «Cerrar». Mientras está abierta,
Tab no sale del diálogo; al cerrar, el foco vuelve al botón que la abrió. Hay uno por elemento:
el del gráfico trae el gráfico a todo el ancho, slicer de período, «Ajustar eje» y una tabla resumida; el de la tabla
trae la tabla completa de 8 columnas y su glosario, sin gráfico. Cada bloque tiene su descarga a Excel. Pendiente
(11-nov): hoy solo existe el del gráfico; el botón de la tarjeta de tabla va primero a canvas.

## Do's and Don'ts

### Do:
- **Do** poner un par gráfico-tabla por fila, el gráfico a la izquierda y la tabla a la derecha.
- **Do** usar 44 px en controles (36 px en la barra superior y en los chips de leyenda) y un foco navy de 2 px visible.
- **Do** escribir títulos de tarjeta descriptivos y dejar el subtítulo para ejes y unidades.
- **Do** marcar «en preparación» o «falta» cuando no hay dato.
- **Do** marcar lo seleccionado con algo más que color: peso, barra o filete.

### Don't:
- **Don't** apilar gráfico y tabla en escritorio, ni mostrar en la tabla la misma serie temporal del gráfico.
- **Don't** colorear filas ni signos en la tabla, ni pintar el Total de cobre en la tabla.
- **Don't** usar cobre para algo que no sea el Total.
- **Don't** poner sombras en tarjetas o controles en reposo.
- **Don't** agregar descripciones, glosarios o lecturas («sube», «preocupa») en la página. Ese detalle va en Agrandar.
- **Don't** hacer un botón más grande que el contenido al que sirve.
- **Don't** bajar de 12 px.
