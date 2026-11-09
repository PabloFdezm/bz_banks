/* «Descargar Excel» (pedido de Pablo, 5-nov): baja lo que muestra cada tarjeta, tal como está dibujado
   (con el filtro o la vista elegida), en un .xlsx propio. Sin dependencias: el libro se arma aquí
   (XML de Office + zip sin compresión).

   De dónde salen los datos de una tarjeta, en orden:
   1. los gráficos ECharts de la zona (getOption: series, ejes y formato del eje de valores);
   2. las tablas HTML de la zona (<table>);
   3. la entrada que armó la tarjeta (zona._entrada: filas o series), para los componentes HTML sin tabla.

   Por tarjeta: hoja «Datos» + hoja «Info» (título, subtítulo, nota, fuente, página, fecha).
   Por página: hoja «Índice» + una hoja por tarjeta. */

/* ====================================================================== */
/* ---------- libro .xlsx ---------- */

const XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n';
const esc = (s) => String(s)
  .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/* formatos de número: id 14 es la fecha corta del sistema; los propios parten en 164 */
const FMT = {
  pct: '0.0%',
  pctn: '0.0" %"',
  pp: '0.0" pp"',
  num: '#,##0.0##',
  entero: '#,##0',
  fecha: 'dd-mm-yyyy',
};

function columnaLetra(i) {
  let s = '';
  for (i += 1; i > 0; i = Math.floor((i - 1) / 26)) s = String.fromCharCode(65 + ((i - 1) % 26)) + s;
  return s;
}

const DIA = 86400000;
const BASE_EXCEL = Date.UTC(1899, 11, 30);
function serialFecha(d) {
  return (Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()) - BASE_EXCEL) / DIA;
}

/* hoja = { nombre, filas: [[celda]], anchos?: [n], congelar?: n filas, negrita?: Set(filas) }
   celda = null | string | number | Date | { v, fmt: 'pct'|'pp'|'num'|'entero'|'fecha', b?: true } */
