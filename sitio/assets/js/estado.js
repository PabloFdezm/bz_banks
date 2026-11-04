import { RUTA_DATOS } from './config.js';

/* Estado global del sitio de bancos (SPEC_WEB_BANCOS_00_GENERAL.md §3). La URL es la fuente de verdad:
     ?banco=<slug>&optica=modelo&grupo=<grupo>&t=<AAAAMM>
   Sin parámetros: banco nulo, óptica «Modelo de negocio», grupo nulo (panel total), último trimestre.
   Con banco y sin grupo explícito, el grupo es el modelo del banco. `grupo=panel` fuerza el panel total.
   No se guarda nada en storage: la URL basta. */

/* Copia al construir el sitio (2026-11-02); no se lee en tiempo de ejecución. Slug y nombre_corto vienen
   de definiciones/bancos__dashboard.json; el modelo de negocio, de definiciones/bcb_ifdata__bancos_balances.json
   (criterio del analista, aprobado por Pablo el 2026-10-09). */
const LISTA = [
  ['itau', 'Itaú Unibanco', 'Grandes'],
  ['bradesco', 'Bradesco', 'Grandes'],
  ['bb', 'Banco do Brasil', 'Grandes'],
  ['santander', 'Santander Brasil', 'Grandes'],
  ['btg', 'BTG Pactual', 'Grandes'],
  ['nubank', 'Nubank', 'Digitales'],
  ['xp', 'XP', 'Digitales'],
  ['safra', 'Safra', 'Medianos y nicho'],
  ['c6', 'C6 Bank', 'Digitales'],
  ['votorantim', 'Votorantim', 'Medianos y nicho'],
  ['inter', 'Inter', 'Digitales'],
  ['daycoval', 'Daycoval', 'Medianos y nicho'],
  ['abc', 'ABC Brasil', 'Medianos y nicho'],
  ['agibank', 'Agibank', 'Digitales'],
  ['bmg', 'BMG', 'Medianos y nicho'],
  ['mercantil', 'Mercantil do Brasil', 'Medianos y nicho'],
  ['pine', 'Pine', 'Medianos y nicho'],
  ['sofisa', 'Sofisa', 'Medianos y nicho'],
  ['original', 'Original', 'Digitales'],
  ['banrisul', 'Banrisul', 'Medianos y nicho'],
  ['banestes', 'Banestes', 'Medianos y nicho'],
  ['basa', 'Banco da Amazônia', 'Desarrollo'],
  ['bnb', 'Banco do Nordeste', 'Desarrollo'],
  ['caixa', 'Caixa', 'Grandes'],
  ['bndes', 'BNDES', 'Desarrollo'],
  ['brb', 'BRB', 'Medianos y nicho'],
  ['mercadopago', 'Mercado Pago', 'Pagos'],
  ['pagseguro', 'PagSeguro', 'Pagos'],
  ['stone', 'Stone', 'Pagos'],
  ['picpay', 'PicPay', 'Pagos'],
  ['neon', 'Neon', 'Digitales'],
  ['cielo', 'Cielo', 'Pagos'],
  ['cloudwalk', 'CloudWalk', 'Pagos'],
  ['porto', 'Porto Seguro', 'Medianos y nicho'],
];

export let BANCOS = LISTA.map(([slug, nombre, modelo]) => ({ slug, nombre, modelo }));

export const GRUPOS = ['Grandes', 'Digitales', 'Medianos y nicho', 'Pagos', 'Desarrollo'];

/* Colores de categoría fijos en todo el sitio (spec web §5). Panel total = tinta. */
export const COLOR_GRUPO = {
  Grandes: '#2E5C8A', // v2: navy suavizado
  Digitales: '#2F7A86',
  'Medianos y nicho': '#6C819B',
  Pagos: '#7B5E8C',
  Desarrollo: '#A9B8CB',
  Panel: '#1B2433',
};

const URL_CLAVE = { banco: 'banco', optica: 'optica', grupo: 'grupo', trimestre: 't' };

/* Trimestres disponibles para el selector; los pone cada página cuando haya datos (fijarTrimestres). */
let TRIMESTRES = [];

/* Si bk_banco está en el manifiesto (data/_manifiesto.json), la lista sale de data/bk_banco.json;
   si no, queda la constante de respaldo. Acepta nombres de columna nombre/nombre_corto y modelo/modelo_negocio. */
export async function cargarBancos(tablasExportadas = []) {
  if (!tablasExportadas.includes('bk_banco')) return BANCOS;
  try {
    const r = await fetch(`${RUTA_DATOS}bk_banco.json`);
    if (!r.ok) return BANCOS;
    const j = await r.json();
    const col = (...nombres) => nombres.map((n) => j.columnas.indexOf(n)).find((i) => i >= 0);
    const cs = col('slug');
    const cn = col('nombre', 'nombre_corto');
    const cm = col('modelo', 'modelo_negocio');
    if ([cs, cn, cm].some((i) => i === undefined)) return BANCOS;
    const cc = col('cod_inst'); // v3: la franja de la Ficha filtra por cod_inst
    const lista = j.filas.map((f) => ({ slug: f[cs], nombre: f[cn], modelo: f[cm], cod: cc === undefined ? null : f[cc] })).filter((b) => b.slug && b.modelo);
    if (lista.length) BANCOS = lista;
  } catch { /* sin datos: se queda con la constante */ }
  return BANCOS;
}

export function bancoPorSlug(slug) {
  return BANCOS.find((b) => b.slug === slug) || null;
}

function parametros() {
  try { return new URLSearchParams(location.search); } catch { return new URLSearchParams(); }
}

