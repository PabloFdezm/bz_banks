/* Monta la página de la ruta actual desde su config: cabecera, barra, franja, apertura, secciones y
   tarjetas (§3 y §4 del general). Todas las páginas comparten esta anatomía y el mismo index.html. */
import { PAGINAS_VISIBLES, MARCA, NOMBRE_SITIO, enlace, moduloConfig, paginaDeRuta } from './config.js';
import { cargar, cargarTodas, tablasExportadas } from './datos.js';
import { trimestre, formatear, pp, tono, TABLA } from './formato.js';
import { FUENTES_WEB } from './tokens.js';
import { ESTADOS, TRANSITORIOS, MOTIVOS, FUENTES_DEL_SITIO, periodoActivo, sinDibujo } from './comun.js';
import { COMPONENTES } from './charts_bancos.js';
import { leer, barra, alCambiar, cargarBancos, hayBarraDeBanco, enfocarBanco } from './estado.js';
import { leerSeleccion, fijarSeleccion, busquedaCompartida } from './url.js';
import { crearColaVisual } from './fluidez.js';
import { el, svgEl } from './dom.js';
import * as presentacion from './presentacion.js';

const COLA_VISUAL = crearColaVisual();
const REDIBUJAR = new Set(); // tarjetas [banco]: se vuelven a dibujar al cambiar el banco
const SECCIONES = new Map(); // número de sección → funciones que redibujan sus tarjetas (selector)
const SELECCION = new Map(); // número de sección → { clave: valor } de sus selectores
let CFG = null;
let FRANJA = null;
let MANIFIESTO = []; // filas de bk_manifiesto: último corte de cada universo

alCambiar(() => {
  enlazarCabecera();
  actualizarTitular();
  for (const f of REDIBUJAR) f();
  if (FRANJA && CFG.franja.some((k) => k.banco)) pintarFranja(CFG, FRANJA);
});

/* Los enlaces de la cabecera conservan banco y grupo (spec §3), sin los selectores de esta página. */
function enlazarCabecera() {
  for (const a of document.querySelectorAll('a[data-base]')) a.href = a.dataset.base + busquedaCompartida();
}

/* Páginas con titularPorBanco: con banco activo, el título de la barra es el banco. */
function actualizarTitular() {
  if (!CFG?.titularPorBanco) return;
  const b = leer().bancoActivo;
  const titulo = document.querySelector('.barra-titulo-nombre');
  if (titulo) titulo.textContent = b ? b.nombre_corto : CFG.nombre;
}

/* ---------- Cabecera: menú lateral fijo ---------- */
function cabecera(cfg) {
  const h = el('header', 'cabecera');
  const id = el('div', 'cabecera-identidad');
  const textos = el('div', 'cabecera-textos');
  textos.append(el('span', 'cabecera-marca', MARCA), el('span', 'cabecera-sub', FUENTES_DEL_SITIO.join(' · ').toUpperCase()));
  id.append(textos);
  const nav = el('nav', 'cabecera-nav');
  nav.setAttribute('aria-label', 'Páginas');
  nav.append(el('span', 'cabecera-rotulo', 'PÁGINAS'));
  PAGINAS_VISIBLES.forEach((p, i) => {
    const a = el('a', 'pestana');
    a.dataset.base = enlace(p.ruta);
    a.href = a.dataset.base + busquedaCompartida();
    a.append(el('span', 'pestana-num', String(i + 1).padStart(2, '0')), el('span', 'pestana-nombre', p.nombre));
    if (cfg.clave === p.clave) a.setAttribute('aria-current', 'page');
    nav.append(a);
  });
  h.append(id, nav, el('span', 'cabecera-ultimo', `Fuentes: BCB · ${FUENTES_DEL_SITIO.join(' · ')}`));
  return h;
}

