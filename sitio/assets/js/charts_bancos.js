/* Componentes propios de bancos (SPEC_WEB_BANCOS_00_GENERAL.md §6): percentiles, cascada_doble,
   burbujas_trayectoria, small_multiples_bancos y comparador. Python calcula todo; aquí solo se dibuja.
   Cada uno: componente(zona, entrada, opciones) → chart o null. Tema común: colores C de charts.js.
   Ninguno calcula ratios, percentiles ni agregados: la suma acumulada de la cascada es posición en pantalla. */
import { C, linea } from './charts.js'; // bancos: linea para la línea de la Ficha
import { numero, pct, pb, pp } from './formato.js';
import { COLOR_GRUPO } from './estado.js';

const NS = 'http://www.w3.org/2000/svg';

function nodo(tag, clase, texto) {
  const n = document.createElement(tag);
  if (clase) n.className = clase;
  if (texto != null) n.textContent = texto;
  return n;
}

/* Formatos de la entrada: los valores vienen en unidad (0,05 = 5 %), salvo los de pp, que vienen en pp. */
export function formatear(v, f) {
  if (v == null || Number.isNaN(v)) return '—';
  switch (f) {
    case 'pct': return pct(v, 1);
    case 'pct0': return pct(v, 0);
    case 'pb': return pb(v, false);
    case 'pp': return pp(v, 1, false);
    case 'ppSigno': return pp(v, 1, true);
    case 'num0': return numero(v, 0);
    case 'texto': return String(v);
    default: return numero(v, 1);
  }
}

/* ---------- percentiles (HTML, una fila de 40 px por métrica) ---------- */
function colorBanco(f) {
  if (f.signo === 'mejora_sube') return f.valor >= f.p50 ? C.navy : C.peor;
  if (f.signo === 'mejora_baja') return f.valor <= f.p50 ? C.navy : C.peor;
  return C.texto2; // neutro: gris, sin juicio de mejora (§5)
}

function filaPercentil(f) {
  const fila = nodo('div', 'pct-fila');
  fila.append(nodo('span', 'pct-nombre', f.nombre || f.metrica || ''));
  const escala = nodo('div', 'pct-escala');
  if (f.p10 == null || f.p50 == null || f.p90 == null) {
    escala.append(nodo('span', 'pct-sin', 'sin dato del grupo'));
  } else {
    // escala propia de la fila: p10–p90 del grupo más el banco, con 15 % de margen
    const puntos = [f.p10, f.p90, f.valor, f.valor_t4].filter((v) => v != null);
    const lo0 = Math.min(...puntos);
    const hi0 = Math.max(...puntos);
    const m = 0.15 * ((hi0 - lo0) || Math.abs(hi0) || 1);
    const lo = lo0 - m;
    const hi = hi0 + m;
    const x = (v) => ((v - lo) / (hi - lo)) * 100;

    const rango = nodo('div', 'pct-rango');
    rango.style.left = `${x(f.p10)}%`;
    rango.style.width = `${x(f.p90) - x(f.p10)}%`;
    const mediana = nodo('div', 'pct-mediana');
    mediana.style.left = `${x(f.p50)}%`;
    escala.append(rango, mediana);

    if (f.valor != null && f.valor_t4 != null) {
      const union = nodo('div', 'pct-enlace');
      const a = Math.min(f.valor, f.valor_t4);
      const b = Math.max(f.valor, f.valor_t4);
      union.style.left = `${x(a)}%`;
      union.style.width = `${x(b) - x(a)}%`;
      escala.append(union);
    }
    if (f.valor_t4 != null) {
      const t4 = nodo('div', 'pct-punto-t4');
      t4.style.left = `${x(f.valor_t4)}%`;
      escala.append(t4);
    }
    if (f.valor != null) {
      const punto = nodo('div', 'pct-punto');
      punto.style.left = `${x(f.valor)}%`;
      punto.style.background = colorBanco(f);
      escala.append(punto);
    }
    const txt = (v) => formatear(v, f.formato);
    fila.title = `p10 ${txt(f.p10)} · mediana ${txt(f.p50)} · p90 ${txt(f.p90)} · banco ${txt(f.valor)}`
      + (f.valor_t4 != null ? ` · hace un año ${txt(f.valor_t4)}` : '');
  }
  fila.append(escala, nodo('span', 'pct-valor', formatear(f.valor, f.formato)));
  return fila;
}

export function percentiles(zona, e = {}) {
  zona.classList.add('pct');
  const lista = nodo('div', 'pct-lista');
  for (const f of e.filas || []) lista.append(filaPercentil(f));
  zona.append(lista);
  return null;
}

/* ---------- caja con nota (// bancos:) ----------
   Una tarjeta con nota del banco (quiebre, líneas omitidas) pone el cuerpo y la nota dentro de su zona.
   La zona se vacía en cada dibujo, así que la nota nunca queda de un banco anterior. */
function caja(zona, nota) {
  const envoltura = nodo('div', 'con-nota-caja');
  const cuerpo = nodo('div', 'con-nota-cuerpo');
  envoltura.append(cuerpo);
  if (nota) envoltura.append(nodo('p', 'con-nota', nota));
  zona.replaceChildren(envoltura);
  return cuerpo;
}

/* ---------- cascada_doble (HTML: banco y mediana del grupo en paralelo, misma secuencia) ---------- */
function pista(intervalo, valor, x, color) {
  const p = nodo('div', 'cas-pista');
  const cero = nodo('div', 'cas-cero');
  cero.style.left = `${x(0)}%`;
  const i = Math.min(...intervalo);
  const j = Math.max(...intervalo);
  const barra = nodo('div', 'cas-barra');
  barra.style.left = `${x(i)}%`;
  barra.style.width = `${Math.max(x(j) - x(i), 0.4)}%`;
  barra.style.background = color;
  const etiqueta = nodo('span', 'cas-etiqueta', pp(valor * 100, 1, true));
  etiqueta.style.left = `${x(j)}%`;
  p.append(cero, barra, etiqueta);
  return p;
}

export function cascada_doble(zona, e = {}) {
  const body = caja(zona, e.nota); // bancos: nota bajo la cascada
  body.classList.add('cas');
  const filas = [];
  let ab = 0;
  let ag = 0;
  for (const l of e.lineas || []) {
    filas.push({ nombre: l.nombre, b: [ab, ab + l.banco], g: [ag, ag + l.grupo], vb: l.banco, vg: l.grupo, total: false });
    ab += l.banco;
    ag += l.grupo;
  }
  if (e.total) {
    filas.push({ nombre: e.total.nombre, b: [0, e.total.banco], g: [0, e.total.grupo], vb: e.total.banco, vg: e.total.grupo, total: true });
  }
  const vals = filas.flatMap((f) => [...f.b, ...f.g, 0]);
  const lo0 = Math.min(...vals);
  const hi0 = Math.max(...vals);
  const m = 0.12 * ((hi0 - lo0) || 1);
  const lo = lo0 - m;
  const hi = hi0 + m;
  const x = (v) => ((v - lo) / (hi - lo)) * 100;

  const cab = nodo('div', 'cas-fila cas-cab');
  cab.append(nodo('span', 'cas-col', ''), nodo('span', 'cas-col', 'Banco'), nodo('span', 'cas-col', 'Mediana del grupo'), nodo('span', 'cas-col cas-brecha', 'Brecha'));
  body.append(cab);

  for (const f of filas) {
    const fila = nodo('div', `cas-fila${f.total ? ' cas-total' : ''}`);
    const colorBancoPaso = f.total ? C.acero : (f.vb >= 0 ? C.navy : C.cobre);
    const colorGrupoPaso = f.total ? C.acero : C.aceroClaro;
    const brecha = (f.vb - f.vg) * 100;
    fila.append(
      nodo('span', 'cas-nombre', f.nombre),
      pista(f.b, f.vb, x, colorBancoPaso),
      pista(f.g, f.vg, x, colorGrupoPaso),
      nodo('span', `cas-brecha ${brecha >= 0 ? 'cas-pos' : 'cas-neg'}`, pp(brecha, 1, true)),
    );
    body.append(fila);
  }
  return null;
}