export function leer() {
  const p = parametros();
  const banco = bancoPorSlug(p.get('banco') || '') ? p.get('banco') : null;
  const g = p.get('grupo');
  let grupo;
  if (GRUPOS.includes(g)) grupo = g;
  else if (g === 'panel') grupo = null;
  else grupo = banco ? bancoPorSlug(banco).modelo : null;
  return {
    banco,
    optica: p.get('optica') || 'modelo',
    grupo,
    trimestre: p.get('t') || null,
  };
}

/* Cambia parámetros de la URL (null o '' los quita) y avisa a las tarjetas [banco] y a la barra. */
export function fijar(cambios = {}) {
  const p = parametros();
  for (const [k, v] of Object.entries(cambios)) {
    const clave = URL_CLAVE[k];
    if (!clave) continue;
    if (v == null || v === '') p.delete(clave);
    else p.set(clave, String(v));
  }
  const q = p.toString();
  try {
    history.replaceState(history.state, '', `${location.pathname}${q ? `?${q}` : ''}${location.hash}`);
  } catch { /* sin historial: el estado sigue en memoria de la página */ }
  window.dispatchEvent(new CustomEvent('bancos:estado', { detail: leer() }));
}

/* Al elegir un banco, el grupo de comparación pasa a ser su modelo (se puede cambiar después). */
export function elegirBanco(slug) {
  const b = bancoPorSlug(slug);
  fijar({ banco: b ? b.slug : null, grupo: b ? b.modelo : null });
}

export function fijarTrimestres(lista) {
  TRIMESTRES = Array.isArray(lista) ? lista : [];
  window.dispatchEvent(new CustomEvent('bancos:estado', { detail: leer() }));
}

export function alCambiar(fn) {
  window.addEventListener('bancos:estado', (e) => fn(e.detail));
}

/* Los enlaces de la cabecera conservan los parámetros del estado (spec §3). */
export function enlazarCabecera() {
  for (const a of document.querySelectorAll('a[data-base]')) a.href = a.dataset.base + location.search;
}

function trimestreTexto(t) {
  if (!/^\d{6}$/.test(t)) return t;
  return `${Math.ceil(Number(t.slice(4)) / 3)}T${t.slice(2, 4)}`;
}

/* Barra de banco activo bajo la cabecera (spec §3): banco, grupo, trimestre y «Quitar banco». 48 px, fija. */
export function barra() {
  const nav = document.createElement('div');
  nav.className = 'barra-banco';
  nav.setAttribute('role', 'region');
  nav.setAttribute('aria-label', 'Banco activo y grupo de comparación');

  const activo = document.createElement('span');
  activo.className = 'barra-activo';

  const buscar = document.createElement('input');
  buscar.type = 'search';
  buscar.className = 'barra-buscar';
  buscar.placeholder = 'Buscar';
  buscar.setAttribute('aria-label', 'Buscar banco');

  const sel = document.createElement('select');
  sel.className = 'barra-sel';
  sel.setAttribute('aria-label', 'Banco');

  const grupo = document.createElement('select');
  grupo.className = 'barra-sel';
  grupo.setAttribute('aria-label', 'Grupo de comparación');
  grupo.append(new Option('Panel total', 'panel'), ...GRUPOS.map((g) => new Option(g, g)));

  const tri = document.createElement('select');
  tri.className = 'barra-sel';
  tri.setAttribute('aria-label', 'Trimestre');

  const quitar = document.createElement('button');
  quitar.type = 'button';
  quitar.className = 'barra-quitar';
  quitar.textContent = 'Quitar banco';

  const campo = (rotulo, ...controles) => {
    const l = document.createElement('div');
    l.className = 'barra-campo';
    const r = document.createElement('span');
    r.className = 'barra-rotulo';
    r.textContent = rotulo;
    l.append(r, ...controles);
    return l;
  };
  nav.append(activo, campo('Banco', buscar, sel), campo('Grupo', grupo), campo('Trimestre', tri), quitar);

  function poblarBancos() {
    const f = buscar.value.trim().toLowerCase();
    const actual = leer().banco;
    sel.replaceChildren(new Option('Sin banco', ''));
    for (const modelo of GRUPOS) {
      const lista = BANCOS.filter((b) => b.modelo === modelo
        && (b.slug === actual || !f || b.nombre.toLowerCase().includes(f) || b.slug.includes(f)));
      if (!lista.length) continue;
      const og = document.createElement('optgroup');
      og.label = modelo;
      og.append(...lista.map((b) => new Option(b.nombre, b.slug)));
      sel.append(og);
    }
    sel.value = actual || '';
  }

  function sincronizar() {
    const e = leer();
    const b = bancoPorSlug(e.banco);
    activo.replaceChildren();
    activo.classList.toggle('con-banco', !!b);
    if (b) {
      const n = document.createElement('b');
      n.textContent = b.nombre;
      activo.append(n, document.createTextNode(` · grupo ${e.grupo || 'panel total'}`));
    } else {
      activo.textContent = 'Sin banco seleccionado';
    }
    quitar.hidden = !b;
    grupo.value = e.grupo || 'panel';
    tri.replaceChildren(new Option('Último', ''), ...TRIMESTRES.map((t) => new Option(trimestreTexto(t), t)));
    tri.value = e.trimestre && TRIMESTRES.includes(e.trimestre) ? e.trimestre : '';
    poblarBancos();
  }

  buscar.addEventListener('input', poblarBancos);
  sel.addEventListener('change', () => elegirBanco(sel.value || null));
  grupo.addEventListener('change', () => fijar({ grupo: grupo.value }));
  tri.addEventListener('change', () => fijar({ trimestre: tri.value || null }));
  quitar.addEventListener('click', () => fijar({ banco: null, grupo: null }));
  window.addEventListener('bancos:estado', sincronizar);
  sincronizar();
  return nav;
}