/* ---------- Apertura: índice de la página ---------- */
function apertura(cfg) {
  const s = el('section', 'apertura');
  const nav = el('nav', 'indice');
  nav.setAttribute('aria-label', 'En esta página');
  nav.append(el('span', 'indice-rotulo', 'EN ESTA PÁGINA'));
  for (const sec of cfg.secciones) {
    const a = el('a', 'indice-item');
    a.href = `#s${sec.numero}`;
    a.append(el('span', 'indice-num', sec.numero), document.createTextNode(sec.nombre));
    nav.append(a);
  }
  s.append(nav);
  return s;
}

/* ---------- Franja de indicadores (diseño FARO) ----------
   Cinco cifras con su serie. Cada indicador (comun.js: indicadorPanel, indicadorBanco, indicadorSistema)
   dice de qué tabla y fila sale; aquí solo se filtra, se toma la última fila y se dibuja. El cambio se
   muestra en pp: la fila trae su unidad (unidad_tt, unidad_d o unidad; «pp» o fracción). */
const VENTANA_FRANJA = 13;

function serieSvg(valores, tonoSerie) {
  const svg = svgEl('svg', { viewBox: '0 0 300 46', preserveAspectRatio: 'none', class: `franja-serie tono-${tonoSerie}`, 'aria-hidden': 'true' });
  if (valores.length < 2) return svg;
  const min = Math.min(...valores), max = Math.max(...valores), r = max - min || 1, n = valores.length;
  const px = (i) => (i * 300) / (n - 1), py = (v) => 42 - ((v - min) / r) * 36;
  const pts = valores.map((v, i) => `${px(i).toFixed(1)},${py(v).toFixed(1)}`).join(' ');
  svg.append(svgEl('polygon', { points: `${px(0).toFixed(1)},46 ${pts} ${px(n - 1).toFixed(1)},46`, class: 'franja-area' }));
  svg.append(svgEl('polyline', { points: pts, class: 'franja-linea' }));
  svg.append(svgEl('line', { x1: 300, x2: 300, y1: 0, y2: 46, class: 'franja-hoy' }));
  return svg;
}

