/* Formatos numéricos y de fecha en español (§7.3 del general).
   Unidad del modelo: 0,05 = 5 %. Signo explícito con U+2212 en cambios, sin signo en niveles. */

const ESPACIO = '\u00A0';
const MENOS = '\u2212';

const nf = (min, max) => new Intl.NumberFormat('es-CL', { minimumFractionDigits: min, maximumFractionDigits: max });

export function numero(v, decimales = 1) {
  if (v == null || Number.isNaN(v)) return '—';
  return nf(decimales, decimales).format(v).replace('-', MENOS);
}

export function nivel(v, decimales = 0) {
  return numero(v, decimales);
}

/* porcentaje desde unidad: pct(0.052) → «5,2 %» */
export function pct(v, decimales = 1, conSigno = false) {
  if (v == null || Number.isNaN(v)) return '—';
  const x = v * 100;
  const s = nf(decimales, decimales).format(Math.abs(x));
  const signo = conSigno ? (x > 0 ? '+' : x < 0 ? MENOS : '') : x < 0 ? MENOS : '';
  return `${signo}${s}${ESPACIO}%`;
}

/* puntos porcentuales: ya vienen en pp (columnas _pp) → pp(0.4) → «+0,4 pp» */
export function pp(v, decimales = 1, conSigno = true) {
  if (v == null || Number.isNaN(v)) return '—';
  const s = nf(decimales, decimales).format(Math.abs(v));
  const signo = conSigno ? (v > 0 ? '+' : v < 0 ? MENOS : '') : v < 0 ? MENOS : '';
  return `${signo}${s}${ESPACIO}pp`;
}

/* puntos básicos, para tasas: pb(0.0025) → «+25 pb» (entrada en unidad) */
export function pb(v, conSigno = true) {
  if (v == null || Number.isNaN(v)) return '—';
  return pp(v * 10000, 0, conSigno).replace('pp', 'pb');
}

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

function partes(fecha) {
  const d = fecha instanceof Date ? fecha : new Date(`${String(fecha).slice(0, 10)}T00:00:00`);
  return { anio: d.getFullYear(), mes: d.getMonth() + 1, dia: d.getDate(), d };
}

export function mmm_aa(fecha) {
  if (!fecha) return '—';
  const { anio, mes } = partes(fecha);
  return `${MESES[mes - 1]}-${String(anio).slice(2)}`;
}

export function dd_mmm_aa(fecha) {
  if (!fecha) return '—';
  const { anio, mes, dia } = partes(fecha);
  return `${String(dia).padStart(2, '0')}-${MESES[mes - 1]}-${String(anio).slice(2)}`;
}

export function anio(fecha) {
  return String(partes(fecha).anio);
}

/* trimestre «2T26» desde una fecha o desde un texto de trimestre */
export function trimestre(fecha) {
  if (!fecha) return '—';
  const s = String(fecha);
  const m = s.match(/(\d{4})[-/]?T?(\d)/i);
  if (m && /T/i.test(s)) return `${m[2]}T${m[1].slice(2)}`;
  const { anio, mes } = partes(fecha);
  return `${Math.floor((mes - 1) / 3) + 1}T${String(anio).slice(2)}`;
}

/* etiqueta de eje: años si la ventana > 3 años, mmm-aa si no (§6 del general) */
export function etiquetaEje(fecha, ventanaAnios) {
  return ventanaAnios > 3 ? anio(fecha) : mmm_aa(fecha);
}

/**
 * Color de signo (§5.4). `signo` es la convención de la página; `invertir` da vuelta
 * el sentido para indicadores donde subir es malo (desocupación, holgura).
 * Devuelve el valor CSS del token, para usarlo tanto en HTML como en ECharts.
 */
export function colorSigno(valor, signo = 'actividad', invertir = false) {
  const css = document.documentElement.style;
  const nav = getComputedStyle(document.documentElement).getPropertyValue('--mejor').trim() || '#123864';
  const cob = getComputedStyle(document.documentElement).getPropertyValue('--peor').trim() || '#A85E24';
  if (valor == null || Number.isNaN(valor) || Math.abs(valor) < 1e-12) return nav;
  const sube = valor > 0;
  let mejora;
  switch (signo) {
    case 'inflacion': mejora = !sube; break;             // ▲ es deterioro
    case 'expectativas': mejora = invertir ? sube : !sube; break;
    case 'fiscal':
    case 'hogares':
    case 'actividad':
    default: mejora = invertir ? !sube : sube; break;    // ▲ es mejora
  }
  void css;
  return mejora ? nav : cob;
}

/* Paleta de series categóricas, en el orden del §5.3. Nunca cobre ni arena para una categoría. */
export function paleta() {
  const g = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  return [g('--navy'), g('--petroleo'), g('--acero'), g('--ciruela'), g('--acero-claro')];
}

export function token(nombre) {
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
}
