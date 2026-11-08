/* Arma cabecera, apertura, índice, tira, secciones, tarjetas y cierre desde la config de la
   página (§3 y §4 del general). Las 11 páginas comparten exactamente esta anatomía.
   Copia del pagina.js del macro. Los cambios de la F0 de bancos van marcados «bancos:». */
import { PAGINAS, MARCA } from './config.js';
import { cargarTodas, maxFecha, tablasExportadas } from './datos.js';
import { mmm_aa, trimestre, token } from './formato.js';
import { COMPONENTES, hay } from './charts.js';
import { COMPONENTES_BANCOS, formatear } from './charts_bancos.js'; // bancos:
import { leer, barra, enlazarCabecera, alCambiar, cargarBancos, bancoPorSlug, leerSeleccion, fijarSeleccion, busquedaCompartida } from './estado.js'; // bancos:
import { crearColaVisual } from './fluidez.js';
import * as presentacion from './presentacion.js'; // bancos:
Object.assign(COMPONENTES, COMPONENTES_BANCOS); // bancos: componentes propios de bancos
const COLA_VISUAL = crearColaVisual();
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
  const tituloVisible = document.querySelector('.barra-titulo-nombre');
  if (tituloVisible) tituloVisible.textContent = b ? b.nombre : CFG.nombre;
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
    a.href = a.dataset.base + busquedaCompartida(); // bancos: (sin los selectores de esta página)
    a.append(el('span', 'pestana-num', String(i + 1).padStart(2, '0')), el('span', 'pestana-nombre', p.nombre));
    if (cfg.clave === p.clave) a.setAttribute('aria-current', 'page');
    nav.append(a);
  });
  h.append(id, nav);
  h.append(el('span', 'cabecera-ultimo', ultimoDato ? `Último dato ${ultimoDato}` : 'Fuentes: BCB · IF.Data · SGS · SCR'));
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
  const version = nodo._version = (nodo._version || 0) + 1;
  // con cifras ya pintadas se conservan mientras llegan las nuevas; tras un error, el reintento se ve
  if (conResultado(nodo)) marcar(nodo, 'actualizando');
  else if (nodo.dataset.estado !== 'cargando') estadoDatos(nodo, 'cargando', 'Cargando indicadores…', '');
  const resultados = await Promise.allSettled(tablas.map(async (tabla) => cargarTodas([tabla])));
  if (nodo._version !== version) return;
  const d = Object.assign({}, ...resultados.filter((r) => r.status === 'fulfilled').map((r) => r.value));
  if (tablas.length && resultados.every((r) => r.status === 'rejected')) {
    estadoDatos(nodo, 'error', 'No pudimos cargar los indicadores', 'Revisa tu conexión y vuelve a intentarlo.', () => pintarFranja(cfg, nodo));
    return;
  }
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
      c.append(cab, el('span', 'franja-valor franja-sin', k.banco && !banco ? 'Elige un banco' : 'Sin datos'));
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
  marcar(nodo, 'lista');
}
function franja(cfg) {
  const n = el('div', 'franja');
  n.setAttribute('role', 'region');
  n.setAttribute('aria-label', 'Indicadores principales');
  FRANJA = n;
  estadoDatos(n, 'cargando', 'Cargando indicadores…', '');
  pintarFranja(cfg, n);
  return n;
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

/* ---------- Ciclo de vida de un nodo con datos (tarjeta, franja, hueco de sección) ----------
   Una sola máquina de estados, explícita en data-estado (en la <figure> si es tarjeta; si no, en el nodo).
   La leen el CSS, herramientas/verificar_f1.py y cualquier agente que inspeccione el DOM:
     cargando ─────────────► lista | en-preparacion | requiere-banco | error
     lista ─► actualizando ─► lista | en-preparacion | requiere-banco | error   (conserva el resultado anterior)
     en-preparacion | requiere-banco | error ─► cargando   (reintento, cambio de banco o de selector)
   aria-busy se deriva del estado: nadie lo fija a mano. */
const ESTADOS = new Set(['cargando', 'actualizando', 'lista', 'en-preparacion', 'requiere-banco', 'error']);
const TRANSITORIOS = new Set(['cargando', 'actualizando']);
const portador = (zona) => zona.closest('figure.tarjeta') || zona;
const conResultado = (zona) => ['lista', 'actualizando'].includes(portador(zona).dataset.estado);

function marcar(zona, estado) {
  if (!ESTADOS.has(estado)) throw new Error(`estado desconocido: ${estado}`);
  const nodo = portador(zona);
  if (estado === 'actualizando' && !conResultado(zona)) console.warn(`transición inválida ${nodo.dataset.estado} → actualizando`, nodo);
  nodo.dataset.estado = estado;
  zona.setAttribute('aria-busy', String(TRANSITORIOS.has(estado)));
}

function estadoDatos(zona, estado, titulo, detalle, reintentar = null) {
  clearTimeout(zona._cargaTimer);
  zona.classList.remove('actualizacion-visible');
  liberar(zona);
  const mensaje = el('div', 'estado-datos od-stack');
  mensaje.setAttribute('role', 'status');
  mensaje.append(el('strong', '', titulo));
  if (detalle) mensaje.append(el('p', '', detalle));
  if (reintentar) {
    const boton = el('button', '', 'Reintentar');
    boton.type = 'button';
    boton.addEventListener('click', reintentar);
    mensaje.append(boton);
  }
  zona.replaceChildren(mensaje);
  marcar(zona, estado);
}

/* requiereBanco lo declara armar() ({ enPreparacion, requiereBanco: true }); antes se adivinaba del texto
   del motivo y «elija un banco» (Ficha) quedaba como «Sin datos disponibles», sin botón. */
function enPreparacion(zona, motivo, requiereBanco = false) {
  const detalle = /función|componente|armar|implementad|error/i.test(motivo || '')
    ? 'Este indicador todavía no está disponible. Puedes consultar los demás indicadores de la página.'
    : (motivo || 'No hay observaciones disponibles para esta selección.');
  estadoDatos(zona, requiereBanco ? 'requiere-banco' : 'en-preparacion',
    requiereBanco ? 'Elige un banco para continuar' : 'Sin datos disponibles', detalle);
  if (requiereBanco && document.getElementById('banco-activo')) {
    const boton = el('button', '', 'Elegir banco');
    boton.type = 'button';
    boton.addEventListener('click', () => document.getElementById('banco-activo')?.focus());
    zona.firstElementChild.append(boton);
  }
}

/* bancos: libera las instancias de ECharts de una tarjeta antes de volver a dibujarla */
function liberar(zona) {
  zona._resizeObserver?.disconnect();
  zona._resizeObserver = null;
  for (const n of zona.querySelectorAll('*')) {
    const chart = window.echarts?.getInstanceByDom(n);
    if (chart) { COLA_VISUAL.quitar(chart); chart.dispose(); }
  }
}

// 4-nov: carga explícita de las fuentes antes de dibujar (máx. 3 s; si no llegan se dibuja igual)
const FUENTES = document.fonts?.load
  ? Promise.race([Promise.all(['400 12px "IBM Plex Sans"', '600 12px "IBM Plex Sans"', '400 12px "IBM Plex Mono"', '700 12px "Bricolage Grotesque"'].map((f) => document.fonts.load(f))), new Promise((r) => setTimeout(r, 3000))]).catch(() => null)
  : Promise.resolve();

async function dibujar(clave, cfgTar, zona, figura, numeroSeccion) {
  const version = zona._version = (zona._version || 0) + 1;
  const vigente = () => zona._version === version;
  clearTimeout(zona._cargaTimer);
  zona.querySelector('.actualizacion-dato')?.remove();
  zona.classList.remove('actualizacion-visible');
  if (conResultado(zona)) {
    // Mantiene el resultado anterior. La carga solo se anuncia si la espera es perceptible.
    marcar(zona, 'actualizando');
    zona._cargaTimer = setTimeout(() => {
      if (!vigente()) return;
      const aviso = el('span', 'actualizacion-dato', 'Actualizando…');
      aviso.setAttribute('role', 'status');
      zona.append(aviso);
      zona.classList.add('actualizacion-visible');
    }, 300);
  } else estadoDatos(zona, 'cargando', 'Cargando indicador…', 'La vista se actualizará cuando lleguen los datos.');
  const reintentar = () => programarDibujo(clave, cfgTar, zona, figura, numeroSeccion);
  await FUENTES;
  if (!vigente()) return; // 4-nov: ECharts mide las etiquetas con la fuente real (antes cortaba nombres)
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
    SECCIONES.get(numeroSeccion)?.add(() => programarDibujo(clave, cfgTar, zona, figura, numeroSeccion));
  }
  // bancos: tarjetas [banco] se vuelven a dibujar cuando cambia el estado (solo filtran y resaltan)
  if (cfgTar.banco && !zona._registrada) {
    zona._registrada = true;
    REDIBUJAR.add(() => programarDibujo(clave, cfgTar, zona, figura, numeroSeccion));
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
  let d;
  try {
    d = await cargarTodas(cfgTar.datos || []);
  } catch (e) {
    if (!vigente()) return;
    console.warn('No se pudieron cargar los datos de', clave, e);
    estadoDatos(zona, 'error', 'No pudimos cargar este indicador', 'Revisa tu conexión y vuelve a intentarlo. El resto de la página sigue disponible.', reintentar);
    return;
  }
  if (!vigente()) return;
  let entrada;
  try {
    entrada = cfgTar.armar ? await cfgTar.armar(d, { clave, ...leer(), seleccion: seleccionDe(numeroSeccion), codBanco: bancoPorSlug(leer().banco)?.cod || null, grupoBanco: bancoPorSlug(leer().banco)?.modelo || null }) : null; // bancos: armar recibe el estado (banco, optica, grupo, trimestre) y el selector de su sección
  } catch (e) {
    if (!vigente()) return;
    console.warn('No se pudo preparar el indicador', clave, e);
    estadoDatos(zona, 'error', 'No pudimos mostrar este indicador', 'Vuelve a intentarlo o consulta otra sección.', reintentar);
    return;
  }
  if (!vigente()) return;
  if (!entrada) { enPreparacion(zona, cfgTar.motivo || 'la función armar() no devolvió datos'); return; }
  if (entrada.enPreparacion) { enPreparacion(zona, entrada.enPreparacion, entrada.requiereBanco === true); return; }

  const desplazamientos = [...zona.querySelectorAll('.tabla-scroll')].map((n) => ({ izquierda: n.scrollLeft, arriba: n.scrollTop }));
  const glosarioAbierto = !!zona.querySelector('.tabla-glosario[open]');
  const cont = el('div', 'tarjeta-visual');
  cont.style.cssText = 'position:absolute;inset:0';
  if (!['tabla', 'comparador', 'percentiles', 'cascada_doble', 'apilada_100', 'pesas', 'barras_ic', 'small_multiples', 'small_multiples_bancos', 'barras_simple', 'mix_banco', 'puertas', 'tabla_estandar'].includes(cfgTar.componente)) { // bancos: los HTML no llevan role=img
    cont.setAttribute('role', 'img');
    cont.setAttribute('aria-label', entrada.ariaLabel || cfgTar.titulo || clave);
  }
  clearTimeout(zona._cargaTimer);
  zona.classList.remove('actualizacion-visible');
  liberar(zona);
  zona.replaceChildren(cont);
  const fig = zona.closest('figure');
  if (fig && 'leyenda' in entrada) { // 3-nov: la leyenda depende de la vista elegida ([] = la dibuja el gráfico)
    fig.querySelector(':scope > .leyenda')?.remove();
    if (entrada.leyenda && entrada.leyenda.length) fig.insertBefore(armarLeyenda(entrada.leyenda), zona);
  }
  const fn = COMPONENTES[entrada.componente || cfgTar.componente];
  let chart;
  try {
    chart = fn(cont, entrada, { clave });
    marcar(zona, 'lista');
  } catch (e) {
    liberar(zona);
    console.warn('No se pudo dibujar el indicador', clave, e);
    estadoDatos(zona, 'error', 'No pudimos mostrar este indicador', 'Vuelve a intentarlo o consulta otra sección.', reintentar);
    return;
  }
  if (!chart) {
    const glosario = cont.querySelector('.tabla-glosario');
    if (glosario) glosario.open = glosarioAbierto;
    for (const [i, scroll] of [...cont.querySelectorAll('.tabla-scroll')].entries()) {
      if (desplazamientos[i]) {
        scroll.scrollLeft = desplazamientos[i].izquierda;
        scroll.scrollTop = desplazamientos[i].arriba;
      }
      scroll.tabIndex = 0;
      scroll.setAttribute('role', 'region');
      scroll.setAttribute('aria-label', `${cfgTar.titulo || 'Tabla de datos'}. Desplázate para consultar todas las columnas.`);
    }
  }
  if (chart && zona.closest('.pres-lamina')) window.__escalaTextoPres?.(zona); // 4-nov: redibujo dentro de una lámina
  if (cfgTar.pastilla && entrada.pastilla) {
    const p = figura.querySelector('[data-pastilla]');
    if (p) {
      p.replaceChildren(document.createTextNode('Último '), Object.assign(document.createElement('b'), { textContent: entrada.pastilla.valor }), document.createTextNode(` · ${entrada.pastilla.fecha}`));
    }
  }
  if (chart) {
    let ancho = Math.round(cont.clientWidth), alto = Math.round(cont.clientHeight);
    const ro = new ResizeObserver(([entrada]) => {
      const nuevoAncho = Math.round(entrada.contentRect.width), nuevoAlto = Math.round(entrada.contentRect.height);
      if (!nuevoAncho || !nuevoAlto || (nuevoAncho === ancho && nuevoAlto === alto)) return;
      ancho = nuevoAncho;
      alto = nuevoAlto;
      COLA_VISUAL.agendar(chart, () => {
        if (cont.isConnected && !chart.isDisposed()) chart.resize();
      });
    });
    ro.observe(cont);
    zona._resizeObserver = ro;
  }
}

function programarDibujo(clave, cfgTar, zona, figura, numeroSeccion) {
  // Invalida el resultado pendiente inmediatamente; los clics del mismo fotograma se agrupan.
  zona._version = (zona._version || 0) + 1;
  COLA_VISUAL.agendar(zona, () => dibujar(clave, cfgTar, zona, figura, numeroSeccion));
}

/* ---------- 4.5 Secciones ---------- */
/* bancos: selección por sección (SELECCION) y helpers del selector y de los KPI del riel */
function seleccionDe(numero) {
  return { ...(SELECCION.get(numero) || {}) };
}

/* Valor por defecto de un selector: el declarado o la primera opción. */
const defectoDe = (b) => b.defecto ?? b.opciones?.[0]?.valor;

/* Al elegir una opción, se redibujan solo las tarjetas de su sección, se recalcula su riel y la elección
   queda en la URL (s<NN>.<clave>, solo si no es el defecto): recargar o compartir conserva la vista. */
function elegirSeleccion(sec, clave, valor, pintarRiel) {
  const numero = sec.numero;
  if (SELECCION.get(numero)?.[clave] === valor) return;
  SELECCION.set(numero, { ...(SELECCION.get(numero) || {}), [clave]: valor });
  const b = (sec.riel || []).find((x) => x.tipo === 'selector' && (x.clave || 'seleccion') === clave);
  fijarSeleccion(numero, clave, valor, b ? defectoDe(b) : undefined);
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
  for (const b of sec.riel || []) { // bancos: valor inicial de cada selector: el de la URL si es una opción válida; si no, el defecto
    if (b.tipo !== 'selector') continue;
    const clave = b.clave || 'seleccion';
    const previo = SELECCION.get(sec.numero) || {};
    const enUrl = leerSeleccion(sec.numero, clave);
    const deUrl = (b.opciones || []).find((o) => String(o.valor) === enUrl);
    if (previo[clave] === undefined) SELECCION.set(sec.numero, { ...previo, [clave]: deUrl ? deUrl.valor : defectoDe(b) });
  }
  SECCIONES.set(sec.numero, new Set());
  return cargarTodas(tablas).catch(() => ({})).then(async (d) => {
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
      const nuevo = riel(cfg, sec, ult, resultados, (clave, valor) => elegirSeleccion(sec, clave, valor, pintarRiel));
      const viejo = s.querySelector(':scope > .riel');
      if (viejo) {
        const bloques = [...nuevo.querySelectorAll(':scope > .riel-bloque:not(.riel-selector)')];
        [...viejo.querySelectorAll(':scope > .riel-bloque:not(.riel-selector)')].forEach((bloque, i) => {
          if (bloques[i]) bloque.replaceWith(bloques[i]);
        });
      } else s.prepend(nuevo);
    };
    await pintarRiel();
    const cuerpo = el('div', sec.apilada ? 'cuerpo apilada' : 'cuerpo');
    if (sec.altoTabla) cuerpo.style.setProperty('--alto-tabla', `${sec.altoTabla}px`);
    for (const fila of sec.filas || []) {
      // bancos: el alto de la fila sale de las tarjetas que lo fijan; `auto` no impone alto.
      const altos = fila.map((c) => (typeof c.alto === 'number' ? c.alto : 0));
      const alto = Math.max(0, ...altos) || null;
      for (const c of fila) {
        const cfgTar = cfg.tarjetas?.[c.clave] || { titulo: c.clave, componente: '—', estado: 'FALTA', motivo: 'la clave no está en cfg.tarjetas' };
        const { figura, zona } = tarjetaShell(cfgTar, typeof c.alto === 'number' ? c.alto : alto);
        figura.dataset.clave = c.clave; // 4-nov: número de tarjeta visible para revisar (canvas, capturas)
        figura.style.gridColumn = `span ${c.ancho}`;
        cuerpo.append(figura);
        dibujar(c.clave, cfgTar, zona, figura, sec.numero);
      }
    }
    s.append(cuerpo);
    // 4-nov: la sección se muestra de inmediato; no espera a sus tarjetas (con bk_grupo de 12 MB,
    // Calidad/Rentabilidad/Ficha quedaban en blanco 20–30 s). Cada tarjeta lleva su propio data-estado.
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
function instalarIndice(contenedor) {
  const enlaces = [...contenedor.querySelectorAll('.indice-item')];
  const secciones = [...contenedor.querySelectorAll('section.seccion')];
  const marcar = (id) => enlaces.forEach((a) => {
    if (a.hash === `#${id}`) a.setAttribute('aria-current', 'location');
    else a.removeAttribute('aria-current');
  });
  if (secciones.length) marcar(secciones[0].id);
  if ('IntersectionObserver' in window) {
    const visibles = new Set();
    const observer = new IntersectionObserver((entradas) => {
      for (const e of entradas) {
        if (e.isIntersecting) visibles.add(e.target);
        else visibles.delete(e.target);
      }
      const primera = secciones.find((sec) => visibles.has(sec));
      if (primera) marcar(primera.id);
    }, { rootMargin: '-15% 0px -45% 0px', threshold: 0 });
    secciones.forEach((sec) => observer.observe(sec));
  }
  for (const a of enlaces) a.addEventListener('click', () => marcar(a.hash.slice(1)));
}

export async function montar(cfg) {
  CFG = cfg;
  // montando → lista: la estructura está armada (las tarjetas siguen su propio data-estado)
  document.documentElement.dataset.pagina = 'montando';
  const app = document.getElementById('app');
  app.replaceChildren(cabecera(cfg, null));
  const espera = el('p', 'carga-inicial', 'Cargando indicadores…');
  espera.setAttribute('role', 'status');
  app.append(espera);
  await Promise.all([leerTextos(), cargarBancos(await tablasExportadas())]);
  espera.remove();
  const b = barra();
  const titulo = el('div', 'barra-titulo');
  titulo.append(el('h1', 'barra-titulo-nombre', cfg.nombre));
  if (cfg.rotulo) titulo.append(el('span', 'barra-titulo-rotulo', cfg.rotulo));
  b.prepend(titulo);
  if (cfg.usaBanco === false) b.classList.add('sin-banco');
  const presentarBarra = el('button', 'barra-presentar', 'Presentar');
  presentarBarra.type = 'button';
  presentarBarra.title = 'Cada sección es una lámina · tecla P';
  presentarBarra.setAttribute('aria-keyshortcuts', 'p');
  presentarBarra.disabled = true;
  presentarBarra.addEventListener('click', () => presentacion.entrar(0));
  b.append(presentarBarra);
  app.append(b);
  if ('ResizeObserver' in window) {
    const barraObserver = new ResizeObserver(() => {
      document.documentElement.style.setProperty('--barra-alto', window.innerWidth >= 1200 ? `${Math.ceil(b.getBoundingClientRect().height)}px` : '0px');
    });
    barraObserver.observe(b);
  }
  if (cfg.franja?.length) app.append(franja(cfg));
  const cont = el('main', 'contenedor');
  cont.id = 'contenido-principal';
  cont.tabIndex = -1;
  cont.append(apertura(cfg), queCambio(cfg));
  app.append(cont);
  const montajes = (cfg.secciones || []).map((sec) => {
    const hueco = el('section', 'seccion');
    hueco.id = `s${sec.numero}`;
    estadoDatos(hueco, 'cargando', sec.nombre, 'Cargando sección…');
    cont.append(hueco);
    const montarSeccion = async () => {
      estadoDatos(hueco, 'cargando', sec.nombre, 'Cargando sección…');
      try {
        const nueva = await seccion(cfg, sec);
        hueco.replaceWith(nueva);
      } catch (error) {
        console.warn('No se pudo montar la sección', sec.numero, error);
        estadoDatos(hueco, 'error', `No pudimos cargar ${sec.nombre}`, 'Vuelve a intentarlo. Las demás secciones siguen disponibles.', montarSeccion);
      }
    };
    return montarSeccion();
  });
  const pie = cierre(cfg);
  if (pie) cont.append(pie);
  document.title = `${cfg.nombre} · Bancos Brasil`;
  if (cfg.ultimoDato) {
    cargarTodas([cfg.ultimoDato.tabla]).then((d) => {
      const fecha = etiquetaFecha(maxFecha(d[cfg.ultimoDato.tabla], cfg.ultimoDato.columna || 'fecha'), cfg.trimestral);
      if (fecha !== '—') app.querySelector('.cabecera-ultimo').textContent = `Último dato ${fecha}`;
    }).catch(() => {});
  }
  await Promise.all(montajes);
  instalarIndice(cont);
  actualizarApertura();
  presentarBarra.disabled = !cont.querySelector('.seccion .cuerpo');
  document.documentElement.dataset.pagina = 'lista';
  presentacion.alMontar();
  if (/^#s\d+$/.test(location.hash)) document.getElementById(location.hash.slice(1))?.scrollIntoView({ behavior: 'instant', block: 'start' });
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
