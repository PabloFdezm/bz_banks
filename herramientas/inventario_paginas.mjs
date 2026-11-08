// El único cargador de las configs del sitio fuera del navegador. Importa config.js (PAGINAS), cada
// paginas/<clave>.js y el registro de componentes con import() real: todos esos módulos son sin DOM al
// importarse. Lo usan contar_tarjetas.mjs (import), verificar_f1.py y generar_spec.py (JSON por stdout).
// Uso: node herramientas/inventario_paginas.mjs [--sin-dom]
//   --sin-dom: falla si algún módulo del sitio toca document, window o un global del navegador al importarse.
import { pathToFileURL, fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import { readFileSync } from 'node:fs';

const aqui = dirname(fileURLToPath(import.meta.url));
const js = join(aqui, '..', 'sitio', 'assets', 'js');
const modulo = (...partes) => import(pathToFileURL(join(js, ...partes)));

/* Tarjetas por página según el esqueleto (ESQUELETO_BANCOS_v0.1.md y sus enmiendas): el criterio
   «terminado» de contar_tarjetas.mjs y verificar_f1.py. */
export const ESPERADO = JSON.parse(readFileSync(join(aqui, 'esqueleto_tarjetas.json'), 'utf8'));

export async function inventario() {
  const { PAGINAS, RUTA_DATOS, MARCA, moduloConfig } = await modulo('config.js');
  const { COMPONENTES } = await modulo('charts_bancos.js');
  const { COLOR } = await modulo('tokens.js');
  const comun = await modulo('comun.js');
  const { ESTADOS, TRANSITORIOS, ESTADOS_ESQUELETO } = comun;
  // Nombres del gold que el sitio repite: tests/test_sitio.py los compara con pipeline/bancos.py.
  const GOLD = {
    GRUPOS: comun.GRUPOS, ROTULO_PANEL: comun.ROTULO_PANEL, OPTICA_MODELO: comun.OPTICA_MODELO,
    OPTICA_PANEL: comun.OPTICA_PANEL, GRUPO_PANEL: comun.GRUPO_PANEL, INST_PANEL: comun.INST_PANEL,
    INST_GRUPO: Object.fromEntries(comun.GRUPOS.map((g) => [g, comun.instGrupo(g)])), UNIVERSO_PANEL: comun.UNIVERSO_PANEL,
  };
  const { NOMBRES_UNIDAD } = await modulo('formato.js');
  // datos puede depender del contexto (la partición del banco activo): se muestra con un banco de ejemplo
  const tablas = (datos) => (typeof datos === 'function' ? datos({ banco: '<banco>' }) : datos);
  const paginas = [];
  for (const p of PAGINAS) {
    let cfg;
    try {
      cfg = (await modulo(moduloConfig(p.clave))).default;
    } catch (e) {
      paginas.push({ ...p, error: String(e) });
      continue;
    }
    const secciones = cfg.secciones || [];
    paginas.push({
      ...p, archivo: `sitio/assets/js/paginas/${p.clave.toLowerCase()}.js`, rotulo: cfg.rotulo, usaBanco: cfg.usaBanco,
      titularPorBanco: !!cfg.titularPorBanco,
      franja: (cfg.franja || []).map((k) => ({ rotulo: k.rotulo, tabla: k.tabla, banco: !!k.banco, filtro: k.filtro })),
      secciones: secciones.map((s) => ({
        numero: s.numero, nombre: s.nombre, frecuencia: s.frecuencia, pregunta: s.pregunta,
        selectores: (s.riel || []).filter((b) => b.tipo === 'selector').map((b) => ({ clave: b.clave, rotulo: b.rotulo, defecto: b.defecto, opciones: (b.opciones || []).map((o) => o.nombre), valores: (b.opciones || []).map((o) => o.valor) })),
        otrosBloques: (s.riel || []).filter((b) => b.tipo !== 'selector').map((b) => b.tipo),
        filas: (s.filas || []).map((f) => f.map((c) => ({ clave: c.clave, ancho: c.ancho, alto: c.alto }))),
      })),
      // tarjetas en el orden en que se colocan en las secciones
      orden: secciones.flatMap((s) => (s.filas || []).flat().map((c) => c.clave)),
      tarjetas: Object.fromEntries(Object.entries(cfg.tarjetas || {}).map(([k, t]) => [k, {
        titulo: t.titulo, sub: t.sub, componente: t.componente, datos: tablas(t.datos), estado: t.estado, banco: !!t.banco,
        fuente: t.fuente, nota: t.nota, armar: typeof t.armar === 'function',
        leyenda: (t.leyenda || []).map((l) => l.nombre),
      }])),
    });
  }
  const componentes = Object.entries(COMPONENTES).map(([nombre, c]) => ({ nombre, entrada: c.entrada, descripcion: c.descripcion }));
  return { RUTA_DATOS, MARCA, COLOR, ESPERADO, ESTADOS, TRANSITORIOS, ESTADOS_ESQUELETO, NOMBRES_UNIDAD, GOLD, paginas, componentes };
}

/* Los módulos del sitio que importan configs y herramientas no deben tocar el navegador al importarse:
   con --sin-dom, document, window, location, history, navigator y localStorage quedan como trampas. */
function trampasDelNavegador() {
  for (const g of ['document', 'window', 'location', 'history', 'navigator', 'localStorage', 'sessionStorage']) {
    Object.defineProperty(globalThis, g, { configurable: true, get() { throw new Error(`un módulo del sitio usa «${g}» al importarse`); } });
  }
}

if (process.argv[1] && resolve(process.argv[1]).toLowerCase() === fileURLToPath(import.meta.url).toLowerCase()) {
  if (process.argv.includes('--sin-dom')) trampasDelNavegador();
  const inv = await inventario();
  const errores = inv.paginas.filter((p) => p.error);
  if (process.argv.includes('--sin-dom')) {
    for (const p of errores) console.error(`${p.clave}: ${p.error}`);
    console.log(errores.length ? `FALLA: ${errores.length} config(s) no cargan sin navegador` : `OK: ${inv.paginas.length} configs y sus módulos cargan sin navegador`);
    process.exit(errores.length ? 1 : 0);
  }
  console.log(JSON.stringify(inv, null, 1));
}
