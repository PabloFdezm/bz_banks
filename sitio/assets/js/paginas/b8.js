/* B8 · Ficha por banco. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec macro) y
   armar() de las tarjetas con dato (encargo 73, ola 3).
   Reglas: aquí solo se filtra, ordena y elige columnas. Lo que necesita un cálculo que no está en las
   tablas queda «en preparación» con su motivo (esqueleto §0.9; spec web §3.3).
   Fuentes: data/ (bk_banco, bk_manifiesto, bk_metrica, bk_cartera_grupo, bk_puente) y la partición
   data/banco/<slug>/ (bk_panel, bk_cartera, bk_roe_arbol) del banco activo.
   Estado de las tarjetas: ver el resultado 73 (docs/orquestacion/73_resultado_ficha_datos_2026-11-03.md). */
/* Sin imports: contar_tarjetas.mjs lee este archivo como texto, igual que los demás configs. Los formatos
   son los de formato.js (es-CL, signo U+2212) y RUTA_DATOS es el de config.js; si cambian allí, cambian aquí. */
const RUTA_DATOS = '/data/';
const ESPACIO = '\u00A0';
const MENOS = '\u2212';
const nfES = (d) => new Intl.NumberFormat('es-CL', { minimumFractionDigits: d, maximumFractionDigits: d });

function numero(v, d = 1) {
  if (v == null || Number.isNaN(v)) return '—';
  return nfES(d).format(v).replace('-', MENOS);
}

function pct(v, d = 1, conSigno = false) {
  if (v == null || Number.isNaN(v)) return '—';
  const x = v * 100;
  const s = nfES(d).format(Math.abs(x));
  const signo = conSigno ? (x > 0 ? '+' : x < 0 ? MENOS : '') : (x < 0 ? MENOS : '');
  return `${signo}${s}${ESPACIO}%`;
}

function pp(v, d = 1, conSigno = true) {
  if (v == null || Number.isNaN(v)) return '—';
  const s = nfES(d).format(Math.abs(v));
  const signo = conSigno ? (v > 0 ? '+' : v < 0 ? MENOS : '') : (v < 0 ? MENOS : '');
  return `${signo}${s}${ESPACIO}pp`;
}

const token = (nombre) => getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();

const IFDATA = 'BCB, IF.Data (conglomerado prudencial)';
const SGS = 'BCB, SGS';
const CVM = 'CVM';
const OLINDA = 'BCB, Olinda';
const CALC = 'cálculo propio';

/* ---------- utilidades de datos (solo lectura y filtro) ---------- */

const cacheBanco = new Map();

/* Partición del banco activo: data/banco/<slug>/<tabla>.json → array de objetos. */
function tablaBanco(slug, tabla) {
  const clave = `${slug}/${tabla}`;
  if (!cacheBanco.has(clave)) {
    cacheBanco.set(clave, fetch(`${RUTA_DATOS}banco/${slug}/${tabla}.json`)
      .then((r) => { if (!r.ok) throw new Error(`${clave}: HTTP ${r.status}`); return r.json(); })
      .then((j) => j.filas.map((f) => Object.fromEntries(j.columnas.map((c, i) => [c, f[i]]))))
      .catch((e) => { cacheBanco.delete(clave); throw e; }));
  }
  return cacheBanco.get(clave);
}

/* «202606» → «2T26». */
const trimTexto = (p) => `${Math.ceil(Number(p.slice(4)) / 3)}T${p.slice(2, 4)}`;

/* «202606» → «2026-06-30» (fecha de fin del trimestre, para el eje del tiempo). */
function fechaDe(p) {
  const fin = { 3: '03-31', 6: '06-30', 9: '09-30', 12: '12-31' }[Number(p.slice(4))];
  return `${p.slice(0, 4)}-${fin}`;
}

