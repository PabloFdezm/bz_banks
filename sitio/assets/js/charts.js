/* Tema de ECharts y componentes generales (§6 del general). Cada componente es un descriptor
   { dibujar(contenedor, entrada, { titulo }), entrada: [claves que lee], descripcion }; dibujar devuelve la
   instancia de ECharts o null si dibujó HTML (charts_bancos.js arma el registro completo). La entrada la arma
   la config de la tarjeta; nunca el JSON crudo. Tema común: sin toolbox ni dataZoom, animation: false.
   ECharts llega como global (assets/vendor/echarts.min.js). */
import { COLOR, PALETA, TIPO, TRAZO_REFERENCIA } from './tokens.js';
import { numero, mmm_aa, formatear, formatoEje } from './formato.js';
import { el } from './dom.js';

export const C = { ...COLOR, fuente: TIPO.texto, paleta: PALETA };

/* Toda instancia nace aquí: SVG, para que el texto se dibuje con la fuente de la página. */
export const iniciar = (nodo) => window.echarts.init(nodo, null, { renderer: 'svg' });

/* Base de toda opción. La familia tipográfica va siempre: ECharts mide las etiquetas con ella y,
   si no coincide con la del SVG, corta nombres. */
export const tema = (textStyle = {}) => ({ animation: false, backgroundColor: 'transparent', textStyle: { fontFamily: C.fuente, ...textStyle } });

export const tooltip = (trigger, extra = {}) => ({
  trigger, backgroundColor: C.tarjeta, borderColor: C.borde, borderWidth: 1,
  textStyle: { fontFamily: C.fuente, fontSize: 12, color: C.texto }, ...extra,
});

/* Eje sin línea ni marcas; rótulos en gris de 11 px. */
export const ejeBase = (axisLabel = {}, extra = {}) => ({
  axisLine: { show: false }, axisTick: { show: false },
  axisLabel: { color: C.texto3, fontSize: 11, ...axisLabel },
  ...extra,
});

export const GRILLA = { show: true, lineStyle: { color: C.regla, width: 1 } };

/* Eje numérico con título: el del eje Y encima del eje y a la izquierda; el del X, centrado bajo el eje. */
export function ejeNumerico(cfg = {}, eje = 'x') {
  const rotulo = eje === 'y'
    ? { nameLocation: 'end', nameGap: 12, nameTextStyle: { color: C.texto3, fontSize: 11, align: 'left' } }
    : { nameLocation: 'middle', nameGap: 30, nameTextStyle: { color: C.texto3, fontSize: 11 } };
  return ejeBase({ formatter: (v) => formatear(v, cfg.formato) }, {
    type: 'value', scale: true, name: cfg.titulo || '', ...rotulo, splitLine: GRILLA,
  });
}

function base(entrada = {}) {
  return {
    ...tema({ fontSize: 11, color: C.texto2 }),
    grid: { left: 8, right: 12, top: 16, bottom: 4, containLabel: true },
    tooltip: tooltip('axis', { axisPointer: { type: 'line', lineStyle: { color: C.referencia, width: 1 } } }),
    ...entrada,
  };
}

/* Eje de tiempo: con más de 3 años rotula años; si no, mmm-aa. */
function ejeTiempo(ventana) {
  return ejeBase({ margin: 8, formatter: (v) => (ventana > 3 ? String(new Date(v).getFullYear()) : mmm_aa(new Date(v))) }, {
    type: 'time', splitNumber: 6, splitLine: { show: false },
  });
}

const ejeValores = (eje = { unidad: 'num', decimales: 1 }) => ejeBase({ formatter: formatoEje(eje) }, {
  type: 'value', splitLine: { ...GRILLA, lineStyle: { ...GRILLA.lineStyle, type: 'solid' } },
});

function ventanaAnios(series) {
  const t = series.flat().filter(Boolean).map(([f]) => new Date(f).getTime());
  if (!t.length) return 0;
  return (Math.max(...t) - Math.min(...t)) / (365.25 * 24 * 3600 * 1000);
}

/* linea: series temporales [fecha, valor]; los nulos quedan como hueco (no se interpolan). */
function linea(nodo, e = {}) {
  const series = e.series || [];
  const opts = base({
    xAxis: ejeTiempo(ventanaAnios(series.map((s) => s.puntos || []))),
    yAxis: ejeValores(e.eje),
    series: series.map((s) => ({
      name: s.nombre, type: 'line', showSymbol: false,
      data: s.puntos || [],
      lineStyle: { width: s.ancho || 2, color: s.color || C.navy, type: s.discontinua ? TRAZO_REFERENCIA : 'solid' },
      itemStyle: { color: s.color || C.navy },
      z: s.discontinua ? 2 : 3,
    })),
  });
  if (e.formatoTooltip) opts.tooltip.valueFormatter = (v) => formatear(v, e.formatoTooltip);
  if ((e.bandas || []).length) {
    opts.series[0] = opts.series[0] || { type: 'line', data: [] };
    opts.series[0].markArea = {
      silent: true,
      itemStyle: { color: C.regla, opacity: 0.4 },
      label: { color: C.texto3, fontSize: 10 },
      data: e.bandas.map((b) => [{ xAxis: b.desde, name: b.nombre || '' }, { xAxis: b.hasta }]),
    };
  }
  const chart = iniciar(nodo);
  chart.setOption(opts);
  return chart;
}

