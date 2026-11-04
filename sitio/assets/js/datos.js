/* Carga de datos (§7.2 del general): caché por tabla + utilidades de filtro y fecha.
   Formato: {"tabla", "columnas":[…], "filas":[[…]]} → array de objetos. */
import { RUTA_DATOS } from './config.js';

const cache = new Map();

export async function cargar(tabla) {
  if (!cache.has(tabla)) {
    cache.set(tabla, fetch(`${RUTA_DATOS}${tabla}.json`)
      .then((r) => { if (!r.ok) throw new Error(`${tabla}: HTTP ${r.status}`); return r.json(); })
      .then((j) => j.filas.map((f) => Object.fromEntries(j.columnas.map((c, i) => [c, f[i]]))))
      .catch((e) => { cache.delete(tabla); throw e; }));
  }
  return cache.get(tabla);
}

export async function cargarTodas(tablas) {
  const unicas = [...new Set(tablas)];
  const resultados = await Promise.all(unicas.map(cargar));
  return Object.fromEntries(unicas.map((t, i) => [t, resultados[i]]));
}

/* ---------- utilidades ---------- */

/* bancos: qué tablas existen lo dice data/_manifiesto.json, que el exportador escribe siempre (encargo 76).
   Sin manifiesto, ninguna: la lista de bancos queda en su respaldo. Se pide una sola vez por carga. */
let MANIFIESTO = null;
export function tablasExportadas() {
  if (!MANIFIESTO) {
    MANIFIESTO = fetch(`${RUTA_DATOS}_manifiesto.json`)
      .then((r) => { if (!r.ok) throw new Error(`manifiesto: HTTP ${r.status}`); return r.json(); })
      .then((j) => Object.keys(j.tablas || {}))
      .catch(() => []);
  }
  return MANIFIESTO;
}

export const filtrar = (filas, condicion) => filas.filter(condicion);

export function por(filas, columna) {
  return filas.reduce((acc, f) => { (acc[f[columna]] ||= []).push(f); return acc; }, {});
}

export function ordenarPor(filas, columna, asc = true) {
  return [...filas].sort((a, b) => {
    const x = a[columna], y = b[columna];
    if (x == null) return 1;
    if (y == null) return -1;
    return (x > y ? 1 : x < y ? -1 : 0) * (asc ? 1 : -1);
  });
}

export function fecha(v) { return v == null ? null : new Date(`${String(v).slice(0, 10)}T00:00:00`); }

export function maxFecha(filas, columna = 'fecha') {
  return filas.reduce((m, f) => (f[columna] != null && (m == null || f[columna] > m) ? f[columna] : m), null);
}

export function minFecha(filas, columna = 'fecha') {
  return filas.reduce((m, f) => (f[columna] != null && (m == null || f[columna] < m) ? f[columna] : m), null);
}

/* último valor no nulo de una serie ya ordenada por fecha (§7.7) */
export function ultimo(puntos) {
  for (let i = puntos.length - 1; i >= 0; i--) if (puntos[i][1] != null) return puntos[i];
  return null;
}

/* re-basar a índice 100 en la primera fecha no nula */
export function rebasar(puntos, base = 100) {
  const primero = puntos.find(([, v]) => v != null);
  if (!primero || primero[1] === 0) return puntos.map(([f]) => [f, null]);
  return puntos.map(([f, v]) => [f, v == null ? null : (v / primero[1]) * base]);
}