function libro(hojas) {
  const formatos = [];          /* códigos propios en orden → numFmtId 164 + i */
  const xfs = [{ fmt: 0, b: false }];
  const estilo = (fmt, b = false) => {
    let id = 0;
    if (fmt === 'fecha') id = 164 + idFormato(FMT.fecha);
    else if (fmt && FMT[fmt]) id = 164 + idFormato(FMT[fmt]);
    let i = xfs.findIndex((x) => x.fmt === id && x.b === b);
    if (i < 0) { xfs.push({ fmt: id, b }); i = xfs.length - 1; }
    return i;
  };
  function idFormato(codigo) {
    let i = formatos.indexOf(codigo);
    if (i < 0) { formatos.push(codigo); i = formatos.length - 1; }
    return i;
  }

  const archivos = [];
  const hojasXml = hojas.map((h, n) => {
    const negrita = h.negrita || new Set();
    const filasXml = h.filas.map((fila, r) => {
      const celdas = fila.map((celda, c) => {
        if (celda == null || celda === '') return '';
        const ref = `${columnaLetra(c)}${r + 1}`;
        let v = celda, fmt = null, b = negrita.has(r);
        if (typeof celda === 'object' && !(celda instanceof Date)) { v = celda.v; fmt = celda.fmt || null; b = b || Boolean(celda.b); }
        if (v == null || v === '') return '';
        if (v instanceof Date) {
          if (Number.isNaN(v.getTime())) return '';
          return `<c r="${ref}" s="${estilo('fecha', b)}"><v>${serialFecha(v)}</v></c>`;
        }
        if (typeof v === 'number') {
          if (!Number.isFinite(v)) return '';
          const s = estilo(fmt, b);
          return `<c r="${ref}"${s ? ` s="${s}"` : ''}><v>${v}</v></c>`;
        }
        if (typeof v === 'boolean') return `<c r="${ref}" t="b"${b ? ` s="${estilo(null, true)}"` : ''}><v>${v ? 1 : 0}</v></c>`;
        const s = b ? estilo(null, true) : 0;
        return `<c r="${ref}" t="inlineStr"${s ? ` s="${s}"` : ''}><is><t xml:space="preserve">${esc(v)}</t></is></c>`;
      }).join('');
      return `<row r="${r + 1}">${celdas}</row>`;
    }).join('');
    const nCols = Math.max(1, ...h.filas.map((f) => f.length));
    const anchos = Array.from({ length: nCols }, (_, c) => {
      if (h.anchos?.[c]) return h.anchos[c];
      let m = 8;
      for (const f of h.filas.slice(0, 400)) {
        const x = f[c];
        const v = x && typeof x === 'object' && !(x instanceof Date) ? x.v : x;
        const largo = v instanceof Date ? 10 : typeof v === 'number' ? 12 : v == null ? 0 : String(v).length;
        m = Math.max(m, Math.min(60, largo + 2));
      }
      return m;
    });
    const cols = `<cols>${anchos.map((a, c) => `<col min="${c + 1}" max="${c + 1}" width="${a}" customWidth="1"/>`).join('')}</cols>`;
    const congelar = h.congelar
      ? `<sheetViews><sheetView workbookViewId="0"><pane ySplit="${h.congelar}" topLeftCell="A${h.congelar + 1}" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>`
      : '<sheetViews><sheetView workbookViewId="0"/></sheetViews>';
    archivos.push([`xl/worksheets/sheet${n + 1}.xml`,
      `${XML}<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">${congelar}${cols}<sheetData>${filasXml}</sheetData></worksheet>`]);
    return h;
  });

  const nombres = nombresHoja(hojasXml.map((h) => h.nombre));
  archivos.push(['xl/workbook.xml',
    `${XML}<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>${
      nombres.map((nm, i) => `<sheet name="${esc(nm)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join('')}</sheets></workbook>`]);
  archivos.push(['xl/_rels/workbook.xml.rels',
    `${XML}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${
      nombres.map((_, i) => `<Relationship Id="rId${i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i + 1}.xml"/>`).join('')
    }<Relationship Id="rId${nombres.length + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`]);
  archivos.push(['xl/styles.xml',
    `${XML}<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">${
      formatos.length ? `<numFmts count="${formatos.length}">${formatos.map((f, i) => `<numFmt numFmtId="${164 + i}" formatCode="${esc(f)}"/>`).join('')}</numFmts>` : ''
    }<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>`
    + '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
    + '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
    + '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    + `<cellXfs count="${xfs.length}">${xfs.map((x) => `<xf numFmtId="${x.fmt}" fontId="${x.b ? 1 : 0}" fillId="0" borderId="0"${x.fmt ? ' applyNumberFormat="1"' : ''}${x.b ? ' applyFont="1"' : ''}/>`).join('')}</cellXfs>`
    + '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    + '</styleSheet>']);
  archivos.push(['_rels/.rels',
    `${XML}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`]);
  archivos.push(['[Content_Types].xml',
    `${XML}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>${
      nombres.map((_, i) => `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('')}</Types>`]);
  /* [Content_Types].xml primero en el zip */
  archivos.unshift(archivos.pop());
  return new Blob([zip(archivos)], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
}

/* nombres de hoja de Excel: ≤ 31 caracteres, sin []:*?/\ y sin repetir */
function nombresHoja(lista) {
  const usados = new Set();
  return lista.map((n, i) => {
    let base = String(n || `Hoja ${i + 1}`).replace(/[[\]:*?/\\]/g, ' ').replace(/\s+/g, ' ').trim().replace(/^'+|'+$/g, '') || `Hoja ${i + 1}`;
    base = base.slice(0, 31);
    let nombre = base, k = 2;
    while (usados.has(nombre.toLowerCase())) { const suf = ` (${k++})`; nombre = base.slice(0, 31 - suf.length) + suf; }
    usados.add(nombre.toLowerCase());
    return nombre;
  });
}

/* ---------- zip sin compresión (método 0) ---------- */
const TABLA_CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  return t;
})();
function crc32(bytes) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < bytes.length; i++) c = TABLA_CRC[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}
function zip(archivos) {
  const cod = new TextEncoder();
  const partes = [], central = [];
  let desplazamiento = 0;
  const ahora = new Date();
  const hora = (ahora.getHours() << 11) | (ahora.getMinutes() << 5) | (ahora.getSeconds() >> 1);
  const fecha = ((ahora.getFullYear() - 1980) << 9) | ((ahora.getMonth() + 1) << 5) | ahora.getDate();
  for (const [nombre, texto] of archivos) {
    const n = cod.encode(nombre), datos = cod.encode(texto), crc = crc32(datos);
    const loc = new DataView(new ArrayBuffer(30));
    loc.setUint32(0, 0x04034b50, true); loc.setUint16(4, 20, true); loc.setUint16(6, 0x0800, true);
    loc.setUint16(8, 0, true); loc.setUint16(10, hora, true); loc.setUint16(12, fecha, true);
    loc.setUint32(14, crc, true); loc.setUint32(18, datos.length, true); loc.setUint32(22, datos.length, true);
    loc.setUint16(26, n.length, true); loc.setUint16(28, 0, true);
    partes.push(new Uint8Array(loc.buffer), n, datos);
    const cen = new DataView(new ArrayBuffer(46));
    cen.setUint32(0, 0x02014b50, true); cen.setUint16(4, 20, true); cen.setUint16(6, 20, true); cen.setUint16(8, 0x0800, true);
    cen.setUint16(10, 0, true); cen.setUint16(12, hora, true); cen.setUint16(14, fecha, true);
    cen.setUint32(16, crc, true); cen.setUint32(20, datos.length, true); cen.setUint32(24, datos.length, true);
    cen.setUint16(28, n.length, true); cen.setUint32(42, desplazamiento, true);
    central.push(new Uint8Array(cen.buffer), n);
    desplazamiento += 30 + n.length + datos.length;
  }
  const tamCentral = central.reduce((t, p) => t + p.length, 0);
  const fin = new DataView(new ArrayBuffer(22));
  fin.setUint32(0, 0x06054b50, true); fin.setUint16(8, archivos.length, true); fin.setUint16(10, archivos.length, true);
  fin.setUint32(12, tamCentral, true); fin.setUint32(16, desplazamiento, true);
  return new Blob([...partes, ...central, new Uint8Array(fin.buffer)]);
}

/* ====================================================================== */
/* ---------- datos de una tarjeta ---------- */

/* bloque = { titulo?, columnas: [{ titulo, fmt? }], filas: [[valor]] } */

const MENOS = /\u2212/g;
const valorDe = (x) => (x && typeof x === 'object' && !Array.isArray(x) && 'value' in x ? x.value : x);
const visible = (s) => s && !String(s.name ?? '').startsWith('_');

/* qué unidad muestra el eje: se le pregunta a su formateador */
const formatoDeEje = (eje) => formatoDeFuncion(eje?.axisLabel?.formatter);

function aFecha(x) {
  if (x instanceof Date) return x;
  if (typeof x === 'number') return new Date(x);
  const s = String(x);
  if (/^\d{4}-\d{2}(-\d{2})?/.test(s)) return new Date(s.length === 7 ? `${s}-01` : s.slice(0, 10));
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? null : d;
}
const claveTiempo = (x) => { const d = aFecha(x); return d ? d.toISOString().slice(0, 10) : String(x); };

function deECharts(chart) {
  const opt = chart.getOption();
  const series = (opt.series || []).filter(visible);
  if (!series.length) return [];
  const bloques = [];
  const ejesX = opt.xAxis || [], ejesY = opt.yAxis || [];

  /* sin ejes: torta, embudo, treemap, sunburst, gauge */
  const sinEje = series.filter((s) => ['pie', 'funnel', 'treemap', 'sunburst', 'gauge'].includes(s.type));
  for (const s of sinEje) {
    const filas = [];
    const recorrer = (nodos, ruta) => {
      for (const n of nodos || []) {
        const nombre = n.name ?? '';
        const v = valorDe(n);
        const valor = Array.isArray(v) ? v[0] : v;
        if (n.children?.length) recorrer(n.children, ruta ? `${ruta} › ${nombre}` : nombre);
        else filas.push(ruta != null ? [ruta, nombre, valor] : [nombre, valor]);
      }
    };
    const anidado = (s.data || []).some((n) => n.children?.length);
    if (anidado) recorrer(s.data, ''); else recorrer(s.data, null);
    if (!filas.length) continue;
    bloques.push({
      titulo: series.length > 1 ? s.name : null,
      columnas: anidado ? [{ titulo: 'Grupo' }, { titulo: 'Nombre' }, { titulo: 'Valor' }] : [{ titulo: 'Nombre' }, { titulo: s.name || 'Valor' }],
      filas: filas.map((f) => (anidado ? f : f)),
    });
  }

  /* mapa de calor: filas = categorías del eje Y, columnas = las del eje X */
  for (const s of series.filter((x) => x.type === 'heatmap')) {
    const ex = ejesX[s.xAxisIndex || 0], ey = ejesY[s.yAxisIndex || 0];
    const cx = ex?.data?.map((d) => valorDe(d)) || [], cy = ey?.data?.map((d) => valorDe(d)) || [];
    const m = new Map();
    for (const it of s.data || []) {
      const v = valorDe(it);
      if (!Array.isArray(v)) continue;
      const [x, y, z] = v;
      m.set(`${typeof x === 'number' && cx.length ? cx[x] : x}|${typeof y === 'number' && cy.length ? cy[y] : y}`, z);
    }
    const xs = cx.length ? cx : [...new Set([...m.keys()].map((k) => k.split('|')[0]))];
    const ys = cy.length ? cy : [...new Set([...m.keys()].map((k) => k.split('|')[1]))];
    bloques.push({
      titulo: series.length > 1 ? s.name : null,
      columnas: [{ titulo: '' }, ...xs.map((x) => ({ titulo: String(x) }))],
      filas: ys.map((y) => [y, ...xs.map((x) => m.get(`${x}|${y}`) ?? null)]),
    });
  }

  /* cartesianas */
  const cart = series.filter((s) => !sinEje.includes(s) && s.type !== 'heatmap' && Array.isArray(s.data));
  /* agrupar por pareja de ejes */
  const grupos = new Map();
  for (const s of cart) {
    const k = `${s.xAxisIndex || 0}|${s.yAxisIndex || 0}`;
    if (!grupos.has(k)) grupos.set(k, []);
    grupos.get(k).push(s);
  }
  /* series que comparten eje X (p. ej. barras + línea con doble eje Y) se juntan en un bloque */
  const porX = new Map();
  for (const [k, ss] of grupos) {
    const xi = Number(k.split('|')[0]);
    const ex = ejesX[xi], ey = ejesY[Number(k.split('|')[1])];
    const horizontal = ey?.type === 'category' && ex?.type !== 'category';
    const clave = horizontal ? `y${k.split('|')[1]}` : `x${xi}`;
    if (!porX.has(clave)) porX.set(clave, { ex, ey, horizontal, series: [] });
    for (const s of ss) porX.get(clave).series.push({ s, ey: ejesY[s.yAxisIndex || 0], ex: ejesX[s.xAxisIndex || 0] });
  }
  for (const { ex, ey, horizontal, series: lista } of porX.values()) {
    const ejeCat = horizontal ? ey : ex;
    const ejeVal = horizontal ? ex : ey;
    /* dispersión: los dos ejes son de valores */
    if (ejeCat?.type === 'value' && lista.every(({ s }) => ['scatter', 'effectScatter'].includes(s.type))) {
      const fx = formatoDeEje(ex), fy = formatoDeEje(ey);
      const conTam = lista.some(({ s }) => (s.data || []).some((d) => Array.isArray(valorDe(d)) && valorDe(d).length > 2));
      const filas = [];
      for (const { s } of lista) for (const d of s.data || []) {
        const v = valorDe(d);
        if (!Array.isArray(v)) continue;
        filas.push([s.name, d?.name ?? '', v[0], v[1], ...(conTam ? [v[2] ?? null] : [])]);
      }
      bloques.push({
        columnas: [{ titulo: 'Serie' }, { titulo: 'Nombre' }, { titulo: ex?.name || 'Eje X', fmt: fx }, { titulo: ey?.name || 'Eje Y', fmt: fy }, ...(conTam ? [{ titulo: 'Tamaño' }] : [])],
        filas,
      });
      continue;
    }
    const cats = ejeCat?.type === 'category' ? (ejeCat.data || []).map((d) => valorDe(d)) : null;
    const tiempo = ejeCat?.type === 'time';
    const claves = [], filasPor = new Map();
    const alta = (k, etiqueta) => { if (!filasPor.has(k)) { filasPor.set(k, { etiqueta, vals: new Map() }); claves.push(k); } return filasPor.get(k); };
    if (cats) cats.forEach((c, i) => alta(`i${i}`, c));
    for (const { s } of lista) {
      (s.data || []).forEach((d, i) => {
        const v = valorDe(d);
        let x, y;
        if (Array.isArray(v)) { [x, y] = horizontal ? [v[1], v[0]] : [v[0], v[1]]; }
        else { x = null; y = v; }
        if (y != null && typeof y === 'object') return;
        let k, etiqueta;
        if (cats) {
          const idx = x == null ? i : typeof x === 'number' ? x : cats.indexOf(x);
          k = `i${idx}`; etiqueta = cats[idx] ?? x;
        } else if (tiempo) {
          if (x == null) return;
          k = claveTiempo(x); etiqueta = aFecha(x);
        } else {
          if (x == null) { x = i; }
          k = `v${x}`; etiqueta = x;
        }
        alta(k, etiqueta).vals.set(s, y == null || y === '-' ? null : y);
      });
    }
    if (!claves.length) continue;
    let orden = claves;
    if (tiempo) orden = [...claves].sort();
    const ss = lista.map(({ s }) => s);
    /* nombres repetidos (p. ej. barras apiladas positivas y negativas de una misma serie): se juntan */
    const nombres = [...new Set(ss.map((s) => s.name))];
    const filas = orden.map((k) => {
      const f = filasPor.get(k);
      return [f.etiqueta, ...nombres.map((nm) => {
        const vs = ss.filter((s) => s.name === nm).map((s) => f.vals.get(s)).filter((v) => v != null && v !== '');
        return vs.length ? (vs.length === 1 ? vs[0] : vs.reduce((a, b) => a + b, 0)) : null;
      })];
    }).filter((f) => f.slice(1).some((v) => v != null));
    const fmtSerie = (nm) => {
      const s = ss.find((x) => x.name === nm);
      return formatoDeEje(horizontal ? ejesX[s.xAxisIndex || 0] : ejesY[s.yAxisIndex || 0]) || formatoDeEje(ejeVal);
    };
    /* series del mismo eje sin formato propio toman el del bloque */
    const fmts = nombres.map((nm) => fmtSerie(nm));
    const comun = fmts.find(Boolean) || null;
    bloques.push({
      columnas: [{ titulo: tiempo ? 'Fecha' : (ejeCat?.name || '') }, ...nombres.map((nm, i) => ({ titulo: nm ?? (nombres.length > 1 ? `Serie ${i + 1}` : 'Valor'), fmt: fmts[i] || comun }))],
      filas,
    });
  }
  return bloques;
}

/* «5,2 %» → 0.052 (pct); «−0,3 pp» → −0.3 (pp); «1.234,5» → 1234.5; el resto queda como texto */
function numeroDeTexto(t) {
  const s = String(t).replace(/\u00A0|\u202F/g, ' ').replace(MENOS, '-').trim();
  const m = s.match(/^([+-]?)\s*(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?\s*(%|pp|pb)?$/);
  if (!m) return null;
  const n = Number(`${m[1] === '-' ? '-' : ''}${m[2].replace(/\./g, '')}${m[3] ? `.${m[3]}` : ''}`);
  if (!Number.isFinite(n)) return null;
  if (m[4] === '%') return { v: n / 100, fmt: 'pct' };
  if (m[4] === 'pp') return { v: n, fmt: 'pp' };
  return { v: n, fmt: m[3] ? 'num' : null };
}
const celdaDeTexto = (t) => {
  const x = String(t ?? '').replace(/\s+/g, ' ').trim();
  if (!x || x === '—' || x === '–' || x === '-') return null;
  return numeroDeTexto(x) || x;
};

function deTablaHtml(tabla) {
  const cab = [...tabla.querySelectorAll('thead tr')].at(-1);
  const columnas = cab ? [...cab.children].map((th) => ({ titulo: th.textContent.replace(/\s+/g, ' ').trim() })) : [];
  const filas = [...tabla.querySelectorAll('tbody tr')].map((tr) => [...tr.children].map((td) => celdaDeTexto(td.textContent)));
  if (!filas.length) return null;
  const n = Math.max(columnas.length, ...filas.map((f) => f.length));
  while (columnas.length < n) columnas.push({ titulo: '' });
  return { columnas, filas };
}

/* ---------- tablas armadas con div (fila de cabecera «…-cab» + filas «…-fila») ---------- */
function deGrillasHtml(zona) {
  const bloques = [];
  const cabs = [...zona.querySelectorAll('[class*="-cab"]')].filter((c) => [...c.classList].some((k) => /-(cab|cabecera)$/.test(k)) && [...c.classList].some((k) => /-fila$/.test(k)));
  for (const cab of cabs) {
    const claseFila = [...cab.classList].find((k) => /-fila$/.test(k));
    const filasEl = [...cab.parentElement.children].filter((n) => n !== cab && n.classList.contains(claseFila));
    if (!filasEl.length) continue;
    const texto = (n) => n.textContent.replace(/\s+/g, ' ').trim();
    const columnas = [...cab.children].map((c) => ({ titulo: texto(c) }));
    const filas = filasEl.map((f) => [...f.children].map((c) => {
      const t = texto(c);
      const baja = /^▼/.test(t);
      const x = celdaDeTexto(t.replace(/^[▲▼]\s*/, ''));
      if (baja && x && typeof x === 'object') return { ...x, v: -x.v };
      return x;
    }));
    const n = Math.max(columnas.length, ...filas.map((f) => f.length));
    while (columnas.length < n) columnas.push({ titulo: '' });
    if (columnas.every((c) => !c.titulo)) columnas[0].titulo = 'Nombre';
    bloques.push({ columnas, filas });
  }
  return bloques;
}

/* ---------- entrada armada por la tarjeta (componentes sin gráfico ni tabla legible) ---------- */
function primitivo(v) { return v == null || v instanceof Date || ['string', 'number', 'boolean'].includes(typeof v); }
const OMITIR = /^(_|color|colores|colorEtiqueta|textoSobre|clase|tt$|id$|negrita|tono|estilo|icono|aria|formatear|tooltip|grid$|pastilla$|ventana)/i;
const NO_BLOQUE = new Set(['leyenda', 'controles', 'cuadrantes', 'refs', 'bandas', 'columnasTooltip', 'definiciones', 'opciones']);
const ROTULOS = {
  nombre: 'Nombre', valor: 'Valor', antes: 'Antes', ahora: 'Ahora', grupo: 'Grupo', sub: 'Detalle', nota: 'Nota',
  total: 'Total', fecha: 'Fecha', anio: 'Año', dato: 'Dato', cab: 'Período', etiqueta: 'Etiqueta', ultimo: 'Último',
  unidad: 'Unidad', sigla: 'Sigla', peso: 'Peso', tamano: 'Tamaño', indicador: 'Indicador', signo: 'Signo',
  umbral: 'Umbral', unidadUmbral: 'Unidad del umbral', desvio: 'Desvío', serie: 'Serie', objetivo: 'Objetivo',
  hoy: 'Hoy', lag: 'Rezago', senal: 'Señal', actividad: 'Actividad', fuente: 'Fuente', destino: 'Destino',
  destinoPct: 'Destino, %', r: 'r', r2: 'R²', nivel: 'Nivel', formal: 'Formal', mediana: 'Mediana', media: 'Media',
  min: 'Mínimo', max: 'Máximo', techo: 'Techo', meta: 'Meta', a: 'A', b: 'B', delta: 'Variación', rotulo: 'Rótulo',
};
const legible = (k) => ROTULOS[k] || (k.charAt(0).toUpperCase() + k.slice(1).replace(/([a-z])([A-Z])/g, '$1 $2').toLowerCase());

/* qué unidad muestra un formateador (eje o entrada): fracción → %, ya en % → « %», pp */
function formatoDeFuncion(f) {
  if (typeof f !== 'function') return null;
  try {
    const a = String(f(0.05)).replace(/\u00A0/g, ' '), b = String(f(5)).replace(/\u00A0/g, ' ');
    if (/(^|[^\d,])5([,.]0+)?\s*%/.test(a)) return 'pct';
    if (/%/.test(b)) return 'pctn';
    if (/pp/.test(b)) return 'pp';
  } catch { /* formateador que espera otra cosa */ }
  return null;
}

/* lista de objetos → filas planas: objetos anidados se aplanan («antes x»), listas de números pasan a columnas,
   listas de objetos (partes, paneles, años) se abren en filas hijas que heredan los campos del padre */
function aplanar(lista, herencia = {}, nivel = 0) {
  const out = [];
  for (const o of lista) {
    if (!o || typeof o !== 'object' || Array.isArray(o)) continue;
    const base = { ...herencia };
    const hijos = [];
    for (const [k, v] of Object.entries(o)) {
      if (OMITIR.test(k) || typeof v === 'function') continue;
      if (primitivo(v)) base[k] = v;
      else if (Array.isArray(v)) {
        if (v.every(primitivo)) v.forEach((x, i) => { base[`${k}#${i}`] = x; });
        else if (v.every((x) => Array.isArray(x) && x.length >= 2 && x.every(primitivo) && typeof x.at(-2) === 'string' && x.at(-2) && !/^\d{4}-\d{2}/.test(x.at(-2)))) {
          /* pares [rótulo, valor] (p. ej. «Hace un año», «4,4 %»): una columna por rótulo */
          for (const x of v) base[`${k}:${x.at(-2)}`] = x.at(-1);
        } else if (v.every((x) => Array.isArray(x))) {
          /* pares [fecha, valor]: filas con Fecha y Valor */
          const fechas = v.every((x) => x.length === 2 && typeof x[0] === 'string' && /^\d{4}-\d{2}/.test(x[0]));
          hijos.push([k, v.map((x) => (fechas ? { fecha: aFecha(x[0]), valor: x[1] } : Object.fromEntries(x.map((y, i) => [`${k}#${i}`, y]))))]);
        }
        else if (v.every((x) => x && typeof x === 'object')) hijos.push([k, v]);
      } else if (typeof v === 'object') {
        for (const [k2, v2] of Object.entries(v)) if (primitivo(v2) && !OMITIR.test(k2)) base[`${k} ${k2}`] = v2;
      }
    }
    if ('valor' in base && 'rotulo' in base) delete base.rotulo;
    if (hijos.length && nivel < 3) {
      const her = Object.fromEntries(Object.entries(base).map(([k, v]) => [k.startsWith('^') ? k : `^${k}`, v]));
      for (const [, v] of hijos) out.push(...aplanar(v, her, nivel + 1));
    } else out.push(base);
  }
  return out;
}

function bloqueDeObjetos(lista, e, titulo) {
  const filas = aplanar(lista);
  if (!filas.length) return null;
  const claves = [];
  for (const f of filas) for (const k of Object.keys(f)) if (!claves.includes(k)) claves.push(k);
  const utiles = claves.filter((k) => filas.some((f) => f[k] != null && f[k] !== ''));
  if (!utiles.some((k) => filas.some((f) => typeof f[k] === 'number'))) return null;
  const etiquetasCol = Array.isArray(e.columnas) && e.columnas.every((c) => typeof c === 'string') ? e.columnas : null;
  const fmtX = formatoDeFuncion(e.formatearX), fmtY = formatoDeFuncion(e.formatear) || formatoDeFuncion(e.formatearCelda);
  const columnas = utiles.map((k) => {
    const padre = k.startsWith('^');
    const base = k.replace(/^\^+/, '');
    let t;
    const m = base.match(/^(.+)#(\d+)$/);
    const par = base.match(/^[^:]+:(.+)$/);
    if (par) t = par[1];
    else if (m) {
      const largo = Math.max(...filas.map((f) => Object.keys(f).filter((x) => x.replace(/^\^+/, '').startsWith(`${m[1]}#`)).length));
      t = etiquetasCol && etiquetasCol.length === largo ? etiquetasCol[Number(m[2])] : `${legible(m[1])} ${Number(m[2]) + 1}`;
    } else if (base === 'x') t = e.nombreX || 'X';
    else if (base === 'y') t = e.nombreY || 'Y';
    else if (base === 'valor' && e.nombreValor) t = e.nombreValor;
    else if (/^antes [xy]$/.test(base)) t = `${base.endsWith('x') ? (e.nombreX || 'X') : (e.nombreY || 'Y')}, antes`;
    else t = base.split(' ').map(legible).join(' ');
    if (padre) t = base === 'nombre' ? 'Grupo' : `${t} (grupo)`;
    const fmt = /(^|\s)x$/.test(base) ? fmtX : /(^|\s)y$/.test(base) || base === 'valor' || /#\d+$/.test(base) ? fmtY : null;
    return { titulo: t, fmt };
  });
  const celda = (v) => (typeof v === 'string' ? (numeroDeTexto(v) || v) : v);
  return { titulo, columnas, filas: filas.map((f) => utiles.map((k) => celda(f[k] ?? null))) };
}

function deEntrada(e) {
  if (!e || typeof e !== 'object') return [];
  const bloques = [];
  const fmt = formatoDeFuncion(e.formatear) || formatoDeFuncion(e.formatearCelda);
  /* matriz: rótulos de filas y columnas + valores (mapa de calor, mapa de sostenibilidad) */
  const matriz = ['valores', 'celdas'].map((k) => e[k]).find((v) => Array.isArray(v) && v.length && v.every(Array.isArray));
  const conMatriz = Boolean(matriz && Array.isArray(e.filas) && Array.isArray(e.columnas));
  if (conMatriz) {
    const cols = Array.isArray(e.columnasTooltip) && e.columnasTooltip.length === e.columnas.length ? e.columnasTooltip : e.columnas;
    bloques.push({
      columnas: [{ titulo: '' }, ...cols.map((c) => ({ titulo: String(c), fmt }))],
      filas: e.filas.map((f, i) => [typeof f === 'object' ? (f?.nombre ?? '') : f, ...cols.map((_, j) => matriz[i]?.[j] ?? null)]),
    });
  }
  /* series con puntos [fecha, valor] o valores por categoría */
  const series = Array.isArray(e.series) ? e.series.filter((s) => s && typeof s === 'object') : [];
  if (series.some((s) => Array.isArray(s.puntos))) {
    const claves = [], filas = new Map();
    const conP = series.filter((s) => Array.isArray(s.puntos));
    for (const s of conP) for (const p of s.puntos) {
      const [x, y] = Array.isArray(p) ? p : [p?.fecha ?? p?.x, p?.valor ?? p?.y];
      const k = claveTiempo(x);
      if (!filas.has(k)) { filas.set(k, { x: aFecha(x) || x, vals: new Map() }); claves.push(k); }
      filas.get(k).vals.set(s, y);
    }
    claves.sort();
    bloques.push({
      columnas: [{ titulo: 'Fecha' }, ...conP.map((s) => ({ titulo: s.nombre || s.name || '', fmt }))],
      filas: claves.map((k) => [filas.get(k).x, ...conP.map((s) => filas.get(k).vals.get(s) ?? null)]),
    });
  } else if (series.some((s) => Array.isArray(s.valores))) {
    const conV = series.filter((s) => Array.isArray(s.valores));
    const ejes = e.categorias || (e.fechas || []).map((f) => aFecha(f) || f);
    const n = Math.max(ejes.length, ...conV.map((s) => s.valores.length));
    bloques.push({
      columnas: [{ titulo: e.fechas ? 'Fecha' : '' }, ...conV.map((s) => ({ titulo: s.nombre || s.name || '', fmt }))],
      filas: Array.from({ length: n }, (_, i) => [ejes[i] ?? i + 1, ...conV.map((s) => valorDe(s.valores[i]) ?? null)]),
    });
  }
  /* listas de objetos (filas, puntos, pasos, hojas, barras, paneles, marcas…) */
  const listas = Object.entries(e).filter(([k, v]) => !NO_BLOQUE.has(k) && !OMITIR.test(k) && k !== 'series' && !(conMatriz && k === 'filas')
    && Array.isArray(v) && v.length && v.every((x) => x && typeof x === 'object' && !Array.isArray(x)));
  for (const [k, v] of listas) {
    const b = bloqueDeObjetos(v, e, listas.length > 1 || bloques.length ? legible(k) : null);
    if (b) bloques.push(b);
  }
  return bloques.filter((b) => b.filas.length);
}

/* componentes cuyo gráfico no se entiende bien desde ECharts (puntos sin serie, bases invisibles, matrices):
   para ellos manda la entrada */
const PRIMERO_ENTRADA = new Set(['trayectoria', 'dispersion', 'dispersionL', 'burbujas', 'heatmap', 'cascada', 'cascada_scroll', 'treemap', 'clu_sectores']);

/** Bloques de datos de una tarjeta (lo que muestra ahora). Vacío si no hay nada que bajar. */
export function datosDeTarjeta(figura) {
  const zona = figura?.querySelector('.tarjeta-zona');
  if (!zona || zona.querySelector('.preparacion, .error-dato')) return [];
  const comp = figura.dataset.componente || '';
  if (PRIMERO_ENTRADA.has(comp)) {
    const b = deEntrada(zona._entrada);
    if (b.length) return b;
  }
  const bloques = [];
  for (const n of zona.querySelectorAll('[_echarts_instance_]')) {
    const ch = window.echarts?.getInstanceByDom(n);
    if (ch && !ch.isDisposed()) { try { bloques.push(...deECharts(ch)); } catch (err) { console.warn('Excel: no se pudo leer el gráfico', err); } }
  }
  for (const t of zona.querySelectorAll('table')) { const b = deTablaHtml(t); if (b) bloques.push(b); }
  if (!bloques.length) bloques.push(...deGrillasHtml(zona));
  if (!bloques.length) bloques.push(...deEntrada(zona._entrada));
  return bloques.filter((b) => b.filas.length);
}

export const tieneDatos = (figura) => datosDeTarjeta(figura).length > 0;

/* ====================================================================== */
/* ---------- hojas y descarga ---------- */

const textoDe = (figura, sel) => figura.querySelector(sel)?.textContent.replace(/\s+/g, ' ').trim() || '';
function metaTarjeta(figura) {
  const sec = figura.closest('section');
  return {
    clave: figura.dataset.clave || '',
    titulo: textoDe(figura, '.tarjeta-titulo'),
    sub: textoDe(figura, '.tarjeta-sub'),
    nota: textoDe(figura, '.tarjeta-nota'),
    fuente: textoDe(figura, '.tarjeta-pie').replace(/^Fuente:\s*/, ''),
    seccion: sec ? [textoDe(sec, '.riel-numero'), textoDe(sec, '.riel-nombre')].filter(Boolean).join(' · ') : '',
    filtros: [...figura.querySelectorAll('.tarjeta-controles button[aria-pressed="true"]')].map((b) => b.textContent.trim()).join(' · '),
  };
}
function nombrePagina() {
  return document.querySelector('.barra-titulo-nombre')?.textContent.trim() || document.title || 'Monitor Brasil';
}

/* bloques → filas de hoja (encabezado en negrita; bloques separados por una fila vacía) */
function hojaDeBloques(nombre, bloques) {
  const filas = [], negrita = new Set();
  bloques.forEach((b, i) => {
    if (i) filas.push([]);
    if (b.titulo) { negrita.add(filas.length); filas.push([b.titulo]); }
    negrita.add(filas.length);
    filas.push(b.columnas.map((c) => c.titulo));
    for (const f of b.filas) {
      filas.push(f.map((v, c) => {
        if (v == null) return null;
        const fmt = b.columnas[c]?.fmt;
        if (v instanceof Date) return v;
        if (typeof v === 'object') return v;
        if (typeof v === 'number' && fmt) return { v, fmt };
        return v;
      }));
    }
  });
  return { nombre, filas, negrita, congelar: bloques.length === 1 && !bloques[0].titulo ? 1 : 0 };
}

function hojaInfo(meta) {
  const filas = [
    ['Monitor Brasil', nombrePagina()],
    ['Sección', meta.seccion],
    ['Gráfico', meta.titulo],
    ['Subtítulo', meta.sub],
    ['Vista elegida', meta.filtros],
    ['Nota', meta.nota],
    ['Fuente', meta.fuente],
    ['Dirección', location.href.split('#')[0]],
    ['Descargado', fechaHora()],
  ].filter(([, v]) => v);
  return { nombre: 'Info', filas, negrita: new Set(), anchos: [16, 90] };
}

const fechaHora = () => {
  const d = new Date(), p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
};
const fechaArchivo = () => fechaHora().slice(0, 10);
const slug = (s) => String(s).replace(/\s*\([^)]*\)/g, '').normalize('NFD').replace(/[\u0300-\u036F]/g, '').replace(/[^A-Za-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 60);

function bajar(blob, nombre) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = nombre; a.rel = 'noopener';
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 30000);
}

/** Excel de una tarjeta. Devuelve false si no hay datos. */
export function descargarTarjeta(figura) {
  const bloques = datosDeTarjeta(figura);
  if (!bloques.length) return false;
  const meta = metaTarjeta(figura);
  const blob = libro([hojaDeBloques('Datos', bloques), hojaInfo(meta)]);
  bajar(blob, `${slug(nombrePagina())}_${slug(meta.titulo || meta.clave) || 'grafico'}_${fechaArchivo()}.xlsx`);
  return true;
}

/** Excel de toda la página: índice + una hoja por tarjeta con datos. Devuelve cuántas hojas. */
export function descargarPagina(raiz = document.getElementById('app')) {
  const figuras = [...(raiz?.querySelectorAll('figure.tarjeta[data-clave]') || [])].filter((f) => !f.closest('.capa-grande'));
  const hojas = [], indice = [['Hoja', 'Sección', 'Gráfico', 'Subtítulo', 'Vista elegida', 'Fuente']];
  for (const f of figuras) {
    const bloques = datosDeTarjeta(f);
    if (!bloques.length) continue;
    const meta = metaTarjeta(f);
    const nombre = `${String(hojas.length + 1).padStart(2, '0')} ${meta.titulo || meta.clave}`;
    hojas.push(hojaDeBloques(nombre, bloques));
    indice.push([null, meta.seccion, meta.titulo, meta.sub, meta.filtros, meta.fuente]);
  }
  if (!hojas.length) return 0;
  const nombres = nombresHoja(hojas.map((h) => h.nombre));
  hojas.forEach((h, i) => { h.nombre = nombres[i]; indice[i + 1][0] = nombres[i]; });
  const cabecera = [
    ['Monitor Brasil', nombrePagina()],
    ['Dirección', location.href.split('#')[0]],
    ['Descargado', fechaHora()],
    [],
  ];
  const hojaIndice = { nombre: 'Índice', filas: [...cabecera, ...indice], negrita: new Set([cabecera.length]), anchos: [34, 30, 50, 60, 24, 50] };
  bajar(libro([hojaIndice, ...hojas]), `${slug(nombrePagina())}_${fechaArchivo()}.xlsx`);
  return hojas.length;
}

/* para pruebas (herramientas/): arma el libro sin bajarlo */
export const _probar = { libro, datosDeTarjeta, numeroDeTexto };
