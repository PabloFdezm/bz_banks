/* B3 · Crédito — tablero 06 del canvas. Cuatro láminas con el gráfico a la izquierda y la
   tabla estándar a la derecha (misma proporción y alto en todas, para que al presentar nada salte).
   Todo viene de preparar_gold_bancos_pag_credito.py (bk_cred_tablas, bk_cred_series). */
import { FUENTE, enPreparacion } from '../comun.js';
import { COLOR } from '../tokens.js';
import { etiquetaMes, trimestre } from '../formato.js';
import { MESES, filasDe, serieDe, ultimasFechas, valoresEn, tablaEstandar, graficoYTabla, leyendaDe, lineasConTotal } from './_series.js';

const { SGS } = FUENTE;

const bloque = (d, b) => filasDe(d.bk_cred_tablas, { bloque: b });
const serie = (d, s) => serieDe(d.bk_cred_series, s);

// Vista Barras (último a/a) o Líneas (historia del a/a); el Total va siempre en otro color (regla de Pablo).
// En Líneas la leyenda es la de ECharts: clic en un tipo lo oculta o lo muestra (como en Power BI).
const COLOR_TIPO = { 'Tarjeta': COLOR.navy, 'Consignado': COLOR.azulMedio, 'Personal no consignado': COLOR.azulClaro, 'Vehículos': COLOR.texto,
  'Inmobiliario (personas)': COLOR.petroleo, 'Rural (personas)': COLOR.petroleoClaro, 'Empresas libre': COLOR.grafito, 'BNDES (empresas)': COLOR.aceroMedio,
  'Rural (empresas)': COLOR.ocre, 'Inmobiliario (empresas)': COLOR.indigo };
const COLOR_DEUDOR = { Personas: COLOR.navy, Empresas: COLOR.aceroMedio };

function armarTipos(d, est) {
  const f = bloque(d, 'tipos');
  if (!f.length) return enPreparacion('falta bk_cred_tablas');
  const tot = f.find((x) => x.fila === 'Total');
  const mods = f.filter((x) => x.fila !== 'Total');
  if (est.seleccion.grafico === 'barras') {
    const color = (x) => (x.grupo === 'Empresas' ? COLOR_DEUDOR.Empresas : COLOR_DEUDOR.Personas);
    const filas = mods.map((x) => ({ nombre: x.fila, valor: x.d12 * 100, color: color(x) })).sort((a, b) => b.valor - a.valor);
    if (tot) filas.unshift({ nombre: 'Total', valor: tot.d12 * 100, color: COLOR.total });
    const leyenda = [{ nombre: 'Total', color: COLOR.total }, ...Object.entries(COLOR_DEUDOR).map(([nombre, c]) => ({ nombre, color: c }))];
    return { componente: 'barras_signo', filas, unidad: '%', decimales: 1, leyenda };
  }
  const fechas = ultimasFechas(serie(d, 'aa|Total'), MESES);
  const valores = (n) => valoresEn(serie(d, `aa|${n}`), fechas);
  return lineasConTotal({
    categorias: fechas.map(etiquetaMes),
    total: { nombre: 'Total', valores: valores('Total') },
    lineas: mods.map((x) => ({ nombre: x.fila, color: COLOR_TIPO[x.fila] || COLOR.aceroMedio, valores: valores(x.fila) })),
    intervalo: 5,
  });
}
function armarContrib(d) {
  const f = bloque(d, 'contrib').filter((x) => x.fila !== 'Total');
  if (!f.length) return enPreparacion('falta bk_cred_tablas');
  return { filas: f.map((x) => ({ nombre: x.fila, valor: x.d1 })).sort((a, b) => b.valor - a.valor), unidad: 'pp', decimales: 2, colorPos: COLOR.navy, colorNeg: COLOR.peor };
}
function armarConc(d) {
  const c = serie(d, 'conc12_aa'), s = serie(d, 'stock_aa');
  if (!c.length) return enPreparacion('falta bk_cred_series');
  const fechas = ultimasFechas(s, MESES);
  const entrada = { categorias: fechas.map(etiquetaMes), barras: [],
    lineas: [{ nombre: 'Concesiones libres 12m, a/a', color: COLOR.navy, valores: valoresEn(c, fechas) }, { nombre: 'Saldo total, a/a', color: COLOR.texto, valores: valoresEn(s, fechas) }],
    ejeIzq: 'pct_nivel', intervalo: 5 };
  return { ...entrada, leyenda: leyendaDe(entrada) };
}
function armarCiclo(d) {
  const n = serie(d, 'cpib_nivel').slice(-16);
  if (!n.length) return enPreparacion('falta bk_cred_series');
  const fechas = n.map((x) => x.fecha);
  const valores = (s) => valoresEn(serie(d, s), fechas, (x) => x.valor);
  const brecha = valores('cpib_brecha');
  // brecha simétrica en torno a cero, para que las barras no cuelguen del borde
  const tope = Math.ceil(Math.max(...brecha.map((v) => Math.abs(v ?? 0)), 1));
  const entrada = { categorias: fechas.map(trimestre), barras: [{ nombre: 'Brecha (pp, eje der.)', color: COLOR.arenaClara, valores: brecha }],
    lineas: [{ nombre: 'Crédito/PIB (%)', color: COLOR.texto, valores: valores('cpib_nivel') }, { nombre: 'Tendencia HP (%)', color: COLOR.aceroMedio, valores: valores('cpib_tendencia'), discontinua: true }],
    rangoIzq: { escala: true }, rangoDer: { min: -tope, max: tope },
    ejeBarras: 'der', ejeIzq: 'pct_nivel', ejeDer: 'pp', intervalo: 1 };
  return { ...entrada, leyenda: leyendaDe(entrada) };
}
const tabla = (b, total = 'Total') => (d) => tablaEstandar(bloque(d, b), 'falta bk_cred_tablas', total);
const fila2 = (a, b, alto = 420) => graficoYTabla(a, b, alto);

