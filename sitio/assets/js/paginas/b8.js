/* B8 · Ficha por banco. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec macro).
   Reglas: aquí solo se filtra, ordena y elige columnas. Lo que necesita un cálculo que no está en las
   tablas queda «en preparación» con su motivo (esqueleto §0.9; spec web §3.3).
   Fuentes: data/ (bk_manifiesto, bk_metrica, bk_cartera_grupo, bk_puente) y la partición
   data/banco/<slug>/ (bk_panel, bk_cartera, bk_roe_arbol) del banco activo, que cada tarjeta pide en
   `datos` según el banco del contexto. */
import { FUENTE, BANDA_2025, ROTULO_PANEL, OPTICA_MODELO, OPTICA_PANEL, tablaBanco, indicadorBanco, lineasArbolRoe, periodoActivo, enPreparacion, requiereBanco } from '../comun.js';
import { COLOR, PALETA } from '../tokens.js';
import { formatear, pct, trimestreDePeriodo, finDeTrimestre, periodosHasta } from '../formato.js';

const { IFDATA, SGS, CVM, CALC } = FUENTE;

/* Las tablas de la tarjeta más las particiones del banco activo (sin banco, solo las primeras). */
const conBanco = (tablas, particiones) => (ctx) => [...tablas, ...(ctx.banco ? particiones.map((t) => tablaBanco(ctx.banco, t)) : [])];
const delBanco = (d, ctx, tabla) => d[tablaBanco(ctx.banco, tabla)];

/* Serie [fecha, valor] de una métrica en los períodos dados; null donde falta (hueco en la línea). */
function serie(filas, metrica, campo, periodos) {
  const porP = new Map(filas.filter((f) => f.metrica === metrica).map((f) => [f.periodo, f]));
  return periodos.map((p) => [finDeTrimestre(p), porP.get(p)?.[campo] ?? null]);
}

/* Banco activo con su fila de bk_banco, período y (si la tarjeta lo necesita) grupo igual al modelo del
   banco. Sin alguno de ellos devuelve el resultado «sin dibujo», que armar() devuelve tal cual. */
function contexto(estado, { conGrupo = false } = {}) {
  if (!estado.banco) return requiereBanco('elija un banco en la barra superior');
  const banco = estado.bancoActivo;
  if (!banco?.cod_inst) return enPreparacion(`el banco «${estado.banco}» no está en bk_banco`);
  const t = estado.periodoActivo;
  if (!t) return enPreparacion('sin último corte del Panel en bk_manifiesto');
  if (conGrupo && estado.grupo !== banco.modelo) {
    return enPreparacion(`las tablas traen la mediana solo del grupo del banco (${banco.modelo}); el grupo elegido no está exportado`);
  }
  return { banco, t };
}

const sinDato = (t) => enPreparacion(`sin dato del banco en ${trimestreDePeriodo(t)}`);

/* Formato de bk_metrica → unidad del sitio (formato.js). Su «brl_mm» trae reales: se pasa a mil millones. */
const UNIDAD_METRICA = { pct1: 'pct', x1: 'num', brl_mm: 'reales_a_mm' };
const unidadMetrica = (formato) => UNIDAD_METRICA[formato] || 'num';
/* Unidad del cambio en bk_panel (unidad_d) → unidad del sitio. */
const UNIDAD_CAMBIO = { pp: 'pp', fraccion: 'pct' };

const COL_DATOS = [
  { clave: 'campo', titulo: 'Dato', tipo: 'texto' },
  { clave: 'valor', titulo: 'Valor', tipo: 'texto' },
];

/* B8-01-0 · ficha técnica */
function armarFicha(d, estado) {
  const c = contexto(estado);
  if (c.estado) return c;
  const b = c.banco;
  const corte = periodoActivo(null, d.bk_manifiesto);
  const filas = [
    { campo: 'Nombre', valor: b.nombre_corto },
    { campo: 'Institución en el BCB', valor: b.institucion_bcb },
    { campo: 'Código del conglomerado', valor: b.cod_inst },
    { campo: 'Modelo de negocio', valor: b.modelo },
    { campo: 'Segmento regulatorio', valor: b.segmento_reg },
    { campo: 'Propiedad', valor: b.propiedad },
    { campo: 'Tradicional o fintech', valor: b.fintech },
    { campo: 'Ticker', valor: b.cotizado ? (b.ticker || '—') : 'no cotiza' },
    { campo: 'Último dato del banco en IF.Data', valor: b.ultimo_periodo ? trimestreDePeriodo(b.ultimo_periodo) : '—' },
    { campo: 'Último corte del universo Panel', valor: corte ? trimestreDePeriodo(corte) : '—' },
    { campo: 'Último publicado (CVM)', valor: 'en preparación' },
  ];
  if (b.nota) filas.push({ campo: 'Nota', valor: b.nota });
  return { columnas: COL_DATOS, filas };
}

