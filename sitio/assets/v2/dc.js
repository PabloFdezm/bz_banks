// Intérprete de las plantillas del canvas de rediseño (formato x-dc) para el sitio.
// Soporta el subconjunto que usan las hojas: {{ruta}} en atributos y texto, <sc-for list as>, <sc-if value>,
// <dc-import name cfg>, eventos onX="{{fn}}" y clases `Component extends DCLogic` con renderVals().
// El render actualiza el DOM en su lugar (sin recrear nodos), así que el estado del navegador (foco, captura del
// puntero, scroll) se conserva entre renders.

const REG = {};
const EVENTOS = { click: 'click', change: 'change', keydown: 'keydown', mouseenter: 'mouseenter', mouseleave: 'mouseleave',
  focus: 'focus', pointerdown: 'pointerdown', pointermove: 'pointermove', pointerup: 'pointerup', input: 'input' };

export class DCLogic {
  constructor(p) { this.props = p || {}; this.state = {}; }
  setState(o) { Object.assign(this.state, o); if (this.__pedir) this.__pedir(); }
}

function preparar(html) {
  const i = html.indexOf('<x-dc>'), j = html.lastIndexOf('</x-dc>');
  let cuerpo = i >= 0 ? html.slice(i + 6, j) : html;
  let estilos = '';
  const h0 = cuerpo.indexOf('<helmet>'), h1 = cuerpo.indexOf('</helmet>');
  if (h0 >= 0) { estilos = cuerpo.slice(h0 + 8, h1); cuerpo = cuerpo.slice(0, h0) + cuerpo.slice(h1 + 9); }
  cuerpo = cuerpo.replace(/<sc-for\b/g, '<template data-scfor').replace(/<\/sc-for>/g, '</template>')
    .replace(/<sc-if\b/g, '<template data-scif').replace(/<\/sc-if>/g, '</template>');
  const t = document.createElement('template');
  t.innerHTML = cuerpo;
  return { raiz: t.content, estilos };
}

export function registrar(nombre, html, Clase) {
  REG[nombre] = { ...preparar(html), Clase, nombre };
}

const ESTILOS_PUESTOS = new Set();
function ponerEstilos(def) {
  if (ESTILOS_PUESTOS.has(def.nombre) || !def.estilos) return;
  ESTILOS_PUESTOS.add(def.nombre);
  const t = document.createElement('template');
  t.innerHTML = def.estilos;
  t.content.querySelectorAll('style').forEach((s) => { const x = document.createElement('style'); x.textContent = s.textContent.replace(/body\{margin:0\}/g, ''); x.dataset.dc = def.nombre; document.head.appendChild(x); });
  t.content.querySelectorAll('link[rel="stylesheet"]').forEach((l) => {
    if ([...document.querySelectorAll('link[rel="stylesheet"]')].some((y) => y.href === l.href)) return;
    const x = document.createElement('link'); x.rel = 'stylesheet'; x.href = l.getAttribute('href'); document.head.appendChild(x);
  });
}

const UNA = /^\{\{\s*([^}]+?)\s*\}\}$/;
const VARIAS = /\{\{\s*([^}]+?)\s*\}\}/g;
function valor(expr, ambito) {
  if (expr === 'true') return true;
  if (expr === 'false') return false;
  if (expr === 'null') return null;
  if (/^-?\d+(\.\d+)?$/.test(expr)) return +expr;
  let v = ambito;
  for (const p of expr.split('.')) { if (v == null) return undefined; v = v[p]; }
  return v;
}
const texto = (s, ambito) => s.indexOf('{{') < 0 ? s : s.replace(VARIAS, (_, e) => { const v = valor(e, ambito); return v == null ? '' : String(v); });

