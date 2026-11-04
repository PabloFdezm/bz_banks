/* Arma cabecera, apertura, índice, tira, secciones, tarjetas y cierre desde la config de la
   página (§3 y §4 del general). Las 11 páginas comparten exactamente esta anatomía.
   Copia del pagina.js del macro. Los cambios de la F0 de bancos van marcados «bancos:». */
import { PAGINAS, MARCA } from './config.js';
import { cargarTodas, maxFecha, tablasExportadas } from './datos.js';
import { mmm_aa, trimestre, token } from './formato.js';
import { COMPONENTES, hay } from './charts.js';
import { COMPONENTES_BANCOS, formatear } from './charts_bancos.js'; // bancos:
import { leer, barra, enlazarCabecera, alCambiar, cargarBancos, bancoPorSlug } from './estado.js'; // bancos:
import * as presentacion from './presentacion.js'; // bancos:
Object.assign(COMPONENTES, COMPONENTES_BANCOS); // bancos: componentes propios de bancos
const REDIBUJAR = new Set(); // bancos: tarjetas [banco] que se vuelven a dibujar al cambiar el estado
let CFG = null; // bancos: configuración de la página montada
const TITULAR_BANCO = new Set(['B8']); // bancos: solo la ficha cambia su titular con el banco activo
const SECCIONES = new Map(); // bancos: número de sección → funciones que redibujan sus tarjetas (selector)
const SELECCION = new Map();
let FRANJA = null; // v3: nodo de la franja de indicadores, se redibuja al cambiar el banco // bancos: número de sección → { clave: valor } de sus selectores
alCambiar(() => { enlazarCabecera(); actualizarApertura(); for (const f of REDIBUJAR) f(); if (FRANJA && CFG?.franja?.some((k) => k.banco)) pintarFranja(CFG, FRANJA); }); // bancos: (v3: franja)

/* bancos: en la ficha, con banco activo, el titular es el banco y el rótulo lleva su modelo. */
function actualizarApertura() {
  if (!CFG || !TITULAR_BANCO.has(CFG.clave)) return;
  const b = bancoPorSlug(leer().banco);
  const titular = document.querySelector('.apertura-titular');
  const rotulo = document.querySelector('.apertura-rotulo');
  if (titular) titular.textContent = b ? b.nombre : t(`${CFG.clave}.titular`, CFG.nombre);
  if (rotulo && CFG.rotulo) rotulo.textContent = b ? `${CFG.rotulo} · ${b.modelo.toUpperCase()}` : CFG.rotulo;
}

let TEXTOS = {};

async function leerTextos() {
  try {
    const r = await fetch('/contenido/textos.json');
    if (r.ok) TEXTOS = await r.json();
  } catch { TEXTOS = {}; }
}

const t = (clave, defecto = '') => {
  const [pag, ...resto] = clave.split('.');
  let v = TEXTOS[pag];
  for (const k of resto) v = v?.[k];
  return (typeof v === 'string' && v.trim()) ? v.trim() : defecto;
};

function el(tag, clase, texto) {
  const n = document.createElement(tag);
  if (clase) n.className = clase;
  if (texto != null) n.textContent = texto;
  return n;
}

/* bancos: la portada (B0) vive en la raíz, así que su ruta es '' y el enlace no lleva «//». */
const enlace = (ruta) => (ruta ? `/${ruta}/` : '/');

function etiquetaFecha(valor, esTrimestral) {
  if (!valor) return '—';
  return esTrimestral ? trimestre(valor) : mmm_aa(valor);
}

/* ---------- 4.1 Cabecera ---------- */
function cabecera(cfg, ultimoDato) {
  // v2 (FARO): la cabecera es un menú lateral fijo; el nombre de la página va en la barra superior.
  const h = el('header', 'cabecera');
  const id = el('div', 'cabecera-identidad');
  const textos = el('div', 'cabecera-textos');
  textos.append(el('span', 'cabecera-marca', MARCA), el('span', 'cabecera-sub', 'IF.DATA · SGS · SCR'));
  id.append(textos);
  const nav = el('nav', 'cabecera-nav');
  nav.setAttribute('aria-label', 'Páginas');
  nav.append(el('span', 'cabecera-rotulo', 'PÁGINAS'));
  PAGINAS.filter((x) => !x.oculta).forEach((p, i) => { // bancos: MVP
    const a = document.createElement('a');
    a.className = 'pestana';
    a.dataset.base = enlace(p.ruta); // bancos: los enlaces conservan los parámetros del estado
    a.href = a.dataset.base + location.search; // bancos:
    a.append(el('span', 'pestana-num', String(i + 1).padStart(2, '0')), el('span', 'pestana-nombre', p.nombre));
    if (cfg.clave === p.clave) a.setAttribute('aria-current', 'page');
    nav.append(a);
  });
  const botonPresentar = el('button', 'boton-presentar', 'Presentar'); // bancos:
  botonPresentar.type = 'button'; // bancos:
  botonPresentar.addEventListener('click', () => presentacion.entrar(0)); // bancos:
  nav.append(botonPresentar); // bancos:
  h.append(id, nav);
  if (ultimoDato) h.append(el('span', 'cabecera-ultimo', `Último dato ${ultimoDato}`));
  return h;
}

