# 5 · Rediseño de gráficos

Pablo anunció (6-nov) un «cambio gigantesco» en el diseño de los gráficos. Todavía no está definido.

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
