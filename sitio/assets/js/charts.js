/* Componentes de gráfico (§6 del general). Cada uno: componente(el, entrada, opciones) → chart.
   La entrada es un objeto simple que arma la config de la tarjeta; nunca el JSON crudo.
   Tema común: sin leyenda de ECharts (la leyenda es HTML), sin toolbox, sin dataZoom, animation:false. */
import { token, paleta, numero, pct, pp, mmm_aa, anio } from './formato.js';

export const C = {};
function cargarColores() {
  const g = token;
  Object.assign(C, {
    fondo: g('--fondo'), texto: g('--texto'), texto2: g('--texto-2'), texto3: g('--texto-3'),
    borde: g('--borde'), regla: g('--regla'), navy: g('--navy'), petroleo: g('--petroleo'),
    acero: g('--acero'), ciruela: g('--ciruela'), aceroClaro: g('--acero-claro'),
    mejor: g('--mejor'), peor: g('--peor'), cobre: g('--cobre'), arena: g('--arena'),
    referencia: g('--referencia'), fuente: g('--fuente'),
    paleta: paleta(),
  });
}
cargarColores();

const REF_TRAZO = [6, 4];

function base(entrada = {}) {
  return {
    animation: false,
    backgroundColor: 'transparent',
    textStyle: { fontFamily: C.fuente, fontSize: 11, color: C.texto2 },
    grid: { left: 8, right: 12, top: 16, bottom: 4, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#FFFFFF', borderColor: C.borde, borderWidth: 1,
      textStyle: { fontFamily: C.fuente, fontSize: 12, color: C.texto },
      axisPointer: { type: 'line', lineStyle: { color: C.reglas || C.referencia, width: 1 } },
    },
    ...entrada,
  };
}

function ejeTiempo(entrada = {}) {
  const ventana = entrada.ventanaAnios || 0;
  return {
    type: 'time',
    splitNumber: 6,
    axisLine: { show: false }, axisTick: { show: false },
    axisLabel: {
      color: C.texto3, fontSize: 11, margin: 8,
      formatter: (v) => {
        const d = new Date(v);
        return ventana > 3 ? String(d.getFullYear()) : mmm_aa(d);
      },
    },
    splitLine: { show: false },
    ...(entrada.ejeX || {}),
  };
}

function ejeValores(entrada = {}) {
  const f = entrada.formatear || ((v) => numero(v, 1));
  return {
    type: 'value',
    axisLine: { show: false }, axisTick: { show: false },
    axisLabel: { color: C.texto3, fontSize: 11, formatter: f },
    splitLine: { show: true, lineStyle: { color: C.regla, width: 1, type: 'solid' } },
    // bancos: título del eje Y encima del eje, a la izquierda, sin montarse sobre las etiquetas
    ...(entrada.tituloY ? { name: entrada.tituloY, nameLocation: 'end', nameGap: 12, nameTextStyle: { color: C.texto3, fontSize: 11, align: 'left' } } : {}),
    ...(entrada.ejeY || {}),
  };
}

function ventanaAnios(serie) {
  const t = serie.flat().filter(Boolean).map(([f]) => new Date(f).getTime());
  if (!t.length) return 0;
  return (Math.max(...t) - Math.min(...t)) / (365.25 * 24 * 3600 * 1000);
}

