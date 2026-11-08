/* Modo presentación (SPEC_WEB_BANCOS_00_GENERAL.md §4). Cada sección de la página es una lámina.
   Diseño de la lámina: 1920 × 1080 con márgenes de 48 px; la lámina entera se escala con transform para
   caber en la ventana (sin re-maquetar). El cuerpo de la sección se MUEVE a la lámina, no se clona, para que
   las instancias de ECharts sigan vivas; al salir vuelve al final de su sección.
   Teclas: P entra · Esc sale · → / Espacio siguiente · ← anterior · Inicio / Fin · número + Enter salta.
   Al final de una página, → pasa a la primera lámina de la siguiente (orden de config.js) con el mismo estado. */
import { PAGINAS_VISIBLES, NOMBRE_SITIO, enlace, paginaDeRuta } from './config.js';
import { crearColaVisual } from './fluidez.js';
import { busquedaCompartida, fijarHash } from './url.js';
import { el } from './dom.js';
const COLA_VISUAL = crearColaVisual();
const GRAFICOS_ESCALADOS = new WeakSet();
let versionLamina = 0;
let transicionLamina = null;

const ANCHO = 1920;
const ALTO = 1080;
const CLAVE_SESION = 'bancos:presentar';

let CFG = null;
let LAMINAS = []; // { cfg, nodo, cuerpo, selectores } de cada sección con cuerpo (las da pagina.js)
let activo = false;
let secciones = [];
let idx = 0;
let seccionActual = null;
let cuerpoActual = null;
let selectoresActuales = []; // [nodo, padre, siguiente] de los selectores del riel llevados a la lámina
let scrollPrevio = 0;
let capa = null;
let lamina = null;
let tecleo = '';
let timerTecleo = null;
let reanudarTrasImprimir = false;
let focoPrevio = null;
let inertePrevio = false;
let pantallaCompletaPropia = false;
let controles = null;

/* Estado de la presentación en la URL, como el resto del sitio: mientras se presenta, el hash es
   #presentar=sNN de la lámina visible. Recargar o compartir el enlace abre esa misma lámina; al salir se
   devuelve el hash que había antes (p. ej. #s03), así recargar después no vuelve a entrar. */
let hashPrevio = '';

/* Posición de esta página en el recorrido (las del menú); -1 si está oculta. */
const paginaIndice = () => PAGINAS_VISIBLES.indexOf(paginaDeRuta(location.pathname));


/* Los gráficos se diseñan para la página (letra 11–12 px); en una lámina de 1920 px eso queda diminuto.
   Al entrar a la lámina se agranda toda la letra de sus gráficos ECharts y al salir se devuelve. */
const FACTOR_TEXTO = 1.5;
function escalarTextos(raiz, f) {
  if (!raiz || !window.echarts) return;
  const recorrer = (o) => {
    if (Array.isArray(o)) { o.forEach(recorrer); return; }
    if (!o || typeof o !== 'object') return;
    for (const k of Object.keys(o)) {
      if (k === 'fontSize' && typeof o[k] === 'number') o[k] = Math.round(o[k] * f * 10) / 10;
      else if (typeof o[k] === 'object') recorrer(o[k]);
    }
  };
  for (const n of raiz.querySelectorAll('[data-grafico]')) {
    const ch = window.echarts.getInstanceByDom(n);
    if (!ch || (f > 1 && GRAFICOS_ESCALADOS.has(ch)) || (f < 1 && !GRAFICOS_ESCALADOS.has(ch))) continue;
    const op = ch.getOption();
    if (!op.textStyle || Array.isArray(op.textStyle)) op.textStyle = {};
    if (typeof op.textStyle.fontSize !== 'number') op.textStyle.fontSize = 12;
    recorrer(op);
    for (const g of op.grid || []) for (const k of ['top', 'right', 'bottom', 'left']) if (typeof g[k] === 'number') g[k] = Math.round(g[k] * f);
    ch.setOption(op);
    if (f > 1) GRAFICOS_ESCALADOS.add(ch); else GRAFICOS_ESCALADOS.delete(ch);
    ch.resize();
  }
}

