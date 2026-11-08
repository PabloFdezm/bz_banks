/* B0 · Portada — tablero 05 del canvas «Bancos Brasil — propuesta visual».
   Cuatro bloques; cada uno es una lámina en modo presentación: gráfico a la izquierda y tabla
   descriptiva de estructura fija a la derecha (m/m, 3m/3m, a/a, 12m/12m; en trimestrales t/t, a/a,
   4T/4T). La tabla nunca repite la serie del gráfico. Todo viene calculado de
   preparar_gold_bancos_portada.py (bk_portada_*); aquí solo se filtra, se formatea y se dibuja. */
import { FUENTE, GRUPOS, COLOR_GRUPO, enPreparacion } from '../comun.js';
import { COLOR } from '../tokens.js';
import { etiquetaMes, porFecha, porPeriodo } from '../formato.js';
import { MESES, filasDe, leyendaDe } from './_series.js';

const { SGS, IFDATA } = FUENTE;

/* Las últimas n fechas con dato. */
const ultimasFechas = (filas, n) => [...new Set(filas.map((f) => f.fecha))].sort().slice(-n);

function armarCredito(d, est) {
  const { vista, modo } = est.seleccion;
  const filas = (d.bk_portada_credito || []).filter((f) => f.modo === modo);
  if (!filas.length) return enPreparacion('falta bk_portada_credito');
  const fechas = ultimasFechas(filas.filter((f) => f.componente === 'total' && f.aa != null), MESES);
  const valor = (comp, col) => { const m = new Map(filas.filter((f) => f.componente === comp).map((f) => [f.fecha, f[col]])); return fechas.map((x) => m.get(x) ?? null); };
  const [a, b] = vista === 'fuente' ? [['libre', 'Libre'], ['direccionado', 'Direccionado']] : [['pf', 'Personas'], ['pj', 'Empresas']];
  const entrada = {
    categorias: fechas.map(etiquetaMes),
    barras: [{ nombre: `${a[1]}: contribución (pp)`, color: COLOR.navy, valores: valor(a[0], 'contrib_pp') }, { nombre: `${b[1]}: contribución (pp)`, color: COLOR.aceroMedio, valores: valor(b[0], 'contrib_pp') }],
    lineas: [{ nombre: 'Total a/a (%)', color: COLOR.texto, valores: valor('total', 'aa').map((v) => (v == null ? null : v * 100)) }],
    ejeIzq: 'pct_nivel',
    intervalo: 5,
  };
  return { ...entrada, leyenda: leyendaDe(entrada) };
}

const tablaDe = (d, filtro) => filasDe(d.bk_portada_tablas, filtro);

function armarTablaCredito(d, est) {
  const filas = tablaDe(d, { bloque: `credito_${est.seleccion.modo}` });
  if (!filas.length) return enPreparacion('falta bk_portada_tablas');
  return { filas };
}

function armarMora(d) {
  const filas = (d.bk_portada_mora || []).filter((f) => f.nivel != null);
  if (!filas.length) return enPreparacion('falta bk_portada_mora');
  const fechas = new Set(ultimasFechas(filas, MESES));
  const v = filas.filter((f) => fechas.has(f.fecha)).sort(porFecha);
  const entrada = {
    categorias: v.map((f) => etiquetaMes(f.fecha)),
    barras: [{ nombre: 'Cambio a/a (pp, eje der.)', color: COLOR.arenaClara, valores: v.map((f) => f.d_aa_pp) }],
    lineas: [{ nombre: 'Mora > 90 días (%)', color: COLOR.peor, valores: v.map((f) => f.nivel * 100) }],
    ejeBarras: 'der',
    ejeIzq: 'pct_nivel',
    ejeDer: 'pp',
    intervalo: 5,
  };
  return { ...entrada, leyenda: leyendaDe(entrada) };
}

function armarTablaMora(d) {
  const filas = tablaDe(d, { bloque: 'mora' }).filter((f) => f.ultimo != null);
  if (!filas.length) return enPreparacion('falta bk_portada_tablas');
  return { filas };
}

function armarRoe(d) {
  const filas = (d.bk_portada_roe || []).filter((f) => f.roe != null).sort(porPeriodo).slice(-16);
  if (!filas.length) return enPreparacion('falta bk_portada_roe');
  const entrada = {
    categorias: filas.map((f) => f.trimestre),
    barras: [{ nombre: 'ROE − CDI (pp)', color: COLOR.petroleo, valores: filas.map((f) => f.roe_cdi_pp) }],
    lineas: [{ nombre: 'ROE 12 meses (%)', color: COLOR.texto, valores: filas.map((f) => f.roe * 100) }],
    ejeIzq: 'num',
    intervalo: 1,
  };
  return { ...entrada, leyenda: leyendaDe(entrada) };
}

function armarTablaRoe(d) {
  const filas = tablaDe(d, { bloque: 'roe' });
  if (!filas.length) return enPreparacion('falta bk_portada_tablas');
  return { filas };
}

const VISTAS = ['Activos totales', 'Crédito total', 'Crédito personas', 'Crédito empresas', 'Depósitos totales', 'Depósitos a la vista', 'Depósitos de ahorro', 'Depósitos a plazo'];

const RESTO = 'Resto';

function armarMapa(d, est) {
  const filas = filasDe(d.bk_portada_cuotas, { vista: est.seleccion.vista });
  if (!filas.length) return enPreparacion('falta bk_portada_cuotas');
  const colores = { ...COLOR_GRUPO, [RESTO]: COLOR.regla };
  // leyenda: los grupos presentes, en el orden del sitio, y el resto al final
  const presentes = new Set(filas.map((f) => f.grupo));
  const leyenda = [...GRUPOS, RESTO].filter((g) => presentes.has(g)).map((g) => ({ nombre: g, color: colores[g] }));
  return { filas, colores, leyenda };
}

export default {
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
      fuente: `${IFDATA}; informes de pasivo y de cartera PF/PJ`,
      componente: 'mapa_cuotas',
      datos: ['bk_portada_cuotas'],
      armar: armarMapa,
      estado: 'LISTO',
    },
  },
};
