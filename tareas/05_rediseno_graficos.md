# 5 · Rediseño de gráficos

Pablo anunció (6-nov) un «cambio gigantesco» en el diseño de los gráficos. Estado al 10-nov: en curso; decisiones
del 9-nov abajo y hojas por producto en el frente 12 (Tarjeta aprobada el 10-nov). Falta cerrarlo.

- Decisión de Pablo (6-nov): no se construyen páginas nuevas (Personas, réplicas del REF) hasta definir el
  rediseño; mientras tanto se avanza solo en datos (pipeline y gold).
- Proceso: canvas → aprobación → construcción.
- Revisión hoja a hoja del sitio al 4-nov, con cada gráfico y tabla numerado:
  canvas «Bancos Brasil · Revisión hoja a hoja» (Portada, Crédito, Calidad, Rentabilidad, Ficha).
- Las reglas fijas de diseño están en `CLAUDE.md`. El rediseño puede cambiarlas solo si Pablo lo dice explícitamente.
- Archivos involucrados:
  - `sitio/assets/js/charts_bancos.js` (componentes);
  - `sitio/assets/js/pagina.js` (montaje);
  - `sitio/assets/js/presentacion.js` (modo Presentar);
  - `sitio/assets/css/bancos.css` (los bloques se acumulan por versión y el último gana).

## Decisiones del 9-nov (canvas «Rediseño de gráficos v3», https://claude.ai/artifact/Prgu2BygZtvCDWBTF52ag8)
- Portada = tres secciones mensuales: 01 Crédito: colocaciones y ciclo · 02 Precio del crédito · 03 NPL: mora y
  atraso temprano. Datos: frente 9.
- (Actualizado 9-nov, 19:20) Lo trimestral va en **una sola página «Bancos por grupo · trimestral»** (lámina
  Trimestral del canvas), con un desplegable único de agrupación arriba y siete secciones: T1 saldos de crédito,
  T2 depósitos por tipo, T3 rendimientos (yield del crédito y costo de captación), T4 margen y riesgo (NIM,
  provisiones, costo del riesgo), T5 resultado y ROE, T6 eficiencia, T7 capital. Sin concesiones (no hay por banco).
- Falta en gold para esa página (hoy calculado desde el crudo para el canvas): depósitos por tipo (informe 3:
  vista, ahorro, interfinancieros, plazo, otros), rentas de operaciones de crédito y gastos de captación (informe 4)
  por banco y grupo, con yield = rentas 12m / cartera media de 5 cierres y costo = gastos de captación 12m /
  captaciones medias; costo del riesgo por grupo.
- Estructura común: dos pares gráfico + tabla corta por sección; un solo Agrandar por par con gráfico, slicer, tabla
  completa en bloques (con Z 10 años y columna Historia) y un bloque inferior gráfico + tabla con box plot; títulos
  descriptivos, nunca preguntas; sin rótulos de frecuencia/fuente en la cabecera; Total en cobre; bandas rotuladas
  en quiebres (Res. 4.966; cambio de panel en 3T23 en Capital).

## Construcción del sitio v2 (10-nov, Pablo aprueba todas las hojas del canvas)
- Motor: `sitio/assets/v2/dc.js` interpreta las plantillas del canvas (x-dc) en el navegador, con render en el lugar.
  Las hojas viven versionadas en `diseno/canvas/*.dc.html` (sin datos) y `diseno/canvas/paginas.json` define páginas,
  rutas y menú. `herramientas/construir_v2.py` genera `sitio/v2/<ruta>/`, `sitio/assets/v2/{componentes,paginas}/` y
  `sitio/data/v2/` (generados, fuera de git); `publicar.bat` lo corre antes de subir.
- Páginas: /v2/portada (Secciones 01–03), trimestral, credito, tarjeta, personal, planilla, vehiculos, inmobiliario,
  mpme, grandes, fondeo, agregados (hoja Ficha), pyb. Probadas en Chromium (1920, 1280 y 390): sin errores, Agrandar,
  Escape, selectores y Ajustar eje funcionan. Ancho fijo de 1600 px escalado con `zoom` en pantallas más chicas.
- Flujo de cambios: se edita la hoja en el canvas → se copia a `diseno/canvas/` (sin la línea `const X`) → los datos
  de la hoja van a `tareas/borradores/_salida/v2/<Hoja>.json` → `publicar.bat`.

Marco común (`sitio/assets/v2/sitio.js`, `v2.css`), 10-nov: menú lateral plegable con índice de secciones; barra
superior con corte de los datos (el más reciente de la columna «Corte»), «Excel de la página» y «Presentar»; Agrandar
como ventana centrada; modo Presentar (un par gráfico + tabla por pantalla, flechas y Esc); botón «Excel» en cada
gráfico y en cada bloque de Agrandar (SheetJS 0.18.5 en `sitio/assets/vendor/`, carga al primer uso). El botón Excel y
los campos `nombre`, `todo` y `etiquetasTodas` de la configuración del gráfico los agrega `construir_v2.py` solo en el
sitio; el canvas no cambia.

Pendiente:
1. Datos: hoy `_salida/v2/*.json` es la foto de los datos del canvas aprobado. Para que `publicar.bat datos` los
   refresque, mover los borradores `extraer_*.py` (producto, empresas, fondeo, pyb, agregados, inmobiliario y los de
   Portada, Trimestral y Crédito) a `pipeline/web_v2/`, que escriban `_salida/v2/<Hoja>.json` leyendo solo gold, y
   llamarlos desde `actualizar.py`. Los de Portada, Trimestral y Crédito hoy no existen en el repo: reconstruirlos
   desde la lógica de las hojas.
2. Pasar la raíz del sitio a v2 cuando Pablo lo valide (redirigir `/` a `/v2/portada/` y retirar las páginas viejas).
3. Diseño para móvil: hoy es la página de escritorio escalada.
