# 05 · Sitio web

Inventario autogenerado de páginas, secciones y tarjetas: `generado/paginas.md`. Componentes, su
descripción y las claves de entrada que lee cada uno: `generado/componentes.md`.

## Archivos

| Archivo | Rol |
|---|---|
| `sitio/index.html`, `sitio/<ruta>/index.html` | Los 13 son **idénticos**: cargan los 3 CSS, ECharts y `pagina.js`. Las carpetas existen porque Cloudflare Pages sirve el `index.html` de cada una |
| `sitio/404.html` | Página estática de «no existe» (tokens + monitor.css) |
| `assets/js/config.js` | Sin DOM. `RUTA_DATOS`, `MARCA`, `NOMBRE_SITIO`, `PAGINAS` (clave, ruta, nombre, `oculta`): el único lugar con la identidad de cada página; `enlace(ruta)`, `paginaDeRuta(pathname)` |
| `assets/js/tokens.js` | Sin DOM. `COLOR` (un valor por token de tokens.css, incluido `total`), `PALETA` categórica, `TIPO`, `FUENTES_WEB`, `TRAZO_REFERENCIA` |
| `assets/js/comun.js` | Sin DOM. El dominio: `FUENTE`, `GRUPOS`/`COLOR_GRUPO`, nombres del gold para los cortes del panel (`OPTICA_MODELO`, `OPTICA_PANEL`, `GRUPO_PANEL`, `INST_PANEL`, `instGrupo`), `ROTULO_PANEL`, `BANDA_2025`, rutas de partición (`tablaMetrica`, `tablaOptica`, `tablaBanco`), el protocolo de `armar()` (`enPreparacion`, `requiereBanco`), `ESTADOS`/`TRANSITORIOS`/`MOTIVOS`, `periodoActivo`, los indicadores de la franja (`indicadorSistema`, `indicadorPanel`, `indicadorBanco`) y el árbol del ROE (`lineasArbolRoe`) |
| `assets/js/formato.js` | Sin DOM. El vocabulario de unidades (`formatear(v, unidad)`: pct, pct_nivel, pp, pb, num, brl, brl_mm, reales_a_mm, texto), `formatoEje`, `numero`, `pct`, `pp`, `pctRotulo`, `tono(delta, signo)`, fechas y períodos (`mmm_aa`, `etiquetaMes`, `trimestre`, `trimestreDePeriodo`, `finDeTrimestre`, `trimestresHasta`, `trimestresEntre`, `periodosHasta`, `porFecha`, `porPeriodo`) |
| `assets/js/url.js` | Query y hash (`parametros`, `reemplazarUrl`, `fijarHash`, `leerSeleccion`, `fijarSeleccion`, `busquedaCompartida`) |
| `assets/js/dom.js` | `el(tag, clase, texto)` y `svgEl`: el único ayudante de DOM |
| `assets/js/pagina.js` | Motor: elige la config por la ruta, monta cabecera (menú lateral), barra, franja, secciones, riel y tarjetas; dibuja |
| `assets/js/paginas/b0.js … b12.js` | Configuración declarativa de cada página; importan `tokens.js`, `comun.js`, `formato.js` |
| `assets/js/paginas/_series.js` | Piezas de las páginas de series con tabla estándar (B0, B3, B11, B12): `filasDe`, `serieDe`, `valoresEn`, `tablaEstandar`, `graficoYTabla`, `lineasConTotal` (Total primero y en `COLOR.total`), `leyendaDe` |
| `assets/js/charts.js` | Tema ECharts (`iniciar`, `tema`, `tooltip`, `ejeNumerico`, `C`) y componentes generales: `linea`, `columnas`, `barras_h`, `tabla` |
| `assets/js/charts_bancos.js` | Componentes del sitio y el **registro único** `COMPONENTES` (incluye los generales) |
| `assets/js/datos.js` | `cargar(tabla)` con caché por sesión, `cargarTodas`, `tablasExportadas()` (lee `_manifiesto.json`) |
| `assets/js/estado.js` | Banco activo y grupo (de la URL), lista de bancos (filas de `bk_banco`), barra de banco, `enfocarBanco()` |
| `assets/js/presentacion.js` | Modo Presentar (láminas 1920×1080) e impresión; recibe de `pagina.js` la config y las láminas (`alMontar(cfg, laminas)`) |
| `assets/js/fluidez.js` | Cola de trabajo visual por fotograma |
| `assets/css/tokens.css` | Paleta (los mismos valores que `COLOR` de tokens.js; `verificar_f1.py` lo comprueba), fuentes (Google Fonts por `@import`), tamaños |
| `assets/css/monitor.css` | Maqueta base (grilla, responsive) |
| `assets/css/bancos.css` | Piel FARO y piezas del sitio; va después de monitor.css y la pisa |
| `assets/vendor/echarts.min.js` | ECharts 5, render SVG |

