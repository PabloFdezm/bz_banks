// Vuelca a JSON la configuración de las once páginas (sitio/assets/js/paginas/b*.js) y config.js.
// Lo usa herramientas/generar_spec.py. Las páginas no importan nada, así que se pueden importar en Node.
import { pathToFileURL, fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const aqui = dirname(fileURLToPath(import.meta.url));
const js = join(aqui, '..', 'sitio', 'assets', 'js');
const { PAGINAS, RUTA_DATOS, MARCA } = await import(pathToFileURL(join(js, 'config.js')));
const salida = { RUTA_DATOS, MARCA, paginas: [] };
for (const p of PAGINAS) {
  const n = p.clave.toLowerCase();
  let cfg;
  try { cfg = (await import(pathToFileURL(join(js, 'paginas', `${n}.js`)))).default; } catch (e) { salida.paginas.push({ ...p, error: String(e) }); continue; }
  const texto = (v) => (typeof v === 'function' ? '(función)' : v);
  salida.paginas.push({
    ...p, archivo: `sitio/assets/js/paginas/${n}.js`, rotulo: cfg.rotulo, usaBanco: cfg.usaBanco, trimestral: cfg.trimestral,
    franja: (cfg.franja || []).map((k) => ({ rotulo: k.rotulo, tabla: texto(k.tabla), banco: !!k.banco, filtro: k.filtro })),
    secciones: (cfg.secciones || []).map((s) => ({
      numero: s.numero, nombre: s.nombre, frecuencia: s.frecuencia, pregunta: s.pregunta, apilada: !!s.apilada,
      selectores: (s.riel || []).filter((b) => b.tipo === 'selector').map((b) => ({ clave: b.clave, rotulo: b.rotulo, defecto: b.defecto, opciones: (b.opciones || []).map((o) => o.nombre) })),
      kpis: (s.riel || []).filter((b) => b.tipo !== 'selector').length,
      filas: (s.filas || []).map((f) => f.map((c) => ({ clave: c.clave, ancho: c.ancho, alto: c.alto }))),
    })),
    tarjetas: Object.fromEntries(Object.entries(cfg.tarjetas || {}).map(([k, t]) => [k, {
      titulo: t.titulo, sub: t.sub, componente: t.componente, datos: t.datos, estado: t.estado, banco: !!t.banco,
      fuente: t.fuente, nota: t.nota, motivo: t.motivo, armar: typeof t.armar === 'function',
      leyenda: (t.leyenda || []).map((l) => l.nombre),
    }])),
  });
}
console.log(JSON.stringify(salida, null, 1));