/* Último corte del universo Panel, de bk_manifiesto: «2026-06-30» → «202606». */
function ultimoPanel(d) {
  const m = (d.bk_manifiesto || []).find((x) => x.universo === 'Panel' && x.ultimo_corte);
  if (!m) return null;
  const [y, mes] = String(m.ultimo_corte).slice(0, 7).split('-');
  return `${y}${mes}`;
}

/* Trimestre de la página: el de la URL si es válido; si no, el último del Panel. */
function periodoDe(d, estado) {
  if (estado.trimestre && /^\d{6}$/.test(estado.trimestre)) return estado.trimestre;
  return ultimoPanel(d);
}

/* Hasta n trimestres que terminan en t (orden cronológico). */
function ventana(filas, t, n = 12) {
  return [...new Set(filas.map((f) => f.periodo))].filter((p) => p <= t).sort().slice(-n);
}

/* Serie [fecha, valor] de una métrica; excluir(p) deja el punto vacío (quiebre, §0.7 del esqueleto). */
function serie(filas, metrica, campo, ps, excluir = () => false) {
  const porP = new Map(filas.filter((f) => f.metrica === metrica).map((f) => [f.periodo, f]));
  return ps.map((p) => {
    const f = porP.get(p);
    const v = f && !excluir(p) && f[campo] != null ? f[campo] : null;
    return [fechaDe(p), v];
  });
}

/* Una serie con huecos se dibuja como tramos separados: nunca se une un hueco por encima (spec web §5). */
function tramos(nombre, puntos, extra = {}) {
  const salida = [];
  let cur = [];
  for (const p of puntos) {
    if (p[1] == null) { if (cur.length) salida.push(cur); cur = []; } else cur.push(p);
  }
  if (cur.length) salida.push(cur);
  return salida.map((t) => ({ nombre, puntos: t, ...extra }));
}

/* Cambio de cobertura en 2025: la variación a/a de 2025-T1 a 2025-T4 cruza el quiebre (esqueleto §0.7). */
const cruza2025 = (p) => p >= '202501' && p <= '202504';
const BANDA_2025 = [{ desde: '2025-01-01', hasta: '2025-03-31', nombre: 'COSIF 2025 · Res. 4.966' }];
const NOTA_QUIEBRE = 'Cambio de cobertura en 2025 (COSIF 2025 y Res. 4.966): la variación a/a de 2025-T1 a 2025-T4 no se muestra para este banco.';

/* Contexto común: banco activo, trimestre y (si la tarjeta lo necesita) grupo igual al modelo del banco. */
async function contexto(d, estado, { conGrupo = false } = {}) {
  if (!estado.banco) return { motivo: 'elija un banco en la barra superior' };
  const banco = (d.bk_banco || []).find((b) => b.slug === estado.banco);
  if (!banco) return { motivo: `el banco «${estado.banco}» no está en bk_banco` };
  const t = periodoDe(d, estado);
  if (!t) return { motivo: 'sin último corte del Panel en bk_manifiesto' };
  if (conGrupo && estado.grupo !== banco.modelo) {
    return { motivo: `las tablas traen la mediana solo del grupo del banco (${banco.modelo}); el grupo elegido no está exportado` };
  }
  return { banco, t };
}

const sinDato = (t) => ({ enPreparacion: `sin dato del banco en ${trimTexto(t)}` });

/* ---------- formatos de las tablas (formato, no cálculo) ---------- */

const FORMATO_METRICA = { pct1: 'pct', x1: 'num', brl_mm: 'num' };

function valorTabla(v, formato) {
  if (v == null) return '—';
  if (formato === 'brl_mm') return numero(v / 1e9, 1);   // R$ → R$ mil millones
  if (formato === 'pct1') return pct(v, 1);
  if (formato === 'x1') return `${numero(v, 1)} veces`;
  return numero(v, 2);
}

function deltaTabla(v, unidad) {
  if (v == null) return '—';
  if (unidad === 'pp') return pp(v, 1, true);
  if (unidad === 'fraccion') return pct(v, 1, true);
  return numero(v, 1);
}