/* ---------- 4.3 Apertura ---------- */
function apertura(cfg) {
  const s = el('section', 'apertura');
  const izq = el('div', 'apertura-texto');
  if (cfg.rotulo) izq.append(el('span', 'apertura-rotulo', cfg.rotulo));
  izq.append(el('h1', 'apertura-titular', t(`${cfg.clave}.titular`, cfg.nombre)));
  const intro = t(`${cfg.clave}.intro`);
  if (intro) izq.append(el('p', 'apertura-intro', intro));
  const nav = el('nav', 'indice');
  nav.setAttribute('aria-label', 'En esta página');
  nav.append(el('span', 'indice-rotulo', 'EN ESTA PÁGINA'));
  for (const sec of cfg.secciones) {
    const a = document.createElement('a');
    a.className = 'indice-item';
    a.href = `#s${sec.numero}`;
    a.append(el('span', 'indice-num', sec.numero), document.createTextNode(sec.nombre));
    nav.append(a);
  }
  s.append(izq, nav);
  return s;
}

/* ---------- v3 · Franja de indicadores (diseño FARO) ----------
   Cinco cifras con su serie. Declarativa: cada indicador dice de qué tabla y fila sale, qué columna es
   el valor y cuál el cambio trimestral; aquí solo se filtra, se toma la última fila y se dibuja.
   `vaciar` deja huecos (períodos que cruzan un quiebre de definición) y se marcan en arena. */
