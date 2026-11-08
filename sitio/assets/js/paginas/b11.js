/* B11 · Personas — crédito a personas por producto y tramo de renta (SCR.data).
   Cartera, mix, mora y ticket por tramo de renta (tarea 3, detalle en referencias/, fuera de git), para todos los
   productos: tarjeta, personal no consignado, consignado, vehículos, inmobiliario, rural, cheque especial y total.
   Todo viene de preparar_gold_bancos_scr_productos.py (bk_scr_tablas, bk_scr_series). Aquí solo se filtra y elige. */
import { FUENTE, enPreparacion } from '../comun.js';
import { COLOR } from '../tokens.js';
import { etiquetaMes } from '../formato.js';
import { MESES, filasDe, serieDe, ultimasFechas, valoresEn, tablaEstandar, graficoYTabla, lineasConTotal } from './_series.js';

const { SCR } = FUENTE;
const TRAMOS = ['Hasta 1 SM', '1–2 SM', '2–3 SM', '3–5 SM', '5–10 SM', '10–20 SM', 'Más de 20 SM'];
const LINEA = { 'Hasta 1 SM': COLOR.azulNoche, '1–2 SM': COLOR.navy, '2–3 SM': COLOR.azulPizarra, '3–5 SM': COLOR.petroleo, '5–10 SM': COLOR.oliva,
  '10–20 SM': COLOR.lavanda, 'Más de 20 SM': COLOR.grisMedio };
// mix: azules hasta 3 SM, tierras desde 3 SM, para que el corte de 3 SM se vea solo
const PILA = { 'Hasta 1 SM': COLOR.azulNoche, '1–2 SM': COLOR.navy, '2–3 SM': COLOR.azulPizarra, '3–5 SM': COLOR.arenaPalida, '5–10 SM': COLOR.trigo,
  '10–20 SM': COLOR.tierraClara, 'Más de 20 SM': COLOR.tierra };
const PRODUCTOS = [
  { valor: 'Tarjeta', nombre: 'Tarjeta' }, { valor: 'Personal no consignado', nombre: 'Personal' },
  { valor: 'Consignado', nombre: 'Consignado' }, { valor: 'Vehículos', nombre: 'Vehículos' },
  { valor: 'Inmobiliario', nombre: 'Inmobiliario' }, { valor: 'Rural', nombre: 'Rural' },
  { valor: 'Cheque especial', nombre: 'Cheque esp.' }, { valor: 'Total personas', nombre: 'Total' }];
const SELECTOR = [{ tipo: 'selector', clave: 'producto', rotulo: 'PRODUCTO', defecto: 'Tarjeta', opciones: PRODUCTOS }];
const producto = (est) => est.seleccion.producto;

const bloque = (d, b, p) => filasDe(d.bk_scr_tablas, { bloque: b, producto: p });
const serie = (d, s) => serieDe(d.bk_scr_series, s);

function lineasTramo(d, est, metrica) {
  const p = producto(est);
  const fechas = ultimasFechas(serie(d, `${metrica}|${p}|Total`), MESES);
  if (!fechas.length) return enPreparacion('falta bk_scr_series');
  const valores = (t) => valoresEn(serie(d, `${metrica}|${p}|${t}`), fechas);
  return lineasConTotal({
    categorias: fechas.map(etiquetaMes),
    total: { nombre: 'Total', valores: valores('Total') },
    lineas: TRAMOS.map((t) => ({ nombre: t, color: LINEA[t], valores: valores(t) })),
    intervalo: 5,
  });
}

function armarCrecimiento(d, est) {
  const f = bloque(d, 'saldo', producto(est));
  if (!f.length) return enPreparacion('falta bk_scr_tablas');
  const filas = f.filter((x) => TRAMOS.includes(x.fila)).map((x) => ({ nombre: x.fila, valor: x.d12 * 100, color: LINEA[x.fila] }));
  const tot = f.find((x) => x.destacar);
  if (tot) filas.unshift({ nombre: 'Total', valor: tot.d12 * 100, color: COLOR.total });
  return { filas, unidad: '%', decimales: 1, leyenda: filas.map((x) => ({ nombre: x.nombre, color: x.color })) };
}

function armarMix(d, est) {
  const p = producto(est);
  const fechas = ultimasFechas(serie(d, `mix|${p}|Hasta 3 SM`), Infinity);
  if (!fechas.length) return enPreparacion('falta bk_scr_series');
  return { categorias: fechas.map(etiquetaMes), barras: TRAMOS.map((t) => ({ nombre: t, color: PILA[t], valores: valoresEn(serie(d, `mix|${p}|${t}`), fechas) })), lineas: [],
    leyendaInteractiva: true, leyenda: [], rangoIzq: { min: 0, max: 100 }, ejeIzq: 'pct_nivel', intervalo: 2 };
}

