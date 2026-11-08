/* Configuración única del sitio. Sin DOM: la importan también las herramientas en Node
   (herramientas/inventario_paginas.mjs). Cambiar RUTA_DATOS si el sitio se sirve desde otra raíz. */
export const RUTA_DATOS = '/data/';

export const MARCA = 'BANCOS BRASIL';
export const NOMBRE_SITIO = 'Bancos Brasil';

/* Identidad de cada página: el único lugar donde viven clave, ruta y nombre. La config de la página
   está en paginas/<clave en minúsculas>.js; todas las carpetas sirven el mismo index.html y pagina.js
   elige la config por la ruta. oculta: true saca la página del menú (se abre por URL). El orden es el
   del menú y el del recorrido en modo presentación. */
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

export const PAGINAS_VISIBLES = PAGINAS.filter((p) => !p.oculta);

/* Enlace a una página: la portada vive en la raíz (ruta ''). */
export const enlace = (ruta) => (ruta ? `/${ruta}/` : '/');

/* Módulo de la config de una página, relativo a assets/js/. */
export const moduloConfig = (clave) => `./paginas/${clave.toLowerCase()}.js`;

/* Página de una ruta del navegador («/credito/», «/credito/index.html», «/»); null si no existe. */
export function paginaDeRuta(pathname) {
  const ruta = pathname.replace(/\/index\.html$/, '/').replace(/^\/+|\/+$/g, '');
  return PAGINAS.find((p) => p.ruta === ruta) || null;
}