function atributos(nodo, t, ambito) {
  let valorSelect;
  for (const a of t.attributes) {
    const n = a.name;
    if (n.startsWith('hint-') || n.startsWith('data-scf') || n.startsWith('data-sci')) continue;
    if (n.startsWith('on') && EVENTOS[n.slice(2)]) {
      const ev = EVENTOS[n.slice(2)], m = UNA.exec(a.value), fn = m ? valor(m[1], ambito) : null;
      nodo.__h = nodo.__h || {}; nodo.__l = nodo.__l || {};
      nodo.__h[ev] = typeof fn === 'function' ? fn : null;
      if (!nodo.__l[ev]) { nodo.__l[ev] = true; nodo.addEventListener(ev, (e) => { const f = nodo.__h[ev]; if (f) f(e); }); }
      continue;
    }
    const m = UNA.exec(a.value);
    const v = m ? valor(m[1], ambito) : texto(a.value, ambito);
    if (n === 'value' && (nodo.localName === 'select' || nodo.localName === 'input')) { valorSelect = v; continue; }
    if (v === false || v == null) { if (nodo.hasAttribute(n)) nodo.removeAttribute(n); continue; }
    const s = v === true ? '' : String(v);
    if (nodo.getAttribute(n) !== s) nodo.setAttribute(n, s);
  }
  return valorSelect;
}

function recortar(padre, desde) { while (padre.childNodes.length > desde) padre.removeChild(padre.lastChild); }

function lista(tnodos, ambito, padre, pos) {
  for (const t of tnodos) {
    if (t.nodeType === 3) {
      const s = texto(t.data, ambito);
      const nodo = padre.childNodes[pos];
      if (nodo && nodo.nodeType === 3) { if (nodo.data !== s) nodo.data = s; }
      else padre.insertBefore(document.createTextNode(s), nodo || null);
      pos++;
      continue;
    }
    if (t.nodeType !== 1) continue;
    if (t.localName === 'template' && t.hasAttribute('data-scfor')) {
      const m = UNA.exec(t.getAttribute('list') || ''), items = (m ? valor(m[1], ambito) : null) || [], como = t.getAttribute('as');
      for (const it of items) { const a = Object.create(ambito); a[como] = it; pos = lista(t.content.childNodes, a, padre, pos); }
      continue;
    }
    if (t.localName === 'template' && t.hasAttribute('data-scif')) {
      const m = UNA.exec(t.getAttribute('value') || '');
      if (m && valor(m[1], ambito)) pos = lista(t.content.childNodes, ambito, padre, pos);
      continue;
    }
    let nodo = padre.childNodes[pos];
    if (!nodo || nodo.nodeType !== 1 || nodo.localName !== t.localName || nodo.namespaceURI !== t.namespaceURI) {
      const nuevo = document.createElementNS(t.namespaceURI, t.localName);
      padre.insertBefore(nuevo, nodo || null);
      nodo = nuevo;
    }
    const vs = atributos(nodo, t, ambito);
    if (t.localName === 'dc-import') {
      const m = UNA.exec(t.getAttribute('cfg') || '');
      montarEn(nodo, t.getAttribute('name'), { cfg: m ? valor(m[1], ambito) : undefined });
    } else {
      const fin = lista(t.childNodes, ambito, nodo, 0);
      recortar(nodo, fin);
      if (vs !== undefined && nodo.value !== String(vs)) nodo.value = vs == null ? '' : String(vs);
    }
    pos++;
  }
  return pos;
}

function montarEn(host, nombre, props) {
  const def = REG[nombre];
  if (!def) throw new Error('componente no registrado: ' + nombre);
  let inst = host.__dc;
  if (!inst || inst.__nombre !== nombre) {
    ponerEstilos(def);
    inst = new def.Clase(props);
    inst.__nombre = nombre;
    let pendiente = false;
    inst.__render = () => { pendiente = false; const v = inst.renderVals(); const fin = lista(def.raiz.childNodes, v, host, 0); recortar(host, fin); };
    inst.__pedir = () => { if (!pendiente) { pendiente = true; requestAnimationFrame(() => inst.__render()); } };
    host.__dc = inst;
    if (host.localName === 'dc-import') host.style.display = 'block';
  } else {
    inst.props = props;
  }
  inst.__render();
  return inst;
}

export function montar(host, nombre, props) { return montarEn(host, nombre, props || {}); }
