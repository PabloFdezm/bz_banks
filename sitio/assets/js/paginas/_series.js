/* Piezas comunes de las páginas de series del sistema con tabla estándar (B0, B3, B11, B12): filtrar
   bloques y series del gold, armar las líneas con su Total y la leyenda desde las series. Sin DOM. */
import { COLOR } from '../tokens.js';
import { enPreparacion } from '../comun.js';
import { porFecha } from '../formato.js';

/* Ventana de los gráficos mensuales. */
export const MESES = 36;

/* Filas de una tabla de bloques (bk_*_tablas) que cumplen el filtro, en su orden. */
export const filasDe = (filas, filtro) => (filas || [])
  .filter((f) => Object.entries(filtro).every(([k, v]) => f[k] === v))
  .sort((x, y) => x.orden - y.orden);

/* Una serie de una tabla bk_*_series, en orden de fecha. */
export const serieDe = (filas, nombre) => (filas || []).filter((f) => f.serie === nombre).sort(porFecha);

/* Las últimas n fechas distintas de una serie. */
export const ultimasFechas = (serie, n) => [...new Set(serie.map((x) => x.fecha))].slice(-n);

/* Valores de una serie en las fechas dadas (null donde falta); por defecto, la fracción pasada a %. */
export function valoresEn(serie, fechas, valor = (x) => x.valor * 100) {
  const m = new Map(serie.map((x) => [x.fecha, valor(x)]));
  return fechas.map((f) => m.get(f) ?? null);
}

/* Entrada de tabla_estandar desde las filas de un bloque; con `total`, esa fila va destacada. */
export function tablaEstandar(filas, motivo, total = null) {
  if (!filas.length) return enPreparacion(motivo);
  return { filas: total ? filas.map((x) => ({ ...x, destacar: x.fila === total })) : filas };
}

/* Una fila de sección: gráfico (4 de 9) a la izquierda y tabla estándar (5 de 9) a la derecha. */
export const graficoYTabla = (grafico, tabla, alto) => [[{ clave: grafico, ancho: 4, alto }, { clave: tabla, ancho: 5, alto }]];

/* Leyenda HTML de un barras_linea, desde sus series: primero las líneas, después las barras. */
export const leyendaDe = ({ lineas = [], barras = [] }) => [
  ...lineas.map((l) => ({ nombre: l.nombre, color: l.color, discontinua: !!l.discontinua })),
  ...barras.map((b) => ({ nombre: b.nombre, color: b.color })),
];

/* barras_linea con una línea por categoría y el Total grueso, primero y en su color (regla de Pablo);
   la leyenda es la de ECharts (clic oculta o muestra una serie). */
export function lineasConTotal({ categorias, lineas, total, eje = 'pct_nivel', intervalo }) {
  return {
    componente: 'barras_linea',
    categorias,
    barras: [],
    lineas: [{ ...total, color: COLOR.total, grosor: 3, z: 9 }, ...lineas.map((l) => ({ grosor: 1.6, ...l }))],
    leyendaInteractiva: true,
    leyenda: [],
    ejeIzq: eje,
    intervalo,
  };
}