const NS = 'http://www.w3.org/2000/svg';
function svgEl(tag, attrs) { const n = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v); return n; }
function tonoDe(k, delta) {
  if (delta == null || Number.isNaN(delta) || Math.abs(delta) < 1e-9 || !k.tono || k.tono === 'neutro') return 'neutro';
  const sube = delta > 0;
  if (k.tono === 'mejora_sube') return sube ? 'mejora' : 'deterioro';
  if (k.tono === 'mejora_baja') return sube ? 'deterioro' : 'mejora';
  return 'neutro';
}
function serieSvg(valores, tono, huecos) {
  const svg = svgEl('svg', { viewBox: '0 0 300 46', preserveAspectRatio: 'none', class: `franja-serie tono-${tono}`, 'aria-hidden': 'true' });
  const nums = valores.filter((v) => v != null);
  if (nums.length < 2) return svg;
  const min = Math.min(...nums), max = Math.max(...nums), r = max - min || 1, n = valores.length;
  const px = (i) => (i * 300) / (n - 1), py = (v) => 42 - ((v - min) / r) * 36;
  for (const [i0, i1] of huecos) svg.append(svgEl('rect', { x: Math.max(0, px(i0) - 300 / (2 * (n - 1))), y: 0, width: (i1 - i0 + 1) * 300 / (n - 1), height: 46, class: 'franja-hueco' }));
  let tramo = [];
  const cerrar = () => {
    if (tramo.length > 1) {
      const pts = tramo.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
      svg.append(svgEl('polygon', { points: `${tramo[0][0].toFixed(1)},46 ${pts} ${tramo[tramo.length - 1][0].toFixed(1)},46`, class: 'franja-area' }));
      svg.append(svgEl('polyline', { points: pts, class: 'franja-linea' }));
    }
    tramo = [];
  };
  valores.forEach((v, i) => { if (v == null) cerrar(); else tramo.push([px(i), py(v)]); });
  cerrar();
  svg.append(svgEl('line', { x1: 300, x2: 300, y1: 0, y2: 46, class: 'franja-hoy' }));
  return svg;
}
async function pintarFranja(cfg, nodo) {
  const tablas = [...new Set(cfg.franja.map((k) => (typeof k.tabla === 'function' ? null : k.tabla)).filter(Boolean))];
  let d = {};
  try { d = await cargarTodas(tablas); } catch { d = {}; }
  const banco = bancoPorSlug(leer().banco);
  const celdas = [];
  for (const k of cfg.franja) {
    const c = el('div', 'franja-celda');
    let filas = (d[k.tabla] || []).filter((f) => Object.entries(k.filtro || {}).every(([col, v]) => f[col] === v));
    if (k.banco) filas = banco?.cod ? filas.filter((f) => f.cod_inst === banco.cod) : [];
    const col = k.orden || 'fecha';
    filas = filas.filter((f) => f[k.valor || 'valor'] != null).sort((a, b) => (a[col] < b[col] ? -1 : a[col] > b[col] ? 1 : 0)).slice(-(k.n || 13));
    const cab = el('div', 'franja-cab');
    cab.append(el('span', 'franja-rotulo', k.rotulo));
    const u = filas[filas.length - 1];
    if (!u) {
      cab.append(el('span', 'franja-corte', ''));
      c.append(cab, el('span', 'franja-valor franja-sin', k.banco && !banco ? 'Elige un banco' : '—'));
      celdas.push(c);
      continue;
    }
    const corte = u.trimestre || trimestre(u.fecha);
    cab.append(el('span', 'franja-corte', k.nota ? `${corte} · ${k.nota}` : corte));
    const delta = u[k.delta || 'd_tt'];
    const deltaPp = delta == null ? null : delta * (k.escalaDelta ?? 100);
    const tono = tonoDe(k, deltaPp);
    const pie = el('div', 'franja-pie');
    pie.append(
      el('span', `franja-delta tono-${tono}`, deltaPp == null ? '—' : (Math.abs(deltaPp) < 0.05 ? `0,0 ${k.unidadDelta || 'pp'}` : `${deltaPp > 0 ? '+' : '−'}${Math.abs(deltaPp).toFixed(1).replace('.', ',')} ${k.unidadDelta || 'pp'}`)),
      el('span', 'franja-base', 'TRIM.'),
      el('span', 'franja-ventana', k.pie || `${filas.length} trim.`),
    );
    const vaciar = new Set(k.vaciar || []);
    const valores = filas.map((f) => (vaciar.has(f.periodo) ? null : f[k.valor || 'valor']));
    const huecos = [];
    valores.forEach((v, i) => { if (v == null && vaciar.size) { if (huecos.length && huecos[huecos.length - 1][1] === i - 1) huecos[huecos.length - 1][1] = i; else huecos.push([i, i]); } });
    c.append(cab, el('span', 'franja-valor', formatear(u[k.valor || 'valor'], k.formato || 'pct')), pie, serieSvg(valores, tono, huecos));
    celdas.push(c);
  }
  nodo.replaceChildren(...celdas);
}
function franja(cfg) {
  const n = el('div', 'franja');
  n.setAttribute('role', 'region');
  n.setAttribute('aria-label', 'Indicadores principales');
  FRANJA = n;
  return pintarFranja(cfg, n).then(() => n);
}

/* ---------- 4.4 Tira «Qué cambió» ---------- */
function queCambio(cfg) {
  const texto = t(`${cfg.clave}.que_cambio`);
  const w = el('div', 'que-cambio-envoltura');
  if (!texto) { w.hidden = true; return w; }
  const d = el('div', 'que-cambio');
  d.append(el('span', 'que-cambio-rotulo', 'QUÉ CAMBIÓ'), el('p', 'que-cambio-texto', texto));
  w.append(d);
  return w;
}

/* ---------- riel ---------- */
/* bancos: color y flecha de un cambio según el signo de la métrica (§5.3); el umbral lo fija armar() */
function colorDelta(delta, signo) {
  if (delta == null || Number.isNaN(delta) || delta === 0) return 'var(--texto-3)';
  const sube = delta > 0;
  if (signo === 'mejora_sube') return sube ? 'var(--mejor)' : 'var(--peor)';
  if (signo === 'mejora_baja') return sube ? 'var(--peor)' : 'var(--mejor)';
  return 'var(--texto-2)';
}

function flechaDelta(delta) {
  if (delta == null || Number.isNaN(delta) || delta === 0) return '—';
  return delta > 0 ? '▲' : '▼';
}

