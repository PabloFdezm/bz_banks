/* Formatos numéricos y de fecha en español (§7.3 del general). Sin DOM.
   Unidad del modelo: 0,05 = 5 %. Signo explícito con U+2212 en cambios, sin signo en niveles. */

const ESPACIO = ' ';
const MENOS = '−';
const AGRUPAR = new Intl.NumberFormat('es-CL', { maximumFractionDigits: 0 });

/* Cifra con coma decimal. signo: «+» en positivos; guion: «-» ASCII en vez de U+2212 (rótulos de
   gráfico que siempre lo llevaron así); miles: separador de miles de es-CL («6.500»);
   fijo: redondeo de Number.toFixed (valor binario exacto: 1,15 → «1,1»), el de la tabla estándar y los
   rótulos de gráfico; sin fijo, el de Intl (decimal más corto: 1,15 → «1,2»). Difieren solo en empates.
   El signo sale del valor ya redondeado: lo que se lee «0,0» no lleva «+» ni «−». */
export function numero(v, decimales = 1, { signo = false, guion = false, miles = true, fijo = false } = {}) {
  if (v == null || Number.isNaN(v)) return '—';
  let s;
  if (fijo) {
    const [entero, fraccion] = Math.abs(v).toFixed(decimales).split('.');
    s = `${miles ? AGRUPAR.format(Number(entero)) : entero}${fraccion ? `,${fraccion}` : ''}`;
  } else {
    s = new Intl.NumberFormat('es-CL', { minimumFractionDigits: decimales, maximumFractionDigits: decimales, useGrouping: miles })
      .format(Math.abs(v));
  }
  const cero = !/[1-9]/.test(s);
  return `${v < 0 && !cero ? (guion ? '-' : MENOS) : signo && v > 0 && !cero ? '+' : ''}${s}`;
}

/* x ya en por ciento: porcentaje(5.2) → «5,2 %» */
export function porcentaje(x, decimales = 1, opciones = {}) {
  if (x == null || Number.isNaN(x)) return '—';
  return `${numero(x, decimales, opciones)}${ESPACIO}%`;
}

/* porcentaje desde unidad: pct(0.052) → «5,2 %» */
export const pct = (v, decimales = 1, conSigno = false) => formatear(v, 'pct', { decimales, signo: conSigno });

/* puntos porcentuales: ya vienen en pp → pp(0.4) → «+0,4 pp» */
export const pp = (v, decimales = 1, conSigno = true, opciones = {}) => formatear(v, 'pp', { ...opciones, decimales, signo: conSigno });

/* Rótulos de gráfico: guion ASCII, sin miles y redondeo de toFixed, como siempre se dibujaron. */
export const ROTULO = { guion: true, miles: false, fijo: true };
/* Celdas de la tabla estándar: U+2212, sin miles y redondeo de toFixed. */
export const TABLA = { miles: false, fijo: true };

/* % de rótulo de gráfico: «12,3 %» con espacio normal. */
export const pctRotulo = (v, decimales = 1) => (v == null || Number.isNaN(v) ? '—' : `${numero(v * 100, decimales, ROTULO)} %`);

/* ---------- Unidades: el único vocabulario de formatos del sitio ----------
   Un formato es el nombre de una unidad ('pct') o { unidad, decimales, signo }. Lo declaran las entradas de
   los componentes (formato, ejeX.formato, ejeIzq…), la franja y las celdas de la tabla estándar (el gold trae
   unidad_ultimo / unidad_cambio con estos nombres).
     pct          fracción → %            (0,052 → «5,2 %»)
     pct_nivel    ya en %                 (5,2 → «5,2 %»)
     pp           puntos porcentuales     (0,4 → «0,4 pp»; con signo «+0,4 pp»)
     pb           fracción → puntos básicos (0,0025 → «25 pb»)
     num          número                  (1,5 → «1,5»)
     brl, brl_mm  reales o R$ mil millones ya escalados, sin decimales («R$ 6.500»)
     reales_a_mm  reales → R$ mil millones (1,2e12 → «1.200,0»): el «brl_mm» de bk_metrica, que trae reales
     texto        tal cual */
const UNIDADES = {
  pct: { decimales: 1, f: (v, d, o) => porcentaje(v * 100, d, o) },
  pct_nivel: { decimales: 1, f: (v, d, o) => porcentaje(v, d, o) },
  pp: { decimales: 1, f: (v, d, o) => `${numero(v, d, o)}${ESPACIO}pp` },
  pb: { decimales: 0, f: (v, d, o) => `${numero(v * 10000, d, o)}${ESPACIO}pb` },
  num: { decimales: 1, f: (v, d, o) => numero(v, d, o) },
  brl: { decimales: 0, f: (v) => `R$ ${numero(v, 0)}` },
  brl_mm: { decimales: 0, f: (v) => `R$ ${numero(v, 0)}` },
  reales_a_mm: { decimales: 1, f: (v, d, o) => numero(v / 1e9, d, o) },
  texto: { f: (v) => String(v) },
};
export const NOMBRES_UNIDAD = Object.keys(UNIDADES);

const leerFormato = (formato) => (typeof formato === 'string' ? { unidad: formato } : { unidad: 'num', ...formato });