const COL_DATOS = [
  { clave: 'campo', titulo: 'Dato', tipo: 'texto' },
  { clave: 'valor', titulo: 'Valor', tipo: 'texto' },
];

/* ---------- B8-01-0 · ficha técnica ---------- */
async function armarFicha(d, estado) {
  const c = await contexto(d, estado);
  if (c.motivo) return { enPreparacion: c.motivo };
  const b = c.banco;
  const corte = ultimoPanel(d);
  const filas = [
    { campo: 'Nombre', valor: b.nombre_corto },
    { campo: 'Institución en el BCB', valor: b.institucion_bcb },
    { campo: 'Código del conglomerado', valor: b.cod_inst },
    { campo: 'Modelo de negocio', valor: b.modelo },
    { campo: 'Segmento regulatorio', valor: b.segmento_reg },
    { campo: 'Propiedad', valor: b.propiedad },
    { campo: 'Tradicional o fintech', valor: b.fintech },
    { campo: 'Ticker', valor: b.cotizado ? (b.ticker || '—') : 'no cotiza' },
    { campo: 'Último dato del banco en IF.Data', valor: b.ultimo_periodo ? trimTexto(b.ultimo_periodo) : '—' },
    { campo: 'Último corte del universo Panel', valor: corte ? trimTexto(corte) : '—' },
    { campo: 'Último publicado (CVM)', valor: 'en preparación' },
  ];
  if (b.nota) filas.push({ campo: 'Nota', valor: b.nota });
  return { columnas: COL_DATOS, filas };
}

/* ---------- B8-01-1 · tamaño y cuotas ---------- */
const METRICAS_TAMANO = ['ativo_total', 'credito_total', 'depositos', 'patrimonio_liquido', 'share_ativo', 'share_credito', 'share_depositos'];

async function armarTamano(d, estado) {
  const c = await contexto(d, estado);
  if (c.motivo) return { enPreparacion: c.motivo };
  const panel = await tablaBanco(c.banco.slug, 'bk_panel');
  if (!panel.some((f) => f.periodo === c.t)) return sinDato(c.t);
  const meta = new Map((d.bk_metrica || []).map((m) => [m.metrica, m]));
  const filas = METRICAS_TAMANO.map((m) => {
    const f = panel.find((x) => x.metrica === m && x.periodo === c.t) || {};
    const mm = meta.get(m) || {};
    return { concepto: mm.nombre || m, formato: mm.formato, valor: f.valor ?? null, delta: f.d_aa ?? null, unidad: f.unidad_d ?? null };
  });
  return {
    columnas: [
      { clave: 'concepto', titulo: 'Concepto', tipo: 'texto' },
      { clave: 'valor', titulo: `Nivel (R$ mil mm o %, ${trimTexto(c.t)})`, formatear: (v, f) => valorTabla(v, f.formato) },
      { clave: 'delta', titulo: 'Δ a/a', formatear: (v, f) => deltaTabla(v, f.unidad) },
    ],
    filas,
  };
}

/* ---------- B8-02-0 · doce métricas (percentiles) ---------- */
async function armarPercentiles(d, estado) {
  const c = await contexto(d, estado, { conGrupo: true });
  if (c.motivo) return { enPreparacion: c.motivo };
  const panel = await tablaBanco(c.banco.slug, 'bk_panel');
  const filas = panel.filter((f) => f.periodo === c.t);
  if (!filas.length) return sinDato(c.t);
  const porM = new Map(filas.map((f) => [f.metrica, f]));
  const lista = (d.bk_metrica || [])
    .filter((m) => m.en_ficha === true)
    .sort((a, b) => a.orden - b.orden)
    .map((m) => {
      const f = porM.get(m.metrica) || {};
      return {
        nombre: m.nombre,
        signo: m.signo,
        formato: FORMATO_METRICA[m.formato] || 'num',
        valor: f.valor ?? null,
        valor_t4: f.valor_t4 ?? null,
        p10: f.p10_grupo ?? null,
        p50: f.p50_grupo ?? null,
        p90: f.p90_grupo ?? null,
      };
    });
  return { filas: lista };
}

