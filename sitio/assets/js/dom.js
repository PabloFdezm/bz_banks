/* Creación de nodos: el único ayudante de DOM del sitio. */
export function el(tag, clase, texto) {
  const n = document.createElement(tag);
  if (clase) n.className = clase;
  if (texto != null) n.textContent = texto;
  return n;
}

const NS = 'http://www.w3.org/2000/svg';
export function svgEl(tag, atributos = {}) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(atributos)) n.setAttribute(k, v);
  return n;
}