/* ---------- linea_banco (// bancos:) ----------
   La línea de la Ficha: `linea` del macro con porcentajes en el eje y en el tooltip (formato de la
   Ficha, no cálculo), más la nota del banco bajo el gráfico. Las bandas de quiebre vienen de la página. */
export function linea_banco(zona, e = {}) {
  const cuerpo = caja(zona, e.nota);
  const chart = linea(cuerpo, { ...e, formatear: (v) => pct(v, 0) });
  if (chart) chart.setOption({ tooltip: { valueFormatter: (v) => pct(v, 1) } });
  return chart;
}

/* ---------- burbujas_trayectoria (ECharts, dispersión + trayectorias trimestrales) ---------- */
function ejeNumerico(cfg = {}, eje = 'x') {
  // bancos: el título del eje Y va encima del eje y a la izquierda; el del eje X, centrado bajo el eje
  const rotulo = eje === 'y'
    ? { nameLocation: 'end', nameGap: 12, nameTextStyle: { color: C.texto3, fontSize: 11, align: 'left' } }
    : { nameLocation: 'middle', nameGap: 30, nameTextStyle: { color: C.texto3, fontSize: 11 } };
  return {
    type: 'value',
    scale: true,
    name: cfg.titulo || '',
    ...rotulo,
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: C.texto3, fontSize: 11, formatter: (v) => formatear(v, cfg.formato) },
    splitLine: { show: true, lineStyle: { color: C.regla, width: 1 } },
  };
}

export function burbujas_trayectoria(zona, e = {}) {
  const activo = e.banco || null;
  const puntos = e.puntos || [];
  const tmax = Math.max(1, ...puntos.map((p) => p.tamaño || 0));
  const colorPunto = (p) => {
    if (activo) return p.banco === activo ? C.navy : C.aceroClaro;
    return COLOR_GRUPO[p.grupo] || COLOR_GRUPO.Panel;
  };
  // trayectoria: solo la del banco activo; sin banco, la de los Grandes
  const trayectorias = (e.trayectorias || []).filter((t) => (activo ? t.banco === activo : t.grupo === 'Grandes'));

  const series = [{
    type: 'scatter',
    name: 'Bancos',
    z: 3,
    data: puntos.map((p) => ({
      value: [p.x, p.y],
      name: p.nombre || p.banco,
      symbolSize: 8 + 26 * Math.sqrt((p.tamaño || 0) / tmax),
      itemStyle: {
        color: colorPunto(p),
        borderColor: p.banco === activo ? C.navy : '#FFFFFF',
        borderWidth: p.banco === activo ? 2.5 : 1,
      },
    })),
  }];
  for (const t of trayectorias) {
    const color = activo ? C.navy : (COLOR_GRUPO[t.grupo] || C.acero);
    const n = t.puntos.length;
    series.push({
      type: 'line',
      name: t.nombre || t.banco,
      z: 4,
      symbol: 'circle',
      lineStyle: { width: 1.5, color },
      itemStyle: { color },
      data: t.puntos.map(([x, y, tri], i) => ({
        value: [x, y],
        tri,
        symbolSize: i === n - 1 ? 10 : 4,
        label: i === n - 1 ? { show: true, formatter: t.nombre || t.banco, position: 'right', fontSize: 11, color: C.texto2 } : { show: false },
      })),
    });
  }

  const opts = {
    animation: false,
    backgroundColor: 'transparent',
    textStyle: { fontFamily: C.fuente, fontSize: 11, color: C.texto2 },
    grid: { left: 8, right: 96, top: e.ejeY?.titulo ? 36 : 16, bottom: 4, containLabel: true }, // margen para la etiqueta del último punto y, con título, el del eje Y
    tooltip: {
      trigger: 'item',
      backgroundColor: '#FFFFFF',
      borderColor: C.borde,
      borderWidth: 1,
      textStyle: { fontFamily: C.fuente, fontSize: 12, color: C.texto },
      formatter: (p) => {
        const d = p.data || {};
        const v = Array.isArray(d.value) ? d.value : [];
        const tri = d.tri ? ` · ${d.tri}` : '';
        return `<b>${d.name || p.seriesName}</b>${tri}<br>${e.ejeX?.titulo || 'x'}: ${formatear(v[0], e.ejeX?.formato)}`
          + `<br>${e.ejeY?.titulo || 'y'}: ${formatear(v[1], e.ejeY?.formato)}`;
      },
    },
    xAxis: ejeNumerico(e.ejeX, 'x'),
    yAxis: ejeNumerico(e.ejeY, 'y'),
    series,
  };
  const chart = echarts.init(zona, null, { renderer: 'svg' });
  chart.setOption(opts);
  return chart;
}

/* ---------- small_multiples_bancos (SVG propio, escala común) ---------- */
function sparkline(puntos, esc, colorTrazo, ancho = 100, alto = 40) {
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', `0 0 ${ancho} ${alto}`);
  svg.setAttribute('preserveAspectRatio', 'none');
  svg.setAttribute('aria-hidden', 'true');
  const n = puntos.length;
  const rango = (esc.max - esc.min) || 1;
  const x = (i) => (n <= 1 ? 0 : (i / (n - 1)) * ancho);
  const y = (v) => alto - ((v - esc.min) / rango) * alto;
  let d = '';
  let abierto = false;
  puntos.forEach(([, v], i) => {
    if (v == null) { abierto = false; return; }
    d += `${abierto ? 'L' : 'M'}${x(i).toFixed(2)},${y(v).toFixed(2)} `;
    abierto = true;
  });
  const path = document.createElementNS(NS, 'path');
  path.setAttribute('d', d.trim());
  path.setAttribute('fill', 'none');
  path.setAttribute('stroke', colorTrazo);
  path.setAttribute('stroke-width', '1.5');
  path.setAttribute('vector-effect', 'non-scaling-stroke');
  svg.append(path);
  return svg;
}

