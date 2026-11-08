/* Componentes propios de bancos (SPEC_WEB_BANCOS_00_GENERAL.md §6) y el registro completo de
   componentes. Python calcula todo; aquí solo se dibuja: ninguno calcula ratios, percentiles ni
   agregados (la suma acumulada de la cascada es posición en pantalla). Los colores por categoría
   llegan en la entrada; aquí solo hay los del tema. */
import { C, COMPONENTES_GENERALES, iniciar, tema, tooltip, ejeBase, ejeNumerico, GRILLA, cajaDesplazable } from './charts.js';
import { TIPO, TRAZO_REFERENCIA } from './tokens.js';
import { numero, pp, porcentaje, formatear, formatoEje, tono, ROTULO, TABLA } from './formato.js';
import { el, svgEl } from './dom.js';

/* Color de un cambio según el signo de la métrica (§5.3). */
const COLOR_TONO = { mejora: C.navy, deterioro: C.peor, neutro: C.texto2, 'sin-cambio': C.texto3 };

/* Tinta o blanco, lo que se lea sobre un fondo hex. */
function textoSobre(fondo) {
  const m = /^#([0-9a-f]{6})$/i.exec(fondo || '');
  if (!m) return C.tarjeta;
  const n = parseInt(m[1], 16);
  const luz = 0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255);
  return luz > 150 ? C.texto : C.tarjeta;
}

/* ---------- percentiles ---------- */
/* El punto del banco: deterioro si está del lado malo de la mediana; en la mediana o del lado bueno, navy;
   métrica sin sentido de mejora, gris (§5). */
function colorBanco(f) {
  const t = tono(f.valor - f.p50, f.signo);
  if (t === 'deterioro') return C.peor;
  return f.signo === 'mejora_sube' || f.signo === 'mejora_baja' ? C.navy : C.texto2;
}

function filaPercentil(f) {
  const fila = el('div', 'pct-fila');
  fila.append(el('span', 'pct-nombre', f.nombre || f.metrica || ''));
  const escala = el('div', 'pct-escala');
  if (f.p10 == null || f.p50 == null || f.p90 == null) {
    escala.append(el('span', 'pct-sin', 'sin dato del grupo'));
  } else {
    // escala propia de la fila: p10–p90 del grupo más el banco, con 15 % de margen
    const puntos = [f.p10, f.p90, f.valor, f.valor_t4].filter((v) => v != null);
    const lo0 = Math.min(...puntos);
    const hi0 = Math.max(...puntos);
    const m = 0.15 * ((hi0 - lo0) || Math.abs(hi0) || 1);
    const lo = lo0 - m;
    const hi = hi0 + m;
    const x = (v) => ((v - lo) / (hi - lo)) * 100;

    const rango = el('div', 'pct-rango');
    rango.style.left = `${x(f.p10)}%`;
    rango.style.width = `${x(f.p90) - x(f.p10)}%`;
    const mediana = el('div', 'pct-mediana');
    mediana.style.left = `${x(f.p50)}%`;
    escala.append(rango, mediana);

    if (f.valor != null && f.valor_t4 != null) {
      const union = el('div', 'pct-enlace');
      const a = Math.min(f.valor, f.valor_t4);
      const b = Math.max(f.valor, f.valor_t4);
      union.style.left = `${x(a)}%`;
      union.style.width = `${x(b) - x(a)}%`;
      escala.append(union);
    }
    if (f.valor_t4 != null) {
      const t4 = el('div', 'pct-punto-t4');
      t4.style.left = `${x(f.valor_t4)}%`;
      escala.append(t4);
    }
    if (f.valor != null) {
      const punto = el('div', 'pct-punto');
      punto.style.left = `${x(f.valor)}%`;
      punto.style.background = colorBanco(f);
      escala.append(punto);
    }
    const txt = (v) => formatear(v, f.formato);
    fila.title = `p10 ${txt(f.p10)} · mediana ${txt(f.p50)} · p90 ${txt(f.p90)} · banco ${txt(f.valor)}`
      + (f.valor_t4 != null ? ` · hace un año ${txt(f.valor_t4)}` : '');
  }
  fila.append(escala, el('span', 'pct-valor', formatear(f.valor, f.formato)));
  return fila;
}

function percentiles(zona, e = {}) {
  zona.classList.add('pct');
  const lista = el('div', 'pct-lista');
  for (const f of e.filas || []) lista.append(filaPercentil(f));
  zona.append(lista);
  return null;
}