/* ---------- linea ---------- */
export function linea(el, e = {}) {
  const series = e.series || [];
  const va = e.ventanaAnios || ventanaAnios(series.map((s) => s.puntos || []));
  const opts = base({
    xAxis: e.categorias
      ? {
          type: 'category', data: e.categorias, boundaryGap: e.boundaryGap ?? false,
          axisLine: { show: false }, axisTick: { show: false },
          axisLabel: { color: C.texto3, fontSize: 11, interval: 0 },
          splitLine: { show: false },
        }
      : ejeTiempo({ ...e, ventanaAnios: va }),
    yAxis: ejeValores(e),
    series: [],
  });

  if (e.tituloY) opts.grid = { ...opts.grid, top: 34 }; // bancos: sitio para el título del eje Y
  for (const s of series) {
    opts.series.push({
      name: s.nombre, type: 'line', showSymbol: false,
      // bancos: los nulos se quedan en la serie; connectNulls es false, así el hueco no se interpola
      data: s.puntos || [],
      lineStyle: {
        width: s.ancho || 2,
        color: s.color || C.navy,
        type: s.discontinua ? REF_TRAZO : 'solid',
      },
      itemStyle: { color: s.color || C.navy },
      z: s.discontinua ? 2 : 3,
      ...(s.area ? { areaStyle: { color: s.area, opacity: s.areaOpacidad ?? 0.18 } } : {}),
    });
  }
  // área entre dos series (§6: base = mínimo, banda = diferencia, dos colores)
  if (e.area && Array.isArray(e.area.entre) && series.length >= 2) {
    const [i, j] = e.area.entre;
    const a = series[i].puntos || [], b = series[j].puntos || [];
    const mapaB = new Map(b.map(([f, v]) => [String(f).slice(0, 10), v]));
    const basePts = [], bandaPts = [];
    for (const [f, v] of a) {
      const w = mapaB.get(String(f).slice(0, 10));
      if (v == null || w == null) continue;
      basePts.push([f, Math.min(v, w)]);
      bandaPts.push([f, Math.abs(v - w)]);
    }
    const encima = (e.area.colores && e.area.colores.arriba) || C.aceroClaro;
    const debajo = (e.area.colores && e.area.colores.abajo) || C.arena;
    opts.series.push(
      { name: '_base', type: 'line', data: basePts, showSymbol: false, stack: '_area', lineStyle: { opacity: 0 }, symbol: 'none', tooltip: { show: false }, silent: true },
      { name: '_banda', type: 'line', data: bandaPts, showSymbol: false, stack: '_area', lineStyle: { opacity: 0 }, symbol: 'none', areaStyle: { color: encima, opacity: 0.55 }, tooltip: { show: false }, silent: true },
    );
    void debajo;
  }
  // referencias: meta, promedio, contrafactual → gris discontinuo (§5.3)
  if ((e.refs || []).length) {
    opts.series[0] = opts.series[0] || { type: 'line', data: [] };
    opts.series[0].markLine = {
      silent: true, symbol: 'none',
      label: { color: C.texto3, fontSize: 11, position: 'insideEndTop', formatter: (p) => p.name || '' },
      lineStyle: { color: C.referencia, width: 1.5, type: REF_TRAZO },
      data: e.refs.map((r) => ({ yAxis: r.valor, name: r.nombre || '' })),
    };
  }
  // bancos: quiebres = líneas verticales grises discontinuas con rótulo arriba (se suman a las refs)
  if ((e.marcas || []).length) {
    const s0 = opts.series.find((s) => s.type === 'line' && !String(s.name || '').startsWith('_')) || opts.series[0];
    if (s0) {
      s0.markLine = s0.markLine || {
        silent: true, symbol: 'none',
        label: { color: C.texto3, fontSize: 11, position: 'insideEndTop', formatter: (p) => p.name || '' },
        lineStyle: { color: C.referencia, width: 1, type: REF_TRAZO },
        data: [],
      };
      s0.markLine.data = [...(s0.markLine.data || []), ...e.marcas.map((m) => ({ xAxis: m.fecha, name: m.nombre || '' }))];
    }
  }
  // bandas de episodios
  if ((e.bandas || []).length) {
    opts.series[0] = opts.series[0] || { type: 'line', data: [] };
    opts.series[0].markArea = {
      silent: true,
      itemStyle: { color: C.regla, opacity: 0.4 },
      label: { color: C.texto3, fontSize: 10 },
      data: e.bandas.map((b) => [{ xAxis: b.desde, name: b.nombre || '' }, { xAxis: b.hasta }]),
    };
  }
  const chart = echarts.init(el, null, { renderer: 'svg' });
  chart.setOption(opts);
  return chart;
}