export function small_multiples_bancos(zona, e = {}) {
  const paneles = e.paneles || [];
  const todos = paneles.flatMap((p) => (p.puntos || []).map(([, v]) => v).filter((v) => v != null));
  const esc = e.escala || { min: Math.min(...todos), max: Math.max(...todos) };
  const grid = nodo('div', 'sm-grid');
  grid.style.gridTemplateColumns = `repeat(${e.columnas || 6}, minmax(0, 1fr))`;
  for (const p of paneles) {
    const f = nodo('figure', `sm-panel${p.destacado ? ' sm-destacado' : ''}`);
    f.setAttribute('aria-label', p.nombre || p.banco || '');
    const ultimo = [...(p.puntos || [])].reverse().find(([, v]) => v != null);
    // nombre completo en su propia línea, valor debajo: nada se trunca
    const cab = nodo('figcaption', 'sm-cab');
    cab.append(nodo('span', 'sm-nombre', p.nombre || p.banco || ''));
    cab.append(nodo('span', 'sm-valor', ultimo ? formatear(ultimo[1], e.formato) : '—'));
    f.append(cab, sparkline(p.puntos || [], esc, p.destacado ? C.navy : C.aceroClaro));
    grid.append(f);
  }
  zona.append(grid);
  return null;
}

/* ---------- comparador (HTML: tabla ordenable, filtros, sparklines, CSV de lo visible) ---------- */
function valorDe(f, clave) {
  return clave === 'nombre' ? f.nombre : (f.valores?.[clave] ?? f[clave]);
}

function textoCelda(f, c) {
  if (c.spark) return (f.serie || []).map((v) => formatear(v, c.formato)).join(' · ');
  const v = valorDe(f, c.clave);
  return c.tipo === 'texto' ? (v == null ? '—' : String(v)) : formatear(v, c.formato);
}

function celdaCsv(v) {
  const s = String(v ?? '');
  return /[;"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function comparador(zona, e = {}) {
  zona.classList.add('cmp');
  const columnas = e.columnas || [];
  const filas = e.filas || [];
  const filtros = e.filtros || [];
  const bancoActivo = e.banco || null;
  const estado = {
    orden: { ...(e.orden || { clave: columnas[0]?.clave, dir: 'desc' }) },
    sel: Object.fromEntries(filtros.map((f) => [f.clave, new Set()])),
  };

  const barra = nodo('div', 'cmp-barra');
  const chips = nodo('div', 'cmp-chips');
  const chipsPorFiltro = [];
  for (const f of filtros) {
    const grupo = nodo('div', 'cmp-grupo');
    grupo.append(nodo('span', 'cmp-rotulo', f.titulo));
    const valores = [...new Set(filas.map((r) => r.filtros?.[f.clave]).filter(Boolean))];
    for (const v of valores) {
      const b = nodo('button', 'cmp-chip', v);
      b.type = 'button';
      b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', () => {
        const s = estado.sel[f.clave];
        if (s.has(v)) s.delete(v); else s.add(v);
        render();
      });
      chipsPorFiltro.push({ f, v, b });
      grupo.append(b);
    }
    chips.append(grupo);
  }
  const cuenta = nodo('span', 'cmp-cuenta');
  const csv = nodo('button', 'cmp-csv', 'Descargar CSV');
  csv.type = 'button';
  barra.append(chips, cuenta, csv);
  const scroll = nodo('div', 'cmp-scroll');
  zona.replaceChildren(barra, scroll);

  function visibles() {
    const r = filas.filter((f) => filtros.every((ff) => !estado.sel[ff.clave].size || estado.sel[ff.clave].has(f.filtros?.[ff.clave])));
    const { clave, dir } = estado.orden;
    const col = columnas.find((c) => c.clave === clave);
    return [...r].sort((a, b) => {
      const x = valorDe(a, clave);
      const y = valorDe(b, clave);
      if (x == null) return 1;
      if (y == null) return -1;
      const c = col?.tipo === 'texto' ? String(x).localeCompare(String(y), 'es') : x - y;
      return dir === 'asc' ? c : -c;
    });
  }

  function render() {
    for (const { f, v, b } of chipsPorFiltro) {
      const on = estado.sel[f.clave].has(v);
      b.classList.toggle('activo', on);
      b.setAttribute('aria-pressed', String(on));
    }
    const filas2 = visibles();
    cuenta.textContent = `${filas2.length} de ${filas.length} bancos`;

    const tabla = nodo('table', 'tabla-datos cmp-tabla');
    const thead = document.createElement('thead');
    const trh = document.createElement('tr');
    for (const c of columnas) {
      const th = document.createElement('th');
      th.className = c.tipo === 'texto' ? '' : 'num';
      const activa = estado.orden.clave === c.clave;
      th.setAttribute('aria-sort', activa ? (estado.orden.dir === 'asc' ? 'ascending' : 'descending') : 'none');
      const b = nodo('button', 'cmp-orden', c.titulo + (activa ? (estado.orden.dir === 'asc' ? ' ▲' : ' ▼') : ''));
      b.type = 'button';
      if (c.spark) b.disabled = true;
      b.addEventListener('click', () => {
        const dir = activa && estado.orden.dir === 'desc' ? 'asc' : 'desc';
        estado.orden = { clave: c.clave, dir };
        render();
      });
      th.append(b);
      trh.append(th);
    }
    thead.append(trh);
    tabla.append(thead);

    const tbody = document.createElement('tbody');
    for (const f of filas2) {
      const tr = document.createElement('tr');
      tr.className = f.slug && f.slug === bancoActivo ? 'cmp-activo' : '';
      tr.tabIndex = 0;
      tr.setAttribute('role', 'link');
      const ir = () => { location.href = `/ficha/?banco=${encodeURIComponent(f.slug)}`; };
      tr.addEventListener('click', ir);
      tr.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') ir(); });
      for (const c of columnas) {
        const td = document.createElement('td');
        td.className = c.tipo === 'texto' ? '' : 'num';
        if (c.spark) {
          td.classList.add('cmp-spark');
          const serie = f.serie || [];
          const vals = serie.map(([, v]) => v).filter((v) => v != null);
          const esc = { min: Math.min(...vals), max: Math.max(...vals) };
          td.append(sparkline(serie, esc, C.navy, 80, 18));
        } else {
          td.textContent = textoCelda(f, c);
          if (c.color) td.style.color = c.color(valorDe(f, c.clave), f);
        }
        tr.append(td);
      }
      tbody.append(tr);
    }
    tabla.append(tbody);
    scroll.replaceChildren(tabla);
  }

  csv.addEventListener('click', () => {
    const filas2 = visibles();
    const lineas = [columnas.map((c) => c.titulo)]
      .concat(filas2.map((f) => columnas.map((c) => textoCelda(f, c))))
      .map((l) => l.map(celdaCsv).join(';'));
    const blob = new Blob([`﻿${lineas.join('\r\n')}`], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'bancos_comparador.csv';
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });

  render();
  return null;
}

/* ---------- piezas de la ola 3 (encargo 76). La entrada llega calculada; aquí solo se dibuja. ---------- */
const POCOS_TRIMESTRES = 24; // barras_ic: con menos trimestres se marca «pocos trimestres» (§7.6)

/* Tinta o blanco, lo que se lea sobre un fondo hex. */
function textoSobre(fondo) {
  const m = /^#([0-9a-f]{6})$/i.exec(fondo || '');
  if (!m) return '#FFFFFF';
  const n = parseInt(m[1], 16);
  const luz = 0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255);
  return luz > 150 ? C.texto : '#FFFFFF';
}

