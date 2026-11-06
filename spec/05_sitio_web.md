# 05 · Sitio web

Inventario autogenerado de páginas, secciones y tarjetas: `generado/paginas.md`. Componentes y las claves
que lee cada uno: `generado/componentes.md`.

## Archivos

| Archivo | Rol |
|---|---|
| `sitio/index.html`, `sitio/<ruta>/index.html` | Carga los 3 CSS y ECharts, e importa `pagina.js` + `paginas/bN.js`; llama `montar(cfg)` |
| `assets/js/config.js` | `RUTA_DATOS = '/data/'`, `MARCA`, `PAGINAS` (clave, ruta, nombre, `oculta`) |
| `assets/js/pagina.js` | Motor: monta cabecera (menú lateral), barra superior, franja, secciones, riel, tarjetas; dibuja; reparte filas |
| `assets/js/paginas/b0.js … b10.js` | Configuración declarativa de cada página (sin imports) |
| `assets/js/charts.js` | Componentes base heredados del macro: `linea`, `columnas`, `barras_h`, `tabla`; paleta y tokens |
| `assets/js/charts_bancos.js` | Componentes del sitio de bancos (`COMPONENTES_BANCOS`), incluida `tabla_estandar` |
| `assets/js/datos.js` | `cargar(tabla)` con caché por sesión, `cargarTodas`, `tablasExportadas()` (lee `_manifiesto.json`) |
| `assets/js/estado.js` | Estado en la URL (`?banco=&optica=&grupo=&t=`), lista de bancos, grupos y colores, barra de banco |
| `assets/js/presentacion.js` | Modo Presentar (láminas 1920×1080) e impresión |
| `assets/js/formato.js` | Formato de números (coma decimal, `pct`, `pp`, `pb`), fechas, colores por signo |
| `assets/css/tokens.css` | Paleta, fuentes (Google Fonts por `@import`), tamaños |
| `assets/css/monitor.css` | Plantilla base heredada del Monitor macro (grilla de 12, responsive) |
| `assets/css/bancos.css` | Todo lo propio. Se agrega por bloques fechados (v2, v3, v3b…, «4-nov»); el último bloque gana |
| `assets/vendor/echarts.min.js` | ECharts 5, render SVG |

## Montaje de una página (`pagina.js → montar(cfg)`)

1. Lee textos (`contenido/textos.json`), carga la lista de bancos desde `bk_banco` si existe.
2. Cabecera = menú lateral con las páginas no ocultas y botón Presentar. Bajo 1200 px pasa arriba.
3. Barra superior: título de la página + botón «Presentar ▸»; selector de banco si `usaBanco !== false`.
4. Franja opcional (`cfg.franja`): celdas con último valor, cambio y mini serie (SVG propio).
5. Por cada sección: `<section class="seccion" id="sNN">` con **riel** (número, nombre, frecuencia, pregunta,
   selectores y KPIs) y **cuerpo** (grilla de 9 columnas con las tarjetas de `filas`).
6. Cada tarjeta se dibuja en paralelo (`dibujar`): espera las fuentes (máx. 3 s), carga sus `datos`, llama
   `armar(d, est)` y pasa el resultado al componente. **La sección se muestra de inmediato**; no espera a
   sus tarjetas (antes esperaba y las páginas con tablas grandes quedaban en blanco 20–30 s).
7. Cuando terminan, `repartirFilas` redistribuye el ancho si alguna tarjeta quedó vacía (`tarjeta-vacia`),
   y oculta la sección si quedaron todas vacías.

## Configuración de página (`paginas/bN.js`, `export default {...}`)

```js
{
  clave: 'B3', ruta: 'credito', nombre: 'Crédito', rotulo: 'SISTEMA BCB · MENSUAL',
  usaBanco: false,                 // oculta la barra de banco
  franja: [ { rotulo, tabla, filtro, banco, orden, delta, escalaDelta, tono, formato, valor, nota, pie } ],  // opcional
  secciones: [{
    numero: '01', nombre: 'Por tipo', frecuencia: 'Mensual · SGS', pregunta: '…',
    riel: [ { tipo: 'selector', clave: 'grafico', rotulo: 'GRÁFICO', defecto: 'barras',
              opciones: [{ valor: 'barras', nombre: 'Barras · último' }, …] } ],   // o bloques KPI
    filas: [[ { clave: 'B3-01', ancho: 4, alto: 570 }, { clave: 'B3-02', ancho: 5, alto: 570 } ]],
  }],
  tarjetas: {
    'B3-01': {
      titulo, sub, plana: true,        // plana: sin borde (estilo v3)
      componente: 'barras_signo',      // clave en COMPONENTES o COMPONENTES_BANCOS
      datos: ['bk_cred_tablas', 'bk_cred_series'],   // tablas o particiones ('metrica/roe_ttm/bk_panel')
      armar: (d, est) => entrada,      // solo selecciona y da forma; NO calcula
      leyenda: [{ nombre, color, discontinua }],      // leyenda HTML fija (opcional)
      nota, fuente, estado: 'LISTO' | 'DERIVAR' | 'FALTA' | 'REF', motivo, banco: true, pastilla: true,
    },
  },
}
```