/* ---------- columnas ---------- */
export function columnas(el, e = {}) {
  const cats = e.categorias || (e.fechas || []).map((f) => mmm_aa(f));
  const esTiempo = Array.isArray(e.fechas);
  const opts = base({
    xAxis: esTiempo ? ejeTiempo(e) : {
      type: 'category', data: cats,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: C.texto3, fontSize: 11, interval: 0, rotate: e.rotular ? 30 : 0 },
      splitLine: { show: false },
    },
    yAxis: ejeValores(e),
    series: (e.series || []).map((s, i) => ({
      name: s.nombre, type: 'bar', barMaxWidth: 14, barGap: '20%',
      stack: e.apilar ? 'total' : undefined,
      data: s.valores,
      // bancos: color por punto en itemStyle (antes se ignoraba)
      itemStyle: { color: s.colorPorPunto ? ({ dataIndex }) => s.colorPorPunto[dataIndex] : (s.color || C.paleta[i % C.paleta.length]) },
    })),
  });
  if (e.tituloY) opts.grid = { ...opts.grid, top: 34 }; // bancos: sitio para el título del eje Y
  if (e.linea) {
    opts.series.push({
      name: e.linea.nombre, type: 'line', showSymbol: false, data: e.linea.valores,
      lineStyle: { width: 2, color: C.navy }, itemStyle: { color: C.navy }, z: 5,
    });
  }
  const chart = echarts.init(el, null, { renderer: 'svg' });
  chart.setOption(opts);
  return chart;
}

/* ---------- barras_h ---------- */
export function barras_h(el, e = {}) {
  const nombres = (e.filas || []).map((f) => f.nombre);
  const opts = base({
    grid: { left: 8, right: 40, top: 8, bottom: 4, containLabel: true },
    xAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { show: false }, splitLine: { show: true, lineStyle: { color: C.regla, width: 1 } } },
    yAxis: { type: 'category', data: nombres, inverse: true, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: C.texto2, fontSize: 11 } },
    series: (e.series || []).map((s, i) => ({
      name: s.nombre, type: 'bar', barWidth: 9, data: s.valores,
      stack: e.apilar === false ? undefined : 'f',
      itemStyle: { color: s.color || C.paleta[i % C.paleta.length] },
      ...(e.mostrarValores ? { label: { show: true, position: 'right', color: C.texto2, fontSize: 11, formatter: (p) => numero(p.value, 1) } } : {}),
    })),
  });
  const chart = echarts.init(el, null, { renderer: 'svg' });
  chart.setOption(opts);
  return chart;
}

/* ---------- tabla (HTML, no ECharts; patrones T4/T8) ---------- */
export function tabla(el, e = {}) {
  const cols = e.columnas || [];
  const t = document.createElement('div');
  t.className = 'tabla-scroll';
  const thead = cols.map((c) => `<th class="${c.tipo === 'texto' ? '' : 'num'}"${c.ancho ? ` style="width:${c.ancho}"` : ''}>${c.titulo}</th>`).join('');
  const cuerpo = (e.filas || []).map((f) => `<tr>${cols.map((c) => {
    const v = f[c.clave ?? c.titulo];
    const txt = c.formatear ? c.formatear(v, f) : (v == null ? '—' : String(v));
    const estilo = c.color ? ` style="color:${typeof c.color === 'function' ? c.color(v, f) : c.color};font-weight:600"` : '';
    return `<td class="${c.tipo === 'texto' ? '' : 'num'}"${estilo}>${txt}</td>`;
  }).join('')}</tr>`).join('');
  t.innerHTML = `<table class="tabla-datos"><thead><tr>${thead}</tr></thead><tbody>${cuerpo}</tbody></table>`;
  el.replaceChildren(t);
  return null;
}

/* ---------- registro ---------- */
export const COMPONENTES = { linea, columnas, barras_h, tabla };

export function hay(nombre) { return Object.prototype.hasOwnProperty.call(COMPONENTES, nombre); }

export { pct, pp, numero, anio, token, paleta };