/* KPI del riel: cifra, nota y flechas de 1 y 4 trimestres. Lo calcula armar(); aquí solo se dibuja. */
function bloqueKpi(b, r) {
  const bl = el('div', 'riel-bloque riel-kpi');
  bl.append(el('span', 'riel-bloque-rotulo', b.rotulo || 'INDICADOR'));
  if (!r || r.enPreparacion) {
    bl.append(el('span', 'riel-bloque-nota', `En preparación: ${r?.enPreparacion || 'sin función de cálculo'}`));
    return bl;
  }
  bl.append(el('span', 'riel-kpi-cifra', typeof r.cifra === 'number' ? formatear(r.cifra, r.formato) : String(r.cifra ?? '—')));
  const flechas = el('span', 'riel-kpi-flechas');
  for (const [etiqueta, delta] of [['1 trim.', r.cambio1], ['4 trim.', r.cambio4]]) {
    const f = el('span', 'riel-kpi-flecha', `${flechaDelta(delta)} ${etiqueta}`);
    f.style.color = colorDelta(delta, r.signo);
    flechas.append(f);
  }
  bl.append(flechas);
  if (r.nota) bl.append(el('span', 'riel-bloque-nota', r.nota));
  return bl;
}

/* Selector de óptica de la sección: un botón por opción; al elegir, cambia solo las tarjetas de su sección. */
function bloqueSelector(b, valorActual, alElegir) {
  const bl = el('div', 'riel-bloque riel-selector');
  bl.append(el('span', 'riel-bloque-rotulo', b.rotulo || 'VER POR'));
  const grupo = el('div', 'riel-seg');
  grupo.setAttribute('role', 'group');
  grupo.setAttribute('aria-label', b.rotulo || 'Selector');
  for (const op of b.opciones || []) {
    const btn = el('button', 'riel-seg-op', op.nombre);
    btn.type = 'button';
    btn.setAttribute('aria-pressed', String(op.valor === valorActual));
    btn.addEventListener('click', () => {
      // v3: marca la opción en este mismo grupo (en presentación el grupo vive en la lámina, fuera del riel)
      for (const o of grupo.children) o.setAttribute('aria-pressed', String(o === btn));
      alElegir(b.clave || 'seleccion', op.valor);
    });
    grupo.append(btn);
  }
  bl.append(grupo);
  return bl;
}

function riel(cfg, sec, datosSeccion, kpis = new Map(), alElegir = () => {}) {
  const r = el('div', 'riel');
  r.append(el('span', 'riel-numero', sec.numero));
  r.append(el('h2', 'riel-nombre', sec.nombre));
  if (sec.frecuencia) {
    const ult = sec.ultimo && datosSeccion ? etiquetaFecha(datosSeccion, sec.trimestral) : null;
    r.append(el('span', 'riel-frecuencia', ult ? `${sec.frecuencia} · último dato ${ult}` : sec.frecuencia));
  }
  const preg = t(`${cfg.clave}.secciones.${sec.numero}`, '');
  if (preg) r.append(el('p', 'riel-pregunta', preg));
  else if (sec.pregunta) { const p = el('p', 'riel-pregunta por-defecto', sec.pregunta); r.append(p); }

  for (const b of sec.riel || []) {
    if (b.tipo === 'dato') {
      const bl = el('div', 'riel-bloque');
      bl.append(el('span', 'riel-bloque-rotulo', b.rotulo || 'DATO DE LA SECCIÓN'));
      if (b.cifra != null && b.cifra !== '') bl.append(el('span', 'riel-bloque-cifra', String(b.cifra)));
      if (b.nota) bl.append(el('span', 'riel-bloque-nota', b.nota));
      r.append(bl);
    } else if (b.tipo === 'texto') {
      r.append(el('p', 'riel-nota', b.texto));
    } else if (b.tipo === 'glosario') {
      const bl = el('div', 'riel-bloque');
      bl.append(el('span', 'riel-bloque-rotulo', b.rotulo || 'GLOSARIO'));
      bl.append(el('span', 'riel-bloque-nota', b.texto));
      r.append(bl);
    } else if (b.tipo === 'kpi') {
      r.append(bloqueKpi(b, kpis.get(b)));
    } else if (b.tipo === 'selector') {
      const clave = b.clave || 'seleccion';
      r.append(bloqueSelector(b, (SELECCION.get(sec.numero) || {})[clave], alElegir));
    }
  }
  return r;
}

/* ---------- tarjeta ---------- */
const BLOQUEADOS = new Set(['FALTA', 'TERCEROS']);

/* bancos (F0): toda tarjeta sin `armar` va «en preparación» con el motivo que le toca por su
   estado del esqueleto (§7 del spec de bancos). En la ola 2 cada `armar` la reemplaza. */
const MOTIVOS = {
  LISTO: 'dato en construcción',
  DERIVAR: 'dato en construcción',
  FALTA: 'fuente no incorporada',
  REF: 'disponible con el próximo REF',
};

function motivoEstado(estado) {
  return MOTIVOS[String(estado || '').toUpperCase()] || MOTIVOS.LISTO;
}