/* Llamado por pagina.js cuando un gráfico se redibuja (selector, banco): dentro de la lámina, a su escala. */
export function alRedibujar(zona) {
  if (activo && zona.closest('.pres-lamina')) escalarTextos(zona, FACTOR_TEXTO);
}

/* El cuerpo vuelve al final de su sección (era su último hijo) antes de desmontar la lámina. */
function devolverCuerpo() {
  if (cuerpoActual) escalarTextos(cuerpoActual, 1 / FACTOR_TEXTO);
  if (cuerpoActual && seccionActual) seccionActual.append(cuerpoActual);
  for (const [n, padre, sig] of selectoresActuales) padre.insertBefore(n, sig && sig.parentNode === padre ? sig : null);
  selectoresActuales = [];
  cuerpoActual = null;
  seccionActual = null;
}

function escalar() {
  if (!activo || !lamina) return;
  // la lámina tiene alto natural (mínimo 1080): el contenido nunca se sale del marco de escala
  const alto = Math.max(ALTO, lamina.offsetHeight);
  const reserva = (controles?.offsetHeight || 60) + 32;
  const disponible = Math.max(80, window.innerHeight - reserva);
  const s = Math.min(Math.max(80, window.innerWidth - 32) / ANCHO, disponible / alto);
  lamina.style.top = `${disponible / 2}px`;
  lamina.style.transform = `translate(-50%, -50%) scale(${s})`;
}

function alCambiarTamano() { COLA_VISUAL.agendar('escala', escalar); }

function mostrar(i) {
  if (i < 0 || i >= secciones.length) return;
  const version = ++versionLamina;
  transicionLamina?.cancel();
  devolverCuerpo();
  idx = i;
  const { cfg: secCfg, nodo: sec, cuerpo, selectores } = secciones[i];
  seccionActual = sec;
  fijarHash(`#presentar=${sec.id}`);
  cuerpoActual = cuerpo;

  lamina.replaceChildren();
  const cab = el('header', 'pres-cab');
  cab.append(
    el('span', 'pres-num', secCfg.numero),
    el('h2', 'pres-nombre', secCfg.nombre),
    el('p', 'pres-pregunta', secCfg.pregunta || ''),
  );

  // los selectores de la sección (vista, medida…) viajan a la lámina, para cambiar la vista presentando
  // la franja de selectores existe siempre (vacía si no hay), para que título, gráfico y tabla
  // queden en la misma posición en todas las láminas
  const caja = el('div', 'pres-selectores');
  for (const n of selectores) { selectoresActuales.push([n, n.parentNode, n.nextSibling]); caja.append(n); }
  cab.append(caja);
  const cw = el('div', 'pres-cuerpo');
  cw.append(cuerpoActual);

  const pie = el('footer', 'pres-pie');
  pie.append(
    el('span', 'pres-frecuencia', secCfg.frecuencia || ''),
    el('span', 'pres-contador', `${i + 1} / ${secciones.length}`),
  );
  lamina.append(cab, cw, pie);
  actualizarControles();
  escalar();
  const cuerpoVisible = cuerpoActual;
  requestAnimationFrame(() => {
    if (!activo || version !== versionLamina) return;
    escalarTextos(cuerpoVisible, FACTOR_TEXTO);
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches && lamina.animate) {
      const duracion = Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--movimiento')) || 180;
      transicionLamina = lamina.animate([{ opacity: .86 }, { opacity: 1 }], { duration: duracion, easing: 'ease-out' });
    }
  });
}

