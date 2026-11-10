// Marco común del sitio v2: escala de la página, menú lateral, índice de secciones, Agrandar centrado,
// modo Presentar y descarga a Excel (por gráfico y por página). Las páginas las monta dc.js.
import { montar } from '/assets/v2/dc.js';
import '/assets/v2/componentes/Grafico.js';
import '/assets/v2/componentes/Rango.js';

const html = document.documentElement;
const $ = (id) => document.getElementById(id);
const ANCHO = 1600;
let presentando = null;

// ---------- escala y menú lateral
const conMenu = () => !(html.classList.contains('v2-plegado') || html.clientWidth < 1100);
function ajustar() {
  const esc = $('v2-escala'); if (!esc) return;
  if (presentando) { ajustarPresentar(); return; }
  const disp = html.clientWidth - (conMenu() ? 248 : 0) - 48;
  esc.style.zoom = Math.max(html.clientWidth < 1100 ? 0.2 : 0.72, Math.min(1, disp / ANCHO));
}
function plegar(cerrar) {
  html.classList.toggle('v2-plegado', cerrar);
  $('v2-plegar').setAttribute('aria-expanded', String(!cerrar));
  try { localStorage.setItem('v2-lateral', cerrar ? 'cerrado' : 'abierto'); } catch (e) { /* sin almacenamiento */ }
  ajustar();
}

// ---------- índice de secciones
function indice(raiz) {
  const ol = $('v2-secs'); if (!ol) return;
  const secs = [...raiz.querySelectorAll('.sh')].filter((s) => !s.closest('[role=dialog]'));
  ol.innerHTML = '';
  const links = secs.map((s, i) => {
    s.id = s.id || 'seccion-' + (i + 1);
    const sp = s.querySelectorAll('span');
    const li = document.createElement('li'); const a = document.createElement('a');
    a.href = '#' + s.id;
    if (sp.length >= 2) { const n = document.createElement('span'); n.className = 'v2-num'; n.textContent = sp[0].textContent.trim(); a.append(n, sp[1].textContent.trim()); }
    else a.textContent = s.textContent.replace(/\s+/g, ' ').trim();
    a.addEventListener('click', (e) => { e.preventDefault(); s.scrollIntoView({ behavior: 'smooth', block: 'start' }); history.replaceState(null, '', '#' + s.id); html.classList.remove('v2-movil-abierto'); });
    li.appendChild(a); ol.appendChild(li); return a;
  });
  const obs = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (!en.isIntersecting) return;
    links.forEach((a) => a.removeAttribute('aria-current'));
    const k = secs.indexOf(en.target); if (links[k]) links[k].setAttribute('aria-current', 'location');
  }), { rootMargin: '0px 0px -75% 0px' });
  secs.forEach((s) => obs.observe(s));
  if (location.hash) { const t = document.getElementById(location.hash.slice(1)); if (t) t.scrollIntoView(); }
}

// ---------- Agrandar: el diálogo queda centrado y fijo; foco adentro; el resto no se desplaza
function vigilarDialogos(raiz) {
  let abierto = false;
  new MutationObserver(() => {
    const d = raiz.querySelector('[role=dialog]');
    if (d && !abierto) {
      abierto = true; html.classList.add('v2-dialogo');
      const c = [...d.querySelectorAll('button')].find((x) => x.textContent.trim() === 'Cerrar');
      (c || d).focus({ preventScroll: true });
      d.parentElement.scrollTop = 0;
    } else if (!d && abierto) { abierto = false; html.classList.remove('v2-dialogo'); }
  }).observe(raiz, { childList: true, subtree: true });
}
const cerrarDialogo = () => {
  const d = document.querySelector('[role=dialog]');
  const c = d && [...d.querySelectorAll('button')].find((x) => x.textContent.trim() === 'Cerrar');
  if (c) { c.click(); return true; }
  return false;
};

