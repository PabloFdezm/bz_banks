# 01 · Propósito y reglas

## Audiencia y uso

- **Usuario principal:** Pablo, Senior Equity Research Analyst buy-side (Principal Asset Management,
  Santiago). Cubre bancos de LatAm; Brasil es nuevo para él. Lo usa para seguir el ciclo de crédito, la
  calidad, la rentabilidad y la competencia del sistema, y para comparar un banco contra su grupo.
- **Uso secundario:** presentar a PMs y al comité. Por eso existe el modo **Presentar**: cada sección de una
  página es una lámina 1920×1080.
- Idioma: todo en castellano (textos del sitio, código, comentarios, commits). Términos técnicos del BCB en
  portugués cuando no hay traducción estable (consignado, IF.Data, COSIF).

## Reglas de diseño del sitio (dictadas por Pablo; no cambiarlas sin preguntarle)

1. **Gráfico a la izquierda y tabla a la derecha, siempre.** Nunca apilar gráfico y tabla en escritorio.
   Proporción gráfico 1,5 : tabla 1, con la tabla de al menos 440 px (aprobado por Pablo el 11-nov-2026; antes
   era 4/9–5/9). Un par por fila. Bajo 1.100 px el par se apila (gráfico arriba, tabla abajo).
2. **Nunca un gráfico y una tabla de la misma serie temporal.** La tabla es siempre **descriptiva**: el
   último dato y sus variaciones, no la serie.
3. **Una tabla estándar con dos formas fijas, idénticas en todo el sitio** (aprobado por Pablo el
   11-nov-2026), mismo formato y mismo color (sin colores por fila ni por signo):
   - **En la página y en Presentar (corta):** `Indicador · Corte · Share · a/a`; `Último` en vez de `Share`
     donde el share no aplica, o `Último · Share` cuando ambos aportan (el monto y su peso, como en concesiones).
   - `a/a` es crecimiento en %; `Δ a/a` es cambio de una tasa o ratio en pp. Decimales: crecimientos y shares 1;
     tasas, spreads, mora y cambios en pp 2. Los niveles en pp (spread) van sin sufijo.
   - **En Agrandar (completa):** `Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m`.
     En series trimestrales: `t/t · — · a/a · 4T/4T`.

   Las filas son las mismas series del gráfico (el a/a de la fila = último punto de la línea). «Share» es el
   peso en el total y lleva «—» donde no aplica. La fila total va en negrita.
4. **Cada sección es una lámina.** En Presentar, las posiciones de título, selectores, gráfico y tabla son
   **idénticas entre láminas** (por eso la franja de selectores existe aunque esté vacía).
5. **El Total siempre visible y en otro color** (cobre `#A85E24`) cuando un gráfico abre un total en partes.
6. **Leyendas interactivas** donde hay muchas series: clic en un ítem lo oculta o lo muestra (como Power BI).
7. Paleta suavizada (sin negro ni azul fuertes): fondo `#F6F7F8`, texto `#24324A`, navy `#2E5C8A`,
   acero `#8FA3BC`, cobre `#A85E24`, petróleo `#2F7A86`. Fuentes IBM Plex Sans, IBM Plex Mono y
   Bricolage Grotesque (títulos). Ver `sitio/assets/css/tokens.css`.
8. La barra superior de banco solo aparece en las páginas que usan banco (`usaBanco`).
9. **Proceso:** cambios de diseño grandes se dibujan primero en un canvas, Pablo aprueba y recién ahí se
   construyen. Se le explica y se le pregunta antes de pasos grandes; no actuar sin avisar.

## Reglas de datos (no negociables)

1. **Python calcula, el navegador solo filtra y dibuja.** Toda variación, contribución, deflactado, cuota,
   percentil o ranking sale del pipeline. Las funciones `armar()` de las páginas solo seleccionan filas,
   ordenan y dan forma a la entrada del componente.
2. **El crudo no se edita nunca** (`datos/crudo/`): es lo que sirvió la fuente, con manifiesto (URL,
   sha256, fecha). Si un parser falla, se arregla el parser.
3. Agregados de grupo = **sumas o cocientes de sumas**, nunca promedios de ratios.
4. No se recalculan en varias partes TTM, ROE, ROA, cuotas ni crédito total: se calculan una vez
   (`preparar_metricas_bancos.py`) y el resto los lee.
5. Lo que no tiene definición segura queda **null**, no se inventa.
6. Unidades en el gold: tasas y ratios en **fracción** (0,05 = 5 %); cambios de tasas en **pp** cuando la
   columna lo dice. El sitio solo formatea.
7. Nada con licencia de terceros en el sitio: el exportador falla si una columna contiene `px_`, `pbv`,
   `pe_`, `bbg`, `bloomberg`, `consenso` o `target` (precios y consenso de mercado no se publican).
8. Quiebres conocidos se respetan, no se suavizan: COSIF 2025-03 (renumeración de cuentas y migración de
   informes de crédito al escopo prudencial), Res. 4.966 desde 2025 (cambia la medida de mora/activos
   problemáticos), 2024-T4 anómalo en IF.Data (queda vacío).