const tabla = (b) => (d, est) => tablaEstandar(bloque(d, b, producto(est)), 'falta bk_scr_tablas');
// 640 px donde la tabla tiene 10 filas
const fila2 = (a, b, alto = 470) => graficoYTabla(a, b, alto);

export default {
  rotulo: 'SCR.DATA · MENSUAL',
  usaBanco: false,

  secciones: [
    { numero: '01', nombre: 'Cartera por renta', frecuencia: 'Mensual · SCR.data', riel: SELECTOR,
      pregunta: 'Cuánto crece la cartera en cada tramo de renta del deudor, en salarios mínimos (SM).', filas: fila2('B11-01', 'B11-02', 640) },
    { numero: '02', nombre: 'Exposición a renta baja', frecuencia: 'Mensual · SCR.data', riel: SELECTOR,
      pregunta: 'Qué parte de la cartera está en deudores de hasta 3 SM, en total y por tipo de institución.', filas: fila2('B11-03', 'B11-04') },
    { numero: '03', nombre: 'Mora por renta', frecuencia: 'Mensual · SCR.data', riel: SELECTOR,
      pregunta: 'Mora de más de 90 días en cada tramo, y cuánto crédito tiene cada operación.', filas: fila2('B11-05', 'B11-06', 640) },
    { numero: '04', nombre: 'Mora temprana', frecuencia: 'Mensual · SCR.data', riel: SELECTOR,
      pregunta: 'El atraso de 15 a 90 días se adelanta unos 3 meses a la mora de más de 90.', filas: fila2('B11-07', 'B11-08', 640) },
  ],

  tarjetas: {
    'B11-01': { titulo: 'Crecimiento a/a de la cartera por tramo', plana: true, componente: 'barras_signo',
      fuente: `${SCR}; tramos según la renta declarada del deudor`, datos: ['bk_scr_tablas'], armar: armarCrecimiento, estado: 'LISTO' },
    'B11-02': { titulo: 'Cartera por tramo de renta', plana: true, componente: 'tabla_estandar',
      nota: 'Último: R$ mil millones. Share: peso del tramo en el producto. Cambios en %. Ago-26: ~R$ 15 mil millones de tarjeta pasan de «más de 20 SM» a «N.D.» por reclasificación de la fuente.',
      fuente: SCR, datos: ['bk_scr_tablas'], armar: tabla('saldo'), estado: 'LISTO' },
    'B11-03': { titulo: 'Mix de la cartera por tramo de renta, %', plana: true, componente: 'barras_linea',
      fuente: `${SCR}; sin «N.D.» ni «sin renta»; jul-25: reclasificación de renta en la fuente`, datos: ['bk_scr_series'], armar: armarMix, estado: 'LISTO' },
    'B11-04': { titulo: 'Exposición hasta 3 SM por tipo de institución', plana: true, componente: 'tabla_estandar',
      nota: 'Último: % de la cartera del tipo en deudores de hasta 3 SM. Share: peso del tipo en el producto. Cambios en pp. Las fintech grandes aparecen según su licencia (financiera o institución de pago). SCR.data no trae S1–S5.',
      fuente: SCR, datos: ['bk_scr_tablas'], armar: tabla('inst'), estado: 'LISTO' },
    'B11-05': { titulo: 'Mora >90 días por tramo, %', plana: true, componente: 'barras_linea',
      fuente: `${SCR}; carteira_inadimplência / carteira ativa; Res. 4.966 desde ene-25`, datos: ['bk_scr_series'], armar: (d, est) => lineasTramo(d, est, 'mora'), estado: 'LISTO' },
    'B11-06': { titulo: 'Ticket por tramo (saldo por operación)', plana: true, componente: 'tabla_estandar',
      nota: 'Último: R$ por operación, en celdas con 15 o más operaciones. Cambios en %. En personal, el ticket de los tramos altos se multiplica en 2025 por un cambio de la fuente: su 12m/12m no es comparable.',
      fuente: SCR, datos: ['bk_scr_tablas'], armar: tabla('ticket'), estado: 'LISTO' },
    'B11-07': { titulo: 'Atraso de 15 a 90 días por tramo, %', plana: true, componente: 'barras_linea',
      fuente: `${SCR}; vencido de 15 a 90 días / carteira ativa`, datos: ['bk_scr_series'], armar: (d, est) => lineasTramo(d, est, 'temprana'), estado: 'LISTO' },
    'B11-08': { titulo: 'Mora >90 días por tramo', plana: true, componente: 'tabla_estandar',
      nota: 'Último: % de la cartera del tramo. Share: peso del tramo en el producto. Cambios en pp; 12m/12m: promedio de 12 meses contra los 12 previos. El SCR incluye todas las instituciones: el nivel difiere de la serie del SGS.',
      fuente: SCR, datos: ['bk_scr_tablas'], armar: tabla('mora'), estado: 'LISTO' },
  },
};