/* Color y flecha de un cambio según el signo de la métrica (§5.3). Dentro del umbral: «=» en gris. */
function colorCambio(cambio, signo, umbral = 0) {
  if (cambio == null || Number.isNaN(cambio) || Math.abs(cambio) <= umbral) return { color: C.texto3, flecha: '=' };
  const sube = cambio > 0;
  const flecha = sube ? '▲' : '▼';
  if (signo === 'mejora_sube') return { color: sube ? C.navy : C.peor, flecha };
  if (signo === 'mejora_baja') return { color: sube ? C.peor : C.navy, flecha };
  return { color: C.texto2, flecha };
}

/* Marcas de corte (mediana o cero) para dispersión y trayectoria. */
function marcaCortes(cortes) {
  if (!cortes) return null;
  const data = [];
  if (cortes.x != null) data.push({ xAxis: cortes.x });
  if (cortes.y != null) data.push({ yAxis: cortes.y });
  if (!data.length) return null;
  return { silent: true, symbol: 'none', label: { show: false }, lineStyle: { color: C.referencia, width: 1, type: 'solid' }, data };
}

/* Textos de cuadrante: superposiciones HTML en las esquinas de la zona (no capturan el puntero). */
function cuadrantes(zona, textos = {}) {
  for (const [pos, texto] of Object.entries(textos)) {
    if (texto) zona.append(nodo('span', `dis-cuadrante dis-${pos}`, texto));
  }
}

/* ---------- apilada_100 (HTML: barras horizontales al 100 %; rótulo dentro si la parte es ≥ 8 %) ---------- */
export function apilada_100(zona, e = {}) {
  zona.classList.add('ap');
  const barras = e.barras || [];
  const lista = nodo('div', 'ap-lista');
  for (const b of barras) {
    const partes = b.partes || [];
    const total = partes.reduce((a, p) => a + (p.valor || 0), 0) || 1;
    const fila = nodo('div', 'ap-fila');
    fila.append(nodo('span', 'ap-nombre', b.nombre || ''));
    const barra = nodo('div', 'ap-barra');
    for (const p of partes) {
      const parte = (p.valor || 0) / total;
      const color = p.color || C.aceroClaro;
      const seg = nodo('div', 'ap-seg');
      seg.style.width = `${parte * 100}%`;
      seg.style.background = color;
      seg.title = `${p.nombre}: ${formatear(p.valor, e.formato || 'pct')}`;
      if (parte >= 0.08) {
        const r = nodo('span', 'ap-rotulo', formatear(p.valor, e.formatoRotulo || 'pct0'));
        r.style.color = textoSobre(color);
        seg.append(r);
      }
      barra.append(seg);
    }
    fila.append(barra);
    lista.append(fila);
  }
  const leyenda = nodo('div', 'ap-leyenda');
  for (const p of barras[0]?.partes || []) {
    const item = nodo('span');
    const sw = nodo('i');
    sw.style.background = p.color || C.aceroClaro;
    item.append(sw, document.createTextNode(p.nombre || ''));
    leyenda.append(item);
  }
  zona.replaceChildren(lista, leyenda);
  return null;
}

/* ---------- pesas (HTML: antes y ahora por fila; color del cambio por signo de la métrica) ---------- */
export function pesas(zona, e = {}) {
  zona.classList.add('pes');
  const filas = e.filas || [];
  const vals = filas.flatMap((f) => [f.antes, f.ahora]).filter((v) => v != null);
  const lo = e.escala ? e.escala[0] : (vals.length ? Math.min(...vals) : 0);
  const hi = e.escala ? e.escala[1] : (vals.length ? Math.max(...vals) : 1);
  const x = (v) => ((v - lo) / ((hi - lo) || 1)) * 100;
  const lista = nodo('div', 'pes-lista');
  const cab = nodo('div', 'pes-fila pes-cab');
  cab.append(nodo('span', 'pes-nombre', ''), nodo('span', 'pes-escala', 'antes ○ · ahora ●'), nodo('span', 'pes-texto', 'antes → ahora'));
  lista.append(cab);
  for (const f of filas) {
    const ok = f.antes != null && f.ahora != null;
    const { color, flecha } = ok ? colorCambio(f.ahora - f.antes, f.signo, e.umbral ?? 0) : { color: C.texto3, flecha: '' };
    const fila = nodo('div', `pes-fila${f.destacada ? ' pes-destacada' : ''}`);
    const escala = nodo('div', 'pes-escala');
    if (ok) {
      const a = Math.min(f.antes, f.ahora);
      const b = Math.max(f.antes, f.ahora);
      const tramo = nodo('div', 'pes-tramo');
      tramo.style.left = `${x(a)}%`;
      tramo.style.width = `${x(b) - x(a)}%`;
      tramo.style.background = color;
      const antes = nodo('div', 'pes-antes');
      antes.style.left = `${x(f.antes)}%`;
      const ahora = nodo('div', 'pes-ahora');
      ahora.style.left = `${x(f.ahora)}%`;
      ahora.style.background = color;
      escala.append(tramo, antes, ahora);
    }
    const texto = nodo('span', 'pes-texto', ok ? `${flecha} ${formatear(f.antes, e.formato)} → ${formatear(f.ahora, e.formato)}` : 'sin dato');
    texto.style.color = color;
    fila.append(nodo('span', 'pes-nombre', f.nombre || ''), escala, texto);
    lista.append(fila);
  }
  zona.replaceChildren(lista);
  return null;
}

/* ---------- dispersion (ECharts: puntos con nombre, cortes en la mediana o en cero, diagonal opcional) ---------- */
export function dispersion(zona, e = {}) {
  const puntos = e.puntos || [];
  const todos = puntos.flatMap((p) => [p.x, p.y]).filter((v) => v != null);
  const lo = todos.length ? Math.min(...todos) : 0;
  const hi = todos.length ? Math.max(...todos) : 1;
  const series = [{
    type: 'scatter', name: 'Bancos', z: 3,
    labelLayout: { hideOverlap: true },
    markLine: marcaCortes(e.cortes) || undefined,
    data: puntos.map((p) => ({
      value: [p.x, p.y],
      name: p.nombre || p.banco || '',
      symbolSize: p.destacado ? 11 : 8,
      itemStyle: { color: p.destacado ? C.texto : C.acero, borderColor: '#FFFFFF', borderWidth: 1 },
      label: {
        show: true, formatter: p.nombre || p.banco || '', position: 'right', fontSize: 11,
        color: p.destacado ? C.texto : C.texto2, fontWeight: p.destacado ? 600 : 400,
      },
    })),
  }];
  if (e.diagonal && todos.length) {
    series.push({
      type: 'line', name: 'Diagonal', z: 2, silent: true, symbol: 'none', tooltip: { show: false },
      lineStyle: { color: C.referencia, width: 1, type: 'dashed' }, data: [[lo, lo], [hi, hi]],
    });
  }
  const chart = echarts.init(zona, null, { renderer: 'svg' });
  chart.setOption({
    animation: false,
    backgroundColor: 'transparent',
    textStyle: { fontFamily: C.fuente, fontSize: 11, color: C.texto2 },
    grid: { left: 8, right: 16, top: 36, bottom: 4, containLabel: true },
    tooltip: {
      trigger: 'item', backgroundColor: '#FFFFFF', borderColor: C.borde, borderWidth: 1,
      textStyle: { fontFamily: C.fuente, fontSize: 12, color: C.texto },
      formatter: (p) => {
        const v = Array.isArray(p.data?.value) ? p.data.value : [];
        return `<b>${p.data?.name || ''}</b><br>${e.ejeX?.titulo || 'x'}: ${formatear(v[0], e.ejeX?.formato)}`
          + `<br>${e.ejeY?.titulo || 'y'}: ${formatear(v[1], e.ejeY?.formato)}`;
      },
    },
    xAxis: ejeNumerico(e.ejeX, 'x'),
    yAxis: ejeNumerico(e.ejeY, 'y'),
    series,
  });
  cuadrantes(zona, e.cuadrantes);
  return chart;
}