/* B8-01-1 · tamaño y cuotas */
const METRICAS_TAMANO = ['ativo_total', 'credito_total', 'depositos', 'patrimonio_liquido', 'share_ativo', 'share_credito', 'share_depositos'];

function armarTamano(d, estado) {
  const c = contexto(estado);
  if (c.estado) return c;
  const panel = delBanco(d, estado, 'bk_panel');
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
      { clave: 'valor', titulo: `Nivel (R$ mil mm o %, ${trimestreDePeriodo(c.t)})`, formatear: (v, f) => formatear(v, unidadMetrica(f.formato)) },
      { clave: 'delta', titulo: 'Δ a/a', formatear: (v, f) => formatear(v, UNIDAD_CAMBIO[f.unidad] || 'num', { signo: true }) },
    ],
    filas,
  };
}

/* B8-02-0 · doce métricas (percentiles) */
function armarPercentiles(d, estado) {
  const c = contexto(estado, { conGrupo: true });
  if (c.estado) return c;
  const filas = delBanco(d, estado, 'bk_panel').filter((f) => f.periodo === c.t);
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
        formato: unidadMetrica(m.formato),
        valor: f.valor ?? null,
        valor_t4: f.valor_t4 ?? null,
        p10: f.p10_grupo ?? null,
        p50: f.p50_grupo ?? null,
        p90: f.p90_grupo ?? null,
      };
    });
  return { filas: lista };
}

/* B8-03-0 · mezcla de cartera por modalidad: banco vs. grupo vs. panel; cada modalidad conserva su color
   de la paleta en las tres barras. */
const colorDe = (i) => PALETA[i % PALETA.length];

function armarMezcla(d, estado) {
  const c = contexto(estado, { conGrupo: true });
  if (c.estado) return c;
  const filas = delBanco(d, estado, 'bk_cartera').filter((f) => f.periodo === c.t);
  if (!filas.length) return sinDato(c.t);
  const grupo = (d.bk_cartera_grupo || []).filter((g) => g.periodo === c.t && g.optica === OPTICA_MODELO && g.grupo === c.banco.modelo);
  const total = (d.bk_cartera_grupo || []).filter((g) => g.periodo === c.t && g.optica === OPTICA_PANEL);
  const pg = new Map(grupo.map((g) => [g.modalidad_id, g.peso]));
  const pt = new Map(total.map((g) => [g.modalidad_id, g.peso]));
  const partes = (valorDe) => filas.map((f, i) => ({ nombre: f.modalidad, valor: valorDe(f), color: colorDe(i) }));
  return {
    barras: [
      { nombre: c.banco.nombre_corto, partes: partes((f) => f.peso_banco) },
      { nombre: `Grupo ${c.banco.modelo}`, partes: partes((f) => pg.get(f.modalidad_id)) },
      { nombre: ROTULO_PANEL, partes: partes((f) => pt.get(f.modalidad_id)) },
    ],
    formato: 'pct',
  };
}

