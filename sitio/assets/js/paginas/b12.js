/* B12 · Mora — calidad de la cartera por modalidad y por sector (SCR.data).
   Sección 01 replica el gráfico 1.2.2.16 del REF (activos problemáticos por modalidad, PF; calza exacto a jun-26) y
   la 03 el 1.2.2.15 (cartera de menor y mayor riesgo; la agrupación es propia). La 02 (mora temprana) y la 04
   (activos problemáticos de empresas por sector) son propias.
   Todo viene de preparar_gold_bancos_scr_productos.py (bk_scr_tablas con producto «_mora», bk_scr_series). */
import { FUENTE, enPreparacion } from '../comun.js';
import { COLOR } from '../tokens.js';
import { etiquetaMes } from '../formato.js';
import { filasDe, serieDe, ultimasFechas, valoresEn, tablaEstandar, graficoYTabla, lineasConTotal } from './_series.js';

const { SCR } = FUENTE;
const MODS = ['Tarjeta', 'Personal no consignado', 'Consignado', 'Vehículos', 'Inmobiliario', 'Rural', 'Cheque especial'];
const COLOR_SERIE = { 'Tarjeta': COLOR.granate, 'Personal no consignado': COLOR.lavanda, 'Consignado': COLOR.petroleo, 'Vehículos': COLOR.aceroMedio,
  'Inmobiliario': COLOR.navy, 'Rural': COLOR.oliva, 'Cheque especial': COLOR.azulNoche, 'Menor riesgo': COLOR.navy, 'Mayor riesgo': COLOR.aceroMedio };

const bloque = (d, b) => filasDe(d.bk_scr_tablas, { bloque: b, producto: '_mora' });
const serie = (d, s) => serieDe(d.bk_scr_series, s);

function lineas(d, prefijo, nombres, total, intervalo = 11) {
  const fechas = ultimasFechas(serie(d, `${prefijo}|${total}`), Infinity);
  if (!fechas.length) return enPreparacion('falta bk_scr_series');
  const valores = (n) => valoresEn(serie(d, `${prefijo}|${n}`), fechas);
  return lineasConTotal({
    categorias: fechas.map(etiquetaMes),
    total: { nombre: total, valores: valores(total) },
    lineas: nombres.map((n) => ({ nombre: n, color: COLOR_SERIE[n] || COLOR.aceroMedio, valores: valores(n) })),
    intervalo,
  });
}

function armarSector(d) {
  const f = bloque(d, 'sector').filter((x) => x.fila !== 'Resto de sectores');
  if (!f.length) return enPreparacion('falta bk_scr_tablas');
  const ult = (n) => { const s = serie(d, `ap_sector|${n}`); return s.length ? s[s.length - 1].valor : null; };
  const filas = f.map((x) => ({ nombre: x.fila, valor: ult(x.fila), destacar: x.destacar, color: x.destacar ? COLOR.total : COLOR.navy }))
    .filter((x) => x.valor != null).sort((a, b) => b.valor - a.valor);
  return { filas, formato: 'pct' };
}

const tabla = (b) => (d) => tablaEstandar(bloque(d, b), 'falta bk_scr_tablas');
const fila2 = (a, b, alto = 470) => graficoYTabla(a, b, alto);