// ---------- modo Presentar: un par gráfico + tabla por pantalla
let laminas = [];
function armarLaminas() {
  const raiz = $('v2-raiz');
  const pares = [];
  raiz.querySelectorAll('.card').forEach((c) => {
    if (c.closest('[role=dialog]')) return;
    const p = c.parentElement;
    if (!pares.includes(p)) pares.push(p);
  });
  const secs = [...raiz.querySelectorAll('.sh')].filter((s) => !s.closest('[role=dialog]'));
  return pares.map((p) => {
    let sec = null;
    secs.forEach((s) => { if (s.compareDocumentPosition(p) & Node.DOCUMENT_POSITION_FOLLOWING) sec = s; });
    return { par: p, sec };
  }).map((l, k, a) => ({ ...l, primera: !!l.sec && (k === 0 || a[k - 1].sec !== l.sec) }));
}
function ajustarPresentar() {
  const l = laminas[presentando.i]; if (!l) return;
  const esc = $('v2-escala');
  esc.style.zoom = 1;
  const r = l.par.getBoundingClientRect(), hs = l.primera ? l.sec.getBoundingClientRect().height + 16 : 0;
  const z = Math.min((html.clientWidth - 48) / ANCHO, (innerHeight - 96) / (r.height + hs), 1.6);
  esc.style.zoom = z;
  const top = (l.primera ? l.sec : l.par).getBoundingClientRect().top + scrollY - 24;
  scrollTo({ top, behavior: 'instant' });
}
function mostrarLamina(i) {
  presentando.i = Math.max(0, Math.min(laminas.length - 1, i));
  laminas.forEach((l, k) => { l.par.classList.toggle('v2-actual', k === presentando.i); if (l.sec) l.sec.classList.remove('v2-actual'); });
  const l = laminas[presentando.i]; if (l.primera) l.sec.classList.add('v2-actual');
  $('v2-pres-n').textContent = (presentando.i + 1) + ' / ' + laminas.length;
  $('v2-pres-t').textContent = l.sec ? [...l.sec.querySelectorAll('span')].map((x) => x.textContent.trim()).join(' ') || l.sec.textContent.trim() : '';
  requestAnimationFrame(ajustarPresentar);
}
function presentar(on) {
  if (on) {
    cerrarDialogo();
    laminas = armarLaminas(); if (!laminas.length) return;
    let i = 0; const y = scrollY + innerHeight / 3;
    laminas.forEach((l, k) => { if (l.par.getBoundingClientRect().top + scrollY <= y) i = k; });
    presentando = { i, y0: scrollY };
    html.classList.add('v2-presentando');
    $('v2-pres').hidden = false;
    if (html.requestFullscreen && !document.fullscreenElement) html.requestFullscreen().catch(() => {});
    mostrarLamina(i);
  } else if (presentando) {
    const l = laminas[presentando.i];
    presentando = null; html.classList.remove('v2-presentando'); $('v2-pres').hidden = true;
    document.querySelectorAll('.v2-actual').forEach((x) => x.classList.remove('v2-actual'));
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    ajustar();
    if (l) (l.sec || l.par).scrollIntoView({ block: 'start' });
  }
}

// ---------- Excel
let XLSX = null;
async function libreria() {
  if (XLSX) return XLSX;
  await new Promise((ok, mal) => { const s = document.createElement('script'); s.src = '/assets/vendor/xlsx.full.min.js'; s.onload = ok; s.onerror = mal; document.head.appendChild(s); });
  XLSX = window.XLSX; return XLSX;
}
const tituloDe = (el) => {
  for (let n = el; n && n !== document.body; n = n.parentElement) {
    const t = n.querySelector && n.querySelector(':scope > div .ct, :scope > .ct, :scope > div > .bt, :scope .bt, :scope .ct');
    if (t && t.textContent.trim()) return t.textContent.trim();
  }
  return 'Gráfico';
};
function graficoDe(boton) {
  for (let n = boton.parentElement; n && n !== document.body; n = n.parentElement) {
    const g = n.querySelector('dc-import[name="Grafico"]');
    if (g && g.__dc) return g;
  }
  return null;
}
function tabla(cfg) {
  const lab = cfg.etiquetasTodas || cfg.etiquetas || [];
  const todo = !!cfg.etiquetasTodas;
  const ser = (cfg.series || []).filter((s) => s.nombre || s.id);
  const num = (s) => { const m = /^s(\d+)$/.exec(s.id || ''); return m ? +m[1] : 1e6; };
  const visto = new Set(), cols = [];
  ser.slice().sort((a, b) => num(a) - num(b)).forEach((s) => { const k = s.nombre || s.id; if (!visto.has(k)) { visto.add(k); cols.push(s); } });
  const filas = [['Período'].concat(cols.map((s) => s.nombre || s.id))];
  lab.forEach((e, i) => filas.push([e].concat(cols.map((s) => { const v = (todo && s.todo ? s.todo : s.valores)[i]; return v == null ? null : v; }))));
  return filas;
}
const hoja = (nombre, usados) => {
  let n = nombre.replace(/[\\/?*[\]:]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 28) || 'Hoja';
  let k = n, i = 2; while (usados.has(k)) k = n.slice(0, 25) + ' ' + i++;
  usados.add(k); return k;
};
const slug = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^\w]+/g, '_').replace(/^_|_$/g, '').toLowerCase().slice(0, 60);
async function excel(graficos, nombreArchivo, titulo) {
  const X = await libreria();
  const wb = X.utils.book_new(), usados = new Set();
  const info = [['Bancos Brasil · ' + titulo], ['Descargado', new Date().toLocaleString('es-CL')], ['Fuente', 'BCB (SGS, IF.Data, SCR.data, REF) y CVM, según cada gráfico'], [], ['Hoja', 'Gráfico']];
  const hojas = [];
  graficos.forEach((g) => {
    const cfg = g.__dc && g.__dc.props && g.__dc.props.cfg; if (!cfg) return;
    const t = tituloDe(g), n = hoja(t, usados);
    hojas.push([n, t]);
    const ws = X.utils.aoa_to_sheet(tabla(cfg));
    ws['!cols'] = [{ wch: 10 }].concat((cfg.series || []).map(() => ({ wch: 18 })));
    X.utils.book_append_sheet(wb, ws, n);
  });
  X.utils.book_append_sheet(wb, X.utils.aoa_to_sheet(info.concat(hojas)), hoja('Índice', usados));
  wb.SheetNames.unshift(wb.SheetNames.pop());
  X.writeFile(wb, nombreArchivo + '.xlsx');
}