export function formatear(v, formato = 'num', opciones = {}) {
  if (v == null || Number.isNaN(v)) return '—';
  const { unidad, ...propias } = leerFormato(formato);
  const u = UNIDADES[unidad];
  if (!u) throw new Error(`unidad desconocida: ${unidad}`);
  const o = { ...propias, ...opciones };
  return u.f(v, o.decimales ?? u.decimales, o);
}

/* Formateador de etiquetas de eje: coma decimal y solo los decimales que hagan falta («2,5 %», nunca
   «2.5 %»), o los fijos que se pidan. Espacio normal y guion ASCII, como el resto de los rótulos. */
const EJE = new Intl.NumberFormat('es-CL', { maximumFractionDigits: 2, useGrouping: false });
const SUFIJO_EJE = { pct: ' %', pct_nivel: ' %', pp: ' pp', num: '' };
export function formatoEje(formato = 'num') {
  const { unidad, decimales } = leerFormato(formato);
  if (!(unidad in SUFIJO_EJE)) throw new Error(`unidad sin eje: ${unidad}`);
  const escala = unidad === 'pct' ? 100 : 1;
  return (v) => {
    const x = v * escala;
    if (decimales != null) return `${numero(x, decimales, ROTULO)}${SUFIJO_EJE[unidad]}`;
    const s = EJE.format(Math.abs(x));
    return `${x < 0 && /[1-9]/.test(s) ? '-' : ''}${s}${SUFIJO_EJE[unidad]}`;
  };
}

/* Juicio de un cambio según el signo de la métrica (§5.3): «sin-cambio» si |delta| ≤ umbral,
   «mejora» o «deterioro» si la métrica tiene sentido (mejora_sube / mejora_baja), si no «neutro». */
export function tono(delta, signo, umbral = 0) {
  if (delta == null || Number.isNaN(delta) || Math.abs(delta) <= umbral) return 'sin-cambio';
  if (signo === 'mejora_sube') return delta > 0 ? 'mejora' : 'deterioro';
  if (signo === 'mejora_baja') return delta > 0 ? 'deterioro' : 'mejora';
  return 'neutro';
}

/* ---------- Fechas y períodos ---------- */
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

function partes(fecha) {
  const d = fecha instanceof Date ? fecha : new Date(`${String(fecha).slice(0, 10)}T00:00:00`);
  return { anio: d.getFullYear(), mes: d.getMonth() + 1 };
}

/* «2026-06-30» → «jun-26» */
export function mmm_aa(fecha) {
  if (!fecha) return '—';
  const { anio, mes } = partes(fecha);
  return `${MESES[mes - 1]}-${String(anio).slice(2)}`;
}

/* «2026-06-30» → «06/26» (eje de categorías mensual) */
export const etiquetaMes = (fecha) => `${fecha.slice(5, 7)}/${fecha.slice(2, 4)}`;

/* trimestre «2T26» desde una fecha o desde un texto de trimestre («2026-T2») */
export function trimestre(fecha) {
  if (!fecha) return '—';
  const s = String(fecha);
  const m = s.match(/(\d{4})[-/]?T?(\d)/i);
  if (m && /T/i.test(s)) return `${m[2]}T${m[1].slice(2)}`;
  const { anio, mes } = partes(fecha);
  return `${Math.floor((mes - 1) / 3) + 1}T${String(anio).slice(2)}`;
}

/* Período AAAAMM de fin de trimestre: «202606» → «2T26» y → «2026-06-30». */
export const trimestreDePeriodo = (p) => `${Math.ceil(Number(p.slice(4, 6)) / 3)}T${p.slice(2, 4)}`;
const FIN_DE_TRIMESTRE = { '03': '31', '06': '30', '09': '30', '12': '31' };
export const finDeTrimestre = (p) => `${p.slice(0, 4)}-${p.slice(4, 6)}-${FIN_DE_TRIMESTRE[p.slice(4, 6)]}`;

/* Los n trimestres calendario que terminan en `ultimo` (AAAAMM), del más antiguo al más reciente.
   Un trimestre sin datos (2024-T4) se conserva como hueco y no desaparece de la escala. */
export function trimestresHasta(ultimo, n) {
  let anio = Number(ultimo.slice(0, 4));
  let mes = Number(ultimo.slice(4, 6));
  const salida = [];
  for (let i = 0; i < n; i += 1) {
    salida.unshift(`${anio}${String(mes).padStart(2, '0')}`);
    mes -= 3;
    if (mes <= 0) { mes += 12; anio -= 1; }
  }
  return salida;
}

/* Número de trimestres de `desde` a `hasta` (AAAAMM), ambos incluidos. */
export function trimestresEntre(desde, hasta) {
  const indice = (p) => Number(p.slice(0, 4)) * 4 + (Number(p.slice(4, 6)) - 1) / 3;
  return indice(hasta) - indice(desde) + 1;
}

/* Hasta n períodos de las filas que terminan en t (orden cronológico). */
export const periodosHasta = (filas, t, n) => [...new Set(filas.map((f) => f.periodo))].filter((p) => p <= t).sort().slice(-n);

/* Comparadores para ordenar filas por fecha o por período. */
export const porFecha = (a, b) => (a.fecha < b.fecha ? -1 : a.fecha > b.fecha ? 1 : 0);
export const porPeriodo = (a, b) => (a.periodo < b.periodo ? -1 : a.periodo > b.periodo ? 1 : 0);