export function entrar(i = 0) {
  if (activo) return;
  secciones = LAMINAS;
  if (!secciones.length) return;
  hashPrevio = /^#presentar/.test(location.hash) ? '' : location.hash;
  scrollPrevio = window.scrollY;
  focoPrevio = document.activeElement;
  capa = el('div', 'presentacion');
  capa.setAttribute('role', 'dialog');
  capa.setAttribute('aria-label', 'Modo presentación');
  capa.setAttribute('aria-modal', 'true');
  capa.tabIndex = -1;
  lamina = el('div', 'pres-lamina');
  controles = el('nav', 'pres-controles');
  controles.setAttribute('aria-label', 'Controles de presentación');
  const boton = (texto, nombre, accion) => {
    const b = el('button', `pres-control pres-${nombre}`, texto);
    b.type = 'button';
    b.addEventListener('click', accion);
    return b;
  };
  const estado = el('span', 'pres-estado');
  estado.setAttribute('role', 'status');
  estado.setAttribute('aria-live', 'polite');
  controles.append(boton('Anterior', 'anterior', anterior), estado,
    boton('Siguiente', 'siguiente', siguiente), boton('Salir', 'salir', salir));
  capa.append(lamina, controles);
  document.body.append(capa);
  document.body.classList.add('modo-presentacion');
  activo = true;
  const app = document.getElementById('app');
  inertePrevio = app?.inert || false;
  if (app) app.inert = true;
  // sin pantalla completa (navegador o permiso), la lámina igual se ve en la ventana
  document.documentElement.requestFullscreen?.().then(() => {
    if (activo) { pantallaCompletaPropia = true; escalar(); }
    else document.exitFullscreen().catch(() => {});
  }).catch(() => {});
  window.addEventListener('resize', alCambiarTamano);
  mostrar(Math.min(Math.max(i, 0), secciones.length - 1));
  controles.querySelector('.pres-salir').focus();
}

function salir() {
  if (!activo) return;
  ++versionLamina;
  transicionLamina?.cancel();
  transicionLamina = null;
  COLA_VISUAL.quitar('escala');
  devolverCuerpo();
  const app = document.getElementById('app');
  if (app) app.inert = inertePrevio;
  capa?.remove();
  capa = null;
  lamina = null;
  controles = null;
  document.body.classList.remove('modo-presentacion');
  window.removeEventListener('resize', alCambiarTamano);
  activo = false;
  if (pantallaCompletaPropia && document.fullscreenElement) document.exitFullscreen().catch(() => {});
  pantallaCompletaPropia = false;
  clearTimeout(timerTecleo);
  tecleo = '';
  fijarHash(hashPrevio);
  window.scrollTo({ top: scrollPrevio, left: 0, behavior: 'instant' });
  if (focoPrevio?.isConnected) focoPrevio.focus({ preventScroll: true });
}

function irPagina(dir) {
  const k = paginaIndice();
  const destino = PAGINAS_VISIBLES[k + dir];
  if (k < 0 || !destino) return;
  try { sessionStorage.setItem(CLAVE_SESION, dir > 0 ? 'primera' : 'ultima'); } catch { /* storage bloqueado (modo privado): entra en la lámina 1 */ }
  location.href = enlace(destino.ruta) + busquedaCompartida() + (dir > 0 ? '#presentar' : '#presentar=ultima');
}

function actualizarControles() {
  if (!controles) return;
  const k = paginaIndice();
  controles.querySelector('.pres-anterior').disabled = idx === 0 && k <= 0;
  const final = idx === secciones.length - 1 && (k < 0 || k === PAGINAS_VISIBLES.length - 1);
  controles.querySelector('.pres-siguiente').textContent = final ? 'Finalizar' : 'Siguiente';
  controles.querySelector('.pres-estado').textContent = `${CFG.nombre} · ${idx + 1} de ${secciones.length}`;
}

function siguiente() {
  if (idx < secciones.length - 1) mostrar(idx + 1);
  else if (paginaIndice() >= 0 && paginaIndice() < PAGINAS_VISIBLES.length - 1) irPagina(1);
  else salir();
}

function anterior() {
  if (idx > 0) mostrar(idx - 1);
  else irPagina(-1);
}

