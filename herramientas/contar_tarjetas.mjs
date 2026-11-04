/* Cuenta las tarjetas de cada config y las compara con el esqueleto
   (ESQUELETO_BANCOS_v0.1.md). Sirve para el criterio «terminado» de la F0 del encargo 62:
   B0 7, B1 11, B2 11, B3 8, B4 10, B5 6, B6 9, B7 6, B8 12, B9 1, B10 0.
   Lee los archivos como texto y reemplaza «export default» por «return» para poder evaluarlos
   sin un paso de build ni un package.json (los configs no importan nada).
   Uso: node sitio_bancos/contar_tarjetas.mjs */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const aqui = dirname(fileURLToPath(import.meta.url));
const PAGINAS = join(aqui, '..', 'sitio', 'assets', 'js', 'paginas');

const ESPERADO = { b0: 7, b1: 11, b2: 11, b3: 8, b4: 5, b5: 6, b6: 5, b7: 6, b8: 8, b9: 1, b10: 0 };
const ESTADOS = ['LISTO', 'DERIVAR', 'FALTA', 'REF'];

function leer(nombre) {
  const src = readFileSync(join(PAGINAS, `${nombre}.js`), 'utf8').replace(/export default/, 'return');
  return new Function(src)();
}

let fallos = 0;
const filas = [];
for (const [clave, esperado] of Object.entries(ESPERADO)) {
  const cfg = leer(clave);
  const declaradas = Object.keys(cfg.tarjetas || {});
  const colocadas = (cfg.secciones || []).flatMap((s) => (s.filas || []).flat().map((c) => c.clave));
  const sinConfig = colocadas.filter((k) => !declaradas.includes(k));
  const sinColocar = declaradas.filter((k) => !colocadas.includes(k));
  const malEstado = declaradas.filter((k) => !ESTADOS.includes(cfg.tarjetas[k].estado));
  const cuenta = { LISTO: 0, DERIVAR: 0, FALTA: 0, REF: 0 };
  for (const k of declaradas) cuenta[cfg.tarjetas[k].estado] += 1;

  const bien = declaradas.length === esperado && !sinConfig.length && !sinColocar.length && !malEstado.length;
  if (!bien) fallos += 1;
  filas.push({
    pagina: cfg.clave,
    esperado,
    declaradas: declaradas.length,
    colocadas: colocadas.length,
    secciones: (cfg.secciones || []).length,
    ...cuenta,
    ok: bien ? 'sí' : 'NO',
    detalle: [...sinConfig.map((k) => `${k} colocada sin config`), ...sinColocar.map((k) => `${k} sin colocar`), ...malEstado.map((k) => `${k} estado inválido`)].join('; '),
  });
}

console.table(filas.map(({ detalle, ...f }) => f));
for (const f of filas.filter((x) => x.detalle)) console.log(`${f.pagina}: ${f.detalle}`);
const total = filas.reduce((s, f) => s + f.declaradas, 0);
console.log(`\nTarjetas declaradas en total: ${total}`);
console.log(fallos ? `\nFALLAN ${fallos} página(s)` : '\nTodas las páginas coinciden con el esqueleto');
process.exit(fallos ? 1 : 0);
