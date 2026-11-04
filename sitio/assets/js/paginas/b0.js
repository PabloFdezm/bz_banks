/* B0 · Portada — v3 (3-nov), tablero 05 del canvas «Bancos Brasil — propuesta visual».
   Cuatro bloques; cada uno es una lámina en modo presentación: gráfico a la izquierda y tabla
   descriptiva de estructura fija a la derecha (m/m, 3m/3m, a/a, 12m/12m; en trimestrales t/t, a/a,
   4T/4T). La tabla nunca repite la serie del gráfico. Todo viene calculado de
   preparar_gold_bancos_portada.py (bk_portada_*); aquí solo se filtra, se formatea y se dibuja.
   Versiones anteriores: b0_v1.js.txt, b0_v2.js.txt. Sin imports: contar_tarjetas.mjs lee este archivo. */
const SGS = 'BCB, SGS';
const IFDATA = 'BCB, IF.Data (conglomerado prudencial)';
const MESES = 36;
const AZUL = '#2E5C8A', ACERO = '#8FA3BC', TINTA = '#24324A', COBRE = '#A85E24', ARENA = '#E7CDB6', PETROLEO = '#2F7A86';
const num = (v, d = 1, signo = false) => (v == null || Number.isNaN(v) ? '—'
  : `${v < 0 ? '−' : signo && v > 0 ? '+' : ''}${Math.abs(v).toFixed(d).replace('.', ',')}`);
const miles = (v) => (v == null ? '—' : Math.round(v).toLocaleString('es-CL'));
const etiquetaMes = (f) => `${f.slice(5, 7)}/${f.slice(2, 4)}`;
const colorCambio = (mejoraSiSube) => (v) => (v == null || Math.abs(v) < 0.05 ? '#5B6573' : (v > 0) === mejoraSiSube ? PETROLEO : COBRE);

function ultimos(filas, n) {
  const fechas = [...new Set(filas.map((f) => f.fecha))].sort().slice(-n);
  return { fechas, set: new Set(fechas) };
}

function armarCredito(d, est) {
  const vista = est.seleccion?.vista || 'fuente';
  const modo = est.seleccion?.modo || 'nominal';
  const filas = (d.bk_portada_credito || []).filter((f) => f.modo === modo);
  if (!filas.length) return { enPreparacion: 'falta bk_portada_credito' };
  const tot = filas.filter((f) => f.componente === 'total' && f.aa != null);
  const { fechas } = ultimos(tot, MESES);
  const valor = (comp, col) => { const m = new Map(filas.filter((f) => f.componente === comp).map((f) => [f.fecha, f[col]])); return fechas.map((x) => m.get(x) ?? null); };
  const [a, b] = vista === 'fuente' ? [['libre', 'Libre'], ['direccionado', 'Direccionado']] : [['pf', 'Personas'], ['pj', 'Empresas']];
  return {
    categorias: fechas.map(etiquetaMes),
    barras: [{ nombre: a[1], color: AZUL, valores: valor(a[0], 'contrib_pp') }, { nombre: b[1], color: ACERO, valores: valor(b[0], 'contrib_pp') }],
    linea: { nombre: 'Total a/a', color: TINTA, valores: valor('total', 'aa').map((v) => (v == null ? null : v * 100)) },
    formatoIzq: (v) => `${v} %`,
    intervalo: 5,
  };
}

/* Tabla estándar de la Portada: mismas columnas, anchos, decimales y color en los tres bloques.
   Mensual: m/m, 3m/3m, a/a, 12m/12m. Trimestral: t/t, —, a/a, 4T/4T. */
function tablaEstandar(filas, { ultimo, cambio, trimestral = false, sentido = null }) {
  void sentido; // v3c: sin color en las tablas; todas con el mismo formato
  const c = undefined;
  const cols = trimestral ? ['t/t', '—', 'a/a', '4T/4T'] : ['m/m', '3m/3m', 'a/a', '12m/12m'];
  return {
    columnas: [
      { titulo: 'Indicador', clave: 'fila', tipo: 'texto', ancho: '26%' },
      { titulo: 'Último', clave: 'ultimo', formatear: (v, f) => ultimo(v, f), ancho: '14%' },
      { titulo: cols[0], clave: 'd1', formatear: cambio, color: c, ancho: '11%' },
      { titulo: cols[1], clave: 'd3', formatear: cambio, color: c, ancho: '11%' },
      { titulo: cols[2], clave: 'd12', formatear: cambio, color: c, ancho: '11%' },
      { titulo: cols[3], clave: 'dventana', formatear: cambio, color: c, ancho: '13%' },
      { titulo: 'Corte', clave: 'corte', ancho: '14%' },
    ],
    filas,
  };
}