/* ---------- B8-03-0 · mezcla de cartera por modalidad: banco vs. grupo vs. panel ---------- */
/* Colores de los segmentos: la paleta del sitio, en orden; cada modalidad conserva su color en las tres barras. */
const COLORES_SEG = () => [token('--navy'), token('--petroleo'), token('--acero'), token('--ciruela'), token('--acero-claro')];

async function armarMezcla(d, estado) {
  const c = await contexto(d, estado, { conGrupo: true });
  if (c.motivo) return { enPreparacion: c.motivo };
  const cart = await tablaBanco(c.banco.slug, 'bk_cartera');
  const filas = cart.filter((f) => f.periodo === c.t);
  if (!filas.length) return sinDato(c.t);
  const grupo = (d.bk_cartera_grupo || []).filter((g) => g.periodo === c.t && g.optica === 'Modelo de negocio' && g.grupo === c.banco.modelo);
  const total = (d.bk_cartera_grupo || []).filter((g) => g.periodo === c.t && g.optica === 'Total panel');
  const pg = new Map(grupo.map((g) => [g.modalidad_id, g.peso]));
  const pt = new Map(total.map((g) => [g.modalidad_id, g.peso]));
  const colores = COLORES_SEG();
  const partes = (valorDe) => filas.map((f, i) => ({ nombre: f.modalidad, valor: valorDe(f), color: colores[i % colores.length] }));
  return {
    barras: [
      { nombre: c.banco.nombre_corto, partes: partes((f) => f.peso_banco) },
      { nombre: `Grupo ${c.banco.modelo}`, partes: partes((f) => pg.get(f.modalidad_id)) },
      { nombre: 'Panel', partes: partes((f) => pt.get(f.modalidad_id)) },
    ],
    formato: 'pct',
    formatoRotulo: 'pct0',
  };
}

/* ---------- B8-03-1 · NPL por modalidad ---------- */
const CALIDAD = { exacta: 'exacta', proxy: 'proxy (serie más amplia)', sin_dato: 'sin dato' };

async function armarNpl(d, estado) {
  const c = await contexto(d, estado, { conGrupo: true });
  if (c.motivo) return { enPreparacion: c.motivo };
  const cart = await tablaBanco(c.banco.slug, 'bk_cartera');
  const filas = cart.filter((f) => f.periodo === c.t);
  if (!filas.length) return sinDato(c.t);
  const grupo = (d.bk_cartera_grupo || []).filter((g) => g.periodo === c.t && g.optica === 'Modelo de negocio' && g.grupo === c.banco.modelo);
  const total = (d.bk_cartera_grupo || []).filter((g) => g.periodo === c.t && g.optica === 'Total panel');
  const pg = new Map(grupo.map((g) => [g.modalidad_id, g]));
  const pt = new Map(total.map((g) => [g.modalidad_id, g]));
  const lista = filas
    .map((f) => {
      const g = pg.get(f.modalidad_id) || {};
      const s = pt.get(f.modalidad_id) || {};
      return {
        modalidad: f.modalidad,
        peso: f.peso_banco ?? null,
        npl_banco: f.npl15 ?? null,
        npl_grupo: g.npl15 ?? null,
        mora_sistema: s.mora_sistema ?? null,
        calidad: CALIDAD[s.calidad_equivalencia] || '—',
      };
    })
    .sort((a, b) => (b.peso ?? -1) - (a.peso ?? -1));
  const pctCol = (v) => (v == null ? '—' : pct(v, 1));
  return {
    columnas: [
      { clave: 'modalidad', titulo: 'Modalidad', tipo: 'texto' },
      { clave: 'peso', titulo: 'Peso en la cartera', formatear: pctCol },
      { clave: 'npl_banco', titulo: 'NPL del banco', formatear: pctCol },
      { clave: 'npl_grupo', titulo: 'NPL del grupo', formatear: pctCol },
      { clave: 'mora_sistema', titulo: 'Mora del sistema (> 90 d)', formatear: pctCol },
      { clave: 'calidad', titulo: 'Equivalencia', tipo: 'texto' },
    ],
    filas: lista,
  };
}