/* B8-04-0 · árbol del ROE */
function armarArbol(d, estado) {
  const c = contexto(estado, { conGrupo: true });
  if (c.estado) return c;
  const filas = delBanco(d, estado, 'bk_roe_arbol').filter((r) => r.periodo === c.t);
  const porL = new Map(filas.map((r) => [r.linea, r]));
  const roa = porL.get('roa');
  const roe = porL.get('roe');
  const apal = porL.get('apalancamiento');
  if (!roa || roa.valor == null) return sinDato(c.t);
  const { lineas, omitidas } = lineasArbolRoe(filas);
  const partes = [];
  if (roe && roe.valor != null && apal && apal.valor != null) {
    partes.push(`ROE ${pct(roe.valor, 1)} = ROA ${pct(roa.valor, 1)} × apalancamiento ${formatear(apal.valor, 'num')} veces.`);
  }
  if (roe && roe.mediana_grupo != null) {
    partes.push(`Mediana del grupo: ROE ${pct(roe.mediana_grupo, 1)}, ROA ${pct(roa.mediana_grupo, 1)}. La mediana de cada línea no suma a la del ROA.`);
  }
  if (omitidas.length) partes.push(`Sin dato en ${trimestreDePeriodo(c.t)} y fuera de la cascada: ${omitidas.join(', ').toLowerCase()}.`);
  return {
    lineas,
    total: { nombre: 'ROA', banco: roa.valor, grupo: roa.mediana_grupo },
    nota: partes.join(' '),
  };
}

/* B8-04-1 · ROE TTM, 12 trimestres; un hueco en la serie queda como hueco en la línea. */
function armarRoe(d, estado) {
  const c = contexto(estado, { conGrupo: true });
  if (c.estado) return c;
  const panel = delBanco(d, estado, 'bk_panel');
  const ps = periodosHasta(panel, c.t, 12);
  if (!ps.length) return sinDato(c.t);
  return {
    series: [
      { nombre: 'Banco', puntos: serie(panel, 'roe_ttm', 'valor', ps) },
      { nombre: 'Mediana del grupo', puntos: serie(panel, 'roe_ttm', 'p50_grupo', ps), discontinua: true, color: COLOR.texto2 },
    ],
    bandas: BANDA_2025,
    eje: { unidad: 'pct', decimales: 0 },
    formatoTooltip: 'pct',
  };
}

/* B8-05-0 · mix de fondeo, banco vs. mediana del grupo */
function armarFondeo(d, estado) {
  const c = contexto(estado, { conGrupo: true });
  if (c.estado) return c;
  const porM = new Map(delBanco(d, estado, 'bk_panel').filter((f) => f.periodo === c.t && f.metrica.startsWith('fondeo_')).map((f) => [f.metrica, f]));
  const meta = (d.bk_metrica || []).filter((m) => porM.has(m.metrica)).sort((a, b) => a.orden - b.orden);
  if (!meta.length) return sinDato(c.t);
  const partes = (valorDe) => meta.map((m, i) => ({ nombre: m.nombre.replace(/^Fondeo:\s*/, ''), valor: valorDe(porM.get(m.metrica)), color: colorDe(i) }));
  return {
    barras: [
      { nombre: c.banco.nombre_corto, partes: partes((f) => f.valor) },
      { nombre: `Mediana del grupo ${c.banco.modelo}`, partes: partes((f) => f.p50_grupo) },
    ],
    formato: 'pct',
  };
}

/* B8-06-1 · puente IF.Data ↔ publicado */
const COL_PUENTE = [
  { clave: 'linea', titulo: 'Línea', tipo: 'texto' },
  { clave: 'publicado', titulo: 'Publicado (R$ mil mm)', formatear: (v) => formatear(v, 'num') },
  { clave: 'ifdata', titulo: 'IF.Data (R$ mil mm)', formatear: (v) => formatear(v, 'num') },
  { clave: 'dif', titulo: 'Diferencia', formatear: (v) => formatear(v, 'pct', { signo: true }) },
  { clave: 'nota', titulo: 'Nota', tipo: 'texto' },
];

function armarPuente(d, estado) {
  const c = contexto(estado);
  if (c.estado) return c;
  const pu = (d.bk_puente || []).filter((p) => p.cod_inst === c.banco.cod_inst);
  if (!pu.length) {
    return { columnas: [{ clave: 'linea', titulo: 'Puente', tipo: 'texto' }], filas: [{ linea: 'sin auditoría para este banco' }] };
  }
  return {
    columnas: COL_PUENTE,
    filas: pu.map((p) => ({ linea: p.linea, publicado: p.gaap, ifdata: p.ifdata, dif: p.dif_pct, nota: p.nota })),
  };
}

