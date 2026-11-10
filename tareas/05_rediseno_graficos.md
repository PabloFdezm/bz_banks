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