function armarLeyenda(items) {
  const l = el('div', 'leyenda');
  for (const it of items) {
    const i = el('span', 'leyenda-item');
    if (it.color) {
      const tr = el('span', it.discontinua ? 'leyenda-trazo discontinua' : 'leyenda-trazo');
      if (it.discontinua) tr.style.color = it.color; else tr.style.background = it.color;
      i.append(tr);
    }
    i.append(document.createTextNode(it.nombre));
    l.append(i);
  }
  return l;
}

function tarjetaShell(cfgTar, alto) {
  const f = el('figure', ['tarjeta', cfgTar.plana && 'tarjeta-plana', cfgTar.estandar && 'tabla-estandar'].filter(Boolean).join(' ')); // v3: sin borde, el título de la sección manda
  if (typeof alto === 'number') f.style.height = `${alto}px`;   // bancos: alto «auto» no se fija
  if (typeof alto === 'number') f.style.setProperty('--alto', `${alto}px`); // 4-nov: lo usa la regla de pantallas angostas
  const cab = el('div', 'tarjeta-cabecera');
  const izq = el('div');
  izq.append(el('h3', 'tarjeta-titulo', cfgTar.titulo || ''));
  if (cfgTar.sub) izq.append(el('p', 'tarjeta-sub', cfgTar.sub));
  cab.append(izq);
  if (cfgTar.pastilla) {
    const p = el('span', 'pastilla');
    p.dataset.pastilla = '1';
    cab.append(p);
  }
  f.append(cab);
  if (cfgTar.leyenda && cfgTar.leyenda.length) f.append(armarLeyenda(cfgTar.leyenda));
  const zona = el('div', 'tarjeta-zona');
  f.append(zona);
  if (cfgTar.nota) f.append(el('p', 'tarjeta-nota', cfgTar.nota));
  if (cfgTar.fuente) f.append(el('p', 'tarjeta-pie', `Fuente: ${cfgTar.fuente}`));
  return { figura: f, zona };
}

function enPreparacion(zona, motivo) {
  zona.replaceChildren(el('div', 'preparacion', `En preparación: ${motivo}`));
  zona.closest('.tarjeta')?.classList.add('tarjeta-vacia'); // v2: se oculta (CSS) y la fila se reparte
}

/* v2: en cada fila, las tarjetas visibles se reparten las 9 columnas; una sección sin ninguna se oculta. */
function repartirFilas(s, filas) {
  let visiblesSeccion = 0;
  for (const figs of filas) {
    const vis = figs.filter((f) => !f.classList.contains('tarjeta-vacia'));
    visiblesSeccion += vis.length;
    if (!vis.length || vis.length === figs.length) continue;
    const base = Math.floor(9 / vis.length);
    vis.forEach((f, i) => { f.style.gridColumn = `span ${i === 0 ? 9 - base * (vis.length - 1) : base}`; });
  }
  if (!visiblesSeccion) s.classList.add('seccion-vacia');
}

/* bancos: libera las instancias de ECharts de una tarjeta antes de volver a dibujarla */
function liberar(zona) {
  for (const n of zona.querySelectorAll('*')) window.echarts?.getInstanceByDom(n)?.dispose();
}

// 4-nov: carga explícita de las fuentes antes de dibujar (máx. 3 s; si no llegan se dibuja igual)
const FUENTES = document.fonts?.load
  ? Promise.race([Promise.all(['400 12px "IBM Plex Sans"', '600 12px "IBM Plex Sans"', '400 12px "IBM Plex Mono"', '700 12px "Bricolage Grotesque"'].map((f) => document.fonts.load(f))), new Promise((r) => setTimeout(r, 3000))]).catch(() => null)
  : Promise.resolve();

