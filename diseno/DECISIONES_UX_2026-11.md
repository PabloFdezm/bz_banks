# Decisiones de UX/UI del sitio · 11-nov-2026

Insumo para reescribir `DESIGN.md`. Pablo pidió decidir estos puntos; quedan como regla del sitio hasta que el
DESIGN.md nuevo diga otra cosa. «Hecho» = ya está en `sitio/assets/v2` (motor y marco); «pendiente» = decidido, sin
construir.

## 1. Retícula y ancho
- **Fluido, sin escalar.** La página usa el ancho disponible (máximo 1.760 px de contenido); gráficos y período se
  dibujan al ancho real de su contenedor. Se acabó el lienzo fijo de 1.600 px achicado con `zoom`. *Hecho.*
- **Un par por fila, siempre**: gráfico a la izquierda (1,5 partes) y tabla a la derecha (1 parte, mínimo 440 px).
  Dos pares por fila fragmenta la lectura y rompe la correspondencia con Presentar. *Hecho.*
- Bajo 1.100 px el par se apila (gráfico arriba, tabla abajo) y el menú se abre por encima. *Hecho.*

## 2. Tipografía (mínimos, a tamaño real)
| Uso | Tamaño | Familia |
|---|---|---|
| Título de página | 32 px | Bricolage 700 |
| Sección | 26 px | Bricolage 700 |
| Título de tarjeta | 18/24 px | Plex Sans 600 |
| Indicador de tabla, controles | 14 px | Plex Sans |
| Cifras de tabla | 13 px | Plex Mono |
| Subtítulo, notas | 13/18 px | Plex Sans |
| Ejes, fuente | 12 px | Plex Mono / Sans |

Nada bajo 12 px en pantalla. *Hecho en el sitio; el canvas sigue con 12–13 px en tablas.*

## 3. Jerarquía de cada página
- **Franja de indicadores arriba** (bajo el título): 4 a 6 cifras clave de la página, cada una con rótulo, último
  valor, corte y Δ a/a. Sin adjetivos ni lecturas («sube», «preocupa»): solo números. *Pendiente* (necesita definir
  las cifras por página; propuesta abajo).
- **Cifra principal en la tarjeta de tabla**: sobre la tabla, el último valor del Total en 28 px mono con su Δ a/a.
  Llena el espacio vacío de las tablas cortas y da el dato de un vistazo. *Pendiente.*
- Propuesta de franja: Portada (concesiones 12m a/a, tasa media, spread, mora > 90, atraso 15–90); Tarjeta (saldo
  a/a, tasa media, mora > 90, saldo medio por operación); Personal y Planilla (ídem); Vehículos e Inmobiliario
  (saldo a/a, tasa, mora); MPME y Grandes (saldo a/a SGS, tasa empresas, mora, % mayor riesgo); Fondeo (M2 a/a,
  depósitos a plazo a/a, poupança a/a, costo de captación del panel); Agregados y P&L (ROE, margen, costo del riesgo,
  capital principal del panel o del banco elegido).

## 4. Color de series
- **Total**: cobre `#A85E24`, 3 px. **Referencias** (Selic, mediana del grupo, panel): gris `#8A8F96` punteado.
- **Categorías**, en este orden, con contraste entre vecinas (hoy casi todo es azul grisáceo):
  `#2E5C8A` azul · `#2F8F83` verde azulado · `#C89B2C` mostaza · `#7B5EA7` violeta · `#5AA3D8` celeste ·
  `#C2577A` frambuesa · `#7A8F3C` oliva · `#6C819B` gris azulado.
- «Sin dato / otros / no informado»: gris claro `#B0B6BE` punteado.
- Barras apiladas: mismo orden; el segmento «otros» siempre último y gris. *Pendiente* (cambia las hojas del canvas).

## 5. Gráfico
- **Valores al pasar el mouse**: recuadro con la fecha y el valor de cada serie visible, en el orden de la leyenda; el
  total en negrita. Se ubica al lado contrario del cursor. *Hecho.*
- Etiqueta del último valor solo en las series seleccionadas (como hoy). Chips ▲▼ para valores fuera de escala (como hoy).

## 6. Controles de la tarjeta
- Alto único de 44 px. «Ajustar eje» y «Agrandar» con texto; descarga a Excel como botón cuadrado con ícono (44 × 44).
  Si la cabecera no cabe, los botones bajan a una segunda línea en vez de salirse de la tarjeta. *Hecho.*

## 7. Estado y navegación
- **Estado en la dirección**: banco, agrupación, corte y Agrandar abierto viajan en la URL (`?banco=…&vista=…`); se
  puede compartir un enlace que abre exactamente esa vista. *Hecho.*
- **Período común por página** (2 años, 5 años, 10 años, todo) que mueve todos los gráficos. *Pendiente.*
- **Buscador de gráficos** (Ctrl+K) en todo el sitio. *Pendiente.*
- **Carga diferida**: cada gráfico se dibuja al entrar en pantalla. *Pendiente.*

## 8. Presentar
- Lámina = título de sección (en la primera lámina de la sección) + par gráfico y tabla, ajustado al alto de la
  pantalla, en pantalla completa; flechas para avanzar, Esc para salir. Sin botones de descarga visibles. *Hecho.*
- *Pendiente*: exportar las láminas de una página a PDF.

## 9. Celular
- Sin diseño propio: una columna, nada se sale de la pantalla, Presentar oculto. El público objetivo usa escritorio.

## 10. Agrandar
- Ventana centrada, fija, con su propio scroll; Esc o «Cerrar». Cada bloque con su descarga a Excel. *Hecho.*
