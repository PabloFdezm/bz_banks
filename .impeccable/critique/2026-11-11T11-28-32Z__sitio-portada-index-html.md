---
target: Portada publicada (segunda pasada)
total_score: 27
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "file:C:\\dev\\bz_banks\\sitio\\portada\\index.html"
target_fingerprint: "sha256:7d5280301fc8ee32d3cde8f9eaec32d1414bda511422d39df33fca845c6c9cee"
target_path: "C:\\dev\\bz_banks\\sitio\\portada\\index.html"
timestamp: 2026-11-11T11-28-32Z
slug: sitio-portada-index-html
---
Method: dual-agent (A: revisión de diseño · B: detector y evidencia automática). Las dos usaron Playwright, porque la extensión de Chrome no conectó. Sitio publicado, 1920, 1280 y 390 px.

# Critique · Portada (segunda pasada, 11-nov, después de los pasos 1, 3, 4, 5 y 6)

| # | Heurística | Nota | Problema clave |
|---|---|---|---|
| 1 | Visibilidad del estado | 3 | «Impulso» fija sep-26 sin dato |
| 2 | Lenguaje | 3 | «Todos» no son todos; NPL |
| 3 | Control | 3 | Al salir de Presentar el foco cae en body |
| 4 | Consistencia | 3 | Presentar: la tarjeta salta ~105 px entre láminas |
| 5 | Prevención de errores | 2 | Selector «Libre / Dirigido»: callejón sin datos |
| 6 | Reconocer | 3 | ago-26 frente a sep-26 sin aviso |
| 7 | Flexibilidad | 3 | Los atajos no se descubren |
| 8 | Estética | 3 | Tablas vacías (canvas); «Eje horizontal: mes.» repetido |
| 9 | Errores | 2 | «En preparación» sin fecha; «ver tareas/09» |
| 10 | Ayuda | 2 | Sin pistas de interacción |
| **Total** | | **27/40** | Aceptable |

Detector:
- CLI: 6 avisos de tamaño de letra (15 y 20 px), falsos positivos porque están documentados en la prosa pero no en los tokens.
- Página a 390 px: «Res. 4.966» cortado.
- Sin errores ni desborde en ningún ancho.
- Texto atenuado: 4,62:1.

## Problemas prioritarios
- [P1] El selector de corte ofrece cortes sin datos en la sección 01 (Libre/Dirigido; «Todos»). → harden + clarify
- [P1] Presentar mueve la tarjeta entre láminas (título solo en la primera); sobran ~150 px; el foco no vuelve a «Presentar». → layout + harden
- [P1] «Impulso del crédito» fija sep-26 sin dato; período por defecto = último con dato. → harden
- [P2] «Ajustar eje» recorta las series atenuadas sin chips ▲▼; deshabilitado sin pista y fuera de Tab. → clarify + harden
- [P2] Agrandar: 4 de 9 filas vacías; glosario con «tareas/09». → distill + clarify

## Menores
- Res. 4.966 cortado a 390 px.
- DESIGN.md: 4,7 → 4,62; faltan los tokens de 15 y 20 px.
- Controles del menú bajo 36 px.
- Cobre en un Total sin partes.
- Navy y acero poco distinguibles.