/* ---------- barras_h_doble (ECharts: dos barras por fila, no apiladas; banco activo resaltado) ---------- */
export function barras_h_doble(zona, e = {}) {
  const filas = e.filas || [];
  const series = e.series || [];
  const formato = e.formato || 'pct';
  const activo = e.activo || null;
  const chart = echarts.init(zona, null, { renderer: 'svg' });
  chart.setOption({
    animation: false,
    backgroundColor: 'transparent',
    textStyle: { fontFamily: C.fuente, fontSize: 11, color: C.texto2 },
    grid: { left: 8, right: 64, top: 8, bottom: 4, containLabel: true },
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: '#FFFFFF', borderColor: C.borde, borderWidth: 1,
      textStyle: { fontFamily: C.fuente, fontSize: 12, color: C.texto },
      valueFormatter: (v) => formatear(v, formato),
    },
    xAxis: {
      type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { show: false },
      splitLine: { show: true, lineStyle: { color: C.regla, width: 1 } },
    },
    yAxis: {
      type: 'category', data: filas.map((r) => r.nombre), inverse: true,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: {
        color: C.texto2, fontSize: 11,
        formatter: (n, i) => (activo && filas[i]?.slug === activo ? `{activo|${n}}` : n),
        rich: { activo: { color: C.texto, fontWeight: 600 } },
      },
    },
    series: series.map((s, k) => ({
      name: s.nombre, type: 'bar', barWidth: 7, barGap: '30%',
      data: filas.map((r) => ({
        value: r.valores?.[k] ?? null,
        itemStyle: { color: s.color || C.paleta[k % C.paleta.length], opacity: activo && r.slug !== activo ? 0.4 : 1 },
      })),
      label: { show: true, position: 'right', color: C.texto2, fontSize: 11, formatter: (p) => formatear(p.value, formato) },
    })),
  });
  return chart;
}

/* ---------- barras_ic (HTML: barra con intervalo; «pocos trimestres» si n < 24) ---------- */
export function barras_ic(zona, e = {}) {
  zona.classList.add('ic');
  const filas = e.filas || [];
  const minimo = e.minTrimestres ?? POCOS_TRIMESTRES;
  const vals = filas.flatMap((f) => [0, f.valor, f.bajo, f.alto]).filter((v) => v != null && !Number.isNaN(v));
  const lo0 = vals.length ? Math.min(...vals) : 0;
  const hi0 = vals.length ? Math.max(...vals) : 1;
  const m = 0.05 * ((hi0 - lo0) || 1);
  const lo = lo0 - m;
  const hi = hi0 + m;
  const x = (v) => ((v - lo) / ((hi - lo) || 1)) * 100;
  const lista = nodo('div', 'ic-lista');
  for (const f of filas) {
    const esActivo = !!e.activo && f.slug === e.activo;
    const fila = nodo('div', `ic-fila${esActivo ? ' ic-activo' : ''}`);
    const pista = nodo('div', 'ic-pista');
    const cero = nodo('div', 'ic-cero');
    cero.style.left = `${x(0)}%`;
    pista.append(cero);
    if (f.valor != null) {
      const a = Math.min(x(0), x(f.valor));
      const b = Math.max(x(0), x(f.valor));
      const barra = nodo('div', 'ic-barra');
      barra.style.left = `${a}%`;
      barra.style.width = `${Math.max(b - a, 0.3)}%`;
      barra.style.background = esActivo ? C.navy : C.aceroClaro;
      pista.append(barra);
    }
    if (f.bajo != null && f.alto != null) {
      const intervalo = nodo('div', 'ic-int');
      intervalo.style.left = `${x(f.bajo)}%`;
      intervalo.style.width = `${Math.max(x(f.alto) - x(f.bajo), 0.3)}%`;
      pista.append(intervalo);
    }
    fila.append(nodo('span', 'ic-nombre', f.nombre || ''), pista, nodo('span', 'ic-valor', formatear(f.valor, e.formato)));
    if (f.n != null && f.n < minimo) {
      const marca = nodo('span', 'ic-marca', 'pocos trimestres');
      marca.title = `n = ${numero(f.n, 0)} trimestres (mínimo ${minimo})`;
      fila.append(marca);
    }
    lista.append(fila);
  }
  zona.replaceChildren(lista);
  return null;
}

/* ---------- trayectoria (ECharts: G3; «hoy» marcado en negro, rótulos de año en su primer punto) ---------- */
export function trayectoria(zona, e = {}) {
  const puntos = e.puntos || [];
  const n = puntos.length;
  const etiquetaHoy = e.etiquetaHoy || 'hoy';
  const data = puntos.map((p, i) => {
    const hoy = i === n - 1;
    const texto = hoy ? etiquetaHoy : (p.rotulo || '');
    return {
      value: [p.x, p.y],
      symbolSize: hoy ? 10 : 4,
      itemStyle: { color: hoy ? C.texto : C.acero },
      label: texto
        ? { show: true, formatter: texto, position: hoy ? 'right' : 'top', fontSize: 11, color: hoy ? C.texto : C.texto3, fontWeight: hoy ? 600 : 400 }
        : { show: false },
    };
  });
  const serie = {
    type: 'line', name: 'Trayectoria', z: 3, symbol: 'circle', showSymbol: true,
    lineStyle: { width: 1.5, color: C.acero }, itemStyle: { color: C.acero },
    markLine: marcaCortes(e.cortes) || undefined,
    data,
  };
  const chart = echarts.init(zona, null, { renderer: 'svg' });
  chart.setOption({
    animation: false,
    backgroundColor: 'transparent',
    textStyle: { fontFamily: C.fuente, fontSize: 11, color: C.texto2 },
    grid: { left: 8, right: 64, top: e.ejeY?.titulo ? 36 : 16, bottom: 4, containLabel: true },
    tooltip: {
      trigger: 'item', backgroundColor: '#FFFFFF', borderColor: C.borde, borderWidth: 1,
      textStyle: { fontFamily: C.fuente, fontSize: 12, color: C.texto },
      formatter: (p) => {
        const v = Array.isArray(p.data?.value) ? p.data.value : [];
        return `${e.ejeX?.titulo || 'x'}: ${formatear(v[0], e.ejeX?.formato)}<br>${e.ejeY?.titulo || 'y'}: ${formatear(v[1], e.ejeY?.formato)}`;
      },
    },
    xAxis: ejeNumerico(e.ejeX, 'x'),
    yAxis: ejeNumerico(e.ejeY, 'y'),
    series: [serie],
  });
  return chart;
}

