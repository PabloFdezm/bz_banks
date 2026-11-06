# Componentes de dibujo

> Generado por `herramientas/generar_spec.py` el 2026-11-06. No editar a mano: se sobrescribe.


Cada tarjeta declara `componente`; `pagina.js` busca la función en `COMPONENTES` (charts.js) o `COMPONENTES_BANCOS` (charts_bancos.js) y la llama con `(contenedor, entrada)`, donde `entrada` es lo que devolvió `armar()`. Si devuelve una instancia de ECharts, se le engancha un ResizeObserver.

## `charts.js` → `COMPONENTES`

- **`linea`** — linea  
  Entrada (`e.*`): `area`, `bandas`, `boundaryGap`, `categorias`, `marcas`, `refs`, `series`, `tituloY`, `ventanaAnios`
- **`columnas`** — columnas  
  Entrada (`e.*`): `apilar`, `categorias`, `fechas`, `linea`, `rotular`, `series`, `tituloY`
- **`barras_h`** — barras_h  
  Entrada (`e.*`): `apilar`, `filas`, `mostrarValores`, `series`
- **`tabla`** — tabla (HTML, no ECharts; patrones T4/T8)  
  Entrada (`e.*`): `columnas`, `filas`

## `charts_bancos.js` → `COMPONENTES_BANCOS`

- **`percentiles`** — percentiles (HTML, una fila de 40 px por métrica)  
  Entrada (`e.*`): `filas`
- **`cascada_doble`** — cascada_doble (HTML: banco y mediana del grupo en paralelo, misma secuencia)  
  Entrada (`e.*`): `lineas`, `nota`, `total`
- **`burbujas_trayectoria`** — burbujas_trayectoria (ECharts, dispersión + trayectorias trimestrales)  
  Entrada (`e.*`): `banco`, `ejeX`, `ejeY`, `puntos`, `trayectorias`
- **`small_multiples_bancos`** — small_multiples_bancos (SVG propio, escala común)  
  Entrada (`e.*`): `columnas`, `escala`, `formato`, `paneles`
- **`comparador`** — comparador (HTML: tabla ordenable, filtros, sparklines, CSV de lo visible)  
  Entrada (`e.*`): `banco`, `columnas`, `filas`, `filtros`, `orden`
- **`linea_banco`** — linea_banco (// bancos:) ---------- La línea de la Ficha: `linea` del macro con porcentajes en el eje y en el tooltip (formato de la Ficha, no cálculo), más la nota del banco bajo el gráfico. Las bandas de quiebre vienen de la página.  
  Entrada (`e.*`): `nota`
- **`apilada_100`** — apilada_100 (HTML: barras horizontales al 100 %; rótulo dentro si la parte es ≥ 8 %)  
  Entrada (`e.*`): `barras`, `formato`, `formatoRotulo`
- **`pesas`** — pesas (HTML: antes y ahora por fila; color del cambio por signo de la métrica)  
  Entrada (`e.*`): `escala`, `filas`, `formato`, `umbral`
- **`dispersion`** — dispersion (ECharts: puntos con nombre, cortes en la mediana o en cero, diagonal opcional)  
  Entrada (`e.*`): `cortes`, `cuadrantes`, `diagonal`, `ejeX`, `ejeY`, `puntos`
- **`barras_h_doble`** — barras_h_doble (ECharts: dos barras por fila, no apiladas; banco activo resaltado)  
  Entrada (`e.*`): `activo`, `filas`, `formato`, `series`
- **`barras_ic`** — barras_ic (HTML: barra con intervalo; «pocos trimestres» si n < 24)  
  Entrada (`e.*`): `activo`, `filas`, `formato`, `minTrimestres`
- **`trayectoria`** — trayectoria (ECharts: G3; «hoy» marcado en negro, rótulos de año en su primer punto)  
  Entrada (`e.*`): `cortes`, `ejeX`, `ejeY`, `etiquetaHoy`, `puntos`
- **`small_multiples`** — small_multiples (HTML genérico: un panel por serie, misma escala, años inicial y final)  
  Entrada (`e.*`): `columnas`, `escala`, `formato`, `paneles`
- **`puertas`** — puertas (HTML: una línea por página con su pregunta; el enlace conserva el banco activo)  
  Entrada (`e.*`): `enlaces`
- **`mosaico_uf`** — Posición (columna, fila) de cada UF en una grilla de 9 × 8, norte arriba y oeste a la izquierda. Es una aproximación de mapa, no cartografía: cada UF ocupa una celda.  
  Entrada (`e.*`): `formato`, `valores`
- **`barras_simple`** — v3 · barras_simple (HTML): una barra horizontal por fila, valor a la derecha ---------- entrada: { filas: [{ nombre, valor, destacar, color }], formato, max, nota }. max fija la escala (lo que pase de max se corta y se marca «›»).  
  Entrada (`e.*`): `filas`, `formato`, `max`
- **`mix_banco`** — v3 · mix_banco (HTML): una barra apilada al 100 % y su leyenda con valores ---------- entrada: { partes: [{ nombre, valor }] } con valores en fracción que suman 1.  
  Entrada (`e.*`): `partes`
- **`barras_linea`** — v3 · barras_linea (ECharts): barras apiladas + una línea, categorías en el eje X ---------- entrada: { categorias: [...], barras: [{ nombre, color, valores }], linea: { nombre, color, valores }, ejeBarras: 'izq' \| 'der', formatoIzq, formatoDer, titulo... }. Valores ya calculados en Python.  
  Entrada (`e.*`): `barras`, `categorias`, `ejeBarras`, `formatoDer`, `formatoIzq`, `intervalo`, `leyendaInteractiva`, `linea`, `lineas`, `rangoDer`, `rangoIzq`
- **`mapa_cuotas`** — v3 · mapa_cuotas (ECharts treemap): cuota de cada banco, color por grupo  
  Entrada (`e.*`): `filas`
- **`tabla_estandar`** — v3 · tabla_estandar: LA tabla descriptiva del sitio (una sola, para que todas sean iguales) ---------- Columnas fijas (4-nov): Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m (trimestral: t/t · — · a/a · 4T/4T). entrada: { filas: [{ fila, ultimo, d1, d3, d12, dventana, corte, unidad_ultimo?, unidad_cambio? }], unidadUltimo, unidadCambio, trimestral }. Unidades: pct (fracción → %)…  
  Entrada (`e.*`): `filas`, `trimestral`, `unidadCambio`, `unidadUltimo`
- **`barras_signo`** — v3 · barras_signo (ECharts): barras horizontales con signo, ordenadas  
  Entrada (`e.*`): `colorNeg`, `colorPos`, `decimales`, `filas`, `unidad`

