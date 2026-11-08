/* Cuenta las tarjetas de cada config y las compara con el esqueleto (esqueleto_tarjetas.json):
   criterio «terminado» de cada página. Además revisa la config contra el sitio:
   - falla: tarjeta colocada sin config o declarada sin colocar, estado fuera de ESTADOS_ESQUELETO,
     tarjeta con armar() cuyo componente no existe, selector sin clave, sin opciones o con defecto inválido,
     bloque de riel que no es selector;
   - aviso: tarjeta sin armar() que nombra un componente inexistente (no se dibuja; el esqueleto la nombra
     así) y tarjeta LISTO sin armar() (se muestra «en preparación»).
   Las configs las carga inventario_paginas.mjs. Uso: node herramientas/contar_tarjetas.mjs */
import { inventario } from './inventario_paginas.mjs';

const { paginas, ESPERADO, ESTADOS_ESQUELETO, componentes } = await inventario();
const COMPONENTES = new Set(componentes.map((c) => c.nombre));

let fallos = 0;
const filas = [];
const avisos = [];
for (const p of paginas) {
  const esperado = ESPERADO[p.clave];
  if (p.error) {
    fallos += 1;
    filas.push({ pagina: p.clave, esperado, ok: 'NO', detalle: `no se pudo cargar: ${p.error}` });
    continue;
  }
  const declaradas = Object.keys(p.tarjetas);
  const problemas = [
    ...p.orden.filter((k) => !declaradas.includes(k)).map((k) => `${k} colocada sin config`),
    ...declaradas.filter((k) => !p.orden.includes(k)).map((k) => `${k} sin colocar`),
    ...declaradas.filter((k) => !ESTADOS_ESQUELETO.includes(p.tarjetas[k].estado)).map((k) => `${k} estado inválido`),
    ...declaradas.filter((k) => p.tarjetas[k].armar && !COMPONENTES.has(p.tarjetas[k].componente)).map((k) => `${k} componente «${p.tarjetas[k].componente}» no existe`),
  ];
  for (const s of p.secciones) {
    for (const sel of s.selectores) {
      if (!sel.clave) problemas.push(`sección ${s.numero}: selector sin clave`);
      if (!sel.opciones.length) problemas.push(`sección ${s.numero}: selector «${sel.clave}» sin opciones`);
      if (sel.defecto !== undefined && !sel.valores.includes(sel.defecto)) problemas.push(`sección ${s.numero}: selector «${sel.clave}» con defecto que no es una opción`);
    }
    for (const tipo of s.otrosBloques) problemas.push(`sección ${s.numero}: bloque de riel «${tipo}» (solo hay selectores)`);
  }
  for (const k of declaradas) {
    const t = p.tarjetas[k];
    if (!t.armar && !COMPONENTES.has(t.componente)) avisos.push(`${p.clave} ${k}: componente «${t.componente}» no existe (sin armar, no se dibuja)`);
    if (!t.armar && t.estado === 'LISTO') avisos.push(`${p.clave} ${k}: LISTO sin armar() (se muestra «en preparación»)`);
  }
  const cuenta = Object.fromEntries(ESTADOS_ESQUELETO.map((e) => [e, 0]));
  for (const k of declaradas) cuenta[p.tarjetas[k].estado] += 1;

  const bien = declaradas.length === esperado && !problemas.length;
  if (!bien) fallos += 1;
  filas.push({
    pagina: p.clave,
    esperado,
    declaradas: declaradas.length,
    colocadas: p.orden.length,
    secciones: p.secciones.length,
    ...cuenta,
    ok: bien ? 'sí' : 'NO',
    detalle: problemas.join('; '),
  });
}
for (const clave of Object.keys(ESPERADO).filter((k) => !paginas.some((p) => p.clave === k))) {
  fallos += 1;
  filas.push({ pagina: clave, esperado: ESPERADO[clave], ok: 'NO', detalle: 'en el esqueleto pero no en config.js (PAGINAS)' });
}

console.table(filas.map(({ detalle, ...f }) => f));
for (const f of filas.filter((x) => x.detalle)) console.log(`${f.pagina}: ${f.detalle}`);
if (avisos.length) console.log(`\nAvisos (${avisos.length}):\n  ${avisos.join('\n  ')}`);
const total = filas.reduce((s, f) => s + (f.declaradas || 0), 0);
console.log(`\nTarjetas declaradas en total: ${total}`);
console.log(fallos ? `\nFALLAN ${fallos} página(s)` : '\nTodas las páginas coinciden con el esqueleto');
process.exit(fallos ? 1 : 0);
