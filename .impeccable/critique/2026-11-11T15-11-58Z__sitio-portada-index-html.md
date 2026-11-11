---
target: Sitio publicado (tercera pasada)
total_score: 26
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "file:C:\\dev\\bz_banks\\sitio\\portada\\index.html"
target_fingerprint: "sha256:5d1a00f44b1e05b3e4b476c2460c7f3f466cc9298f9c020e08854284860fb669"
target_path: "C:\\dev\\bz_banks\\sitio\\portada\\index.html"
timestamp: 2026-11-11T15-11-58Z
slug: sitio-portada-index-html
---
Method: dual-agent (A: revisión de diseño · B: detector y evidencia de navegador). Sitio publicado, 1920, 1280 y 390 px. El overlay no se pudo inyectar en el sitio publicado (Chromium bloquea https → localhost); se corrió en el sitio servido en local.

# Critique · Sitio publicado (tercera pasada, 11-nov, después de las etapas 1 a 4)

| # | Heurística | Nota | Problema clave |
|---|---|---|---|
| 1 | Visibilidad del estado | 2 | MPME E1 corta en sep-22 series del SCR que llegan a sep-26; Tarjeta recorta el eje sin «Ajustar eje» |
| 2 | Lenguaje | 3 | «Corte» nombra el selector y la columna de fecha |
| 3 | Control | 3 | Al salir de Presentar queda en la última lámina |
| 4 | Consistencia | 2 | Rótulos del eje X: 8 en la Portada, 2 en Tarjeta y MPME; Portada sin título |
| 5 | Prevención de errores | 2 | Total fuera de escala por defecto en Tarjeta |
| 6 | Reconocer | 3 | Ctrl + clic y flechas solo en «Cómo leer» |
| 7 | Flexibilidad | 3 | Inicio va al inicio de la ventana; Excel con el mismo nombre en los 6 |
| 8 | Estética | 3 | Tablas de 3 filas dejan media tarjeta en blanco |
| 9 | Errores | 2 | Datos cortados sin declarar; «Reclasifica» en 12 gráficos de MPME |
| 10 | Ayuda | 3 | «Cómo leer» igual en todas las páginas; no explica las bandas |
| **Total** | | **26/40** | Aceptable |

Detector: Portada sin antipatrones (1920 y 390), contraste 0/283 bajo mínimo, sin scroll horizontal. MPME: 12 text-overflow («Reclasificación» recortada) y 4 line-length; P&L: 3 line-length (~270 caracteres por línea). Falsos positivos: avisos de fuente (nombre mal leído), #6B7684/#8A93A0/#1F3F60 (están en DESIGN.md), rgb(0,0,0) de plantillas. Válidos: #1B2433, #4F5B6B, #3B4656 fuera de paleta; tamaños 11–26 px fuera de la escala documentada. 19 SVG de trazado sin aria-hidden; columnas de mes de 9,7 px a 390.

## Problemas prioritarios
- [P1] MPME E1: series del SCR (desde ene-18, 105 meses) dibujadas sobre el eje del SGS (desde ene-14, 153): el gráfico y la tabla las cortan en sep-22 aunque llegan a sep-26. Alinear cada serie a su calendario en el motor de la hoja; revisar las hojas que mezclan SGS y SCR. → harden
- [P1] Tarjeta: el Total «con interés» (25,2 %) fuera de la escala por defecto (mecanismo de valores extremos); también Rotativo en «Saldo de tarjeta, a/a». La escala por defecto incluye siempre el Total; solo «Ajustar eje» recorta. → harden
- [P1] Agrandar a 390 px: controles encima de la leyenda y del gráfico; tabla de 8 columnas cortada sin pista. → adapt
- [P2] Inconsistencias entre páginas: rótulos del eje X, «Reclasificación» recortada, notas de 270 caracteres por línea en P&L, tablas cortas que estiran la tarjeta. → polish
- [P2] Portada sin entrada: franja de 5 cifras con corte y a/a como índice (diseño nuevo: canvas). → layout

## Personas
- Experto con teclado: Excel sin nombre del gráfico; Inicio no va a 2014; sin atajo entre secciones.
- PM nuevo: sin título ni síntesis en la Portada; «Corte» ambiguo; Δ a/a de una tasa de crecimiento sin explicar; Tarjeta sin Total.
- Celular: se lee; Agrandar inutilizable; objetivos de 9,7 px.
- Comité: sin «1 de 2» dentro de la sección; barra de 12–13 px; ~150 px vacíos.

## Menores
SVG de trazado sin aria-hidden; colores y tamaños fuera de DESIGN.md; «Cómo leer» define Z en la Portada; eje de NPL desde 2 % sin marca; Personas dirigido con poco contraste.

## Preguntas
- ¿Qué cifra debería llevarse un PM en 20 segundos, sin adjetivos?
- ¿La tabla no debería traer el nivel en R$ o el share en vez del último punto del gráfico?
- Si el motor decide la escala solo, ¿qué otras reglas decide sin que nadie lo vea?