/* Cuerpo y nota del banco (quiebre, líneas omitidas) dentro de la zona. La zona se vacía en cada
   dibujo, así que la nota nunca queda de un banco anterior. */
function caja(zona, nota) {
  const envoltura = el('div', 'con-nota-caja');
  const cuerpo = el('div', 'con-nota-cuerpo');
  envoltura.append(cuerpo);
  if (nota) envoltura.append(el('p', 'con-nota', nota));
  zona.replaceChildren(envoltura);
  return cuerpo;
}

/* ---------- cascada_doble ---------- */
function pista(intervalo, valor, x, color) {
  const p = el('div', 'cas-pista');
  const cero = el('div', 'cas-cero');
  cero.style.left = `${x(0)}%`;
  const i = Math.min(...intervalo);
  const j = Math.max(...intervalo);
  const barra = el('div', 'cas-barra');
  barra.style.left = `${x(i)}%`;
  barra.style.width = `${Math.max(x(j) - x(i), 0.4)}%`;
  barra.style.background = color;
  const etiqueta = el('span', 'cas-etiqueta', pp(valor * 100, 1, true));
  etiqueta.style.left = `${x(j)}%`;
  p.append(cero, barra, etiqueta);
  return p;
}

function cascada_doble(zona, e = {}) {
  const body = caja(zona, e.nota);
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

  const cab = el('div', 'cas-fila cas-cab');
  cab.append(el('span', 'cas-col', ''), el('span', 'cas-col', 'Banco'), el('span', 'cas-col', 'Mediana del grupo'), el('span', 'cas-col cas-brecha', 'Brecha'));
  body.append(cab);

  for (const f of filas) {
    const fila = el('div', `cas-fila${f.total ? ' cas-total' : ''}`);
    const colorBancoPaso = f.total ? C.acero : (f.vb >= 0 ? C.navy : C.cobre);
    const colorGrupoPaso = f.total ? C.acero : C.aceroClaro;
    const brecha = (f.vb - f.vg) * 100;
    fila.append(
      el('span', 'cas-nombre', f.nombre),
      pista(f.b, f.vb, x, colorBancoPaso),
      pista(f.g, f.vg, x, colorGrupoPaso),
      el('span', `cas-brecha ${brecha >= 0 ? 'cas-pos' : 'cas-neg'}`, pp(brecha, 1, true)),
    );
    body.append(fila);
  }
  return null;
}

/* ---------- burbujas_trayectoria ---------- */
function burbujas_trayectoria(zona, e = {}) {
  const activo = e.banco || null;
  const colores = e.colores || {};
  const puntos = e.puntos || [];
  const tmax = Math.max(1, ...puntos.map((p) => p.tamaño || 0));
  const colorPunto = (p) => {
    if (activo) return p.banco === activo ? C.navy : C.aceroClaro;
    return colores[p.grupo] || colores.Panel;
  };

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
        borderColor: p.banco === activo ? C.navy : C.tarjeta,
        borderWidth: p.banco === activo ? 2.5 : 1,
      },
    })),
  }];
  for (const t of e.trayectorias || []) {
    const color = activo ? C.navy : (colores[t.grupo] || C.acero);
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

  const chart = iniciar(zona);
  chart.setOption({
    ...tema({ fontSize: 11, color: C.texto2 }),
    grid: { left: 8, right: 96, top: e.ejeY?.titulo ? 36 : 16, bottom: 4, containLabel: true }, // margen para la etiqueta del último punto y, con título, el del eje Y
    tooltip: tooltip('item', {
      formatter: (p) => {
        const d = p.data || {};
        const v = Array.isArray(d.value) ? d.value : [];
        const tri = d.tri ? ` · ${d.tri}` : '';
        return `<b>${d.name || p.seriesName}</b>${tri}<br>${e.ejeX?.titulo || 'x'}: ${formatear(v[0], e.ejeX?.formato)}`
          + `<br>${e.ejeY?.titulo || 'y'}: ${formatear(v[1], e.ejeY?.formato)}`;
      },
    }),
    xAxis: ejeNumerico(e.ejeX, 'x'),
    yAxis: ejeNumerico(e.ejeY, 'y'),
    series,
  });
  return chart;
}

