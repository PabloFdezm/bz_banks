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
2. Hecho el 10-nov: el sitio anterior se borró de `sitio/` (queda en el historial de git); las páginas nuevas están en la raíz (`/portada/`, `/tarjeta/`…; `/` es la Portada) y `sitio/_redirects` lleva las rutas viejas y `/v2/*` a su equivalente. Quedan obsoletos para el sitio: `herramientas/verificar_f1.py` e `inventario_paginas.mjs` (leían el sitio anterior) y el paso `exportar` de `actualizar.py` (`sitio/data/*.json` ya no lo lee ninguna página): rehacer o retirar.
3. Diseño para móvil: hoy es la página de escritorio escalada.

## Pendientes de canvas de la revisión del 11-nov (critique de la Portada)
Aprobados por Pablo el 11-nov; van primero a canvas porque cambian la cabecera de todas las hojas:
1. **Selector de corte por sección:** una sola vez junto al título de la sección (hoy está en cada tarjeta y cambia
   las dos). En Presentar se muestra como texto («Corte: …»). La cabecera de tarjeta baja de 5 a 4 controles.
2. **Agrandar de la tabla:** botón en la tarjeta de tabla que abre la tabla completa de 8 columnas y su glosario, sin
   gráfico (regla del 8-nov; DESIGN.md lo marca como pendiente).
3. **Cifra de entrada:** franja de 4–6 cifras bajo el título y cifra del Total (28 px mono, Δ a/a) sobre cada tabla
   (DECISIONES_UX_2026-11 §3).
Hecho el 11-nov sin canvas (correcciones de reglas ya decididas): Presentar sin controles, sección 02 sin series
vacías, teclado y lector de pantalla, unidades del spread, encabezados de la tabla corta, banda neutra, rótulo de
referencias, contraste del menú.

## Por hacer · segunda revisión de la Portada (11-nov, 27/40; informe en .impeccable/critique/)
Mayores:
- [x] (11-nov, sin publicar) **Selector de corte de la sección 01 sin callejones:** «Libre / Dirigido» deja el gráfico sin datos y «Todos»
      trae «Empresas libre/dirigido · en preparación». Aplicar la regla de la sección 02: opciones sin datos
      deshabilitadas con «(en preparación)» y sin chips vacíos.
- [x] (11-nov, sin publicar; copia fija del título en sitio.js, salto de 3 px; el foco vuelve) **Presentar estable:** la tarjeta salta ~105 px entre láminas porque el título de sección solo va en la primera
      (choca con spec/01 regla 4). Reservar el alto del título en todas (repetido en gris desde la 2), estirar el par al
      alto disponible y devolver el foco a «Presentar» al salir (hoy cae en body).
- [x] (11-nov, sin publicar; en Grafico: retrocede al último período con dato) **«Impulso del crédito» fija sep-26 sin dato** (la serie llega a ago-26): el período fijado por defecto debe ser
      el último con dato de alguna serie visible (Grafico.dc.html, vale para todo el sitio).
Medianos:
- [x] (11-nov, sin publicar; queda decidir el recuadro) «Ajustar eje»: chips ▲▼ también para las series atenuadas que quedan fuera del eje; `aria-disabled` con la pista
      «Resalte una serie para ajustar el eje» en vez de `disabled`; decidir si el recuadro lista todas las visibles.
- [x] (11-nov, sin publicar) Agrandar: agrupar las filas «en preparación» (4 de 9 en concesiones) en una nota con las series SGS que faltan;
      quitar «ver tareas/09» y «datos del 8-nov-26» del glosario.
Menores:
- [x] (11-nov, sin publicar; se oculta si la banda mide menos de 66 px) Rótulo «Res. 4.966» cortado a 390 px (la banda mide 20 px): ocultarlo o moverlo fuera de la banda en angosto.
- [x] (11-nov, publicado; menú lateral subido a 36 px en vez de excepción) DESIGN.md: contraste del texto atenuado es 4,62:1 (no 4,7); agregar 15 px y 20 px a los tokens de tipografía;
      decidir la excepción de tamaño de los controles del menú lateral (24–34 px).
- [x] (11-nov: cobre siempre; recuadro de «Ajustar eje» solo con las resaltadas; anotado en DESIGN.md) Decidir con Pablo: ¿Total en cobre aunque no se abra en partes (tasa y spread hoy) o navy cuando es serie única?
- [x] (11-nov, publicado: botón «Cómo leer» con uso y glosario en la barra; «Eje horizontal: …» quitado de las 15 hojas) Pistas de interacción (Ctrl + clic, flechas, Ajustar eje) y glosario de «NPL», «Share», «a/a», «Δ a/a» fuera de
      Agrandar; «Eje horizontal: mes.» repetido en las seis tarjetas.
- [ ] Ideas para discutir: sección 02 como un solo par (tasa y spread con la Selic) mientras falten los cortes; subir la
      mora como cifra de entrada.

## Tercera revisión (11-nov, 26/40; informe en .impeccable/critique/2026-11-11T15-11-58Z…)
Hecho y publicado el 11-nov:
- [x] P1 Total siempre en la escala por defecto (12 hojas; solo «Ajustar eje» lo saca).
- [x] P1 MPME E1/E3: series del SCR en el calendario mensual completo (antes cortadas en sep-22).
- [x] P1 Agrandar en celular: cabecera que baja de línea y tabla con desplazamiento horizontal.
- [x] P2 Portada: franja de entrada con cinco cifras y enlace a su par (aprobada).
- [x] Tablas de página con saldo, share y a/a donde el gráfico muestra el a/a del saldo (aprobada; 5 hojas).
Pendiente (P2 y menores):
- [ ] Una sola regla de rótulos del eje X (2 rótulos en Tarjeta/MPME contra 8 en la Portada al mismo ancho).
- [ ] «Reclasificación» recortada en las bandas de MPME (12 gráficos): texto corto o mismo mecanismo que «Res. 4.966».
- [ ] Notas de P&L de ~270 caracteres por línea: ancho máximo ~75.
- [ ] Tablas cortas que estiran la tarjeta; botones Excel con el nombre del gráfico; SVG de trazado con aria-hidden.
- [ ] Colores fuera de DESIGN.md (#4F5B6B, #1B2433, #3B4656) y escala tipográfica real (11–26 px) por documentar.
- [ ] MPME y Grandes: tabla de volumen con saldo y share (falta el saldo en R$ por porte en el par).