export default {
  rotulo: 'SCR.DATA · MENSUAL',
  usaBanco: false,

  secciones: [
    { numero: '01', nombre: 'Activos problemáticos por modalidad', frecuencia: 'Mensual · SCR.data',
      pregunta: 'Qué parte de cada modalidad de personas está en atraso de 90 días o reestructurada con deterioro. Réplica del gráfico 1.2.2.16 del REF.',
      filas: fila2('B12-01', 'B12-02', 610) },
    { numero: '02', nombre: 'Mora temprana por modalidad', frecuencia: 'Mensual · SCR.data',
      pregunta: 'El atraso de 15 a 90 días anticipa la mora de más de 90 en unos 3 meses.', filas: fila2('B12-03', 'B12-04', 610) },
    { numero: '03', nombre: 'Crédito de mayor riesgo', frecuencia: 'Mensual · SCR.data',
      pregunta: 'Si el crédito más riesgoso crece más que el resto, la mora futura sube. Réplica del gráfico 1.2.2.15 del REF.',
      filas: fila2('B12-05', 'B12-06', 610) },
    { numero: '04', nombre: 'Empresas por sector', frecuencia: 'Mensual · SCR.data',
      pregunta: 'Activos problemáticos de la cartera de empresas por sector de actividad (sección CNAE).', filas: fila2('B12-07', 'B12-08', 700) },
  ],

  tarjetas: {
    'B12-01': { titulo: 'Activos problemáticos / cartera, %', plana: true, componente: 'barras_linea',
      fuente: `${SCR}; personas; Res. 4.966 desde ene-25 (otra definición de activo problemático)`, datos: ['bk_scr_series'],
      armar: (d) => lineas(d, 'ap', MODS, 'Total personas'), estado: 'LISTO' },
    'B12-02': { titulo: 'Stock de activos problemáticos por modalidad', plana: true, componente: 'tabla_estandar',
      nota: 'Último: R$ mil millones. Share: peso en el total de personas. Cambios en %. A jun-26 calza con el REF: total 9,2 %, tarjeta 12,7 %, no consignado 14,9 %.',
      fuente: SCR, datos: ['bk_scr_tablas'], armar: tabla('ap_stock'), estado: 'LISTO' },
    'B12-03': { titulo: 'Atraso de 15 a 90 días / cartera, %', plana: true, componente: 'barras_linea',
      fuente: `${SCR}; personas`, datos: ['bk_scr_series'], armar: (d) => lineas(d, 'temprana_mod', MODS, 'Total personas'), estado: 'LISTO' },
    'B12-04': { titulo: 'Mora >90 días por modalidad', plana: true, componente: 'tabla_estandar',
      nota: 'Último: % de la cartera. Share: peso de la modalidad en la cartera de personas. Cambios en pp; 12m/12m: promedio de 12 meses contra los 12 previos.',
      fuente: SCR, datos: ['bk_scr_tablas'], armar: tabla('mora_mod'), estado: 'LISTO' },
    'B12-05': { titulo: 'Crecimiento a/a de la cartera de personas, %', plana: true, componente: 'barras_linea',
      fuente: `${SCR}; menor riesgo = inmobiliario, consignado, vehículos, rural; mayor = tarjeta, personal, cheque especial, otros`,
      datos: ['bk_scr_series'], armar: (d) => lineas(d, 'aa_riesgo', ['Menor riesgo', 'Mayor riesgo'], 'Total personas'), estado: 'LISTO' },
    'B12-06': { titulo: 'Cartera de personas por modalidad', plana: true, componente: 'tabla_estandar',
      nota: 'Último: R$ mil millones. Share: peso en la cartera de personas. Cambios en %.',
      fuente: SCR, datos: ['bk_scr_tablas'], armar: tabla('cartera_mod'), estado: 'LISTO' },
    'B12-07': { titulo: 'Activos problemáticos / cartera por sector, último mes', plana: true, componente: 'barras_simple',
      fuente: `${SCR}; 10 mayores sectores por cartera`, datos: ['bk_scr_tablas', 'bk_scr_series'], armar: armarSector, estado: 'LISTO' },
    'B12-08': { titulo: 'Cartera de empresas por sector', plana: true, componente: 'tabla_estandar',
      nota: 'Último: R$ mil millones. Cambios en %. El nivel total queda bajo el del REF por diferencia de universo: sirve para comparar sectores. Financieras +38 % a/a: revisar reclasificación.',
      fuente: SCR, datos: ['bk_scr_tablas'], armar: tabla('sector'), estado: 'LISTO' },
  },
};