/* ---------- sparkline (SVG propio, escala dada) ---------- */
function sparkline(puntos, esc, colorTrazo, ancho = 100, alto = 40) {
  const svg = svgEl('svg', { viewBox: `0 0 ${ancho} ${alto}`, preserveAspectRatio: 'none', 'aria-hidden': 'true' });
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
  svg.append(svgEl('path', { d: d.trim(), fill: 'none', stroke: colorTrazo, 'stroke-width': '1.5', 'vector-effect': 'non-scaling-stroke' }));
  return svg;
}

/* ---------- comparador ---------- */
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

function comparador(zona, e = {}) {
  zona.classList.add('cmp');
  const columnas = e.columnas || [];
  const filas = e.filas || [];
  const filtros = e.filtros || [];
  const bancoActivo = e.banco || null;
  const estado = {
    orden: { ...(e.orden || { clave: columnas[0]?.clave, dir: 'desc' }) },
    sel: Object.fromEntries(filtros.map((f) => [f.clave, new Set()])),
  };

  const barra = el('div', 'cmp-barra');
  const chips = el('div', 'cmp-chips');
  const chipsPorFiltro = [];
  for (const f of filtros) {
    const grupo = el('div', 'cmp-grupo');
    grupo.append(el('span', 'cmp-rotulo', f.titulo));
    const valores = [...new Set(filas.map((r) => r.filtros?.[f.clave]).filter(Boolean))];
    for (const v of valores) {
      const b = el('button', 'cmp-chip', v);
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
  const cuenta = el('span', 'cmp-cuenta');
  const csv = el('button', 'cmp-csv', 'Descargar CSV');
  csv.type = 'button';
  barra.append(chips, cuenta, csv);
  const scroll = el('div', 'cmp-scroll');
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

    const tabla = el('table', 'tabla-datos cmp-tabla');
    const thead = el('thead');
    const trh = el('tr');
    for (const c of columnas) {
      const th = el('th', c.tipo === 'texto' ? '' : 'num');
      const activa = estado.orden.clave === c.clave;
      th.setAttribute('aria-sort', activa ? (estado.orden.dir === 'asc' ? 'ascending' : 'descending') : 'none');
      const b = el('button', 'cmp-orden', c.titulo + (activa ? (estado.orden.dir === 'asc' ? ' ▲' : ' ▼') : ''));
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

    const tbody = el('tbody');
    for (const f of filas2) {
      const tr = el('tr', f.slug && f.slug === bancoActivo ? 'cmp-activo' : '');
      if (e.enlaceFila) {
        tr.tabIndex = 0;
        tr.setAttribute('role', 'link');
        const ir = () => { location.href = e.enlaceFila(f); };
        tr.addEventListener('click', ir);
        tr.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') ir(); });
      }
      for (const c of columnas) {
        const td = el('td', c.tipo === 'texto' ? '' : 'num');
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
    // el navegador inicia la descarga de forma asíncrona: revocar la URL en el acto la corta en Firefox
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });

  render();
  return null;
}

/* ---------- apilada_100 ---------- */
const ROTULO_MINIMO = 0.08; // una parte lleva rótulo dentro si pesa al menos 8 %

function apilada_100(zona, e = {}) {
  zona.classList.add('ap');
  const barras = e.barras || [];
  const lista = el('div', 'ap-lista');
  for (const b of barras) {
    const partes = b.partes || [];
    const total = partes.reduce((a, p) => a + (p.valor || 0), 0) || 1;
    const fila = el('div', 'ap-fila');
    fila.append(el('span', 'ap-nombre', b.nombre || ''));
    const barra = el('div', 'ap-barra');
    for (const p of partes) {
      const parte = (p.valor || 0) / total;
      const color = p.color || C.aceroClaro;
      const seg = el('div', 'ap-seg');
      seg.style.width = `${parte * 100}%`;
      seg.style.background = color;
      seg.title = `${p.nombre}: ${formatear(p.valor, e.formato || 'pct')}`;
      if (parte >= ROTULO_MINIMO) {
        const r = el('span', 'ap-rotulo', formatear(p.valor, e.formatoRotulo || { unidad: 'pct', decimales: 0 }));
        r.style.color = textoSobre(color);
        seg.append(r);
      }
      barra.append(seg);
    }
    fila.append(barra);
    lista.append(fila);
  }
  const leyenda = el('div', 'ap-leyenda');
  for (const p of barras[0]?.partes || []) {
    const item = el('span');
    const sw = el('i');
    sw.style.background = p.color || C.aceroClaro;
    item.append(sw, document.createTextNode(p.nombre || ''));
    leyenda.append(item);
  }
  zona.replaceChildren(lista, leyenda);
  return null;
}

/* ---------- pesas ---------- */
function pesas(zona, e = {}) {
  zona.classList.add('pes');
  const filas = e.filas || [];
  const vals = filas.flatMap((f) => [f.antes, f.ahora]).filter((v) => v != null);
  const lo = e.escala ? e.escala[0] : (vals.length ? Math.min(...vals) : 0);
  const hi = e.escala ? e.escala[1] : (vals.length ? Math.max(...vals) : 1);
  const x = (v) => ((v - lo) / ((hi - lo) || 1)) * 100;
  const lista = el('div', 'pes-lista');
  const cab = el('div', 'pes-fila pes-cab');
  cab.append(el('span', 'pes-nombre', ''), el('span', 'pes-escala', 'antes ○ · ahora ●'), el('span', 'pes-texto', 'antes → ahora'));
  lista.append(cab);
  for (const f of filas) {
    const ok = f.antes != null && f.ahora != null;
    const t = ok ? tono(f.ahora - f.antes, f.signo, e.umbral ?? 0) : null;
    const color = t ? COLOR_TONO[t] : C.texto3;
    const flecha = !t ? '' : t === 'sin-cambio' ? '=' : f.ahora > f.antes ? '▲' : '▼';
    const fila = el('div', `pes-fila${f.destacada ? ' pes-destacada' : ''}`);
    const escala = el('div', 'pes-escala');
    if (ok) {
      const a = Math.min(f.antes, f.ahora);
      const b = Math.max(f.antes, f.ahora);
      const tramo = el('div', 'pes-tramo');
      tramo.style.left = `${x(a)}%`;
      tramo.style.width = `${x(b) - x(a)}%`;
      tramo.style.background = color;
      const antes = el('div', 'pes-antes');
      antes.style.left = `${x(f.antes)}%`;
      const ahora = el('div', 'pes-ahora');
      ahora.style.left = `${x(f.ahora)}%`;
      ahora.style.background = color;
      escala.append(tramo, antes, ahora);
    }
    const texto = el('span', 'pes-texto', ok ? `${flecha} ${formatear(f.antes, e.formato)} → ${formatear(f.ahora, e.formato)}` : 'sin dato');
    texto.style.color = color;
    fila.append(el('span', 'pes-nombre', f.nombre || ''), escala, texto);
    lista.append(fila);
  }
  zona.replaceChildren(lista);
  return null;
}

/* ---------- dispersion ---------- */
function dispersion(zona, e = {}) {
  const puntos = e.puntos || [];
  const todos = puntos.flatMap((p) => [p.x, p.y]).filter((v) => v != null);
  const lo = todos.length ? Math.min(...todos) : 0;
  const hi = todos.length ? Math.max(...todos) : 1;
  const series = [{
    type: 'scatter', name: 'Bancos', z: 3,
    labelLayout: { hideOverlap: true },
    data: puntos.map((p) => ({
      value: [p.x, p.y],
      name: p.nombre || p.banco || '',
      symbolSize: p.destacado ? 11 : 8,
      itemStyle: { color: p.destacado ? C.texto : C.acero, borderColor: C.tarjeta, borderWidth: 1 },
      label: {
        show: true, formatter: p.nombre || p.banco || '', position: 'right', fontSize: 11,
        color: p.destacado ? C.texto : C.texto2, fontWeight: p.destacado ? 600 : 400,
      },
    })),
  }];
  if (e.diagonal && todos.length) {
    series.push({
      type: 'line', name: 'Diagonal', z: 2, silent: true, symbol: 'none', tooltip: { show: false },
      lineStyle: { color: C.referencia, width: 1, type: TRAZO_REFERENCIA }, data: [[lo, lo], [hi, hi]],
    });
  }
  const chart = iniciar(zona);
  chart.setOption({
    ...tema({ fontSize: 11, color: C.texto2 }),
    grid: { left: 8, right: 16, top: 36, bottom: 4, containLabel: true },
    tooltip: tooltip('item', {
      formatter: (p) => {
        const v = Array.isArray(p.data?.value) ? p.data.value : [];
        return `<b>${p.data?.name || ''}</b><br>${e.ejeX?.titulo || 'x'}: ${formatear(v[0], e.ejeX?.formato)}`
          + `<br>${e.ejeY?.titulo || 'y'}: ${formatear(v[1], e.ejeY?.formato)}`;
      },
    }),
    xAxis: ejeNumerico(e.ejeX, 'x'),
    yAxis: ejeNumerico(e.ejeY, 'y'),
    series,
  });
  // textos de cuadrante: arriba a la izquierda (tl) y abajo a la derecha (br); no capturan el puntero
  for (const [pos, texto] of Object.entries(e.cuadrantes || {})) {
    if (texto) zona.append(el('span', `dis-cuadrante dis-${pos}`, texto));
  }
  return chart;
}

/* ---------- barras_h_doble ---------- */
function barras_h_doble(zona, e = {}) {
  const filas = e.filas || [];
  const series = e.series || [];
  const formato = e.formato || 'pct';
  const activo = e.activo || null;
  const chart = iniciar(zona);
  chart.setOption({
    ...tema({ fontSize: 11, color: C.texto2 }),
    grid: { left: 8, right: 64, top: 8, bottom: 4, containLabel: true },
    tooltip: tooltip('axis', { axisPointer: { type: 'shadow' }, valueFormatter: (v) => formatear(v, formato) }),
    xAxis: ejeBase({ show: false }, { type: 'value', splitLine: GRILLA }),
    yAxis: ejeBase({
      color: C.texto2,
      formatter: (n, i) => (activo && filas[i]?.slug === activo ? `{activo|${n}}` : n),
      rich: { activo: { color: C.texto, fontWeight: 600 } },
    }, { type: 'category', data: filas.map((r) => r.nombre), inverse: true }),
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

/* ---------- barras_ic ---------- */
const POCOS_TRIMESTRES = 24; // con menos trimestres se marca «pocos trimestres» (§7.6)

function barras_ic(zona, e = {}) {
  zona.classList.add('ic');
  const filas = e.filas || [];
  const vals = filas.flatMap((f) => [0, f.valor, f.bajo, f.alto]).filter((v) => v != null && !Number.isNaN(v));
  const lo0 = vals.length ? Math.min(...vals) : 0;
  const hi0 = vals.length ? Math.max(...vals) : 1;
  const m = 0.05 * ((hi0 - lo0) || 1);
  const lo = lo0 - m;
  const hi = hi0 + m;
  const x = (v) => ((v - lo) / ((hi - lo) || 1)) * 100;
  const lista = el('div', 'ic-lista');
  for (const f of filas) {
    const esActivo = !!e.activo && f.slug === e.activo;
    const fila = el('div', `ic-fila${esActivo ? ' ic-activo' : ''}`);
    const pistaIc = el('div', 'ic-pista');
    const cero = el('div', 'ic-cero');
    cero.style.left = `${x(0)}%`;
    pistaIc.append(cero);
    if (f.valor != null) {
      const a = Math.min(x(0), x(f.valor));
      const b = Math.max(x(0), x(f.valor));
      const barra = el('div', 'ic-barra');
      barra.style.left = `${a}%`;
      barra.style.width = `${Math.max(b - a, 0.3)}%`;
      barra.style.background = esActivo ? C.navy : C.aceroClaro;
      pistaIc.append(barra);
    }
    if (f.bajo != null && f.alto != null) {
      const intervalo = el('div', 'ic-int');
      intervalo.style.left = `${x(f.bajo)}%`;
      intervalo.style.width = `${Math.max(x(f.alto) - x(f.bajo), 0.3)}%`;
      pistaIc.append(intervalo);
    }
    fila.append(el('span', 'ic-nombre', f.nombre || ''), pistaIc, el('span', 'ic-valor', formatear(f.valor, e.formato)));
    if (f.n != null && f.n < POCOS_TRIMESTRES) {
      const marca = el('span', 'ic-marca', 'pocos trimestres');
      marca.title = `n = ${numero(f.n, 0)} trimestres (mínimo ${POCOS_TRIMESTRES})`;
      fila.append(marca);
    }
    lista.append(fila);
  }
  zona.replaceChildren(lista);
  return null;
}

/* ---------- barras_simple ---------- */
function barras_simple(cont, e) {
  const raiz = el('div', 'v3-barras');
  const max = e.max ?? Math.max(...e.filas.map((f) => Math.abs(f.valor ?? 0)), 1e-9);
  for (const f of e.filas) {
    const fila = el('div', 'v3-barras-fila' + (f.destacar ? ' destacar' : ''));
    const pistaB = el('div', 'v3-barras-pista');
    const b = el('div', 'v3-barras-barra');
    b.style.width = `${(Math.min(1, Math.abs(f.valor ?? 0) / max) * 100).toFixed(1)}%`;
    if (f.color) b.style.background = f.color;
    pistaB.append(b);
    const valor = formatear(f.valor, e.formato || 'pct') + (Math.abs(f.valor ?? 0) > max ? ' ›' : '');
    fila.append(el('span', 'v3-barras-nombre', f.nombre), pistaB, el('span', 'v3-barras-valor', valor));
    raiz.append(fila);
  }
  cont.append(raiz);
  return null;
}

/* ---------- barras_linea ---------- */
function barras_linea(cont, e) {
  const ch = iniciar(cont);
  const der = e.ejeBarras === 'der';
  const ejeY = (formato, mostrarGrilla, r = {}) => ejeBase({ fontFamily: TIPO.mono, formatter: formatoEje(formato || 'num') }, {
    type: 'value', scale: !!r.escala, min: r.min, max: r.max,
    splitLine: { show: mostrarGrilla, lineStyle: { color: C.regla } },
  });
  const series = (e.barras || []).map((b) => ({ name: b.nombre, type: 'bar', stack: 'b', data: b.valores, barMaxWidth: 18,
    itemStyle: { color: b.color }, yAxisIndex: der ? 1 : 0, emphasis: { disabled: true } }));
  for (const l of e.lineas || []) series.push({ name: l.nombre, type: 'line', data: l.valores, showSymbol: false, connectNulls: false,
    lineStyle: { width: l.grosor || 2.2, color: l.color, type: l.discontinua ? TRAZO_REFERENCIA : 'solid' }, itemStyle: { color: l.color }, z: l.z || 5 });
  ch.setOption({
    ...tema({ color: C.texto2 }),
    grid: { left: 6, right: der ? 6 : 12, top: e.leyendaInteractiva ? 36 : 14, bottom: 4, containLabel: true },
    legend: e.leyendaInteractiva ? { show: true, top: 0, left: 0, right: 0, type: 'scroll', pageIconColor: C.texto2, pageTextStyle: { color: C.texto3 }, icon: 'roundRect', itemWidth: 14, itemHeight: 3, itemGap: 14,
      textStyle: { color: C.texto2, fontSize: 11, fontFamily: C.fuente }, inactiveColor: C.leyendaInactiva } : { show: false },
    tooltip: tooltip('axis', { valueFormatter: (v) => numero(v, 2, ROTULO) }),
    xAxis: ejeBase({ fontFamily: TIPO.mono, interval: e.intervalo ?? 'auto' }, { type: 'category', data: e.categorias, axisLine: { lineStyle: { color: C.borde } } }),
    yAxis: der ? [ejeY(e.ejeIzq, true, e.rangoIzq), ejeY(e.ejeDer, false, e.rangoDer)] : [ejeY(e.ejeIzq, true, e.rangoIzq)],
    series,
  });
  return ch;
}

/* ---------- mapa_cuotas ---------- */
function mapa_cuotas(cont, e) {
  const cuota = (v) => `${numero(v * 100, 1, ROTULO)} %`;
  const ch = iniciar(cont);
  ch.setOption({
    ...tema(),
    tooltip: tooltip('item', { formatter: (p) => `${p.name}: ${cuota(p.value)}` }),
    series: [{
      type: 'treemap', roam: false, nodeClick: false, breadcrumb: { show: false }, width: '100%', height: '100%', top: 0, left: 0,
      squareRatio: 1.2,
      itemStyle: { borderColor: C.tarjeta, borderWidth: 2, gapWidth: 2 },
      label: { show: true, formatter: (p) => `{n|${p.name}}\n{v|${cuota(p.value)}}`,
        rich: { n: { fontSize: 13, fontWeight: 600, fontFamily: C.fuente, lineHeight: 18 }, v: { fontSize: 12, fontFamily: TIPO.mono, lineHeight: 16 } },
        position: 'insideTopLeft', padding: [6, 8] },
      data: e.filas.map((f) => {
        const color = e.colores[f.grupo];
        return { name: f.banco, value: f.cuota, itemStyle: { color }, label: { color: textoSobre(color) } };
      }),
    }],
  });
  return ch;
}

/* ---------- tabla_estandar ---------- */
const SHARE_COMPLETO = 0.9995; // desde aquí la participación se lee «100 %» (no «100,0 %»)

function tabla_estandar(cont, e, { titulo } = {}) {
  const filas = e.filas || [];
  const tri = filas.some((f) => f.trimestral);
  const cab = tri ? ['t/t', '—', 'a/a', '4T/4T'] : ['m/m', '3m/3m', 'a/a', '12m/12m'];
  const anchos = ['22%', '10%', '14%', '10%', '11%', '11%', '11%', '11%'];
  const titulos = ['Indicador', 'Corte', 'Último', 'Share', ...cab];
  const descripciones = ['Indicador', 'Fecha de corte', 'Último valor disponible', 'Participación en el total',
    tri ? 'Variación trimestral' : 'Variación mensual', tri ? 'No aplica' : 'Variación de tres meses contra los tres meses anteriores',
    'Variación interanual', tri ? 'Cuatro trimestres contra los cuatro anteriores' : 'Doce meses contra los doce anteriores'];
  const raiz = cajaDesplazable('tabla-estandar-cuerpo', titulo);
  const t = el('table', 'tabla-datos');
  t.append(el('caption', 'solo-lector', 'Indicadores, fecha de corte, último valor, participación y variaciones. El guion indica un dato no disponible o no aplicable.'));
  const columnas = el('colgroup');
  for (const ancho of anchos) {
    const c = el('col');
    c.style.width = ancho;
    columnas.append(c);
  }
  t.append(columnas);
  const head = el('thead');
  const encabezado = el('tr');
  titulos.forEach((tituloCol, i) => {
    const th = el('th', i ? 'num' : '');
    th.scope = 'col';
    const abbr = el('abbr', '', tituloCol);
    abbr.title = descripciones[i];
    th.append(abbr);
    encabezado.append(th);
  });
  head.append(encabezado);
  t.append(head);
  const tb = el('tbody');
  for (const f of filas) {
    const uu = f.unidad_ultimo, uc = f.unidad_cambio;
    const cambio = (v) => formatear(v, uc, { ...TABLA, signo: true });
    const share = f.share == null || Number.isNaN(f.share) ? '—' : (f.share >= SHARE_COMPLETO ? '100 %' : porcentaje(f.share * 100, 1, TABLA));
    const celdas = [f.fila, f.corte || '—', formatear(f.ultimo, uu, { ...TABLA, signo: uu === 'pp' }), share, cambio(f.d1), tri ? '—' : cambio(f.d3),
      cambio(f.d12), cambio(f.dventana)];
    const tr = el('tr', f.destacar ? 'fila-total' : '');
    celdas.forEach((valor, i) => {
      const celda = el(i ? 'td' : 'th', i ? 'num' : '', valor == null ? '—' : String(valor));
      if (!i) celda.scope = 'row';
      tr.append(celda);
    });
    tb.append(tr);
  }
  t.append(tb);
  const ayuda = el('details', 'tabla-glosario');
  ayuda.dataset.conservarAbierto = '';
  const glosario = el('dl');
  titulos.forEach((tituloCol, i) => glosario.append(el('dt', '', tituloCol), el('dd', '', descripciones[i])));
  ayuda.append(el('summary', '', 'Cómo leer las columnas'), glosario);
  raiz.append(ayuda, el('p', 'tabla-ayuda', 'Desplaza la tabla para consultar todas las columnas.'), t);
  cont.append(raiz);
  return null;
}

/* ---------- barras_signo ---------- */
function barras_signo(cont, e) {
  const ch = iniciar(cont);
  const filas = e.filas;
  const cifra = (v, d) => numero(v, d, ROTULO);
  ch.setOption({
    ...tema(),
    grid: { left: 6, right: 56, top: 6, bottom: 6, containLabel: true }, // espacio para la etiqueta de la barra más larga
    tooltip: tooltip('axis', { axisPointer: { type: 'shadow' }, valueFormatter: (v) => `${cifra(v, 2)} ${e.unidad || ''}` }),
    xAxis: { type: 'value', axisLabel: { color: C.texto3, fontSize: 11, fontFamily: TIPO.mono, formatter: formatoEje('num') }, splitLine: { lineStyle: { color: C.regla } } },
    yAxis: ejeBase({ color: C.texto, fontSize: 12 }, { type: 'category', inverse: true, data: filas.map((f) => f.nombre) }),
    series: [{ type: 'bar', barMaxWidth: 18, data: filas.map((f) => ({ value: f.valor, itemStyle: { color: f.color || (f.valor >= 0 ? (e.colorPos || C.navy) : (e.colorNeg || C.peor)) } })),
      label: { show: true, position: 'right', fontFamily: TIPO.mono, fontSize: 11, color: C.texto2, formatter: (p) => numero(p.value, e.decimales ?? 2, { ...ROTULO, signo: true }) } }],
  });
  return ch;
}

/* Registro único de componentes. dibujar(contenedor, entrada, { titulo }) devuelve la instancia de ECharts
   (pagina.js le pone role=img y un ResizeObserver) o null si dibujó HTML. entrada: las claves que lee
   (generar_spec.py las publica). */
export const COMPONENTES = Object.freeze({
  ...COMPONENTES_GENERALES,
  percentiles: { dibujar: percentiles, entrada: ['filas'], descripcion: 'Una fila de 40 px por métrica: rango p10–p90 del grupo, mediana, banco y hace un año; color del banco según el lado de la mediana.' },
  cascada_doble: { dibujar: cascada_doble, entrada: ['lineas', 'total', 'nota'], descripcion: 'Cascada HTML: banco y mediana del grupo en paralelo, misma secuencia de líneas, total y brecha; nota del banco debajo.' },
  burbujas_trayectoria: { dibujar: burbujas_trayectoria, entrada: ['puntos', 'trayectorias', 'banco', 'colores', 'ejeX', 'ejeY'], descripcion: 'Dispersión de bancos (tamaño = activo, color por grupo según colores) y las trayectorias trimestrales que mande la página.' },
  comparador: { dibujar: comparador, entrada: ['columnas', 'filas', 'filtros', 'orden', 'banco', 'enlaceFila'], descripcion: 'Tabla ordenable con filtros, sparklines y CSV de lo visible; enlaceFila(fila) hace de cada fila un enlace.' },
  apilada_100: { dibujar: apilada_100, entrada: ['barras', 'formato', 'formatoRotulo'], descripcion: 'Barras horizontales al 100 %; rótulo dentro si la parte es ≥ 8 %.' },
  pesas: { dibujar: pesas, entrada: ['filas', 'escala', 'formato', 'umbral'], descripcion: 'Antes y ahora por fila; color del cambio por signo de la métrica.' },
  dispersion: { dibujar: dispersion, entrada: ['puntos', 'diagonal', 'cuadrantes', 'ejeX', 'ejeY'], descripcion: 'Puntos con nombre, diagonal opcional y textos de cuadrante (tl, br).' },
  barras_h_doble: { dibujar: barras_h_doble, entrada: ['filas', 'series', 'formato', 'activo'], descripcion: 'Dos barras por fila, no apiladas; banco activo resaltado.' },
  barras_ic: { dibujar: barras_ic, entrada: ['filas', 'formato', 'activo'], descripcion: 'Barra con intervalo de confianza; «pocos trimestres» si n < 24.' },
  barras_simple: { dibujar: barras_simple, entrada: ['filas', 'formato', 'max'], descripcion: 'Una barra horizontal por fila con el valor a la derecha; max fija la escala y lo que pasa se marca «›».' },
  barras_linea: { dibujar: barras_linea, entrada: ['categorias', 'barras', 'lineas', 'ejeBarras', 'ejeIzq', 'ejeDer', 'rangoIzq', 'rangoDer', 'intervalo', 'leyendaInteractiva'], descripcion: 'Barras apiladas y líneas sobre categorías; eje de barras a la izquierda o a la derecha; leyenda de ECharts opcional (clic oculta series).' },
  mapa_cuotas: { dibujar: mapa_cuotas, entrada: ['filas', 'colores'], descripcion: 'Treemap de cuotas por banco; colores por grupo (los manda la página) y tinta según el fondo.' },
  tabla_estandar: { dibujar: tabla_estandar, entrada: ['filas'], descripcion: 'LA tabla descriptiva del sitio: Indicador · Corte · Último · Share · m/m · 3m/3m · a/a · 12m/12m (trimestral: t/t · — · a/a · 4T/4T); sin colores, fila destacada para el total.' },
  barras_signo: { dibujar: barras_signo, entrada: ['filas', 'unidad', 'decimales', 'colorPos', 'colorNeg'], descripcion: 'Barras horizontales con signo, en el orden dado; color por fila o por signo.' },
});
