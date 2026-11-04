/* B9 · Comparador. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec macro).
   Transcrito de ESQUELETO_BANCOS_v0.1.md §B9: título, ancho, alto y estado son los del esqueleto.
   En la F0 la tarjeta no tiene `armar`.
   El esqueleto no le da nombre ni pregunta a la sección 01: los fija la decisión del arquitecto
   del 2026-11-02 (revisión del encargo 62) y entran al esqueleto v0.2 — nombre «Todos los bancos»
   y pregunta «¿cómo se comparan los 34 bancos en el último trimestre?».
   Datos: bk_panel. Columnas de capital FALTA (depende de bk_capital).
   Sin narrativa: es la herramienta de consulta. */
const IFDATA = 'BCB, IF.Data (conglomerado prudencial)';
const CALC = 'cálculo propio';

export default {
  clave: 'B9',
  ruta: 'comparador',
  nombre: 'Comparador',
  rotulo: '9 · COMPARADOR',
  signo: 'bancos',
  usaBanco: true,
  optica: 'Modelo de negocio',

  secciones: [
    {
      numero: '01',
      nombre: 'Todos los bancos',
      frecuencia: 'Trimestral · Panel IF.Data',
      preguntaClave: 'B9.01',
      pregunta: '¿cómo se comparan los 34 bancos en el último trimestre?',
      filas: [[{ clave: 'B9-01-0', ancho: 9, alto: 'auto' }]],
    },
  ],

  tarjetas: {
    'B9-01-0': {
      titulo: 'Los 34 bancos × ~20 métricas',
      sub: 'Panel IF.Data · 34 bancos × ~20 métricas · sparkline de 8 trimestres',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'comparador',
      datos: [],
      banco: true,
      estado: 'LISTO',
    },
  },
};