## Montaje de una página (`pagina.js`)

1. `paginaDeRuta(location.pathname)` da la entrada de `PAGINAS`; se importa `paginas/<clave>.js` y la config
   final es `{ ...PAGINAS[i], ...config }`. Ruta desconocida: «Esta página no existe».
2. Cabecera = menú lateral con las páginas no ocultas. Bajo 1200 px pasa arriba.
3. Carga la lista de bancos desde `bk_banco` si está en el manifiesto. Barra superior: título de la página,
   buscador y selector de banco (si `usaBanco`) y botón «Presentar».
4. Franja opcional (`cfg.franja`): celdas con último valor, cambio y mini serie (SVG propio).
5. Por cada sección: `<section class="seccion" id="sNN">` con **riel** (número, nombre, frecuencia, pregunta y
   selectores) y **cuerpo** (grilla de 9 columnas con las tarjetas de `filas`).
6. Cada tarjeta se dibuja en paralelo (`dibujar`): espera las fuentes (máx. 3 s), carga sus `datos`, llama
   `armar(d, contexto)` y pasa el resultado al componente. La página no espera a sus tarjetas.
7. Al terminar la estructura, `<html data-pagina="lista">` (antes `montando`). Las tarjetas siguen su propio
   ciclo de vida (abajo). Una tarjeta sin dato nunca se oculta: va «en preparación» (regla de CLAUDE.md).

### Ciclo de vida de tarjetas y franja (`data-estado`)

Una sola máquina de estados en `pagina.js` (`marcar`, `estadoDatos`). El estado vive en `data-estado` de la
`<figure class="tarjeta">` (o del nodo de la franja) y `aria-busy` se deriva de él.

| Estado | Qué se ve | Sale a |
|---|---|---|
| `cargando` | «Cargando indicador…» (sin resultado previo) | `lista`, `en-preparacion`, `requiere-banco`, `error` |
| `actualizando` | el resultado anterior; «Actualizando…» si tarda más de 300 ms | ídem |
| `lista` | el gráfico o la tabla | `actualizando` (cambio de banco o selector) |
| `en-preparacion` | «Sin datos disponibles» + motivo | `cargando` |
| `requiere-banco` | «Elige un banco para continuar» + botón | `cargando` |
| `error` | «No pudimos…» + Reintentar | `cargando` |

- Solo se entra a `actualizando` desde `lista`/`actualizando`; otra transición deja un `console.warn`.
- Para inspeccionar o probar (personas, `verificar_f1.py`, agentes): la página terminó cuando
  `html[data-pagina=lista]` y no queda ningún `[data-estado=cargando|actualizando]`. No leer el texto visible.

## Configuración de página (`paginas/bN.js`, `export default {...}`)

Clave, ruta y nombre **no** van aquí: están en `PAGINAS` de `config.js`.

