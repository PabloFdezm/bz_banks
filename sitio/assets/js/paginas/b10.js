/* B10 · Metodología y fuentes. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del
   spec macro). El esqueleto §B10 dice: «Texto fijo, sin tarjetas de datos», así que la página no
   tiene secciones ni tarjetas: solo cabecera y apertura. El sitio todavía no tiene dónde poner
   texto fijo (el cierre con fuentes y «cómo leer» de la plantilla se quitó sin uso).
   El esqueleto no le da rótulo a esta página: lo fija la decisión del 2026-11-02
   y entra al esqueleto v0.2 — «10 · METODOLOGÍA».
   El contenido del texto fijo —los cinco universos y su rezago, las definiciones desde
   `bk_metrica`, los quiebres de §0.7, las ópticas de §0.5, el puente IF.Data ↔ publicado y las
   fuentes con su fecha de corte— está pendiente: depende de `bk_metrica` y de `bk_manifiesto`. */
export default {
  rotulo: '10 · METODOLOGÍA',
  usaBanco: false,

  secciones: [],
  tarjetas: {},
};