async function pintarFranja(cfg, nodo) {
  // bk_metrica da el tono de las métricas que no lo traen escrito
  const tablas = [...new Set([...cfg.franja.map((k) => k.tabla), ...(cfg.franja.some((k) => !k.tono) ? ['bk_metrica'] : [])])];
  const version = nodo._version = (nodo._version || 0) + 1;
  // con cifras ya pintadas se conservan mientras llegan las nuevas; tras un error, el reintento se ve
  if (conResultado(nodo)) marcar(nodo, 'actualizando');
  else if (nodo.dataset.estado !== 'cargando') estadoDatos(nodo, 'cargando', 'Cargando indicadores…', '');
  const resultados = await Promise.allSettled(tablas.map((tabla) => cargarTodas([tabla])));
  if (nodo._version !== version) return;
  for (const r of resultados) if (r.status === 'rejected') console.warn('Franja: tabla sin cargar', r.reason);
  if (tablas.length && resultados.every((r) => r.status === 'rejected')) {
    estadoDatos(nodo, 'error', 'No pudimos cargar los indicadores', 'Revisa tu conexión y vuelve a intentarlo.', () => pintarFranja(cfg, nodo));
    return;
  }
  const d = Object.assign({}, ...resultados.filter((r) => r.status === 'fulfilled').map((r) => r.value));
  const banco = leer().bancoActivo;
  const signoDe = new Map((d.bk_metrica || []).map((m) => [m.metrica, m.signo]));
  const celdas = [];
  for (const k of cfg.franja) {
    const c = el('div', 'franja-celda');
    let filas = (d[k.tabla] || []).filter((f) => Object.entries(k.filtro).every(([col, v]) => f[col] === v));
    if (k.banco) filas = banco?.cod_inst ? filas.filter((f) => f.cod_inst === banco.cod_inst) : [];
    filas = filas.filter((f) => f.valor != null).sort((a, b) => (a[k.orden] < b[k.orden] ? -1 : a[k.orden] > b[k.orden] ? 1 : 0)).slice(-VENTANA_FRANJA);
    const cab = el('div', 'franja-cab');
    cab.append(el('span', 'franja-rotulo', k.rotulo));
    const u = filas[filas.length - 1];
    if (!u) {
      cab.append(el('span', 'franja-corte', ''));
      c.append(cab, el('span', 'franja-valor franja-sin', k.banco && !banco ? 'Elige un banco' : 'Sin datos'));
      celdas.push(c);
      continue;
    }
    cab.append(el('span', 'franja-corte', u.trimestre || trimestre(u.fecha)));
    const unidadDelta = u.unidad_tt ?? u.unidad_d ?? u.unidad;
    const deltaPp = u[k.delta] == null ? null : u[k.delta] * (unidadDelta === 'pp' ? 1 : 100);
    const t = tono(deltaPp, k.tono || signoDe.get(k.metrica), 1e-9);
    const tonoFranja = t === 'sin-cambio' ? 'neutro' : t;
    const pie = el('div', 'franja-pie');
    pie.append(
      el('span', `franja-delta tono-${tonoFranja}`, deltaPp == null ? '—' : pp(deltaPp, 1, true, TABLA)),
      el('span', 'franja-base', 'TRIM.'),
      el('span', 'franja-ventana', `${filas.length} trim.`),
    );
    c.append(cab, el('span', 'franja-valor', formatear(u.valor, 'pct')), pie, serieSvg(filas.map((f) => f.valor), tonoFranja));
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

/* ---------- Riel: número, nombre, frecuencia, pregunta y selectores ---------- */
/* Selector de la sección: un botón por opción; al elegir, cambia solo las tarjetas de su sección. */
function bloqueSelector(b, valorActual, alElegir) {
  const bl = el('div', 'riel-bloque riel-selector');
  bl.append(el('span', 'riel-bloque-rotulo', b.rotulo));
  const grupo = el('div', 'riel-seg');
  grupo.setAttribute('role', 'group');
  grupo.setAttribute('aria-label', b.rotulo);
  for (const op of b.opciones) {
    const btn = el('button', 'riel-seg-op', op.nombre);
    btn.type = 'button';
    btn.setAttribute('aria-pressed', String(op.valor === valorActual));
    btn.addEventListener('click', () => {
      // marca la opción en este mismo grupo (en presentación el grupo vive en la lámina, fuera del riel)
      for (const o of grupo.children) o.setAttribute('aria-pressed', String(o === btn));
      alElegir(b.clave, op.valor);
    });
    grupo.append(btn);
  }
  bl.append(grupo);
  return bl;
}

/* ---------- Tarjeta ---------- */
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
  const f = el('figure', cfgTar.plana ? 'tarjeta tarjeta-plana' : 'tarjeta');
  if (typeof alto === 'number') {
    f.style.height = `${alto}px`;
    f.style.setProperty('--alto', `${alto}px`); // lo usa la regla de pantallas angostas
  }
  const cab = el('div', 'tarjeta-cabecera');
  const izq = el('div');
  izq.append(el('h3', 'tarjeta-titulo', cfgTar.titulo || ''));
  if (cfgTar.sub) izq.append(el('p', 'tarjeta-sub', cfgTar.sub));
  cab.append(izq);
  f.append(cab);
  if (cfgTar.leyenda && cfgTar.leyenda.length) f.append(armarLeyenda(cfgTar.leyenda));
  const zona = el('div', 'tarjeta-zona');
  f.append(zona);
  if (cfgTar.nota) f.append(el('p', 'tarjeta-nota', cfgTar.nota));
  if (cfgTar.fuente) f.append(el('p', 'tarjeta-pie', `Fuente: ${cfgTar.fuente}`));
  return { figura: f, zona };
}

/* ---------- Ciclo de vida de un nodo con datos (tarjeta, franja) ----------
   Una sola máquina de estados (comun.js: ESTADOS), explícita en data-estado (en la <figure> si es tarjeta;
   si no, en el nodo). La leen el CSS, herramientas/verificar_f1.py y cualquier agente que inspeccione el DOM:
     cargando ─────────────► lista | en-preparacion | requiere-banco | error
     lista ─► actualizando ─► lista | en-preparacion | requiere-banco | error   (conserva el resultado anterior)
     en-preparacion | requiere-banco | error ─► cargando   (reintento, cambio de banco o de selector)
   aria-busy se deriva del estado: nadie lo fija a mano. */
const portador = (zona) => zona.closest('figure.tarjeta') || zona;
const conResultado = (zona) => ['lista', 'actualizando'].includes(portador(zona).dataset.estado);

function marcar(zona, estado) {
  if (!ESTADOS.includes(estado)) throw new Error(`estado desconocido: ${estado}`);
  const nodo = portador(zona);
  if (estado === 'actualizando' && !conResultado(zona)) console.warn(`transición inválida ${nodo.dataset.estado} → actualizando`, nodo);
  nodo.dataset.estado = estado;
  zona.setAttribute('aria-busy', String(TRANSITORIOS.includes(estado)));
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

/* Sin dibujo por decisión de la config (comun.js: enPreparacion / requiereBanco): el motivo se muestra. */
function mostrarSinDibujo(zona, estado, motivo) {
  const pideBanco = estado === 'requiere-banco';
  estadoDatos(zona, estado, pideBanco ? 'Elige un banco para continuar' : 'Sin datos disponibles',
    motivo || 'No hay observaciones disponibles para esta selección.');
  if (pideBanco && hayBarraDeBanco()) {
    const boton = el('button', '', 'Elegir banco');
    boton.type = 'button';
    boton.addEventListener('click', enfocarBanco);
    zona.firstElementChild.append(boton);
  }
}

/* Sin dibujo por un problema del sitio (componente inexistente, armar sin resultado): mensaje genérico para
   quien lee y un error de consola, que verificar_f1.py cuenta como falla. */
function noDisponible(zona, causa) {
  console.error('Indicador no disponible:', causa);
  estadoDatos(zona, 'en-preparacion', 'Sin datos disponibles',
    'Este indicador todavía no está disponible. Puedes consultar los demás indicadores de la página.');
}

/* Libera las instancias de ECharts de una zona antes de volver a dibujarla. */
function liberar(zona) {
  zona._resizeObserver?.disconnect();
  zona._resizeObserver = null;
  for (const n of zona.querySelectorAll('.tarjeta-visual')) {
    const chart = window.echarts?.getInstanceByDom(n);
    if (chart) { COLA_VISUAL.quitar(chart); chart.dispose(); }
  }
}

/* Lo que un componente pide conservar al redibujar: desplazamiento ([data-conservar-scroll]) y
   detalles abiertos ([data-conservar-abierto]), en el orden en que aparecen. */
function guardarVista(zona) {
  return {
    scroll: [...zona.querySelectorAll('[data-conservar-scroll]')].map((n) => [n.scrollLeft, n.scrollTop]),
    abierto: [...zona.querySelectorAll('[data-conservar-abierto]')].map((n) => n.open),
  };
}
function restaurarVista(zona, vista) {
  [...zona.querySelectorAll('[data-conservar-scroll]')].forEach((n, i) => {
    if (vista.scroll[i]) [n.scrollLeft, n.scrollTop] = vista.scroll[i];
  });
  [...zona.querySelectorAll('[data-conservar-abierto]')].forEach((n, i) => { n.open = !!vista.abierto[i]; });
}

// Carga explícita de las fuentes web antes del primer dibujo: ECharts mide las etiquetas con la fuente
// disponible en ese momento y, si la web llega después, cortaba nombres. Máx. 3 s; si no llegan se dibuja igual.
const FUENTES = document.fonts?.load
  ? Promise.race([Promise.all(FUENTES_WEB.map((f) => document.fonts.load(f))), new Promise((r) => setTimeout(r, 3000))]).catch(() => null)
  : Promise.resolve();

/* Contexto que recibe armar(d, contexto) y datos(contexto) (comun.js, protocolo de armar). */
function contextoArmar(numeroSeccion) {
  const { banco, bancoActivo, grupo, trimestre: t } = leer();
  return { banco, bancoActivo, grupo, periodoActivo: periodoActivo(t, MANIFIESTO), seleccion: { ...(SELECCION.get(numeroSeccion) || {}) } };
}

async function dibujar(clave, cfgTar, zona, figura, numeroSeccion) {
  const version = zona._version = (zona._version || 0) + 1;
  const vigente = () => zona._version === version;
  clearTimeout(zona._cargaTimer);
  zona.querySelector('.actualizacion-dato')?.remove();
  zona.classList.remove('actualizacion-visible');
  if (conResultado(zona)) {
    // Mantiene el resultado anterior. La carga solo se anuncia si la espera es perceptible (300 ms).
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
  if (!vigente()) return;
  if (!zona._registrada) {
    zona._registrada = true;
    // las tarjetas de una sección con selector se redibujan al cambiarlo; las [banco], al cambiar el banco
    SECCIONES.get(numeroSeccion)?.add(reintentar);
    if (cfgTar.banco) REDIBUJAR.add(reintentar);
  }
  if (typeof cfgTar.armar !== 'function') { mostrarSinDibujo(zona, 'en-preparacion', MOTIVOS[String(cfgTar.estado || '').toUpperCase()] || MOTIVOS.DERIVAR); return; }
  const contexto = contextoArmar(numeroSeccion);
  let d;
  try {
    d = await cargarTodas(typeof cfgTar.datos === 'function' ? cfgTar.datos(contexto) : (cfgTar.datos || []));
  } catch (e) {
    if (!vigente()) return;
    console.warn('No se pudieron cargar los datos de', clave, e);
    estadoDatos(zona, 'error', 'No pudimos cargar este indicador', 'Revisa tu conexión y vuelve a intentarlo. El resto de la página sigue disponible.', reintentar);
    return;
  }
  if (!vigente()) return;
  let entrada;
  try {
    entrada = await cfgTar.armar(d, contexto);
  } catch (e) {
    if (!vigente()) return;
    console.warn('No se pudo preparar el indicador', clave, e);
    estadoDatos(zona, 'error', 'No pudimos mostrar este indicador', 'Vuelve a intentarlo o consulta otra sección.', reintentar);
    return;
  }
  if (!vigente()) return;
  if (!entrada) { noDisponible(zona, `${clave}: armar() no devolvió datos`); return; }
  if (sinDibujo(entrada)) { mostrarSinDibujo(zona, entrada.estado, entrada.motivo); return; }
  // armar() puede elegir el componente según la vista (p. ej. barras o líneas)
  const nombre = entrada.componente || cfgTar.componente;
  const componente = COMPONENTES[nombre];
  if (!componente) { noDisponible(zona, `${clave}: componente «${nombre}» no existe`); return; }

  const vista = guardarVista(zona);
  const cont = el('div', 'tarjeta-visual');
  clearTimeout(zona._cargaTimer);
  zona.classList.remove('actualizacion-visible');
  liberar(zona);
  zona.replaceChildren(cont);
  if ('leyenda' in entrada) { // la leyenda depende de la vista elegida ([] = la dibuja el gráfico)
    figura.querySelector(':scope > .leyenda')?.remove();
    if (entrada.leyenda && entrada.leyenda.length) figura.insertBefore(armarLeyenda(entrada.leyenda), zona);
  }
  let chart;
  try {
    chart = componente.dibujar(cont, entrada, { titulo: cfgTar.titulo || clave });
    marcar(zona, 'lista');
  } catch (e) {
    liberar(zona);
    console.warn('No se pudo dibujar el indicador', clave, e);
    estadoDatos(zona, 'error', 'No pudimos mostrar este indicador', 'Vuelve a intentarlo o consulta otra sección.', reintentar);
    return;
  }
  if (!chart) { restaurarVista(zona, vista); return; }
  // un gráfico es una imagen para los lectores de pantalla; las tablas y listas se leen tal cual
  cont.dataset.grafico = '';
  cont.setAttribute('role', 'img');
  cont.setAttribute('aria-label', entrada.ariaLabel || cfgTar.titulo || clave);
  presentacion.alRedibujar(zona);
  let ancho = Math.round(cont.clientWidth), alto = Math.round(cont.clientHeight);
  const ro = new ResizeObserver(([medida]) => {
    const nuevoAncho = Math.round(medida.contentRect.width), nuevoAlto = Math.round(medida.contentRect.height);
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

function programarDibujo(clave, cfgTar, zona, figura, numeroSeccion) {
  // Invalida el resultado pendiente inmediatamente; los clics del mismo fotograma se agrupan.
  zona._version = (zona._version || 0) + 1;
  COLA_VISUAL.agendar(zona, () => dibujar(clave, cfgTar, zona, figura, numeroSeccion));
}

/* ---------- Secciones ---------- */
const defectoDe = (b) => b.defecto ?? b.opciones[0].valor;

/* Al elegir una opción se redibujan solo las tarjetas de su sección y la elección queda en la URL
   (s<NN>.<clave>, solo si no es el defecto): recargar o compartir conserva la vista. */
function elegirSeleccion(sec, clave, valor) {
  const numero = sec.numero;
  if (SELECCION.get(numero)?.[clave] === valor) return;
  SELECCION.set(numero, { ...SELECCION.get(numero), [clave]: valor });
  fijarSeleccion(numero, clave, valor, defectoDe(sec.riel.find((x) => x.clave === clave)));
  for (const redibujar of SECCIONES.get(numero) || []) redibujar();
}

/* Una sección: riel y cuerpo. Devuelve lo que presentacion.js necesita para su lámina. */
function seccion(cfg, sec) {
  const s = el('section', 'seccion');
  s.id = `s${sec.numero}`;
  const selectores = (sec.riel || []).filter((b) => b.tipo === 'selector');
  // valor inicial de cada selector: el de la URL si es una opción válida; si no, el defecto
  const inicial = {};
  for (const b of selectores) {
    const deUrl = b.opciones.find((o) => String(o.valor) === leerSeleccion(sec.numero, b.clave));
    inicial[b.clave] = deUrl ? deUrl.valor : defectoDe(b);
  }
  SELECCION.set(sec.numero, inicial);
  SECCIONES.set(sec.numero, new Set());

  const r = el('div', 'riel');
  r.append(el('span', 'riel-numero', sec.numero), el('h2', 'riel-nombre', sec.nombre));
  if (sec.frecuencia) r.append(el('span', 'riel-frecuencia', sec.frecuencia));
  if (sec.pregunta) r.append(el('p', 'riel-pregunta', sec.pregunta));
  const bloques = selectores.map((b) => bloqueSelector(b, inicial[b.clave], (clave, valor) => elegirSeleccion(sec, clave, valor)));
  r.append(...bloques);
  s.append(r);

  const cuerpo = el('div', 'cuerpo');
  for (const fila of sec.filas || []) {
    // el alto de la fila sale de las tarjetas que lo fijan; `auto` no impone alto
    const alto = Math.max(0, ...fila.map((c) => (typeof c.alto === 'number' ? c.alto : 0))) || null;
    for (const c of fila) {
      const cfgTar = cfg.tarjetas?.[c.clave] || { titulo: c.clave, estado: 'FALTA' };
      const { figura, zona } = tarjetaShell(cfgTar, typeof c.alto === 'number' ? c.alto : alto);
      figura.dataset.clave = c.clave; // clave de la tarjeta visible en el DOM (canvas, capturas)
      figura.style.gridColumn = `span ${c.ancho}`;
      cuerpo.append(figura);
      dibujar(c.clave, cfgTar, zona, figura, sec.numero);
    }
  }
  s.append(cuerpo);
  return { cfg: sec, nodo: s, cuerpo, selectores: bloques };
}

/* ---------- Montar una página ---------- */
function instalarIndice(contenedor, secciones) {
  const enlaces = [...contenedor.querySelectorAll('.indice-item')];
  const marcarActual = (id) => enlaces.forEach((a) => {
    if (a.hash === `#${id}`) a.setAttribute('aria-current', 'location');
    else a.removeAttribute('aria-current');
  });
  if (secciones.length) marcarActual(secciones[0].id);
  const visibles = new Set();
  const observer = new IntersectionObserver((entradas) => {
    for (const e of entradas) {
      if (e.isIntersecting) visibles.add(e.target);
      else visibles.delete(e.target);
    }
    const primera = secciones.find((sec) => visibles.has(sec));
    if (primera) marcarActual(primera.id);
  }, { rootMargin: '-15% 0px -45% 0px', threshold: 0 });
  secciones.forEach((sec) => observer.observe(sec));
  for (const a of enlaces) a.addEventListener('click', () => marcarActual(a.hash.slice(1)));
}

async function montar(cfg) {
  CFG = cfg;
  // montando → lista: la estructura está armada (las tarjetas siguen su propio data-estado)
  document.documentElement.dataset.pagina = 'montando';
  document.title = `${cfg.nombre} · ${NOMBRE_SITIO}`;
  const app = document.getElementById('app');
  app.replaceChildren(cabecera(cfg));
  const espera = el('p', 'carga-inicial', 'Cargando indicadores…');
  espera.setAttribute('role', 'status');
  app.append(espera);
  const tablas = await tablasExportadas();
  [, MANIFIESTO] = await Promise.all([
    cargarBancos(tablas),
    tablas.includes('bk_manifiesto') ? cargar('bk_manifiesto').catch((e) => { console.warn('bk_manifiesto no se pudo leer', e); return []; }) : [],
  ]);
  espera.remove();
  const b = barra();
  const titulo = el('div', 'barra-titulo');
  titulo.append(el('h1', 'barra-titulo-nombre', cfg.nombre));
  if (cfg.rotulo) titulo.append(el('span', 'barra-titulo-rotulo', cfg.rotulo));
  b.prepend(titulo);
  if (!cfg.usaBanco) b.classList.add('sin-banco');
  const presentarBarra = el('button', 'barra-presentar', 'Presentar');
  presentarBarra.type = 'button';
  presentarBarra.title = 'Cada sección es una lámina · tecla P';
  presentarBarra.setAttribute('aria-keyshortcuts', 'p');
  presentarBarra.addEventListener('click', () => presentacion.entrar(0));
  b.append(presentarBarra);
  app.append(b);
  // el alto real de la barra (el CSS decide desde qué ancho la barra es fija y lo usa: --barra-alto)
  new ResizeObserver(() => {
    document.documentElement.style.setProperty('--barra-medida', `${Math.ceil(b.getBoundingClientRect().height)}px`);
  }).observe(b);
  if (cfg.franja?.length) app.append(franja(cfg));
  const cont = el('main', 'contenedor');
  cont.id = 'contenido-principal';
  cont.tabIndex = -1;
  cont.append(apertura(cfg));
  const laminas = cfg.secciones.map((sec) => seccion(cfg, sec));
  cont.append(...laminas.map((l) => l.nodo));
  app.append(cont);
  instalarIndice(cont, laminas.map((l) => l.nodo));
  actualizarTitular();
  presentarBarra.disabled = !laminas.length;
  document.documentElement.dataset.pagina = 'lista';
  presentacion.alMontar(cfg, laminas);
  if (/^#s\d+$/.test(location.hash)) document.getElementById(location.hash.slice(1))?.scrollIntoView({ behavior: 'instant', block: 'start' });
}

/* La config sale de la ruta (config.js, PAGINAS): todas las carpetas sirven el mismo index.html. */
const pagina = paginaDeRuta(location.pathname);
if (pagina) {
  const { default: cfg } = await import(moduloConfig(pagina.clave));
  await montar({ ...pagina, secciones: [], ...cfg });
} else {
  document.getElementById('app').replaceChildren(el('p', 'carga-inicial', 'Esta página no existe.'));
}
