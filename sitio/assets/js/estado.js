/* Estado global del sitio de bancos (SPEC_WEB_BANCOS_00_GENERAL.md §3): banco activo y grupo de
   comparación, leídos de la URL (url.js), la lista de bancos y la barra de banco. Grupo y trimestre no
   tienen control en la barra: se fijan por URL. No se guarda nada en storage: la URL basta.
   Sin parámetros: banco nulo, grupo nulo (panel total), último trimestre. Con banco y sin grupo
   explícito, el grupo es el modelo del banco. `grupo=panel` fuerza el panel total. */
import { cargar } from './datos.js';
import { GRUPOS } from './comun.js';
import { parametros, reemplazarUrl } from './url.js';
import { el } from './dom.js';

/* Respaldo de la lista de bancos, copiado el 2026-11-02: se usa solo si bk_banco no está en el
   manifiesto. Slug y nombre_corto vienen de definiciones/bancos__dashboard.json; el modelo de negocio,
   de definiciones/bcb_ifdata__bancos_balances.json (criterio del analista, aprobado por Pablo el 2026-10-09). */
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

/* Filas de bancos: las de bk_banco (slug, nombre_corto, modelo, cod_inst…) o, sin ella, las del respaldo. */
let BANCOS = LISTA.map(([slug, nombre_corto, modelo]) => ({ slug, nombre_corto, modelo }));

/* Si bk_banco está en el manifiesto (data/_manifiesto.json), la lista sale de data/bk_banco.json. */
export async function cargarBancos(tablasExportadas = []) {
  if (!tablasExportadas.includes('bk_banco')) return BANCOS;
  try {
    const filas = (await cargar('bk_banco')).filter((b) => b.slug && b.modelo);
    if (filas.length) BANCOS = filas;
  } catch (e) {
    console.warn('bk_banco no se pudo leer; queda la lista de respaldo', e);
  }
  return BANCOS;
}

function bancoPorSlug(slug) {
  return BANCOS.find((b) => b.slug === slug) || null;
}

export function leer() {
  const p = parametros();
  const banco = bancoPorSlug(p.get('banco') || '');
  const g = p.get('grupo');
  let grupo;
  if (GRUPOS.includes(g)) grupo = g;
  else if (g === 'panel') grupo = null;
  else grupo = banco ? banco.modelo : null;
  return { banco: banco ? banco.slug : null, bancoActivo: banco, grupo, trimestre: p.get('t') || null };
}

/* Cambia banco y grupo en la URL (null o '' los quita) y avisa a las tarjetas [banco] y a la barra. */
function fijar(cambios) {
  const p = parametros();
  for (const [k, v] of Object.entries(cambios)) {
    if (v == null || v === '') p.delete(k);
    else p.set(k, String(v));
  }
  reemplazarUrl(p);
  window.dispatchEvent(new CustomEvent('bancos:estado', { detail: leer() }));
}

/* Al elegir un banco, el grupo de comparación pasa a ser su modelo. */
function elegirBanco(slug) {
  const b = bancoPorSlug(slug);
  fijar({ banco: b ? b.slug : null, grupo: b ? b.modelo : null });
}

export function alCambiar(fn) {
  window.addEventListener('bancos:estado', (e) => fn(e.detail));
}

/* Lleva el foco al selector de banco (botón «Elegir banco» de una tarjeta que lo pide). */
export function enfocarBanco() {
  document.getElementById('banco-activo')?.focus();
}
export const hayBarraDeBanco = () => !!document.getElementById('banco-activo');

/* Barra de banco bajo la cabecera (spec §3): buscador, banco y «Quitar banco». */
export function barra() {
  const nav = el('div', 'barra-banco');
  nav.setAttribute('role', 'region');
  nav.setAttribute('aria-label', 'Contexto y selección de banco');

  const buscar = el('input', 'barra-buscar');
  buscar.type = 'search';
  buscar.id = 'buscar-banco';
  buscar.placeholder = 'Nombre del banco';
  buscar.autocomplete = 'off';
  buscar.setAttribute('aria-controls', 'banco-activo');
  buscar.setAttribute('aria-describedby', 'bancos-resultados');
  const sel = el('select', 'barra-sel');
  sel.id = 'banco-activo';
  sel.setAttribute('aria-label', 'Banco');
  const ayuda = el('span', 'barra-ayuda');
  ayuda.id = 'bancos-resultados';
  ayuda.setAttribute('role', 'status');
  ayuda.setAttribute('aria-live', 'polite');
  const quitar = el('button', 'barra-quitar', 'Quitar banco');
  quitar.type = 'button';

  const campo = (rotulo, control, ...extras) => {
    const caja = el('div', 'barra-campo od-field');
    const label = el('label', 'barra-rotulo', rotulo);
    label.htmlFor = control.id;
    caja.append(label, control, ...extras);
    return caja;
  };
  nav.append(campo('Buscar banco', buscar, ayuda), campo('Banco', sel), quitar);
  const normalizar = (v) => String(v).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  let coincidencias = [];
  function poblarBancos() {
    const filtro = normalizar(buscar.value);
    const actual = leer().banco;
    coincidencias = BANCOS.filter((b) => !filtro || normalizar(`${b.nombre_corto} ${b.slug}`).includes(filtro));
    const visibles = new Set(coincidencias.map((b) => b.slug));
    if (actual) visibles.add(actual);
    sel.replaceChildren(new Option('Seleccionar banco', ''));
    for (const modelo of GRUPOS) {
      const lista = BANCOS.filter((b) => b.modelo === modelo && visibles.has(b.slug));
      if (!lista.length) continue;
      const og = el('optgroup');
      og.label = modelo;
      og.append(...lista.map((b) => new Option(b.nombre_corto, b.slug)));
      sel.append(og);
    }
    sel.value = actual || '';
    ayuda.textContent = filtro
      ? (coincidencias.length ? `${coincidencias.length} ${coincidencias.length === 1 ? 'coincidencia' : 'coincidencias'}. Elige en Banco.` : 'Sin coincidencias. Prueba otro nombre.')
      : '';
  }
  function sincronizar() {
    quitar.hidden = !leer().banco;
    poblarBancos();
  }
  buscar.addEventListener('input', poblarBancos);
  buscar.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && coincidencias.length === 1) {
      e.preventDefault();
      elegirBanco(coincidencias[0].slug);
      sel.focus();
    }
  });
  sel.addEventListener('change', () => elegirBanco(sel.value || null));
  quitar.addEventListener('click', () => {
    buscar.value = '';
    fijar({ banco: null, grupo: null });
    sel.focus();
  });
  alCambiar(sincronizar);
  sincronizar();
  return nav;
}