/* ---------- B8-03-2 · crecimiento de cartera a/a, 12 trimestres ---------- */
async function armarCredito(d, estado) {
  const c = await contexto(d, estado, { conGrupo: true });
  if (c.motivo) return { enPreparacion: c.motivo };
  const panel = await tablaBanco(c.banco.slug, 'bk_panel');
  const cart = await tablaBanco(c.banco.slug, 'bk_cartera');
  const ps = ventana(panel, c.t);
  if (!ps.length) return sinDato(c.t);
  const quiebre = cart.some((f) => f.quiebre_2025 === true);
  const excluir = quiebre ? cruza2025 : undefined;
  return {
    series: [
      ...tramos('Crecimiento a/a del banco', serie(panel, 'credito_aa', 'valor', ps, excluir), { color: token('--navy') }),
      ...tramos('Crecimiento a/a, mediana del grupo', serie(panel, 'credito_aa', 'p50_grupo', ps, excluir), { discontinua: true, color: token('--texto-2') }),
      ...tramos('NPL del banco', serie(panel, 'npl15_total', 'valor', ps), { color: token('--cobre') }),
      ...tramos('NPL, mediana del grupo', serie(panel, 'npl15_total', 'p50_grupo', ps), { discontinua: true, color: token('--cobre') }),
    ],
    bandas: BANDA_2025,
    nota: quiebre ? NOTA_QUIEBRE : null,
  };
}

/* ---------- B8-04-0 · árbol del ROE ---------- */
const LINEAS_ARBOL = [
  ['margen_antes_provisiones', 'Margen antes de provisiones'],
  ['provisiones', 'Provisiones'],
  ['tarifas_servicios', 'Tarifas y servicios'],
  ['transacciones_pago', 'Transacciones de pago'],
  ['personal', 'Personal'],
  ['administrativos', 'Administrativos'],
  ['tributarios', 'Tributarios'],
  ['no_operacional', 'No operacional'],
  ['otros', 'Otros'],
  ['impuesto_participaciones', 'Impuesto y participaciones'],
];

async function armarArbol(d, estado) {
  const c = await contexto(d, estado, { conGrupo: true });
  if (c.motivo) return { enPreparacion: c.motivo };
  const arbol = await tablaBanco(c.banco.slug, 'bk_roe_arbol');
  const porL = new Map(arbol.filter((r) => r.periodo === c.t).map((r) => [r.linea, r]));
  const roa = porL.get('roa');
  const roe = porL.get('roe');
  const apal = porL.get('apalancamiento');
  if (!roa || roa.valor == null) return sinDato(c.t);
  const lineas = [];
  const omitidas = [];
  for (const [clave, nombre] of LINEAS_ARBOL) {
    const r = porL.get(clave);
    if (!r || r.valor == null || r.mediana_grupo == null) { omitidas.push(nombre); continue; }
    lineas.push({ nombre, banco: r.valor, grupo: r.mediana_grupo });
  }
  const partes = [];
  if (roe && roe.valor != null && apal && apal.valor != null) {
    partes.push(`ROE ${pct(roe.valor, 1)} = ROA ${pct(roa.valor, 1)} × apalancamiento ${numero(apal.valor, 1)} veces.`);
  }
  if (roe && roe.mediana_grupo != null) {
    partes.push(`Mediana del grupo: ROE ${pct(roe.mediana_grupo, 1)}, ROA ${pct(roa.mediana_grupo, 1)}. La mediana de cada línea no suma a la del ROA.`);
  }
  if (omitidas.length) partes.push(`Sin dato en ${trimTexto(c.t)} y fuera de la cascada: ${omitidas.join(', ').toLowerCase()}.`);
  return {
    lineas,
    total: { nombre: 'ROA', banco: roa.valor, grupo: roa.mediana_grupo },
    nota: partes.join(' '),
  };
}

