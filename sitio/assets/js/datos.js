/* Carga de datos (§7.2 del general): un fetch por tabla, en caché. Formato que escribe
   pipeline/exportar_web_bancos.py: {"tabla", "columnas":[…], "filas":[[…]]} → array de objetos.
   `tabla` puede ser una partición («banco/itau/bk_panel», ver comun.js). */
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

/* Qué tablas existen lo dice data/_manifiesto.json, que el exportador escribe siempre. Sin manifiesto
   (falta o no se pudo leer) no hay ninguna y la lista de bancos queda en su respaldo (estado.js);
   el fallo se avisa en la consola. Se pide una sola vez por carga. */
let MANIFIESTO = null;
export function tablasExportadas() {
  if (!MANIFIESTO) {
    MANIFIESTO = fetch(`${RUTA_DATOS}_manifiesto.json`)
      .then((r) => { if (!r.ok) throw new Error(`manifiesto: HTTP ${r.status}`); return r.json(); })
      .then((j) => Object.keys(j.tablas || {}))
      .catch((e) => { console.warn('Sin manifiesto de datos', e); return []; });
  }
  return MANIFIESTO;
}