function alTeclear(e) {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const enCampo = e.target?.closest?.('input, select, textarea, [contenteditable="true"]');
  if (activo && e.key === 'Tab') {
    const enfocables = [...capa.querySelectorAll('button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), [tabindex="0"]')].filter((n) => n.getClientRects().length);
    const primero = enfocables[0], ultimo = enfocables[enfocables.length - 1];
    if (e.shiftKey && (document.activeElement === primero || !capa.contains(document.activeElement))) { e.preventDefault(); ultimo?.focus(); }
    else if (!e.shiftKey && (document.activeElement === ultimo || !capa.contains(document.activeElement))) { e.preventDefault(); primero?.focus(); }
    return;
  }
  if (activo && e.key === 'Escape') { e.preventDefault(); salir(); return; }
  if (enCampo || (activo && e.target?.closest?.('button') && [' ', 'Enter'].includes(e.key))) return;
  if (!activo) {
    if (e.key === 'p' || e.key === 'P') { e.preventDefault(); entrar(0); }
    return;
  }
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); siguiente(); }
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); anterior(); }
  else if (e.key === 'Home') { e.preventDefault(); mostrar(0); }
  else if (e.key === 'End') { e.preventDefault(); mostrar(secciones.length - 1); }
  else if (/^[0-9]$/.test(e.key)) {
    tecleo += e.key;
    clearTimeout(timerTecleo);
    timerTecleo = setTimeout(() => { tecleo = ''; }, 1500);
  } else if (e.key === 'Enter' && tecleo) {
    const n = Number(tecleo) - 1;
    tecleo = '';
    if (n >= 0 && n < secciones.length) mostrar(n);
  }
}

/* Una hoja de impresión por sección: página, sección, frecuencia y fuentes al pie (solo se ve al imprimir). */
function instalarHojaPie() {
  for (const { cfg: sec, nodo: nodoSec } of LAMINAS) {
    if (nodoSec.querySelector(':scope > .hoja-pie')) continue;
    const claves = (sec.filas || []).flat().map((c) => c.clave);
    const fuentes = [...new Set(claves.map((k) => CFG.tarjetas?.[k]?.fuente).filter(Boolean))];
    nodoSec.append(el('p', 'hoja-pie', `${NOMBRE_SITIO} · ${CFG.nombre} · ${sec.nombre}`
      + `${sec.frecuencia ? ` · ${sec.frecuencia}` : ''}${fuentes.length ? ` · Fuentes: ${fuentes.join('; ')}` : ''}`));
  }
}

/* Llamado por pagina.js al terminar de montar la página, con la config y las láminas ({ cfg, nodo, cuerpo,
   selectores } de cada sección): instala la hoja de impresión y, si la URL trae #presentar=sNN o venimos
   de otra página del recorrido, entra directo a esa lámina. */
export function alMontar(cfg, laminas) {
  CFG = cfg;
  LAMINAS = laminas;
  instalarHojaPie();
  let marca = null;
  try {
    marca = sessionStorage.getItem(CLAVE_SESION);
    sessionStorage.removeItem(CLAVE_SESION);
  } catch { /* storage bloqueado (modo privado): no hay recorrido en curso */ }
  const m = location.hash.match(/^#presentar(?:=(ultima|s?\d{1,2}))?$/);
  if ((m || marca) && !LAMINAS.length) {
    // página sin láminas (p. ej. B10): si venimos recorriendo, el recorrido sigue a la próxima
    if (marca) irPagina(marca === 'ultima' ? -1 : 1);
    return;
  }
  if (m) {
    const j = m[1] === 'ultima' ? LAMINAS.length - 1 : m[1] ? LAMINAS.findIndex((s) => s.nodo.id === `s${m[1].replace(/^s/, '').padStart(2, '0')}`) : 0;
    entrar(j < 0 ? 0 : j);
  } else if (marca) {
    entrar(marca === 'ultima' ? LAMINAS.length - 1 : 0);
  }
}

window.addEventListener('keydown', alTeclear);
window.addEventListener('fullscreenchange', () => {
  if (activo && pantallaCompletaPropia && !document.fullscreenElement) salir();
});

/* Imprimir desde la presentación: se sale antes (la impresión necesita las secciones en su lugar). */
window.addEventListener('beforeprint', () => {
  reanudarTrasImprimir = activo;
  if (activo) {
    const j = idx;
    salir();
    reanudarTrasImprimir = true;
    idx = j;
  }
});
window.addEventListener('afterprint', () => {
  if (reanudarTrasImprimir) { reanudarTrasImprimir = false; entrar(idx); }
});