/* ---------- small_multiples (HTML genérico: un panel por serie, misma escala, años inicial y final) ---------- */
export function small_multiples(zona, e = {}) {
  const paneles = e.paneles || [];
  const todos = paneles.flatMap((p) => (p.puntos || []).map(([, v]) => v).filter((v) => v != null));
  const esc = e.escala
    ? { min: e.escala[0], max: e.escala[1] }
    : { min: todos.length ? Math.min(...todos) : 0, max: todos.length ? Math.max(...todos) : 1 };
  const grid = nodo('div', 'sm-grid');
  grid.style.gridTemplateColumns = `repeat(${e.columnas || 4}, minmax(0, 1fr))`;
  for (const p of paneles) {
    const pts = p.puntos || [];
    const f = nodo('figure', `sm-panel${p.destacado ? ' sm-destacado' : ''}`);
    const ultimo = [...pts].reverse().find(([, v]) => v != null);
    const cab = nodo('figcaption', 'sm-cab');
    cab.append(nodo('span', 'sm-nombre', p.titulo || p.nombre || ''), nodo('span', 'sm-valor', ultimo ? formatear(ultimo[1], e.formato) : '—'));
    const anios = nodo('div', 'sm-anios');
    anios.append(nodo('span', '', pts.length ? String(pts[0][0]).slice(0, 4) : ''), nodo('span', '', pts.length ? String(pts[pts.length - 1][0]).slice(0, 4) : ''));
    f.append(cab, sparkline(pts, esc, p.destacado ? C.navy : C.acero, 100, 40), anios);
    grid.append(f);
  }
  zona.replaceChildren(grid);
  return null;
}

/* ---------- puertas (HTML: una línea por página con su pregunta; el enlace conserva el banco activo) ---------- */
export function puertas(zona, e = {}) {
  zona.removeAttribute('role'); // bancos: no es una imagen; la lista es texto y enlaces
  zona.removeAttribute('aria-label');
  const lista = nodo('ul', 'puertas-lista');
  lista.style.cssText = 'list-style:none;margin:0;padding:0;display:grid;gap:16px;';
  for (const p of e.enlaces || []) {
    const li = nodo('li');
    const a = nodo('a', 'puerta-enlace', p.nombre);
    a.style.cssText = 'font-weight:600;font-size:16px;';
    a.dataset.base = p.ruta ? `/${p.ruta}/` : '/';
    a.href = a.dataset.base + location.search;
    a.addEventListener('click', () => { a.href = a.dataset.base + location.search; }); // el banco activo puede haber cambiado desde que se dibujó
    const pregunta = nodo('p', 'puerta-pregunta', p.pregunta);
    pregunta.style.cssText = 'margin:4px 0 0;color:var(--texto-2);font-size:14px;';
    li.append(a, pregunta);
    lista.append(li);
  }
  zona.replaceChildren(lista);
  return null;
}

/* ---------- mosaico_uf (HTML: 27 UF en una grilla geográfica aproximada; color secuencial por valor) ---------- */
/* Posición (columna, fila) de cada UF en una grilla de 9 × 8, norte arriba y oeste a la izquierda.
   Es una aproximación de mapa, no cartografía: cada UF ocupa una celda. */