export default {
  rotulo: '8 · FICHA',
  usaBanco: true,
  titularPorBanco: true,

  franja: [
    indicadorBanco('ROE 12 meses', 'roe_ttm'),
    indicadorBanco('NPL ≥ 15 días', 'npl15_total'),
    // bk_metrica le da mejora_sube; la franja lo muestra sin juicio (decisión de diseño previa, a confirmar por Pablo)
    indicadorBanco('Cuota de crédito', 'share_credito', { tono: 'neutro' }),
    indicadorBanco('Costo del riesgo', 'costo_riesgo_ttm'),
    indicadorBanco('Eficiencia', 'eficiencia_ttm'),
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
      plana: true,
      titulo: 'Ficha técnica',
      sub: 'Panel IF.Data y Publicado CVM · último corte de cada universo',
      fuente: `${IFDATA}; ${CVM}`,
      componente: 'tabla',
      datos: ['bk_manifiesto'],
      banco: true,
      estado: 'LISTO',
      armar: armarFicha,
    },
    'B8-01-1': {
      plana: true,
      titulo: 'Tamaño y cuotas',
      sub: 'Panel IF.Data · activo, crédito, depósitos y PL · cuota y Δ cuota en 4 trimestres',
      fuente: IFDATA,
      componente: 'tabla',
      datos: conBanco(['bk_metrica'], ['bk_panel']),
      banco: true,
      estado: 'LISTO',
      armar: armarTamano,
    },
    'B8-02-0': {
      plana: true,
      titulo: 'Doce métricas, una fila cada una',
      sub: 'Panel IF.Data · rango p10–p90 del grupo, mediana, banco y hace un año · doce métricas',
      fuente: `${IFDATA}; ${CALC}`,
      nota: 'Grupo de comparación: el modelo del banco. Doce métricas; Basilea queda fuera hasta que exista bk_capital.',
      componente: 'percentiles',
      datos: conBanco(['bk_metrica'], ['bk_panel']),
      banco: true,
      estado: 'DERIVAR',
      armar: armarPercentiles,
    },
    'B8-03-0': {
      plana: true,
      titulo: 'Mix de cartera: banco vs. grupo vs. panel',
      sub: 'Panel IF.Data · banco vs. grupo vs. panel · apilado al 100 %',
      fuente: IFDATA,
      componente: 'apilada_100',
      nota: 'Un segmento por modalidad de cartera; el grupo y el panel usan las mismas modalidades. Rótulo solo si el segmento pesa 8 % o más.',
      datos: conBanco(['bk_cartera_grupo'], ['bk_cartera']),
      banco: true,
      estado: 'DERIVAR',
      armar: armarMezcla,
    },
    'B8-04-0': {
      plana: true,
      titulo: 'Árbol del ROE: banco vs. mediana del grupo',
      sub: 'Panel IF.Data · banco vs. mediana del grupo',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'cascada_doble',
      datos: conBanco([], ['bk_roe_arbol']),
      banco: true,
      estado: 'DERIVAR',
      armar: armarArbol,
    },
    'B8-04-1': {
      plana: true,
      titulo: 'ROE TTM, 12 trimestres, banco vs. grupo y vs. CDI',
      sub: 'Panel IF.Data · 12 trimestres · banco vs. mediana del grupo',
      fuente: `${IFDATA}; ${SGS}`,
      nota: 'Sin línea del CDI: la serie no está exportada.',
      componente: 'linea',
      datos: conBanco([], ['bk_panel']),
      banco: true,
      estado: 'LISTO',
      armar: armarRoe,
    },
    'B8-05-0': {
      plana: true,
      titulo: 'Mix de fondeo, banco vs. grupo',
      sub: 'Panel IF.Data · banco vs. grupo · apilado al 100 %',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'apilada_100',
      nota: 'La mediana de cada línea del grupo no suma 100 %: la barra del grupo se escala a su suma.',
      datos: conBanco(['bk_metrica'], ['bk_panel']),
      banco: true,
      estado: 'DERIVAR',
      armar: armarFondeo,
    },
    'B8-06-1': {
      plana: true,
      titulo: 'Puente IF.Data ↔ publicado',
      sub: 'Panel IF.Data y Publicado CVM · diferencia por línea · último trimestre auditado',
      fuente: `${IFDATA}; ${CVM}; ${CALC}`,
      componente: 'tabla',
      datos: ['bk_puente'],
      banco: true,
      estado: 'LISTO',
      armar: armarPuente,
    },
  },
};