- `armar(d, est)`: `d` es un objeto `{tabla: filas}`; `est` = `{clave, banco, optica, grupo, trimestre,
  seleccion: {clave: valor de los selectores de la sección}, codBanco, grupoBanco}`.
- Lo que devuelve es la `entrada` del componente, más claves que entiende el motor:
  `{ enPreparacion: 'motivo' }` (muestra el aviso), `componente` (cambia el componente según el selector),
  `leyenda` (reemplaza la leyenda; `[]` = la dibuja el gráfico), `ariaLabel`, `pastilla`.
- Un selector cambia → solo se redibujan las tarjetas de **esa** sección.
- Las configs no pueden importar nada (las leen herramientas de Node como texto/módulo aislado).

## Componentes

`COMPONENTES` (charts.js): `linea`, `columnas`, `barras_h`, `tabla`.
`COMPONENTES_BANCOS` (charts_bancos.js): `percentiles`, `cascada_doble`, `burbujas_trayectoria`,
`small_multiples_bancos`, `comparador`, `linea_banco`, `apilada_100`, `pesas`, `dispersion`,
`barras_h_doble`, `barras_ic`, `trayectoria`, `small_multiples`, `puertas`, `mosaico_uf`, `barras_simple`,
`mix_banco`, `barras_linea`, `mapa_cuotas`, `tabla_estandar`, `barras_signo`.

Los usados por las páginas v3 (Portada y Crédito):

- **`barras_linea`** (ECharts): barras (apiladas, eje izquierdo o derecho con `ejeBarras: 'der'`) + una o
  varias líneas (`lineas: [{nombre, color, valores, discontinua, grosor, z}]`). `rangoIzq/rangoDer =
  {escala, min, max}`. `leyendaInteractiva: true` → leyenda ECharts en una fila con desplazamiento; clic
  oculta/muestra series.
- **`barras_signo`** (ECharts): barras horizontales con valor rotulado; color por fila (`color`) o por
  signo (`colorPos`/`colorNeg`). Margen derecho para la etiqueta más larga.
- **`mapa_cuotas`** (ECharts treemap): cuota por banco coloreada por grupo.
- **`tabla_estandar`** (HTML): la única tabla descriptiva. Anchos fijos por columna (`colgroup`), cifras en
  IBM Plex Sans con `tabular-nums`, letra que escala con el ancho de la tarjeta (container query
  `100cqw/44`, entre 10 y 13 px), nombres largos en dos líneas, nunca «…»; si no cabe aparece scroll
  horizontal. Formatea con `fmtEstandar(v, unidad, conSigno)`.

Todo gráfico ECharts se crea con `echarts.init(cont, null, {renderer: 'svg'})`. `pagina.js` envuelve
`echarts.init` para fijar `textStyle.fontFamily = 'IBM Plex Sans'`: ECharts mide el texto con su fuente y el
SVG lo pinta con la de la página; si no coinciden, las etiquetas se cortan.

## Estado y URL

`estado.js` guarda el estado en la query string: `banco` (slug), `optica`, `grupo` (`panel` = sin grupo),
`t` (trimestre). Al elegir banco, el grupo pasa a su modelo de negocio. Cambiar estado dispara
`bancos:estado` y se redibujan las tarjetas marcadas `banco: true` y la franja. Los enlaces del menú
conservan la query.

## Modo Presentar (`presentacion.js`)

- Entra con el botón, la tecla **P** o `#presentar=sNN` en la URL. **Esc** sale; **→ / Espacio** siguiente;
  **←** anterior; **Inicio/Fin**; número + Enter salta. Al final de una página pasa a la siguiente del menú.
- Cada sección es una lámina 1920×1080 escalada con `transform` para caber en la ventana. El cuerpo de la
  sección **se mueve** (no se clona) a la lámina para que ECharts siga vivo; al salir vuelve a su lugar.
  Los selectores del riel viajan a la franja `.pres-selectores` (que existe siempre, para fijar posiciones).
- Al entrar, la letra de los gráficos ECharts se multiplica por 1,5 (y los márgenes de la grilla); al
  salir se divide. También se aplica a un gráfico que se redibuja dentro de la lámina (cambio de selector).
- Posición verificada de las tarjetas en todas las láminas de Portada y Crédito: idéntica.

## Diseño responsive

- ≥1440 px: grilla de 9 columnas, menú lateral.
- 1200–1439: el riel de la sección pasa arriba en fila; la grilla sigue de 9 (antes la plantilla la pasaba a
  12 y dejaba 3 columnas vacías).
- 700–1199: menú arriba; gráfico y tabla siguen lado a lado con alto fijo (`--alto`).
- <700: una columna (celular).

## Rendimiento

- Cargar particiones, no tablas completas: `bk_panel` 27 MB, `bk_grupo` 12 MB, `bk_cre_panorama` 6,5 MB,
  `bk_cre_calidad` 5 MB. Ejemplo correcto: `datos: ['metrica/costo_riesgo_ttm/bk_panel', 'bk_banco']`.
- Cabeceras `no-cache` en `/assets/*` y `/data/*` (`sitio/_headers`, que Cloudflare Pages lee igual que Netlify): cada visita
  revalida; tras un deploy basta recargar.