export const POSICION_UF = {
  AC: [0, 2], RO: [1, 3], AM: [2, 1], RR: [3, 0], PA: [4, 1], AP: [5, 0], MA: [5, 1], TO: [4, 2],
  PI: [5, 2], CE: [6, 1], RN: [7, 1], PB: [7, 2], PE: [7, 3], AL: [8, 3], SE: [8, 4], BA: [6, 3],
  MT: [3, 3], GO: [4, 3], DF: [5, 3], MS: [3, 4], MG: [5, 4], ES: [6, 4], RJ: [6, 5], SP: [5, 5],
  PR: [4, 5], SC: [4, 6], RS: [4, 7],
};
const RAMPA_UF = [[233, 238, 245], [18, 56, 100]]; // claro → navy (tema de la página)
function colorSecuencial(t) {
  const [a, b] = RAMPA_UF;
  return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * t)).join(',')})`;
}

export function mosaico_uf(zona, e = {}) {
  const valores = new Map((e.valores || []).filter((v) => v.valor != null).map((v) => [v.uf, v.valor]));
  const todos = [...valores.values()];
  const lo = todos.length ? Math.min(...todos) : 0;
  const hi = todos.length ? Math.max(...todos) : 1;
  const envoltura = nodo('div');
  envoltura.style.cssText = 'height:100%;box-sizing:border-box;padding:8px;display:flex;flex-direction:column;gap:8px;';
  const grilla = nodo('div', 'mosaico-uf');
  grilla.style.cssText = 'flex:1;min-height:0;display:grid;grid-template-columns:repeat(9,1fr);grid-template-rows:repeat(8,1fr);gap:4px;';
  for (const [uf, [x, y]] of Object.entries(POSICION_UF)) {
    const v = valores.get(uf);
    const t = v == null ? null : (hi - lo ? (v - lo) / (hi - lo) : 0.5);
    const celda = nodo('div', 'mosaico-uf-celda');
    celda.style.cssText = `grid-column:${x + 1};grid-row:${y + 1};display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:3px;font-size:12px;line-height:1.2;`;
    celda.style.background = t == null ? '#f3f4f6' : colorSecuencial(t);
    celda.style.color = t != null && t > 0.55 ? '#ffffff' : '#1d2433';
    celda.title = `${uf}: ${v == null ? 'sin dato' : formatear(v, e.formato)}`;
    const sigla = nodo('b', null, uf);
    const cifra = nodo('span', null, v == null ? '—' : formatear(v, e.formato));
    celda.append(sigla, cifra);
    grilla.append(celda);
  }
  const escala = nodo('div', 'mosaico-uf-escala', `Escala: ${formatear(lo, e.formato)} a ${formatear(hi, e.formato)}`);
  escala.style.cssText = 'font-size:12px;color:var(--texto-2);text-align:right;';
  envoltura.append(grilla, escala);
  zona.replaceChildren(envoltura);
  return null;
}


/* ---------- v3 · barras_simple (HTML): una barra horizontal por fila, valor a la derecha ----------
   entrada: { filas: [{ nombre, valor, destacar, color }], formato, max, nota }. max fija la escala
   (lo que pase de max se corta y se marca «›»). */
function barras_simple(cont, e) {
  const raiz = document.createElement('div');
  raiz.className = 'v3-barras';
  const max = e.max ?? Math.max(...e.filas.map((f) => Math.abs(f.valor ?? 0)), 1e-9);
  for (const f of e.filas) {
    const fila = document.createElement('div');
    fila.className = 'v3-barras-fila' + (f.destacar ? ' destacar' : '');
    const n = document.createElement('span'); n.className = 'v3-barras-nombre'; n.textContent = f.nombre;
    const pista = document.createElement('div'); pista.className = 'v3-barras-pista';
    const b = document.createElement('div'); b.className = 'v3-barras-barra';
    const w = Math.min(1, Math.abs(f.valor ?? 0) / max);
    b.style.width = `${(w * 100).toFixed(1)}%`;
    if (f.color) b.style.background = f.color;
    pista.append(b);
    const v = document.createElement('span'); v.className = 'v3-barras-valor';
    v.textContent = formatear(f.valor, e.formato || 'pct') + (Math.abs(f.valor ?? 0) > max ? ' ›' : '');
    fila.append(n, pista, v);
    raiz.append(fila);
  }
  cont.append(raiz);
  return null;
}

/* ---------- v3 · mix_banco (HTML): una barra apilada al 100 % y su leyenda con valores ----------
   entrada: { partes: [{ nombre, valor }] } con valores en fracción que suman 1. */
const TONOS_MIX = ['#2E5C8A', '#5B7FA6', '#2F7A86', '#8FA3BC', '#B5C0CD', '#D4DCE6', '#E6EAEF'];
function mix_banco(cont, e) {
  const raiz = document.createElement('div');
  raiz.className = 'v3-mix';
  const barra = document.createElement('div'); barra.className = 'v3-mix-barra';
  const ley = document.createElement('div'); ley.className = 'v3-mix-leyenda';
  e.partes.forEach((p, i) => {
    const color = TONOS_MIX[i % TONOS_MIX.length];
    const seg = document.createElement('div');
    seg.className = 'v3-mix-seg';
    seg.style.width = `${((p.valor ?? 0) * 100).toFixed(2)}%`;
    seg.style.background = color;
    if (i < 3) seg.style.color = '#FFFFFF';
    if ((p.valor ?? 0) >= 0.08) seg.textContent = `${Math.round(p.valor * 100)} %`;
    barra.append(seg);
    const it = document.createElement('div'); it.className = 'v3-mix-item';
    const cuadro = document.createElement('span'); cuadro.className = 'v3-mix-cuadro'; cuadro.style.background = color;
    const nom = document.createElement('span'); nom.className = 'v3-mix-nombre'; nom.textContent = p.nombre;
    const val = document.createElement('span'); val.className = 'v3-mix-valor'; val.textContent = formatear(p.valor, 'pct');
    it.append(cuadro, nom, val);
    ley.append(it);
  });
  raiz.append(barra, ley);
  cont.append(raiz);
  return null;
}


/* ---------- v3 · barras_linea (ECharts): barras apiladas + una línea, categorías en el eje X ----------
   entrada: { categorias: [...], barras: [{ nombre, color, valores }], linea: { nombre, color, valores },
   ejeBarras: 'izq' | 'der', formatoIzq, formatoDer, titulo... }. Valores ya calculados en Python. */
function barras_linea(cont, e) {
  const ch = window.echarts.init(cont, null, { renderer: 'svg' });
  const der = e.ejeBarras === 'der';
  const fmtI = e.formatoIzq || ((v) => `${v}`), fmtD = e.formatoDer || ((v) => `${v}`);
  const ejeY = (fmt, mostrarGrilla, r = {}) => ({ type: 'value', scale: !!r.escala, min: r.min, max: r.max, axisLine: { show: false }, axisTick: { show: false },
    axisLabel: { color: C.texto3, fontSize: 11, fontFamily: 'IBM Plex Mono, monospace', formatter: fmt },
    splitLine: { show: mostrarGrilla, lineStyle: { color: C.regla } } });
  const series = (e.barras || []).map((b) => ({ name: b.nombre, type: 'bar', stack: 'b', data: b.valores, barMaxWidth: 18,
    itemStyle: { color: b.color }, yAxisIndex: der ? 1 : 0, emphasis: { disabled: true } }));
  for (const l of e.lineas || (e.linea ? [e.linea] : [])) series.push({ name: l.nombre, type: 'line', data: l.valores, showSymbol: false, connectNulls: false,
    lineStyle: { width: l.grosor || 2.2, color: l.color, type: l.discontinua ? 'dashed' : 'solid' }, itemStyle: { color: l.color }, z: l.z || 5 });
  ch.setOption({
    animation: false, backgroundColor: 'transparent',
    textStyle: { fontFamily: C.fuente, color: C.texto2 },
    grid: { left: 6, right: der ? 6 : 12, top: e.leyendaInteractiva ? 36 : 14, bottom: 4, containLabel: true },
    legend: e.leyendaInteractiva ? { show: true, top: 0, left: 0, right: 0, type: 'scroll', pageIconColor: C.texto2, pageTextStyle: { color: C.texto3 }, icon: 'roundRect', itemWidth: 14, itemHeight: 3, itemGap: 14,
      textStyle: { color: C.texto2, fontSize: 11, fontFamily: 'IBM Plex Sans, sans-serif' }, inactiveColor: '#C9D1DB' } : { show: false },
    tooltip: { trigger: 'axis', backgroundColor: '#FFFFFF', borderColor: C.borde, textStyle: { color: C.texto, fontSize: 12 },
      valueFormatter: (v) => (v == null ? '—' : Number(v).toFixed(2).replace('.', ',')) },
    xAxis: { type: 'category', data: e.categorias, axisLine: { lineStyle: { color: C.borde } }, axisTick: { show: false },
      axisLabel: { color: C.texto3, fontSize: 11, fontFamily: 'IBM Plex Mono, monospace', interval: e.intervalo ?? 'auto' } },
    yAxis: der ? [ejeY(fmtI, true, e.rangoIzq), ejeY(fmtD, false, e.rangoDer)] : [ejeY(fmtI, true, e.rangoIzq)],
    series,
  });
  return ch;
}

/* ---------- v3 · mapa_cuotas (ECharts treemap): cuota de cada banco, color por grupo ---------- */
const COLOR_MAPA = { Grandes: '#2E5C8A', Desarrollo: '#8FA3BC', Digitales: '#2F7A86', 'Medianos y nicho': '#B5C0CD', Pagos: '#7B5E8C', Resto: '#E6EAEF' };
const TINTA_MAPA = { Grandes: '#FFFFFF', Digitales: '#FFFFFF', Pagos: '#FFFFFF' };
function mapa_cuotas(cont, e) {
  const ch = window.echarts.init(cont, null, { renderer: 'svg' });
  ch.setOption({
    animation: false,
    tooltip: { formatter: (p) => `${p.name}: ${(p.value * 100).toFixed(1).replace('.', ',')} %` },
    series: [{
      type: 'treemap', roam: false, nodeClick: false, breadcrumb: { show: false }, width: '100%', height: '100%', top: 0, left: 0,
      squareRatio: 1.2,
      itemStyle: { borderColor: '#FFFFFF', borderWidth: 2, gapWidth: 2 },
      label: { show: true, formatter: (p) => `{n|${p.name}}\n{v|${(p.value * 100).toFixed(1).replace('.', ',')} %}`,
        rich: { n: { fontSize: 13, fontWeight: 600, fontFamily: C.fuente, lineHeight: 18 }, v: { fontSize: 12, fontFamily: 'IBM Plex Mono, monospace', lineHeight: 16 } },
        position: 'insideTopLeft', padding: [6, 8] },
      data: e.filas.map((f) => ({ name: f.banco, value: f.cuota,
        itemStyle: { color: COLOR_MAPA[f.grupo] || '#B5C0CD' }, label: { color: TINTA_MAPA[f.grupo] || '#24324A' } })),
    }],
  });
  return ch;
}


/* ---------- v3 · tabla_estandar: LA tabla descriptiva del sitio (una sola, para que todas sean iguales) ----------
   Columnas fijas (4-nov): Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m (trimestral: t/t · — · a/a · 4T/4T).
   entrada: { filas: [{ fila, ultimo, d1, d3, d12, dventana, corte, unidad_ultimo?, unidad_cambio? }],
   unidadUltimo, unidadCambio, trimestral }. Unidades: pct (fracción → %), pct_nivel (ya en %), pp, brl_mm
   (R$ mil millones). Sin colores: el formato es el mismo en todas las páginas. */
function fmtEstandar(v, u, signo) {
  if (v == null || Number.isNaN(v)) return '—';
  const n = (x, d = 1) => `${signo && x > 0 ? '+' : ''}${x < 0 ? '−' : ''}${Math.abs(x).toFixed(d).replace('.', ',')}`;
  if (u === 'pct') return `${n(v * 100)} %`;
  if (u === 'pct_nivel') return `${n(v)} %`;
  if (u === 'pp') return `${n(v)} pp`;
  if (u === 'brl_mm') return `R$ ${Math.round(v).toLocaleString('es-CL')}`;
  return n(v);
}
function tabla_estandar(cont, e) {
  const filas = e.filas || [];
  const tri = e.trimestral || filas.some((f) => f.trimestral);
  const cab = tri ? ['t/t', '—', 'a/a', '4T/4T'] : ['m/m', '3m/3m', 'a/a', '12m/12m'];
  const anchos = ['22%', '10%', '14%', '10%', '11%', '11%', '11%', '11%'];
  const titulos = ['Indicador', 'Corte', 'Último', 'Share', ...cab];
  const descripciones = ['Indicador', 'Fecha de corte', 'Último valor disponible', 'Participación en el total',
    tri ? 'Variación trimestral' : 'Variación mensual', tri ? 'No aplica' : 'Variación de tres meses contra los tres meses anteriores',
    'Variación interanual', tri ? 'Cuatro trimestres contra los cuatro anteriores' : 'Doce meses contra los doce anteriores'];
  const raiz = document.createElement('div');
  raiz.className = 'tabla-scroll tabla-estandar-cuerpo';
  raiz.tabIndex = 0;
  raiz.setAttribute('role', 'region');
  raiz.setAttribute('aria-label', 'Tabla de indicadores. Desplázate para consultar todas las columnas.');
  const t = document.createElement('table');
  t.className = 'tabla-datos';
  const caption = document.createElement('caption');
  caption.className = 'solo-lector';
  caption.textContent = 'Indicadores, fecha de corte, último valor, participación y variaciones. El guion indica un dato no disponible o no aplicable.';
  t.append(caption);
  const columnas = document.createElement('colgroup');
  for (const ancho of anchos) {
    const c = document.createElement('col');
    c.style.width = ancho;
    columnas.append(c);
  }
  t.append(columnas);
  const head = document.createElement('thead');
  const encabezado = document.createElement('tr');
  titulos.forEach((titulo, i) => {
    const th = document.createElement('th');
    th.scope = 'col';
    if (i) th.className = 'num';
    const abbr = document.createElement('abbr');
    abbr.title = descripciones[i];
    abbr.textContent = titulo;
    th.append(abbr);
    encabezado.append(th);
  });
  head.append(encabezado);
  t.append(head);
  const tb = document.createElement('tbody');
  for (const f of filas) {
    const uu = f.unidad_ultimo || e.unidadUltimo, uc = f.unidad_cambio || e.unidadCambio;
    const share = f.share == null || Number.isNaN(f.share) ? '—' : (f.share >= 0.9995 ? '100 %' : `${(f.share * 100).toFixed(1).replace('.', ',')} %`);
    const celdas = [f.fila, f.corte || '—', fmtEstandar(f.ultimo, uu, uu === 'pp'), share, fmtEstandar(f.d1, uc, true), tri ? '—' : fmtEstandar(f.d3, uc, true),
      fmtEstandar(f.d12, uc, true), fmtEstandar(f.dventana, uc, true)];
    const tr = document.createElement('tr');
    if (f.destacar) tr.className = 'fila-total';
    celdas.forEach((valor, i) => {
      const celda = document.createElement(i ? 'td' : 'th');
      if (i) celda.className = 'num';
      else celda.scope = 'row';
      celda.textContent = valor == null ? '—' : String(valor);
      tr.append(celda);
    });
    tb.append(tr);
  }
  t.append(tb);
  const ayuda = document.createElement('details');
  ayuda.className = 'tabla-glosario';
  const resumen = document.createElement('summary');
  resumen.textContent = 'Cómo leer las columnas';
  const glosario = document.createElement('dl');
  titulos.forEach((titulo, i) => {
    const dt = document.createElement('dt');
    const dd = document.createElement('dd');
    dt.textContent = titulo;
    dd.textContent = descripciones[i];
    glosario.append(dt, dd);
  });
  ayuda.append(resumen, glosario);
  const aviso = document.createElement('p');
  aviso.className = 'tabla-ayuda';
  aviso.textContent = 'Desplaza la tabla para consultar todas las columnas.';
  raiz.append(ayuda, aviso, t);
  cont.append(raiz);
  return null;
}

/* ---------- v3 · barras_signo (ECharts): barras horizontales con signo, ordenadas ---------- */
function barras_signo(cont, e) {
  const ch = window.echarts.init(cont, null, { renderer: 'svg' });
  const filas = e.filas;
  ch.setOption({
    animation: false, backgroundColor: 'transparent',
    grid: { left: 6, right: 56, top: 6, bottom: 6, containLabel: true }, // 4-nov: espacio para la etiqueta de la barra más larga
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (v) => `${Number(v).toFixed(2).replace('.', ',')} ${e.unidad || ''}` },
    xAxis: { type: 'value', axisLabel: { color: C.texto3, fontSize: 11, fontFamily: 'IBM Plex Mono, monospace', formatter: (v) => `${v}` }, splitLine: { lineStyle: { color: C.regla } } },
    yAxis: { type: 'category', inverse: true, data: filas.map((f) => f.nombre), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: C.texto, fontSize: 12 } },
    series: [{ type: 'bar', barMaxWidth: 18, data: filas.map((f) => ({ value: f.valor, itemStyle: { color: f.color || (f.valor >= 0 ? (e.colorPos || '#2E5C8A') : (e.colorNeg || '#A85E24')) } })),
      label: { show: true, position: 'right', fontFamily: 'IBM Plex Mono, monospace', fontSize: 11, color: C.texto2, formatter: (p) => `${p.value > 0 ? '+' : ''}${Number(p.value).toFixed(e.decimales ?? 2).replace('.', ',')}` } }],
  });
  return ch;
}

export const COMPONENTES_BANCOS = { percentiles, cascada_doble, burbujas_trayectoria, small_multiples_bancos, comparador, linea_banco, apilada_100, pesas, dispersion, barras_h_doble, barras_ic, trayectoria, small_multiples, puertas, mosaico_uf, barras_simple, mix_banco, barras_linea, mapa_cuotas, tabla_estandar, barras_signo }; // bancos: piezas de la ola 3 (encargo 76)