function armarTablaCredito(d, est) {
  const modo = est.seleccion?.modo || 'nominal';
  const filas = (d.bk_portada_tablas || []).filter((f) => f.bloque === `credito_${modo}`).sort((x, y) => x.orden - y.orden);
  if (!filas.length) return { enPreparacion: 'falta bk_portada_tablas' };
  return { filas, unidadUltimo: 'brl_mm', unidadCambio: 'pct' };
}

function armarMora(d) {
  const filas = (d.bk_portada_mora || []).filter((f) => f.nivel != null);
  if (!filas.length) return { enPreparacion: 'falta bk_portada_mora' };
  const { set } = ultimos(filas, MESES);
  const v = filas.filter((f) => set.has(f.fecha)).sort((x, y) => (x.fecha < y.fecha ? -1 : 1));
  return {
    categorias: v.map((f) => etiquetaMes(f.fecha)),
    barras: [{ nombre: 'Cambio a/a (pp, eje der.)', color: ARENA, valores: v.map((f) => f.d_aa_pp) }],
    linea: { nombre: 'Mora > 90 días (%)', color: COBRE, valores: v.map((f) => f.nivel * 100) },
    ejeBarras: 'der',
    formatoIzq: (x) => `${x} %`, formatoDer: (x) => `${x} pp`,
    intervalo: 5,
  };
}

function armarTablaMora(d) {
  const filas = (d.bk_portada_tablas || []).filter((f) => f.bloque === 'mora' && f.ultimo != null).sort((x, y) => x.orden - y.orden);
  if (!filas.length) return { enPreparacion: 'falta bk_portada_tablas' };
  return { filas, unidadUltimo: 'pct', unidadCambio: 'pp' };
}

function armarRoe(d) {
  const filas = (d.bk_portada_roe || []).filter((f) => f.roe != null).sort((x, y) => (x.periodo < y.periodo ? -1 : 1)).slice(-16);
  if (!filas.length) return { enPreparacion: 'falta bk_portada_roe' };
  return {
    categorias: filas.map((f) => f.trimestre),
    barras: [{ nombre: 'ROE − CDI (pp)', color: PETROLEO, valores: filas.map((f) => f.roe_cdi_pp) }],
    linea: { nombre: 'ROE 12 meses (%)', color: TINTA, valores: filas.map((f) => f.roe * 100) },
    formatoIzq: (v) => `${v}`,
    intervalo: 1,
  };
}

function armarTablaRoe(d) {
  const filas = (d.bk_portada_tablas || []).filter((f) => f.bloque === 'roe').sort((x, y) => x.orden - y.orden)
    .map((f) => ({ ...f, unidad_ultimo: f.orden === 0 ? 'pct' : 'pp' }));
  if (!filas.length) return { enPreparacion: 'falta bk_portada_tablas' };
  return { filas, unidadCambio: 'pp', trimestral: true };
}

const VISTAS = ['Activos totales', 'Crédito total', 'Crédito personas', 'Crédito empresas', 'Depósitos totales', 'Depósitos a la vista', 'Depósitos de ahorro', 'Depósitos a plazo'];

function armarMapa(d, est) {
  const vista = est.seleccion?.vista || VISTAS[0];
  const filas = (d.bk_portada_cuotas || []).filter((f) => f.vista === vista).sort((x, y) => x.orden - y.orden);
  if (!filas.length) return { enPreparacion: 'falta bk_portada_cuotas' };
  return { filas };
}

