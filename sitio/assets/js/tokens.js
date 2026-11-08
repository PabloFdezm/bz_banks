/* Tokens visuales para el JS (ECharts, SVG). Sin DOM: lo importan también las herramientas en Node.
   Cada clave de COLOR es un token de tokens.css (navy → --navy, texto2 → --texto-2, aceroMedio →
   --acero-medio): el CSS usa el token y el JS este valor. herramientas/verificar_f1.py comprueba en el
   navegador que ambos coincidan. */
export const COLOR = {
  fondo: '#F6F7F8',
  tarjeta: '#FFFFFF',
  borde: '#E1E6EC',
  regla: '#E6EAEF',
  texto: '#24324A',
  texto2: '#5B6573',
  texto3: '#5B6573',
  navy: '#2E5C8A',
  petroleo: '#2F7A86',
  acero: '#6C819B',
  ciruela: '#7B5E8C',
  aceroClaro: '#A9B8CB',
  mejor: '#2F7A86',
  peor: '#A85E24',
  cobre: '#C2773A',
  arena: '#EDC9A6',
  referencia: '#8A8F96',
  panel: '#1B2433',
  total: '#A85E24', // regla de Pablo: el Total siempre en otro color
  // series de las páginas (tipos de crédito, tramos de renta, modalidades)
  aceroMedio: '#8FA3BC',
  arenaClara: '#E7CDB6',
  azulNoche: '#1F3F60',
  azulMedio: '#5B8DB8',
  azulPizarra: '#6F93BA',
  azulClaro: '#9DBBDB',
  petroleoClaro: '#7FB5B9',
  grafito: '#6F7884',
  grisMedio: '#8A93A0',
  oliva: '#6B8E5A',
  lavanda: '#7A5C99',
  indigo: '#5C4B8A',
  granate: '#B04A5A',
  ocre: '#B79C6A',
  arenaPalida: '#E3D3B5',
  trigo: '#CBAE80',
  tierraClara: '#A9875A',
  tierra: '#7A5C3A',
  leyendaInactiva: '#C9D1DB',
};

/* Paleta categórica, en este orden (§5.3): nunca cobre ni arena para una categoría. */
export const PALETA = [COLOR.navy, COLOR.petroleo, COLOR.acero, COLOR.ciruela, COLOR.aceroClaro];

/* Familias tipográficas (las mismas de --fuente y --fuente-mono). */
export const TIPO = {
  texto: "'IBM Plex Sans', 'Segoe UI', system-ui, Arial, sans-serif",
  mono: "'IBM Plex Mono', ui-monospace, Menlo, monospace",
};

/* Fuentes web que se esperan antes del primer dibujo (pagina.js). Las mismas que importa tokens.css. */
export const FUENTES_WEB = ['400 12px "IBM Plex Sans"', '600 12px "IBM Plex Sans"', '400 12px "IBM Plex Mono"', '700 12px "Bricolage Grotesque"'];

/* Trazo discontinuo de las líneas de referencia (meta, mediana, tendencia). */
export const TRAZO_REFERENCIA = [6, 4];
