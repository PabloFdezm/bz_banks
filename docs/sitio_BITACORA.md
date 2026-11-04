# Bitácora — sitio de bancos

## 2026-11-02 · 65b — corrección del arquitecto sobre 65

- Datos ficticios de `_prueba/`: el punto del banco caía en la mediana cuando no había banco activo
  (defecto de los datos de prueba, no del componente). Ahora la distribución es asimétrica, sin banco
  usa una entidad ficticia propia y 10 de 12 filas quedan fuera de la mediana.
- `small_multiples_bancos`: nombre completo en su línea, valor debajo, 5 columnas y alto 800 px en la
  sección 02 de la prueba; la grilla muestra las 34 miniaturas sin recortes.
- Eje de valores de la control (P-06): formato de porcentaje con un decimal desde la config de prueba
  (`formatear`), sin tocar `charts.js`. Ninguna etiqueta se repite.
- `burbujas_trayectoria`: margen derecho de 96 px y título del eje X centrado (antes se salía del marco).
- Ficha con banco activo: titular = nombre del banco; rótulo = «8 · FICHA · MODELO» (solo B8).
- `estado.js` prefiere `data/bk_banco.json` cuando `TABLAS_EXPORTADAS` lo declara; la constante queda de respaldo.

## 2026-11-02 · 65 — front de la ola 2: estado, presentación y piezas nuevas

**Alcance** (encargo `65_encargo_haiku_front.md`): `estado.js` (estado por URL y barra de banco
activo), `presentacion.js` (modo presentación y hoja de impresión), `charts_bancos.js` (`percentiles`,
`cascada_doble`, `burbujas_trayectoria`, `small_multiples_bancos`, `comparador`), `bancos.css`,
cambios `// bancos:` en `pagina.js` y la página de prueba `site/_prueba/` (**no publicable**).

**Decisiones tomadas en la construcción** (revisar):

1. **Lista de bancos copiada al construir**, no leída en ejecución: slug y nombre de
   `definiciones/bancos__dashboard.json`; modelo de negocio de `definiciones/bcb_ifdata__bancos_balances.json`
   (criterio del analista aprobado 2026-10-09). `data/bk_banco.json` no existe todavía.
2. **Grupo por defecto = modelo del banco** al elegirlo; `grupo=panel` fuerza el panel total.
   Sin banco, el grupo es el panel total. El estado vive solo en la URL (sin storage).
3. **Barra de banco activo** en todas las páginas (también en la portada), sticky, 48 px. El
   selector de trimestre solo muestra «Último» hasta que las páginas llamen a `fijarTrimestres()`
   con datos.
4. **Redibujo de tarjetas [banco]** al cambiar el estado: `armar` recibe `{clave, banco, optica,
   grupo, trimestre}`; cada tarjeta con `banco: true` libera sus instancias de ECharts y se vuelve a
   dibujar. Las tarjetas sin `banco` no se tocan (criterio 13).
5. **Presentación**: la lámina tiene diseño 1920 × 1080 con margen de 48 px y alto natural (mínimo
   1080); se escala con `transform` para caber. El cuerpo de la sección se mueve (no se clona) para
   no perder las instancias de ECharts y vuelve a su sección al salir. Recorrido: `→` al final de
   una página pasa a la primera lámina de la siguiente según el orden de `config.js` (B0 → B10),
   con el mismo estado; las páginas sin secciones (B10 hoy) se saltan.
6. **Impresión**: una lámina por hoja de **1920 × 1080 px** (16:9), no A4 apaisada como dice el
   spec §4, para no re-maquetar la lámina. Pie de hoja con fuente y fecha de corte.
7. **Comparador**: CSV con `;` y BOM UTF-8 (para Excel en es-CL), con las filas y columnas visibles.
8. **`_prueba/`**: no se enlaza desde ninguna página; `noindex` en `<meta>` y en `_headers`; datos
   ficticios marcados «DATOS FICTICIOS DE PRUEBA» en pantalla. **No publicable.**
9. **Botón «Presentar»** en la cabecera con clase propia (no `pestana`), para que el conteo de
   pestañas de la F0 siga en 11.

**Verificación** (salida literal en `RESULTADOS.md`, sección 65): criterios 13, 14 y 15 sobre
`/_prueba/` y `/ficha/?banco=itau`; `verificar_f0.py` pasa; `contar_tarjetas.mjs` pasa (82).