```js
import { FUENTE, enPreparacion } from '../comun.js';
import { COLOR } from '../tokens.js';
import { etiquetaMes } from '../formato.js';

export default {
  rotulo: 'SISTEMA BCB · MENSUAL',
  usaBanco: false,                 // sin barra de banco
  titularPorBanco: false,          // true (Ficha): con banco activo, el titular es el banco
  franja: [ indicadorPanel('ROE 12 meses · Panel', 'roe_ttm') ],  // opcional (comun.js); el tono sale de bk_metrica
  secciones: [{
    numero: '01', nombre: 'Por tipo', frecuencia: 'Mensual · SGS', pregunta: '…',
    riel: [ { tipo: 'selector', clave: 'grafico', rotulo: 'GRÁFICO', defecto: 'barras',
              opciones: [{ valor: 'barras', nombre: 'Barras · último' }, …] },
          ],
    filas: [[ { clave: 'B3-01', ancho: 4, alto: 570 }, { clave: 'B3-02', ancho: 5, alto: 570 } ]],
  }],
  tarjetas: {
    'B3-01': {
      titulo, sub, plana: true,        // plana: sin borde
      componente: 'barras_signo',      // clave en COMPONENTES (charts_bancos.js)
      datos: ['bk_cred_tablas', 'bk_cred_series'],   // tablas o particiones (tablaMetrica('roe_ttm'))
      armar: (d, contexto) => entrada, // solo selecciona y da forma; NO calcula
      leyenda: [{ nombre, color, discontinua }],      // leyenda HTML fija (opcional)
      nota, fuente: FUENTE.SGS, estado: 'LISTO' | 'DERIVAR' | 'FALTA' | 'REF', banco: true,
    },
  },
};
```

- `armar(d, contexto)`: `d` es `{tabla: filas}`; `contexto` = `{banco, bancoActivo (fila de bk_banco), grupo,
  periodoActivo (AAAAMM: ?t= o el último corte del Panel), seleccion: {clave: valor de los selectores de la sección}}`.
- `datos` es una lista de tablas o una función del mismo contexto (p. ej. la partición `banco/<slug>/` del banco
  activo): así `armar` no carga nada y un fallo de carga pasa por el «Reintentar» de la tarjeta.
- Devuelve una de dos cosas:
  - **sin dibujo**: `enPreparacion('motivo')` o `requiereBanco('motivo')` (comun.js). La tarjeta pasa a
    `en-preparacion` o `requiere-banco` y muestra el motivo tal cual (con el botón «Elegir banco» en el segundo);
  - **la entrada del componente**, que además puede llevar `componente` (cambia el componente según la vista),
    `leyenda` (reemplaza la leyenda; `[]` = la dibuja el gráfico) y `ariaLabel`.
- Sin `armar`, la tarjeta va «en preparación» con el motivo de su `estado`. Un `armar` que no devuelve nada
  o un componente inexistente dan el aviso genérico y un `console.error` (es un problema del sitio, no del
  dato; `verificar_f1.py` lo cuenta como falla).
- Un selector cambia → solo se redibujan las tarjetas de **esa** sección.
- Las configs importan solo módulos sin DOM (`comun.js`, `formato.js`, `datos.js`): las herramientas de Node las
  cargan con `import()` (`herramientas/inventario_paginas.mjs`).

## Componentes

Registro único `COMPONENTES` (charts_bancos.js): cada uno es `{ dibujar(contenedor, entrada), entrada, descripcion }`.
El papel de la zona lo decide lo que devuelve `dibujar`: una instancia de ECharts (ResizeObserver, `role=img` con
`ariaLabel`) o `null` si dibujó HTML. La lista con descripción y claves de entrada está en `generado/componentes.md`.

Los usados por las páginas del canvas (Portada, Crédito, Personas, Mora):

- **`barras_linea`** (ECharts): barras (apiladas, eje izquierdo o derecho con `ejeBarras: 'der'`) + una o
  varias líneas (`lineas: [{nombre, color, valores, discontinua, grosor, z}]`). `rangoIzq/rangoDer =
  {escala, min, max}`. `leyendaInteractiva: true` → leyenda ECharts en una fila con desplazamiento; clic
  oculta/muestra series.
- **`barras_signo`** (ECharts): barras horizontales con valor rotulado; color por fila (`color`) o por
  signo (`colorPos`/`colorNeg`).
- **`mapa_cuotas`** (ECharts treemap): cuota por banco; los colores por grupo los manda la página (`colores`).
- **`tabla_estandar`** (HTML): la única tabla descriptiva. Columnas fijas, cifras con `tabular-nums`; formatea
  con `formatear(v, unidad, opciones)` (formato.js), con las unidades de `unidad_ultimo` / `unidad_cambio`.