export default {
  rotulo: 'SISTEMA BCB · MENSUAL',
  usaBanco: false,

  secciones: [
    { numero: '01', nombre: 'Por tipo', frecuencia: 'Mensual · SGS', pregunta: 'Crecimiento a/a del saldo de cada modalidad.',
      riel: [{ tipo: 'selector', clave: 'grafico', rotulo: 'GRÁFICO', defecto: 'barras', opciones: [{ valor: 'barras', nombre: 'Barras · último' }, { valor: 'lineas', nombre: 'Líneas · historia' }] }],
      filas: fila2('B3-01', 'B3-02', 570) },
    { numero: '02', nombre: 'Qué lo movió', frecuencia: 'Mensual · SGS', pregunta: 'Contribución de cada modalidad al crecimiento del total en el último mes.', filas: fila2('B3-03', 'B3-04', 590) },
    { numero: '03', nombre: 'Crédito nuevo', frecuencia: 'Mensual · SGS', pregunta: 'Concesiones contra stock: si lo que se presta crece más que el saldo, el saldo tiende a acelerar.', filas: fila2('B3-05', 'B3-06') },
    { numero: '04', nombre: 'Ciclo', frecuencia: 'Trimestral · SGS 20622', pregunta: 'Crédito/PIB contra su tendencia: la brecha dice si el crédito está sobre o bajo lo sostenible.', filas: fila2('B3-07', 'B3-08') },
  ],

  tarjetas: {
    'B3-01': { titulo: 'Crecimiento a/a por tipo', plana: true,
      fuente: `${SGS}; consignado = privado + público + INSS`, componente: 'barras_signo', datos: ['bk_cred_tablas', 'bk_cred_series'], armar: armarTipos, estado: 'LISTO' },
    'B3-02': { titulo: 'Cartera por tipo', plana: true, nota: 'Último: saldo en R$ mil millones. Share: peso en la cartera total. Cambios en %. 3m/3m y 12m/12m: promedio de la ventana contra la anterior.',
      fuente: SGS, componente: 'tabla_estandar', datos: ['bk_cred_tablas'], armar: tabla('tipos'), estado: 'LISTO' },
    'B3-03': { titulo: 'Contribución al crecimiento m/m', plana: true, leyenda: [{ nombre: 'Suma', color: COLOR.navy }, { nombre: 'Resta', color: COLOR.peor }],
      fuente: `${SGS}; Otros = resto de libre y direccionado`, componente: 'barras_signo', datos: ['bk_cred_tablas'], armar: armarContrib, estado: 'LISTO' },
    'B3-04': { titulo: 'Contribución por tipo', plana: true, nota: 'Último: saldo en R$ mil millones. Share: peso en la cartera total. Cambios: contribución al crecimiento del total, en pp; suman el total.',
      fuente: SGS, componente: 'tabla_estandar', datos: ['bk_cred_tablas'], armar: tabla('contrib', 'Total'), estado: 'LISTO' },
    'B3-05': { titulo: 'Concesiones contra saldo, a/a', plana: true,
      fuente: `${SGS} 20631, 20539`, componente: 'barras_linea', datos: ['bk_cred_series'], armar: armarConc, estado: 'LISTO' },
    'B3-06': { titulo: 'Concesiones y saldo', plana: true, nota: 'Último: flujo del mes (concesiones) o saldo, en R$ mil millones. Cambios en %; 12m/12m de concesiones compara sumas de doce meses.',
      fuente: `${SGS} 20631, 20633, 20632, 20539`, componente: 'tabla_estandar', datos: ['bk_cred_tablas'], armar: tabla('conc', 'Saldo total'), estado: 'LISTO' },
    'B3-07': { titulo: 'Crédito/PIB, tendencia y brecha', plana: true,
      fuente: `${SGS} 20622; HP unilateral, λ = 400.000`, componente: 'barras_linea', datos: ['bk_cred_series'], armar: armarCiclo, estado: 'LISTO' },
    'B3-08': { titulo: 'Ciclo del crédito', plana: true, nota: 'Último en % (crédito/PIB, tendencia) y pp (brecha). Cambios en pp. El BIS mide crédito total al sector privado y su brecha difiere.',
      fuente: SGS, componente: 'tabla_estandar', datos: ['bk_cred_tablas'], armar: tabla('ciclo', 'Brecha'), estado: 'LISTO' },
  },
};