/* ---------- B8-04-1 · ROE TTM, 12 trimestres ---------- */
async function armarRoe(d, estado) {
  const c = await contexto(d, estado, { conGrupo: true });
  if (c.motivo) return { enPreparacion: c.motivo };
  const panel = await tablaBanco(c.banco.slug, 'bk_panel');
  const ps = ventana(panel, c.t);
  if (!ps.length) return sinDato(c.t);
  return {
    series: [
      ...tramos('Banco', serie(panel, 'roe_ttm', 'valor', ps)),
      ...tramos('Mediana del grupo', serie(panel, 'roe_ttm', 'p50_grupo', ps), { discontinua: true, color: token('--texto-2') }),
    ],
    bandas: BANDA_2025,
    nota: null,
  };
}

/* ---------- B8-05-0 · mix de fondeo, banco vs. mediana del grupo ---------- */
async function armarFondeo(d, estado) {
  const c = await contexto(d, estado, { conGrupo: true });
  if (c.motivo) return { enPreparacion: c.motivo };
  const panel = await tablaBanco(c.banco.slug, 'bk_panel');
  const porM = new Map(panel.filter((f) => f.periodo === c.t && f.metrica.startsWith('fondeo_')).map((f) => [f.metrica, f]));
  const meta = (d.bk_metrica || []).filter((m) => porM.has(m.metrica)).sort((a, b) => a.orden - b.orden);
  if (!meta.length) return sinDato(c.t);
  const colores = COLORES_SEG();
  const partes = (valorDe) => meta.map((m, i) => ({ nombre: m.nombre.replace(/^Fondeo:\s*/, ''), valor: valorDe(porM.get(m.metrica)), color: colores[i % colores.length] }));
  return {
    barras: [
      { nombre: c.banco.nombre_corto, partes: partes((f) => f.valor) },
      { nombre: `Mediana del grupo ${c.banco.modelo}`, partes: partes((f) => f.p50_grupo) },
    ],
    formato: 'pct',
    formatoRotulo: 'pct0',
  };
}

/* ---------- B8-06-1 · puente IF.Data ↔ publicado ---------- */
const COL_PUENTE = [
  { clave: 'linea', titulo: 'Línea', tipo: 'texto' },
  { clave: 'publicado', titulo: 'Publicado (R$ mil mm)', formatear: (v) => (v == null ? '—' : numero(v, 1)) },
  { clave: 'ifdata', titulo: 'IF.Data (R$ mil mm)', formatear: (v) => (v == null ? '—' : numero(v, 1)) },
  { clave: 'dif', titulo: 'Diferencia', formatear: (v) => (v == null ? '—' : pct(v, 1, true)) },
  { clave: 'nota', titulo: 'Nota', tipo: 'texto' },
];

async function armarPuente(d, estado) {
  const c = await contexto(d, estado);
  if (c.motivo) return { enPreparacion: c.motivo };
  const pu = (d.bk_puente || []).filter((p) => p.cod_inst === c.banco.cod_inst);
  if (!pu.length) {
    return { columnas: [{ clave: 'linea', titulo: 'Puente', tipo: 'texto' }], filas: [{ linea: 'sin auditoría para este banco' }] };
  }
  return {
    columnas: COL_PUENTE,
    filas: pu.map((p) => ({ linea: p.linea, publicado: p.gaap, ifdata: p.ifdata, dif: p.dif_pct, nota: p.nota })),
  };
}