async function dibujar(clave, cfgTar, zona, figura, numeroSeccion) {
  await FUENTES; // 4-nov: ECharts mide las etiquetas con la fuente real (antes cortaba nombres)
  // 4-nov: ECharts mide el texto con su fuente por defecto pero el SVG lo dibuja con la de la página (Plex):
  // se fija la misma fuente en todos los gráficos para que medida y dibujo coincidan.
  if (window.echarts && !window.echarts.__fuenteFija) {
    const init = window.echarts.init.bind(window.echarts);
    window.echarts.init = (...a) => { const ch = init(...a); ch.setOption({ textStyle: { fontFamily: "'IBM Plex Sans', 'Segoe UI', sans-serif" } }); return ch; };
    window.echarts.__fuenteFija = true;
  }
  // bancos: las tarjetas de una sección con selector se vuelven a dibujar al cambiarlo (solo esa sección)
  if (numeroSeccion && !zona._seccionRegistrada) {
    zona._seccionRegistrada = true;
    SECCIONES.get(numeroSeccion)?.add(() => { liberar(zona); zona.replaceChildren(); dibujar(clave, cfgTar, zona, figura, numeroSeccion); });
  }
  // bancos: tarjetas [banco] se vuelven a dibujar cuando cambia el estado (solo filtran y resaltan)
  if (cfgTar.banco && !zona._registrada) {
    zona._registrada = true;
    REDIBUJAR.add(() => { liberar(zona); zona.replaceChildren(); dibujar(clave, cfgTar, zona, figura); });
  }
  if (typeof cfgTar.armar !== 'function') { enPreparacion(zona, motivoEstado(cfgTar.estado)); return; }
  if (BLOQUEADOS.has((cfgTar.estado || '').toUpperCase())) {
    enPreparacion(zona, cfgTar.motivo || 'sin dato en el modelo');
    return;
  }
  if (!hay(cfgTar.componente)) {
    enPreparacion(zona, `componente «${cfgTar.componente}» todavía no implementado`);
    return;
  }
  figura.classList.remove('tarjeta-vacia'); // v2
  zona.append(el('div', 'esqueleto'));
  let d;
  try {
    d = await cargarTodas(cfgTar.datos || []);
  } catch (e) {
    zona.replaceChildren(el('div', 'error-dato', `No se pudieron cargar los datos: ${e.message}`));
    return;
  }
  let entrada;
  try {
    entrada = cfgTar.armar ? await cfgTar.armar(d, { clave, ...leer(), seleccion: seleccionDe(numeroSeccion), codBanco: bancoPorSlug(leer().banco)?.cod || null, grupoBanco: bancoPorSlug(leer().banco)?.modelo || null }) : null; // bancos: armar recibe el estado (banco, optica, grupo, trimestre) y el selector de su sección
  } catch (e) {
    zona.replaceChildren(el('div', 'error-dato', `Error al armar la tarjeta: ${e.message}`));
    return;
  }
  if (!entrada) { enPreparacion(zona, cfgTar.motivo || 'la función armar() no devolvió datos'); return; }
  if (entrada.enPreparacion) { enPreparacion(zona, entrada.enPreparacion); return; }

  const cont = el('div');
  cont.style.cssText = 'position:absolute;inset:0';
  if (!['tabla', 'comparador', 'percentiles', 'cascada_doble', 'apilada_100', 'pesas', 'barras_ic', 'small_multiples', 'small_multiples_bancos', 'barras_simple', 'mix_banco', 'puertas', 'tabla_estandar'].includes(cfgTar.componente)) { // bancos: los HTML no llevan role=img
    cont.setAttribute('role', 'img');
    cont.setAttribute('aria-label', entrada.ariaLabel || cfgTar.titulo || clave);
  }
  zona.replaceChildren(cont);
  const fig = zona.closest('figure');
  if (fig && 'leyenda' in entrada) { // 3-nov: la leyenda depende de la vista elegida ([] = la dibuja el gráfico)
    fig.querySelector(':scope > .leyenda')?.remove();
    if (entrada.leyenda && entrada.leyenda.length) fig.insertBefore(armarLeyenda(entrada.leyenda), zona);
  }
  const fn = COMPONENTES[entrada.componente || cfgTar.componente];
  const chart = fn(cont, entrada, { clave });
  if (chart && zona.closest('.pres-lamina')) window.__escalaTextoPres?.(zona); // 4-nov: redibujo dentro de una lámina
  if (cfgTar.pastilla && entrada.pastilla) {
    const p = figura.querySelector('[data-pastilla]');
    if (p) {
      p.replaceChildren(document.createTextNode('Último '), Object.assign(document.createElement('b'), { textContent: entrada.pastilla.valor }), document.createTextNode(` · ${entrada.pastilla.fecha}`));
    }
  }
  if (chart) {
    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(cont);
  }
}

/* ---------- 4.5 Secciones ---------- */
/* bancos: selección por sección (SELECCION) y helpers del selector y de los KPI del riel */
function seleccionDe(numero) {
  return { ...(SELECCION.get(numero) || {}) };
}

/* Al elegir una opción, se redibujan solo las tarjetas de su sección y se recalcula su riel. */
function elegirSeleccion(numero, clave, valor, pintarRiel) {
  SELECCION.set(numero, { ...(SELECCION.get(numero) || {}), [clave]: valor });
  for (const redibujar of SECCIONES.get(numero) || []) redibujar();
  pintarRiel();
}

