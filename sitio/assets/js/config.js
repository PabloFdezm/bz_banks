/* Configuración única del sitio de bancos. Copia de la del macro (misma forma) con dos
   cambios: las páginas son las once del esqueleto de bancos y la portada vive en la raíz
   (`ruta: ''`). Cambiar RUTA_DATOS si el sitio se sirve desde otra raíz. */
export const RUTA_DATOS = '/data/';

/* Qué tablas existen: data/_manifiesto.json (lo lee datos.js, tablasExportadas). Ya no hay lista a mano. */

/* Rótulo de la cabecera: el del esqueleto de bancos (§B0, «BANCOS BRASIL · MONITOR»). */
export const MARCA = 'BANCOS BRASIL';

/* oculta: true saca la página del menú (MVP: solo las cinco con datos). La página sigue
   existiendo y se abre por URL. */
/* Las once páginas del esqueleto (ESQUELETO_BANCOS_v0.1 §0.1) más Personas (B11) y Mora (B12), 6-nov. */
export const PAGINAS = [
  { clave: 'B0', ruta: '', nombre: 'Portada' },
  { clave: 'B1', ruta: 'ciclo', nombre: 'Ciclo y condiciones', oculta: true },
  { clave: 'B2', ruta: 'competencia', nombre: 'Estructura y competencia', oculta: true },
  { clave: 'B3', ruta: 'credito', nombre: 'Crédito' },
  { clave: 'B11', ruta: 'personas', nombre: 'Personas' },
  { clave: 'B4', ruta: 'calidad', nombre: 'Calidad' },
  { clave: 'B12', ruta: 'mora', nombre: 'Mora' },
  { clave: 'B5', ruta: 'fondeo', nombre: 'Fondeo y liquidez', oculta: true },
  { clave: 'B6', ruta: 'rentabilidad', nombre: 'Rentabilidad' },
  { clave: 'B7', ruta: 'capital', nombre: 'Capital', oculta: true },
  { clave: 'B8', ruta: 'ficha', nombre: 'Ficha por banco' },
  { clave: 'B9', ruta: 'comparador', nombre: 'Comparador', oculta: true },
  { clave: 'B10', ruta: 'metodologia', nombre: 'Metodología y fuentes', oculta: true },
];