Cada componente declara las claves de su entrada (`entrada`) y su `descripcion`; `dibujar` devuelve la instancia
de ECharts (la zona pasa a `role=img`) o `null` si dibujó HTML. Las tablas se ocupan de su propia accesibilidad
(`cajaDesplazable`) y marcan con `data-conservar-scroll` / `data-conservar-abierto` lo que el motor conserva al
redibujar. Todo gráfico ECharts nace en `iniciar(cont)` (charts.js, render SVG) y su opción parte de `tema()`, que fija
`textStyle.fontFamily` (= `--fuente`): ECharts mide el texto con esa familia y el SVG lo pinta con la de la
página; si no coinciden, las etiquetas se cortan.

Formato de cifras: un solo vocabulario de unidades en `formato.js` (`formatear(v, 'pct')` o
`formatear(v, { unidad: 'pct', decimales: 0, signo: true })`); los ejes usan `formatoEje(unidad)`, con coma
decimal y solo los decimales necesarios. `fijo` usa el redondeo de `toFixed` (tabla estándar y rótulos de
gráfico); sin `fijo`, el de `Intl`: solo difieren en empates (1,15). El signo sale del valor redondeado
(«0,0», nunca «−0,0» ni «+0,0»).

## Estado y URL

`estado.js` guarda el estado en la query string: `banco` (slug), `grupo` (`panel` = sin grupo), `t`
(trimestre). La barra solo elige banco; grupo y trimestre se fijan por URL. Al elegir banco, el grupo pasa
a su modelo de negocio. Cambiar estado dispara `bancos:estado` y se redibujan las tarjetas marcadas
`banco: true` y la franja. Los enlaces del menú conservan la query.

Los selectores de sección también van en la query, como `s<NN>.<clave>=<valor>` (p. ej. `?s01.grafico=lineas`),
solo cuando difieren del defecto; un valor que no es una opción del selector se ignora. Son de la página: los
enlaces a otras páginas (menú, recorrido de Presentar) usan `busquedaCompartida()`, que los quita,
porque el mismo número de sección es otra cosa en otra página. Cambiar un selector no dispara `bancos:estado`.

## Modo Presentar (`presentacion.js`)

- Entra con el botón, la tecla **P** o `#presentar=sNN` en la URL. Mientras se presenta, el hash es
  `#presentar=sNN` de la lámina visible (recargar o compartir abre esa lámina); al salir vuelve el hash previo.
  Al pasar a una página sin láminas, el recorrido sigue a la próxima. **Esc** sale; **→ / Espacio** siguiente;
  **←** anterior; **Inicio/Fin**; número + Enter salta. Al final de una página pasa a la siguiente del menú.
- Cada sección es una lámina 1920×1080 escalada con `transform` para caber en la ventana. Número, nombre,
  pregunta y frecuencia salen de la config; el cuerpo de la sección **se mueve** (no se clona) a la lámina para
  que ECharts siga vivo; al salir vuelve a su lugar. Los selectores del riel viajan a la franja `.pres-selectores`.
- Al entrar, la letra de los gráficos ECharts se multiplica por 1,5 (y los márgenes de la grilla); al
  salir se divide. `pagina.js` avisa con `alRedibujar(zona)` cuando un gráfico se redibuja dentro de la lámina.
- Impresión: una hoja por sección con pie «Bancos Brasil · página · sección · frecuencia · Fuentes».

## Diseño responsive

- ≥1440 px: grilla de 9 columnas, menú lateral.
- 1200–1439: el riel de la sección pasa arriba en fila; la grilla sigue de 9.
- 700–1199: menú arriba; gráfico y tabla siguen lado a lado con alto fijo (`--alto`).
- <700: una columna (celular).

## Rendimiento

- Cargar particiones, no tablas completas: `bk_panel` 27 MB, `bk_grupo` 12 MB, `bk_cre_panorama` 6,5 MB,
  `bk_cre_calidad` 5 MB. Ejemplo correcto: `datos: [tablaMetrica('costo_riesgo_ttm'), 'bk_banco']`.
- Cabeceras `no-cache` en `/assets/*` y `/data/*` (`sitio/_headers`, que lee Cloudflare Pages): cada visita
  revalida; tras un deploy basta recargar.
