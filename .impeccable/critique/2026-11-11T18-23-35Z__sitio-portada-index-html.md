---
target: Portada y páginas interiores
total_score: 25
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 2
target_identity: "file:C:\\dev\\bz_banks\\sitio\\portada\\index.html"
target_fingerprint: "sha256:a834586bb33f25c2f086768f29c0d101bb29a6a958af844f70ddbb86b59f442c"
target_path: "C:\\dev\\bz_banks\\sitio\\portada\\index.html"
timestamp: 2026-11-11T18-23-35Z
slug: sitio-portada-index-html
---
Method: dual-agent (A: revisión de diseño · B: detector y navegador)

| # | Heurística | Nota | Problema principal |
|---|---|---|---|
| 1 | Visibilidad del estado | 3 | Título gris en la 2.ª lámina de cada sección parece deshabilitado |
| 2 | Mundo real | 3 | «Mora > 90» vs «Mora mayor a 90»; «gráfico de la izquierda» en celular |
| 3 | Control | 3 | Sin «Soltar todo» del resaltado |
| 4 | Consistencia | 2 | Prefijos 01/P1/E1 (P doble sentido); Total primero o último; a/a vs Δ a/a sin unidad |
| 5 | Prevención | 3 | Bien |
| 6 | Reconocer | 2 | «Último» cambia de significado según la tabla |
| 7 | Flexibilidad | 3 | Sin atajo para Segmentos |
| 8 | Estética | 3 | Barras de 8 tramos indistinguibles |
| 9 | Recuperación | 2 | Sin estado de error visible si falla data/ |
| 10 | Ayuda | 3 | Cómo leer contextual; no explica título gris ni prefijos |
| Total | | 25/40 | Aceptable |

Especificidad: propio del producto; la franja de 5 cifras repite Totales. Detector: Portada limpia; 16 design-system-font falsos positivos (parser); contraste real en chips ▲▼ de Tarjeta (#6C819B 4,0:1; #B0B6BE 2,0:1); line-length/straggler discutibles en Definición/notas.

Problemas prioritarios:
- [P1] «Último» ambiguo / doble Δ (Tarjeta P4, MPME): unidad en encabezado, Último nunca variación si otra columna lo es, Total en posición fija. → clarify
- [P1] Sin h1/h2/h3, sin caption/scope, SVG sin role, Agrandar ×6 iguales. → audit/harden
- [P2] Contraste chips ▲▼ (4,0:1 y 2,0:1). → polish
- [P2] Inconsistencias: prefijos, «Mora > 90», «izquierda» en celular, cobre fuera del Total (Tramos con renta), paleta de 8 categorías. → clarify/colorize
- [P3] Presentar: título de continuación gris, sin fin de deck, espacio vacío en tablas cortas. → layout

Personas: Alex (7–9 controles por tarjeta, sin atajo de Segmentos, resaltado fuera de la URL); Sam (22 Tab antes de la primera tarjeta, sin encabezados, parada del gráfico difícil); PM (Último como Δ, prefijos E1/P1).

Menores: franja enlaza a la sección, no al par; Total casi invisible en Agrandar con resaltado; Rotativo fuera de escala en Tarjeta P1; nota de 5 líneas en MPME.

Preguntas: franja con Z/percentil en vez de repetir Totales; gráfico más bajo en pares cortos; cifra clave por lámina.