## 2026-11-02 · 62b — decisiones del arquitecto sobre la F0

Aprobada la F0. Se aplicaron las cuatro decisiones del arquitecto (revisión del encargo 62, en
`docs/dashboard_bancos/PENDIENTES.md`) **solo dentro de `sitio_bancos/`**:

1. **Prefijo «BCB ·»** para reclamos y tarifas (B2-05-0, B2-05-1, B8-07-0): no es un universo
   nuevo, es la fuente BCB fuera de los cinco universos de §0.4. **Pix sigue «Sistema BCB ·»**
   (es SGS). Verificado en pantalla.
2. **B9 · 01**: nombre «Todos los bancos» y pregunta «¿cómo se comparan los 34 bancos en el último
   trimestre?». Con eso `verificar_f0.py` volvió a exigir nombre en todas las secciones: la lista
   `HUECOS` quedó vacía (una excepción que deja de aplicar se borra, no se deja de adorno).
3. **B10**: rótulo «10 · METODOLOGÍA» (el contenido del texto fijo sigue en la ola 2/3).
4. **B8 · 07**: pregunta «¿cómo lo evalúan sus clientes frente a sus pares?». El riel sigue sin
   definir porque el esqueleto no le da bloques.

Estas cuatro entran al esqueleto v0.2; hasta entonces la config es la que las tiene escritas.
`contar_tarjetas.mjs` y `verificar_f0.py` se volvieron a correr: 82 tarjetas, los once conteos
iguales al esqueleto y las once URLs sin errores de consola (`RESULTADOS.md`).

## 2026-11-02 · F0 (encargo `62_encargo_barato_sitio_f0.md`)

**Alcance:** estructura del sitio (spec web de bancos §2), módulos comunes copiados del Monitor
Brasil, las 11 páginas navegables con cabecera, apertura, índice y secciones, y **todas las
tarjetas «en preparación»**. Sin gráficos, sin `estado.js`, sin `presentacion.js`, sin
`charts_bancos.js`: eso es la ola 2 (H4).

### Base provisoria: el sitio del macro todavía no está aprobado

Los módulos comunes se copiaron de **`pb/pbip/diseno/paginas_desde_cero/qwen3.8-max/site/`**, que
es el **único sitio del macro construido** hoy y que **todavía no está aprobado por Pablo**. Se
tomó como **base provisoria**: sirve para no arrancar de cero, pero cuando Pablo marque la versión
vigente (o apruebe esa), los módulos hay que **volver a copiarlos** y comparar contra este árbol.
No se modificó nada en el sitio de origen (solo lectura + `cp`).

Copiados tal cual, sin bifurcar:

| Archivo | Origen | Nota |
|---|---|---|
| `assets/css/tokens.css` | qwen3.8-max | tokens del sistema visual; no editar |
| `assets/css/monitor.css` | qwen3.8-max | layout, cabecera, apertura, secciones, tarjetas, tablas, responsive |
| `assets/js/datos.js` | qwen3.8-max | `cargar()`, filtros, utilidades de fecha |
| `assets/js/formato.js` | qwen3.8-max | números, %, pp, pb, fechas en español |
| `assets/js/charts.js` | qwen3.8-max | `linea`, `columnas`, `barras_h`, `tabla` (existe: no hubo que dejar el archivo vacío) |
| `assets/js/pagina.js` | qwen3.8-max | arma la página; los cambios de bancos van marcados `bancos:` |
| `assets/vendor/echarts.min.js` | qwen3.8-max | ECharts 5.5.1 local |

Archivos nuevos propios de bancos: `assets/js/config.js` (once páginas + `MARCA`), `assets/css/bancos.css`
(vacío con cabecera: solo entra lo que tenga pieza), `assets/js/paginas/b0.js … b10.js`,
`contenido/textos.json`, `netlify.toml`, `_headers`, `404.html`.

### Cambios hechos sobre el `pagina.js` copiado

Todos marcados `// bancos:` en el archivo. Ninguno toca la anatomía:

1. **Tarjeta sin `armar` → «en preparación»** con el motivo del estado del esqueleto:
   `LISTO`/`DERIVAR` → «dato en construcción», `FALTA` → «fuente no incorporada», `REF` →
   «disponible con el próximo REF» (paso 8 del encargo, §7.5 del spec macro). El resto de la
   lógica del macro (`armar`, `BLOQUEADOS`, componentes) queda intacta para la ola 2.
2. **Portada en la raíz:** `ruta: ''` no puede generar `href="//"`, así que los enlaces de la
   cabecera pasan por `enlace(ruta)`.
3. **Alto `auto`** (B9-01-0, «9 × auto»): solo se fija alto cuando es número.
4. **Cierre invisible** si no hay `fuentes` ni `comoLeer`. En F0 el esqueleto no los da (van en
   §B10) y no se pinta un bloque vacío.
5. **Rótulo de la cabecera:** `MARCA = 'BANCOS BRASIL'` en `config.js`, en vez de «MONITOR BRASIL»
   (§B0 del esqueleto: «BANCOS BRASIL · MONITOR»).

### Cómo se transcribió el esqueleto (y qué se derivó)

- **Títulos, preguntas de sección, anchos, altos, estados y marcas [banco]:** literales del
  esqueleto. Las preguntas van en `pregunta` (texto por defecto) y en `preguntaClave`; como
  `contenido/textos.json` está vacío (Pablo escribe el titular y la intro), la pregunta del
  esqueleto se ve **en cursiva**, que es el comportamiento del macro.
- **`estado`:** un solo valor por tarjeta, el de la columna Estado. Cuando el esqueleto agrega un
  matiz («LISTO salvo Basilea», «DERIVAR (un corte hoy; FALTA la serie)») queda anotado en
  `PENDIENTES.md`, no en la tarjeta: el spec prohíbe notas de trabajo en texto visible.
- **`sub`:** empieza con el universo (§5) y sigue con la unidad, la transformación y la ventana
  que **dice el esqueleto en esa fila**; no se agregó nada que no esté ahí.
- **`frecuencia` de cada sección:** el esqueleto no la da como columna, así que se derivó del
  universo de la columna «Datos» de sus tarjetas (Panel IF.Data → trimestral, SGS → mensual,
  SCR → mensual, REF → semestral). **A confirmar** (ver `PENDIENTES.md`).
- **`fuente`:** la fuente pública del universo de la tarjeta (regla de oro 4), más «cálculo
  propio» en las que el pipeline calcula (DERIVAR). Las de Olinda, BNDES/FGI y FGO/Pronampe son
  propuestas: el esqueleto no las fija y §B10 las tiene que confirmar.
- **`datos: []`** (paso 4 del encargo): en F0 el sitio **no hace ningún `fetch`**, así que las
  once URLs cargan sin 404 ni errores de consola. Las tablas que pide el esqueleto para cada
  tarjeta quedaron en el comentario de cabecera de cada `bN.js`, para que la ola 2 las complete.
- **`componente`:** el nombre de la pieza tal como la escribe el esqueleto; cuando el spec de
  bancos §6 define una pieza propia se usa ese nombre (`percentiles`, `cascada_doble`,
  `burbujas_trayectoria`, `small_multiples_bancos`, `comparador`). Las tarjetas compuestas
  (`columnas` + línea, `linea` ×2 paneles, `barras_h` con marcas, `dispersion` con diagonal)
  guardan la pieza principal; la composición está en el esqueleto.
- **Rótulos con hueco en el esqueleto:** B8 es «8 · FICHA · [Banco]» y el corchete no se pinta
  (criterio §9: cero `[` visibles); el nombre del banco lo agregará `estado.js`. B10 no tiene
  rótulo en el esqueleto: va vacío. B9 no tiene nombre ni pregunta de sección: van vacíos.

### Verificación (ver `RESULTADOS.md`)

`node sitio_bancos/contar_tarjetas.mjs` (conteos por página y por estado contra el esqueleto) y
`python -X utf8 sitio_bancos/verificar_f0.py` (Chromium real sobre
`python -m http.server -d sitio_bancos/site 8080`: las once URLs, secciones, tarjetas en
preparación y captura de B8 a 1 920 px en `capturas/b8_f0_1920.png`).

### Git

No se commiteó: el plan `57` §2.7 pide commits solo si el encargo lo pide, y el §6 del plan hace
revisar el diff al arquitecto antes de cerrar.