function seccion(cfg, sec) {
  const s = el('section', sec.apilada ? 'seccion seccion-apilada' : 'seccion'); // v3b: gráfico arriba, tabla abajo
  s.id = `s${sec.numero}`;
  const tablas = [];
  if (sec.ultimo) tablas.push(sec.ultimo.tabla);
  const kpis = (sec.riel || []).filter((b) => b.tipo === 'kpi' && typeof b.armar === 'function');
  const tablasKpi = [...new Set(kpis.flatMap((k) => k.datos || []))];
  for (const b of sec.riel || []) { // bancos: valor inicial de cada selector (el primero o el declarado)
    if (b.tipo !== 'selector') continue;
    const clave = b.clave || 'seleccion';
    const previo = SELECCION.get(sec.numero) || {};
    if (previo[clave] === undefined) SELECCION.set(sec.numero, { ...previo, [clave]: b.defecto ?? b.opciones?.[0]?.valor });
  }
  SECCIONES.set(sec.numero, new Set());
  return cargarTodas(tablas).then(async (d) => {
    let ult = null;
    if (sec.ultimo && d[sec.ultimo.tabla]) ult = maxFecha(d[sec.ultimo.tabla], sec.ultimo.columna || 'fecha');
    // las tablas de los KPI se cargan aparte: si una falla, ese KPI va en preparación y la sección sigue
    const dk = tablasKpi.length ? await cargarTodas(tablasKpi).catch(() => ({})) : {};
    const pintarRiel = async () => {
      const resultados = new Map();
      for (const k of kpis) {
        try {
          resultados.set(k, await k.armar({ ...d, ...dk }, { clave: cfg.clave, ...leer(), seleccion: seleccionDe(sec.numero) }));
        } catch (e) {
          resultados.set(k, { enPreparacion: `error al armar: ${e.message}` });
        }
      }
      const nuevo = riel(cfg, sec, ult, resultados, (clave, valor) => elegirSeleccion(sec.numero, clave, valor, pintarRiel));
      const viejo = s.querySelector(':scope > .riel');
      if (viejo) viejo.replaceWith(nuevo); else s.prepend(nuevo);
    };
    await pintarRiel();
    const cuerpo = el('div', sec.apilada ? 'cuerpo apilada' : 'cuerpo');
    if (sec.altoTabla) cuerpo.style.setProperty('--alto-tabla', `${sec.altoTabla}px`);
    const pendientes = [];
    const figsPorFila = []; // v2
    for (const fila of sec.filas || []) {
      const figs = []; figsPorFila.push(figs); // v2
      // bancos: el alto de la fila sale de las tarjetas que lo fijan; `auto` no impone alto.
      const altos = fila.map((c) => (typeof c.alto === 'number' ? c.alto : 0));
      const alto = Math.max(0, ...altos) || null;
      for (const c of fila) {
        const cfgTar = cfg.tarjetas?.[c.clave] || { titulo: c.clave, componente: '—', estado: 'FALTA', motivo: 'la clave no está en cfg.tarjetas' };
        const { figura, zona } = tarjetaShell(cfgTar, typeof c.alto === 'number' ? c.alto : alto);
        figura.dataset.clave = c.clave; // 4-nov: número de tarjeta visible para revisar (canvas, capturas)
        figura.style.gridColumn = `span ${c.ancho}`;
        figs.push(figura); // v2
        cuerpo.append(figura);
        pendientes.push(dibujar(c.clave, cfgTar, zona, figura, sec.numero));
      }
    }
    s.append(cuerpo);
    // 4-nov: la sección se muestra de inmediato; antes se esperaba a que TODAS sus tarjetas cargaran datos
    // (con bk_grupo de 12 MB, Calidad/Rentabilidad/Ficha quedaban en blanco 20–30 s)
    Promise.all(pendientes).then(() => repartirFilas(s, figsPorFila));
    return s;
  });
}

/* ---------- 4.7 Cierre ---------- */
function cierre(cfg) {
  /* bancos: en F0 no hay fuentes ni «cómo leer» (los fija el esqueleto §B10); no se pinta vacío. */
  if (!cfg.fuentes && !(cfg.comoLeer || []).length) return null;
  const c = el('footer', 'cierre');
  const f = el('div', 'cierre-bloque');
  f.append(el('span', 'cierre-rotulo', 'FUENTES'), el('p', 'cierre-texto', cfg.fuentes || ''));
  const l = el('div', 'cierre-bloque como-leer');
  l.append(el('span', 'cierre-rotulo', 'CÓMO LEER ESTA PÁGINA'));
  for (const p of cfg.comoLeer || []) l.append(el('p', 'cierre-texto', p));
  c.append(f, l);
  return c;
}