// ---------- arranque
export async function iniciar(HOJAS, titulo) {
  const raiz = $('v2-raiz');
  $('v2-plegar').addEventListener('click', () => plegar(true));
  $('v2-abrir').addEventListener('click', () => { if (html.clientWidth < 1100) html.classList.toggle('v2-movil-abierto'); else plegar(false); });
  addEventListener('resize', ajustar); ajustar();
  addEventListener('keydown', (e) => {
    if (presentando) {
      if (['ArrowRight', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); mostrarLamina(presentando.i + 1); }
      else if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); mostrarLamina(presentando.i - 1); }
      else if (e.key === 'Escape') { e.preventDefault(); if (!cerrarDialogo()) presentar(false); }
      return;
    }
    if (e.key === 'Escape') { if (cerrarDialogo()) e.preventDefault(); else html.classList.remove('v2-movil-abierto'); }
  });
  document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && presentando) presentar(false); });
  $('v2-presentar').addEventListener('click', () => presentar(true));
  $('v2-pres-ant').addEventListener('click', () => mostrarLamina(presentando.i - 1));
  $('v2-pres-sig').addEventListener('click', () => mostrarLamina(presentando.i + 1));
  $('v2-pres-salir').addEventListener('click', () => presentar(false));
  $('v2-excel-pag').addEventListener('click', async (e) => {
    const b = e.currentTarget; b.disabled = true;
    try { await excel([...raiz.querySelectorAll('dc-import[name="Grafico"]')].filter((g) => !g.closest('[role=dialog]')), slug('bancos_brasil_' + titulo), titulo); } finally { b.disabled = false; }
  });
  document.addEventListener('click', async (e) => {
    const b = e.target.closest('.v2-excel'); if (!b) return;
    const g = graficoDe(b); if (!g) return;
    const t = tituloDe(g);
    b.disabled = true;
    try { await excel([g], slug(titulo + '_' + t), titulo + ' · ' + t); } finally { b.disabled = false; }
  });
  try {
    const mods = await Promise.all(HOJAS.map((h) => import('/assets/v2/paginas/' + h.hoja + '.js')));
    const datos = await Promise.all(HOJAS.map(async (h) => {
      if (!h.datos) return null;
      const r = await fetch('/data/v2/' + h.datos + '.json', { cache: 'no-cache' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }));
    raiz.textContent = '';
    HOJAS.forEach((h, i) => {
      if (datos[i]) mods[i].datos(datos[i]);
      const d = document.createElement('div'); d.className = 'v2-hoja'; raiz.appendChild(d);
      montar(d, h.hoja, {});
    });
    const corte = cortes(raiz);
    if (corte) $('v2-corte').textContent = corte;
    indice(raiz);
    vigilarDialogos(raiz);
  } catch (e) {
    raiz.innerHTML = '<p class="v2-carga" role="alert">No se pudieron cargar los datos de esta página.</p>';
    console.error(e);
  }
}

// Corte de los datos: el más reciente de la columna «Corte» de las tablas de la página (mensual y trimestral).
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
function cortes(raiz) {
  let m = null, q = null;
  raiz.querySelectorAll('table').forEach((t) => {
    if (t.closest('[role=dialog]')) return;
    const ths = [...t.querySelectorAll('thead th')], k = ths.findIndex((th) => th.textContent.trim() === 'Corte');
    if (k < 0) return;
    t.querySelectorAll('tbody tr').forEach((tr) => {
      const c = tr.children[k]; if (!c) return;
      const v = c.textContent.trim();
      let x = /^([a-z]{3})-(\d{2})$/.exec(v);
      if (x && MESES.includes(x[1])) { const n = +x[2] * 12 + MESES.indexOf(x[1]); if (!m || n > m.n) m = { n, v }; return; }
      x = /^([1-4])T(\d{2})$/.exec(v);
      if (x) { const n = +x[2] * 4 + +x[1]; if (!q || n > q.n) q = { n, v }; }
    });
  });
  const p = [];
  if (m) p.push('mensual a ' + m.v);
  if (q) p.push('trimestral a ' + q.v);
  return p.length ? 'Datos: ' + p.join(' · ') : '';
}
