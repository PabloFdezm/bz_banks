---
target: Portada publicada
total_score: 26
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "file:C:\\dev\\bz_banks\\sitio\\portada\\index.html"
target_fingerprint: "sha256:7d5280301fc8ee32d3cde8f9eaec32d1414bda511422d39df33fca845c6c9cee"
target_path: "C:\\dev\\bz_banks\\sitio\\portada\\index.html"
timestamp: 2026-11-11T10-33-25Z
slug: sitio-portada-index-html
---
Method: dual-agent (A: revisión de diseño · B: detector y evidencia automática). Las dos evaluaciones usaron Chromium sin interfaz (Playwright), porque la extensión de Chrome no conectó. Se revisó el sitio publicado a 1920, 1280 y 390 px.

# Critique · Portada (banks-bz.pages.dev/portada/)

## Puntaje de diseño
| # | Heurística | Nota | Problema clave |
|---|---|---|---|
| 1 | Visibilidad del estado | 3 | En Presentar no se ve qué corte está activo; la banda gris del período fijado no tiene rótulo |
| 2 | Lenguaje del usuario | 3 | «NPL» y «Share» en inglés; «Eje completo» aparece como presionado |
| 3 | Control y libertad | 3 | El foco no vuelve a «Agrandar» al cerrar; cae en BODY al plegar el menú |
| 4 | Consistencia | 2 | Encabezados de tabla distintos en cada par; Excel visible en Presentar |
| 5 | Prevención de errores | 3 | Las series «en preparación» se pueden resaltar; «Personalizado» no sirve |
| 6 | Reconocer antes que recordar | 3 | Ctrl + clic y las flechas no se anuncian |
| 7 | Flexibilidad y eficiencia | 2 | Faltan el período común y Ctrl+K |
| 8 | Estética y minimalismo | 3 | ~60 % de blanco en las tarjetas de tabla; 5 controles por cabecera |
| 9 | Recuperación de errores | 2 | Error de carga genérico, sin causa ni reintento |
| 10 | Ayuda | 2 | En la página solo hay `title`; la interacción no se explica |
| **Total** | | **26/40** | **Aceptable** |

## Especificidad
El contenido es propio: Total en cobre, columna «Corte», códigos SGS, banda Res. 4.966, glosario de Agrandar. El marco es genérico: cabecera de tarjeta, tarjetas idénticas, barra superior. Falta la pieza propia (franja de cifras y cifra principal, decididas pero sin construir).

El detector encontró 10 avisos de deriva en el código:
- 6 por tamaño de letra: 15 px en el número de sección y 20 px en el título de Agrandar (Seccion0x.js:53/93);
- 2 por color: la banda #F3E6D8/#7A5C3A (Grafico.js:135);
- 2 por radio de 3 px (Grafico.js:155/161).

En la página:
- A 1920 px, 1 de contraste: v2-num en #8A93A0, 3,1:1.
- A 390 px, 8 problemas: 7 rótulos del eje X encimados y 1 desborde.
- Desborde horizontal a 390 px: el ancho de la página llega a 516 px.
- Falso positivo parcial: `button.fb` de 24 px, porque la fila entera de la tabla es clicable.

## Problemas prioritarios
- **[P1] Presentar no está listo para el comité.** Quedan visibles los controles y el Excel; el corte no se ve; queda un hueco del «01»; la barra tapa la tabla; el período fijado se arrastra a la lámina. → polish + harden
- **[P1] La sección 02 (Precio) se ve rota.** Hay chips «en preparación» que se pueden activar y filas con «–». → distill + clarify
- **[P1] No hay cifra de entrada y las tarjetas de tabla están medio vacías.** Construir la franja y la cifra principal de DECISIONES §3, primero en canvas. → layout + bolder
- **[P2] Teclado y lector de pantalla se cortan.** El foco se sale del diálogo y no vuelve al cerrar; queda en BODY al plegar el menú; los puntos del gráfico se anuncian sin valores; la atenuación al 45 % da 2,3:1. → harden + audit
- **[P2] La implementación se aparta de las reglas.**
  - Encabezados no estándar; «Δ a/a» frente a «a/a»; decimales distintos; «pp» faltante.
  - Banda de la familia del cobre; Selic sin rótulo; la tabla sin su propio Agrandar.
  - Desborde en celular. → polish + adapt

## Alertas por persona
- **Alex:**
  - dos selectores de corte;
  - el detalle de la tabla pasa por el Agrandar del gráfico;
  - los atajos no se anuncian;
  - falta Ctrl+K.
- **Sam:**
  - el foco se sale del diálogo;
  - el foco queda en BODY;
  - el gráfico no se puede leer con lector de pantalla;
  - «Eje completo, presionado»;
  - contrastes de 2,3:1 y 3,1:1.
- **PM:**
  - no hay cifra de entrada;
  - la banda gris parece una proyección;
  - «Índice 142,2» no se entiende sin el subtítulo;
  - cortes sep-26 y ago-26 sin explicación.

## Observaciones menores
- No hay cierre de página.
- El título «NPL» se parte en el menú.
- El título «Impulso del crédito» se parte en dos líneas.
- Dos tipos de muestra en la tabla de Agrandar.
- 15 y 20 px sin documentar.

## Preguntas
1. ¿La sección 02 va completa en la Portada o solo lo que tiene datos?
2. ¿El selector de corte va por sección, una sola vez, y visible en Presentar?
3. ¿Qué se lleva un PM en los primeros 5 segundos?
