/* La URL como fuente de verdad del estado (spec §3). Sin document: solo location e history al llamar.
     ?banco=<slug>&grupo=<grupo>&t=<AAAAMM>[&s<NN>.<clave>=<valor>…][#sNN | #presentar=sNN]
   Los s<NN>.<clave> son los selectores de sección de ESTA página (solo si difieren del defecto); no viajan
   en los enlaces a otras páginas, donde el mismo número de sección es otra cosa (busquedaCompartida). */

export const parametros = () => new URLSearchParams(location.search);

/* Reemplaza la query (sin agregar historial) y conserva el hash. */
export function reemplazarUrl(p) {
  const q = p.toString();
  history.replaceState(history.state, '', `${location.pathname}${q ? `?${q}` : ''}${location.hash}`);
}

/* Reemplaza el hash y conserva la query. */
export function fijarHash(h) {
  history.replaceState(history.state, '', `${location.pathname}${location.search}${h}`);
}

const ES_SELECCION = /^s\d+\./;

export function leerSeleccion(numero, clave) {
  return parametros().get(`s${numero}.${clave}`);
}

/* No avisa a nadie: un selector solo redibuja su sección (pagina.js, elegirSeleccion). */
export function fijarSeleccion(numero, clave, valor, defecto) {
  const p = parametros();
  const k = `s${numero}.${clave}`;
  if (valor == null || valor === defecto) p.delete(k);
  else p.set(k, String(valor));
  reemplazarUrl(p);
}

/* La query que se lleva a OTRA página: la de esta sin sus selectores de sección. */
export function busquedaCompartida() {
  const p = parametros();
  for (const k of [...p.keys()]) if (ES_SELECCION.test(k)) p.delete(k);
  const q = p.toString();
  return q ? `?${q}` : '';
}