/* columnas: barras verticales por categoría o por fecha, apilables, con una línea opcional. */
function columnas(nodo, e = {}) {
  const esTiempo = Array.isArray(e.fechas);
  const opts = base({
    xAxis: esTiempo ? ejeTiempo(0) : ejeBase({ interval: 0 }, { type: 'category', data: e.categorias || [], splitLine: { show: false } }),
    yAxis: ejeValores(e.eje),
    series: (e.series || []).map((s, i) => ({
      name: s.nombre, type: 'bar', barMaxWidth: 14, barGap: '20%',
      stack: e.apilar ? 'total' : undefined,
      data: s.valores,
      itemStyle: { color: s.color || C.paleta[i % C.paleta.length] },
    })),
  });
  if (e.linea) {
    opts.series.push({
      name: e.linea.nombre, type: 'line', showSymbol: false, data: e.linea.valores,
      lineStyle: { width: 2, color: C.navy }, itemStyle: { color: C.navy }, z: 5,
    });
  }
  const chart = iniciar(nodo);
  chart.setOption(opts);
  return chart;
}

/* barras_h: barras horizontales por fila (apiladas salvo apilar: false), valores opcionales a la derecha. */
function barras_h(nodo, e = {}) {
  const opts = base({
    grid: { left: 8, right: 40, top: 8, bottom: 4, containLabel: true },
    xAxis: ejeBase({ show: false }, { type: 'value', splitLine: GRILLA }),
    yAxis: ejeBase({ color: C.texto2 }, { type: 'category', data: (e.filas || []).map((f) => f.nombre), inverse: true }),
    series: (e.series || []).map((s, i) => ({
      name: s.nombre, type: 'bar', barWidth: 9, data: s.valores,
      stack: e.apilar === false ? undefined : 'f',
      itemStyle: { color: s.color || C.paleta[i % C.paleta.length] },
      ...(e.mostrarValores ? { label: { show: true, position: 'right', color: C.texto2, fontSize: 11, formatter: (p) => numero(p.value, 1) } } : {}),
    })),
  });
  const chart = iniciar(nodo);
  chart.setOption(opts);
  return chart;
}

/* Contenedor desplazable de una tabla: accesible por teclado y con su desplazamiento conservado al
   redibujar (pagina.js respeta data-conservar-scroll). */
export function cajaDesplazable(clase, titulo) {
  const caja = el('div', `tabla-scroll ${clase || ''}`.trim());
  caja.tabIndex = 0;
  caja.setAttribute('role', 'region');
  caja.setAttribute('aria-label', `${titulo || 'Tabla de datos'}. Desplázate para consultar todas las columnas.`);
  caja.dataset.conservarScroll = '';
  return caja;
}

/* tabla: tabla HTML de columnas declaradas ({ clave, titulo, tipo: 'texto', formatear(v, fila) }). */
function tabla(nodo, e = {}, { titulo } = {}) {
  const cols = e.columnas || [];
  const caja = cajaDesplazable('', titulo);
  const t = el('table', 'tabla-datos');
  const cabecera = el('tr');
  for (const c of cols) cabecera.append(el('th', c.tipo === 'texto' ? '' : 'num', c.titulo));
  const cuerpo = el('tbody');
  for (const f of e.filas || []) {
    const tr = el('tr');
    for (const c of cols) {
      const v = f[c.clave];
      tr.append(el('td', c.tipo === 'texto' ? '' : 'num', c.formatear ? c.formatear(v, f) : (v == null ? '—' : String(v))));
    }
    cuerpo.append(tr);
  }
  const thead = el('thead');
  thead.append(cabecera);
  t.append(thead, cuerpo);
  caja.append(t);
  nodo.replaceChildren(caja);
  return null;
}

export const COMPONENTES_GENERALES = {
  linea: { dibujar: linea, entrada: ['series', 'eje', 'formatoTooltip', 'bandas'], descripcion: 'Líneas en el tiempo ([fecha, valor]); nulos como hueco, bandas de episodios, discontinua para referencias.' },
  columnas: { dibujar: columnas, entrada: ['categorias', 'fechas', 'series', 'apilar', 'linea', 'eje'], descripcion: 'Columnas por categoría o fecha, apilables, con una línea opcional.' },
  barras_h: { dibujar: barras_h, entrada: ['filas', 'series', 'apilar', 'mostrarValores'], descripcion: 'Barras horizontales por fila, apiladas salvo apilar: false; valores a la derecha con mostrarValores.' },
  tabla: { dibujar: tabla, entrada: ['columnas', 'filas'], descripcion: 'Tabla HTML con columnas declaradas (clave, título, tipo, formatear); patrones T4/T8.' },
};