export default {
  clave: 'B0',
  ruta: '',
  nombre: 'Portada',
  rotulo: 'SISTEMA BCB · PANEL IF.DATA',
  usaBanco: false,

  secciones: [
    {
      numero: '01',
      nombre: 'Crédito',
      frecuencia: 'Mensual · Sistema BCB',
      pregunta: 'Crecimiento a/a de la cartera y contribución de cada componente.',
      riel: [
        { tipo: 'selector', clave: 'vista', rotulo: 'COMPONENTES', defecto: 'fuente', opciones: [{ valor: 'fuente', nombre: 'Libre · Direccionado' }, { valor: 'deudor', nombre: 'Personas · Empresas' }] },
        { tipo: 'selector', clave: 'modo', rotulo: 'MEDIDA', defecto: 'nominal', opciones: [{ valor: 'nominal', nombre: 'Nominal' }, { valor: 'real', nombre: 'Real (IPCA)' }] },
      ],
      filas: [[{ clave: 'B0-01', ancho: 4, alto: 420 }, { clave: 'B0-02', ancho: 5, alto: 420 }]],
    },
    {
      numero: '02',
      nombre: 'Mora',
      frecuencia: 'Mensual · Sistema BCB',
      pregunta: 'Mora mayor a 90 días y su cambio en doce meses.',
      filas: [[{ clave: 'B0-03', ancho: 4, alto: 420 }, { clave: 'B0-04', ancho: 5, alto: 420 }]],
    },
    {
      numero: '03',
      nombre: 'Rentabilidad',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'ROE del sistema y su exceso sobre la tasa libre de riesgo.',
      filas: [[{ clave: 'B0-05', ancho: 4, alto: 420 }, { clave: 'B0-06', ancho: 5, alto: 420 }]],
    },
    {
      numero: '04',
      nombre: 'Estructura',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Cuota de cada banco: diez mayores y el resto.',
      riel: [
        { tipo: 'selector', clave: 'vista', rotulo: 'CUOTA EN', defecto: VISTAS[0], opciones: VISTAS.map((v) => ({ valor: v, nombre: v })) },
      ],
      filas: [[{ clave: 'B0-07', ancho: 9, alto: 460 }]],
    },
  ],

  tarjetas: {
    'B0-01': {
      titulo: 'Crecimiento a/a y contribución',
      plana: true,
      leyenda: [{ nombre: 'Total a/a (%)', color: TINTA }, { nombre: 'Componentes: contribución al a/a (pp)', color: AZUL }],
      fuente: `${SGS} 20539, 20542, 20593, 20541, 20540; deflactor IPCA (433)`,
      componente: 'barras_linea',
      datos: ['bk_portada_credito'],
      armar: armarCredito,
      estado: 'LISTO',
    },
    'B0-02': {
     
      titulo: 'Cartera de crédito',
      plana: true,
      nota: 'Último: saldo nominal en R$ mil millones. Cambios en %. 3m/3m y 12m/12m: promedio de la ventana contra la anterior. Libre y direccionado llegan con un mes de rezago.',
      fuente: SGS,
      componente: 'tabla_estandar',
      datos: ['bk_portada_tablas'],
      armar: armarTablaCredito,
      estado: 'LISTO',
    },
    'B0-03': {
      titulo: 'Mora > 90 días y cambio a/a',
      plana: true,
      leyenda: [{ nombre: 'Mora total (%)', color: COBRE }, { nombre: 'Cambio a/a (pp, eje der.)', color: ARENA }],
      fuente: `${SGS} 21082; desde 2025 rige la Res. 4.966`,
      componente: 'barras_linea',
      datos: ['bk_portada_mora'],
      armar: armarMora,
      estado: 'LISTO',
    },
    'B0-04': {
     
      titulo: 'Mora por segmento',
      plana: true,
      nota: 'Último en %. Cambios en pp. 3m/3m y 12m/12m: promedio de la ventana contra la anterior.',
      fuente: `${SGS} 21082, 21084, 21112, 21086 y los que el SGS sirva de 21083, 21085, 21132`,
      componente: 'tabla_estandar',
      datos: ['bk_portada_tablas'],
      armar: armarTablaMora,
      estado: 'LISTO',
    },
    'B0-05': {
      titulo: 'ROE y ROE − CDI',
      plana: true,
      leyenda: [{ nombre: 'ROE 12 meses (%)', color: TINTA }, { nombre: 'ROE − CDI (pp)', color: PETROLEO }],
      fuente: `${IFDATA}; CDI SGS 4389, promedio de 4 trimestres`,
      componente: 'barras_linea',
      datos: ['bk_portada_roe'],
      armar: armarRoe,
      estado: 'LISTO',
    },
    'B0-06': {
     
      titulo: 'Rentabilidad del panel',
      plana: true,
      nota: 'Último en % (ROE) y pp (ROE − CDI). Cambios en pp. 4T/4T: promedio de cuatro trimestres contra los cuatro anteriores. El ROE no se publica mensual.',
      fuente: IFDATA,
      componente: 'tabla_estandar',
      datos: ['bk_portada_tablas'],
      armar: armarTablaRoe,
      estado: 'LISTO',
    },
    'B0-07': {
      titulo: 'Cuota por banco',
      plana: true,
      leyenda: [{ nombre: 'Grandes', color: '#2E5C8A' }, { nombre: 'Desarrollo', color: '#8FA3BC' }, { nombre: 'Digitales', color: '#2F7A86' }, { nombre: 'Medianos y nicho', color: '#B5C0CD' }, { nombre: 'Pagos', color: '#7B5E8C' }, { nombre: 'Resto', color: '#E6EAEF' }],
      fuente: `${IFDATA}; informes de pasivo y de cartera PF/PJ`,
      componente: 'mapa_cuotas',
      datos: ['bk_portada_cuotas'],
      armar: armarMapa,
      estado: 'LISTO',
    },
  },
};