/* ---------- montar una página ---------- */
export async function montar(cfg) {
  await leerTextos();
  CFG = cfg; // bancos:
  await cargarBancos(await tablasExportadas()); // bancos: lista de bancos desde bk_banco si el manifiesto la trae
  const app = document.getElementById('app');
  app.replaceChildren();
  let ultimoDato = null;
  if (cfg.ultimoDato) {
    try {
      const d = await cargarTodas([cfg.ultimoDato.tabla]);
      ultimoDato = etiquetaFecha(maxFecha(d[cfg.ultimoDato.tabla], cfg.ultimoDato.columna || 'fecha'), cfg.trimestral);
    } catch { ultimoDato = null; }
  }
  app.append(cabecera(cfg, ultimoDato));
  const b = barra(); // bancos: barra de banco activo (spec §3)
  const titulo = el('div', 'barra-titulo'); // v2: el título de la página vive aquí, una sola vez
  titulo.append(el('span', 'barra-titulo-rotulo', cfg.rotulo || 'BANCOS BRASIL'), el('span', 'barra-titulo-nombre', cfg.nombre));
  b.prepend(titulo);
  if (cfg.usaBanco === false) b.classList.add('sin-banco'); // v3: la Portada no usa banco activo
  const presentarBarra = el('button', 'barra-presentar', 'Presentar ▸'); // v3: a la vista, en la barra superior
  presentarBarra.type = 'button';
  presentarBarra.title = 'Cada sección es una lámina · tecla P';
  presentarBarra.addEventListener('click', () => presentacion.entrar(0));
  b.append(presentarBarra);
  app.append(b);
  if (cfg.franja?.length) app.append(await franja(cfg)); // v3
  const cont = el('div', 'contenedor');
  if (!cfg.franja?.length) cont.append(apertura(cfg));
  cont.append(queCambio(cfg));
  for (const sec of cfg.secciones) cont.append(await seccion(cfg, sec));
  const pie = cierre(cfg);
  if (pie) cont.append(pie);
  app.append(cont);
  document.title = `${cfg.nombre} · Bancos Brasil`;
  actualizarApertura(); // bancos: titular y rótulo según el banco activo
  presentacion.alMontar(); // bancos: hoja de impresión y entrada directa a presentación (#presentar=sNN)
}

/* ---------- 4.6 Portada ---------- */
export async function montarPortada(cfgs) {
  await leerTextos();
  const app = document.getElementById('app');
  app.replaceChildren();
  const h = el('header', 'cabecera');
  const id = el('div', 'cabecera-identidad');
  id.append(el('span', 'cabecera-marca', 'MONITOR BRASIL'), el('span', 'cabecera-nombre', 'Monitor Brasil'));
  const nav = el('nav', 'cabecera-nav');
  nav.setAttribute('aria-label', 'Páginas');
  for (const p of PAGINAS.filter((x) => !x.oculta)) { // bancos: MVP
    const a = document.createElement('a');
    a.className = 'pestana'; a.href = enlace(p.ruta); a.textContent = p.nombre;
    nav.append(a);
  }
  h.append(id, nav);
  app.append(h);

  const cont = el('div', 'contenedor');
  const ap = el('section', 'apertura');
  const izq = el('div', 'apertura-texto');
  izq.append(el('h1', 'portada-titular', t('PORTADA.titular', 'Monitor Brasil')));
  const intro = t('PORTADA.intro');
  if (intro) izq.append(el('p', 'apertura-intro', intro));
  ap.append(izq);
  cont.append(ap);

  const g = el('div', 'portada-grilla');
  for (const cfg of cfgs) {
    const a = document.createElement('a');
    a.className = 'portada-tarjeta';
    a.href = `/${cfg.ruta}/`;
    a.append(el('h2', 'portada-nombre', cfg.nombre));
    a.append(el('p', 'portada-pregunta', t(`${cfg.clave}.idea`, cfg.idea || '')));
    let dato = '—';
    if (cfg.ultimoDato) {
      try {
        const d = await cargarTodas([cfg.ultimoDato.tabla]);
        dato = etiquetaFecha(maxFecha(d[cfg.ultimoDato.tabla], cfg.ultimoDato.columna || 'fecha'), cfg.trimestral);
      } catch { dato = '—'; }
    }
    a.append(el('span', 'portada-dato', `Último dato ${dato}`), el('span', 'portada-ver', 'Ver página →'));
    g.append(a);
  }
  cont.append(g);
  app.append(cont);
  document.title = 'Bancos Brasil';
  void token;
}