/* ---------- riel: un KPI por sección (cifra del banco activo; cambios de 1 y 4 trimestres vienen de bk_panel) ---------- */
const kpiBanco = (rotulo, metrica, signo) => ({
  tipo: 'kpi',
  rotulo,
  datos: ['bk_banco', 'bk_manifiesto'],
  armar: async (d, estado) => {
    const c = await contexto(d, estado);
    if (c.motivo) return { enPreparacion: c.motivo };
    const panel = await tablaBanco(c.banco.slug, 'bk_panel');
    const f = panel.find((x) => x.metrica === metrica && x.periodo === c.t);
    if (!f || f.valor == null) return sinDato(c.t);
    return {
      cifra: f.valor,
      formato: 'pct',
      cambio1: f.d_tt ?? null,
      cambio4: f.d_aa ?? null,
      signo,
      nota: f.p50_grupo != null ? `Mediana del grupo ${pct(f.p50_grupo, 1)}` : null,
    };
  },
});

const DATOS_BASE = ['bk_banco', 'bk_manifiesto'];

export default {
  clave: 'B8',
  ruta: 'ficha',
  nombre: 'Ficha por banco',
  rotulo: '8 · FICHA',
  signo: 'bancos',
  usaBanco: true,
  optica: 'Modelo de negocio',

  // v3 (3-nov): estructura del canvas; la versión anterior queda en el .v1.txt de este archivo.
  franja: [
    { rotulo: 'ROE 12 meses', tabla: 'metrica/roe_ttm/bk_panel', filtro: { metrica: 'roe_ttm' }, banco: true, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_sube' },
    { rotulo: 'NPL ≥ 15 días', tabla: 'metrica/npl15_total/bk_panel', filtro: { metrica: 'npl15_total' }, banco: true, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_baja' },
    { rotulo: 'Cuota de crédito', tabla: 'metrica/share_credito/bk_panel', filtro: { metrica: 'share_credito' }, banco: true, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'neutro' },
    { rotulo: 'Costo del riesgo', tabla: 'metrica/costo_riesgo_ttm/bk_panel', filtro: { metrica: 'costo_riesgo_ttm' }, banco: true, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_baja' },
    { rotulo: 'Eficiencia', tabla: 'metrica/eficiencia_ttm/bk_panel', filtro: { metrica: 'eficiencia_ttm' }, banco: true, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_baja' },
  ],

  secciones: [
    {
      numero: '01',
      nombre: 'Contra su grupo',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Doce métricas del banco contra el rango de su grupo.',
      filas: [
        [{ clave: 'B8-02-0', ancho: 9, alto: 540 }],
      ],
    },
    {
      numero: '02',
      nombre: 'Tamaño y cartera',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Balance y mix de cartera contra grupo y panel.',
      filas: [
        [{ clave: 'B8-01-1', ancho: 4, alto: 340 }, { clave: 'B8-03-0', ancho: 5, alto: 340 }],
      ],
    },
    {
      numero: '03',
      nombre: 'Rentabilidad',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Árbol del ROA y ROE contra grupo y CDI.',
      filas: [
        [{ clave: 'B8-04-0', ancho: 5, alto: 460 }, { clave: 'B8-04-1', ancho: 4, alto: 460 }],
      ],
    },
    {
      numero: '04',
      nombre: 'Fondeo',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Mix de fondeo contra el grupo.',
      filas: [
        [{ clave: 'B8-05-0', ancho: 9, alto: 260 }],
      ],
    },
    {
      numero: '05',
      nombre: 'Identidad y puente',
      frecuencia: 'Trimestral · IF.Data y publicado',
      pregunta: 'Ficha técnica y diferencias contra lo publicado.',
      filas: [
        [{ clave: 'B8-01-0', ancho: 4, alto: 400 }, { clave: 'B8-06-1', ancho: 5, alto: 400 }],
      ],
    },
  ],


  tarjetas: {
    'B8-01-0': {
      plana: true, // v3
      titulo: 'Ficha técnica',
      sub: 'Panel IF.Data y Publicado CVM · último corte de cada universo',
      fuente: `${IFDATA}; ${CVM}`,
      componente: 'tabla',
      datos: DATOS_BASE,
      banco: true,
      estado: 'LISTO',
      armar: armarFicha,
    },
    'B8-01-1': {
      plana: true, // v3
      titulo: 'Tamaño y cuotas',
      sub: 'Panel IF.Data · activo, crédito, depósitos y PL · cuota y Δ cuota en 4 trimestres',
      fuente: IFDATA,
      componente: 'tabla',
      datos: [...DATOS_BASE, 'bk_metrica'],
      banco: true,
      estado: 'LISTO',
      armar: armarTamano,
    },
    'B8-02-0': {
      plana: true, // v3
      titulo: 'Doce métricas, una fila cada una',
      sub: 'Panel IF.Data · rango p10–p90 del grupo, mediana, banco y hace un año · doce métricas',
      fuente: `${IFDATA}; ${CALC}`,
      nota: 'Grupo de comparación: el modelo del banco. Doce métricas; Basilea queda fuera hasta que exista bk_capital.',
      componente: 'percentiles',
      datos: [...DATOS_BASE, 'bk_metrica'],
      banco: true,
      estado: 'DERIVAR',
      armar: armarPercentiles,
    },
    'B8-03-0': {
      plana: true, // v3
      titulo: 'Mix de cartera: banco vs. grupo vs. panel',
      sub: 'Panel IF.Data · banco vs. grupo vs. panel · apilado al 100 %',
      fuente: IFDATA,
      componente: 'apilada_100',
      nota: 'Un segmento por modalidad de cartera; el grupo y el panel usan las mismas modalidades. Rótulo solo si el segmento pesa 8 % o más.',
      datos: [...DATOS_BASE, 'bk_cartera_grupo'],
      banco: true,
      estado: 'DERIVAR',
      armar: armarMezcla,
    },
    'B8-04-0': {
      plana: true, // v3
      titulo: 'Árbol del ROE: banco vs. mediana del grupo',
      sub: 'Panel IF.Data · banco vs. mediana del grupo',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'cascada_doble',
      datos: DATOS_BASE,
      banco: true,
      estado: 'DERIVAR',
      armar: armarArbol,
    },
    'B8-04-1': {
      plana: true, // v3
      titulo: 'ROE TTM, 12 trimestres, banco vs. grupo y vs. CDI',
      sub: 'Panel IF.Data · 12 trimestres · banco vs. mediana del grupo',
      fuente: `${IFDATA}; ${SGS}`,
      nota: 'Sin línea del CDI: la serie no está exportada.',
      componente: 'linea_banco',
      datos: DATOS_BASE,
      banco: true,
      estado: 'LISTO',
      armar: armarRoe,
    },
    'B8-05-0': {
      plana: true, // v3
      titulo: 'Mix de fondeo, banco vs. grupo',
      sub: 'Panel IF.Data · banco vs. grupo · apilado al 100 %',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'apilada_100',
      nota: 'La mediana de cada línea del grupo no suma 100 %: la barra del grupo se escala a su suma.',
      datos: [...DATOS_BASE, 'bk_metrica'],
      banco: true,
      estado: 'DERIVAR',
      armar: armarFondeo,
    },
    'B8-06-1': {
      plana: true, // v3
      titulo: 'Puente IF.Data ↔ publicado',
      sub: 'Panel IF.Data y Publicado CVM · diferencia por línea · último trimestre auditado',
      fuente: `${IFDATA}; ${CVM}; ${CALC}`,
      componente: 'tabla',
      datos: [...DATOS_BASE, 'bk_puente'],
      banco: true,
      estado: 'LISTO',
      armar: armarPuente,
    },
  },
};
