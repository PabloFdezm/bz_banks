# Componentes de dibujo

> Generado por `herramientas/generar_spec.py`. No editar a mano: se sobrescribe.


Registro único `COMPONENTES` (charts_bancos.js; los generales vienen de charts.js). Cada tarjeta declara `componente` y `armar()` puede elegir otro según la vista; `pagina.js` llama `dibujar(contenedor, entrada, { titulo })`, donde `entrada` es lo que devolvió `armar()`. Si devuelve una instancia de ECharts, la zona lleva role=img y un ResizeObserver; si devuelve null, dibujó HTML. La lista de claves de entrada la declara cada componente.

- **`linea`** — Líneas en el tiempo ([fecha, valor]); nulos como hueco, bandas de episodios, discontinua para referencias.  
  Entrada (`e.*`): `series`, `eje`, `formatoTooltip`, `bandas`
- **`columnas`** — Columnas por categoría o fecha, apilables, con una línea opcional.  
  Entrada (`e.*`): `categorias`, `fechas`, `series`, `apilar`, `linea`, `eje`
- **`barras_h`** — Barras horizontales por fila, apiladas salvo apilar: false; valores a la derecha con mostrarValores.  
  Entrada (`e.*`): `filas`, `series`, `apilar`, `mostrarValores`
- **`tabla`** — Tabla HTML con columnas declaradas (clave, título, tipo, formatear); patrones T4/T8.  
  Entrada (`e.*`): `columnas`, `filas`
- **`percentiles`** — Una fila de 40 px por métrica: rango p10–p90 del grupo, mediana, banco y hace un año; color del banco según el lado de la mediana.  
  Entrada (`e.*`): `filas`
- **`cascada_doble`** — Cascada HTML: banco y mediana del grupo en paralelo, misma secuencia de líneas, total y brecha; nota del banco debajo.  
  Entrada (`e.*`): `lineas`, `total`, `nota`
- **`burbujas_trayectoria`** — Dispersión de bancos (tamaño = activo, color por grupo según colores) y las trayectorias trimestrales que mande la página.  
  Entrada (`e.*`): `puntos`, `trayectorias`, `banco`, `colores`, `ejeX`, `ejeY`
- **`comparador`** — Tabla ordenable con filtros, sparklines y CSV de lo visible; enlaceFila(fila) hace de cada fila un enlace.  
  Entrada (`e.*`): `columnas`, `filas`, `filtros`, `orden`, `banco`, `enlaceFila`
- **`apilada_100`** — Barras horizontales al 100 %; rótulo dentro si la parte es ≥ 8 %.  
  Entrada (`e.*`): `barras`, `formato`, `formatoRotulo`
- **`pesas`** — Antes y ahora por fila; color del cambio por signo de la métrica.  
  Entrada (`e.*`): `filas`, `escala`, `formato`, `umbral`
- **`dispersion`** — Puntos con nombre, diagonal opcional y textos de cuadrante (tl, br).  
  Entrada (`e.*`): `puntos`, `diagonal`, `cuadrantes`, `ejeX`, `ejeY`
- **`barras_h_doble`** — Dos barras por fila, no apiladas; banco activo resaltado.  
  Entrada (`e.*`): `filas`, `series`, `formato`, `activo`
- **`barras_ic`** — Barra con intervalo de confianza; «pocos trimestres» si n < 24.  
  Entrada (`e.*`): `filas`, `formato`, `activo`
- **`barras_simple`** — Una barra horizontal por fila con el valor a la derecha; max fija la escala y lo que pasa se marca «›».  
  Entrada (`e.*`): `filas`, `formato`, `max`
- **`barras_linea`** — Barras apiladas y líneas sobre categorías; eje de barras a la izquierda o a la derecha; leyenda de ECharts opcional (clic oculta series).  
  Entrada (`e.*`): `categorias`, `barras`, `lineas`, `ejeBarras`, `ejeIzq`, `ejeDer`, `rangoIzq`, `rangoDer`, `intervalo`, `leyendaInteractiva`
- **`mapa_cuotas`** — Treemap de cuotas por banco; colores por grupo (los manda la página) y tinta según el fondo.  
  Entrada (`e.*`): `filas`, `colores`
- **`tabla_estandar`** — LA tabla descriptiva del sitio: Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m (trimestral: t/t · — · a/a · 4T/4T); sin colores, fila destacada para el total.  
  Entrada (`e.*`): `filas`
- **`barras_signo`** — Barras horizontales con signo, en el orden dado; color por fila o por signo.  
  Entrada (`e.*`): `filas`, `unidad`, `decimales`, `colorPos`, `colorNeg`

