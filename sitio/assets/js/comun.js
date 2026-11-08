/* Dominio compartido por las configs de página y el motor: fuentes, grupos, quiebres, particiones,
   el protocolo de armar() y los estados de una tarjeta. Sin DOM: lo importan también las herramientas en
   Node (inventario_paginas.mjs). Los colores y las fuentes tipográficas están en tokens.js. */
import { COLOR, PALETA } from './tokens.js';

/* Fuentes que se citan al pie de las tarjetas. */
export const FUENTE = {
  IFDATA: 'BCB, IF.Data (conglomerado prudencial)',
  SGS: 'BCB, SGS',
  SCR: 'BCB, SCR.data',
  REF: 'BCB, Relatório de Estabilidade Financeira',
  FOCUS: 'BCB, Focus',
  OLINDA: 'BCB, Olinda',
  IBGE: 'IBGE, PNAD Contínua',
  CVM: 'CVM',
  CALC: 'cálculo propio',
};

/* Las fuentes que nombra la cabecera del sitio. */
export const FUENTES_DEL_SITIO = ['IF.Data', 'SGS', 'SCR'];

/* Modelos de negocio (los de pipeline/bancos.py), en el orden del sitio; cada uno lleva fijo el color de la
   paleta en su misma posición (spec web §5) y el panel total, el suyo. */
export const GRUPOS = ['Grandes', 'Digitales', 'Medianos y nicho', 'Pagos', 'Desarrollo'];
export const ROTULO_PANEL = 'Panel';
export const COLOR_GRUPO = { ...Object.fromEntries(GRUPOS.map((g, i) => [g, PALETA[i]])), [ROTULO_PANEL]: COLOR.panel };

/* Nombres del gold para los cortes del panel (bk_grupo, bk_cartera_grupo, bk_cre_calidad). Vienen de
   pipeline/bancos.py (OPTICAS, TODOS, CLAVE_PANEL, PANEL); tests/test_sitio.py comprueba que coincidan. */
export const OPTICA_MODELO = 'Modelo de negocio';   // óptica por modelo de negocio
export const OPTICA_PANEL = 'Total panel';          // óptica del panel completo
export const GRUPO_PANEL = 'Todos los grupos';      // grupo del panel completo en bk_grupo
export const INST_PANEL = 'panel|todos';            // inst_key del panel en bk_cre_calidad
export const instGrupo = (grupo) => `modelo|${grupo}`;  // inst_key de un modelo en bk_cre_calidad
export const UNIVERSO_PANEL = 'Panel';               // universo del panel en bk_manifiesto

/* Quiebre de 2025 (COSIF 2025 y Res. 4.966, esqueleto §0.7): banda gris en las series trimestrales. */
export const BANDA_2025 = [{ desde: '2025-01-01', hasta: '2025-03-31', nombre: 'COSIF 2025 · Res. 4.966' }];

/* Particiones que escribe pipeline/exportar_web_bancos.py (rutas relativas a RUTA_DATOS, sin .json). */
export const tablaMetrica = (metrica) => `metrica/${metrica}/bk_panel`;
export const tablaOptica = (slug) => `optica/${slug}/bk_grupo`;
export const tablaBanco = (slug, tabla) => `banco/${slug}/${tabla}`;

/* ---------- Protocolo de armar(d, contexto) ----------
   contexto = { banco, bancoActivo, grupo, periodoActivo, seleccion } (pagina.js, contextoArmar).
   Devuelve una de dos cosas:
   - sin dibujo: enPreparacion(motivo) o requiereBanco(motivo); el motivo se muestra tal cual;
   - la entrada del componente, que además puede llevar:
       componente  otro componente del registro, según la vista elegida;
       leyenda     leyenda HTML de la tarjeta ([] = la dibuja el gráfico);
       ariaLabel   descripción del gráfico para lectores de pantalla. */
export const enPreparacion = (motivo) => ({ estado: 'en-preparacion', motivo });
export const requiereBanco = (motivo) => ({ estado: 'requiere-banco', motivo });
export const sinDibujo = (r) => r?.estado === 'en-preparacion' || r?.estado === 'requiere-banco';

/* Ciclo de vida de un nodo con datos (data-estado; ver pagina.js) y el motivo de una tarjeta sin armar()
   según su estado del esqueleto. LISTO sin armar() es una incoherencia de la config: contar_tarjetas.mjs
   la avisa. */
export const ESTADOS = ['cargando', 'actualizando', 'lista', 'en-preparacion', 'requiere-banco', 'error'];
export const TRANSITORIOS = ['cargando', 'actualizando'];
export const ESTADOS_ESQUELETO = ['LISTO', 'DERIVAR', 'FALTA', 'REF'];
export const MOTIVOS = {
  LISTO: 'dato en construcción',
  DERIVAR: 'dato en construcción',
  FALTA: 'fuente no incorporada',
  REF: 'disponible con el próximo REF',
};

/* Período activo (AAAAMM): el de la URL (?t=) si es válido; si no, el último corte del universo Panel
   (bk_manifiesto). Es el único criterio de trimestre del sitio. */
export function periodoActivo(trimestreUrl, manifiesto = []) {
  if (trimestreUrl && /^\d{6}$/.test(trimestreUrl)) return trimestreUrl;
  const m = manifiesto.find((x) => x.universo === UNIVERSO_PANEL && x.ultimo_corte);
  if (!m) return null;
  const [anio, mes] = String(m.ultimo_corte).slice(0, 7).split('-');
  return `${anio}${mes}`;
}

/* ---------- Franja de indicadores ----------
   Cada indicador dice de qué tabla y fila sale, la columna de orden y la del cambio trimestral; la unidad
   del cambio la trae la fila (unidad_tt, unidad_d o unidad). El tono (mejora_sube, mejora_baja, neutro)
   de una métrica del panel sale de bk_metrica (signo); `tono` en las opciones lo fija la página. Las series
   del sistema (bk_sistema_q) no están en bk_metrica: llevan su tono escrito. */
export const indicadorSistema = (rotulo, serie, tono) => ({ rotulo, tabla: 'bk_sistema_q', filtro: { serie_id: serie }, orden: 'fecha', delta: 'd_tt', tono });
export const indicadorPanel = (rotulo, metrica, { tono } = {}) => ({ rotulo, tabla: tablaOptica('panel'), filtro: { grupo: GRUPO_PANEL, metrica }, orden: 'periodo', delta: 'valor_tt', metrica, tono });
export const indicadorBanco = (rotulo, metrica, { tono } = {}) => ({ rotulo, tabla: tablaMetrica(metrica), filtro: { metrica }, banco: true, orden: 'periodo', delta: 'valor_tt', metrica, tono });

/* ---------- Árbol del ROE (bk_roe_arbol: linea, nombre, orden, es_resumen) ----------
   Las filas de un banco y período que no son de resumen (es_resumen: ROA, apalancamiento, ROE) son los pasos
   de la cascada en su orden. Los pasos sin valor del banco o sin mediana del grupo quedan fuera y se nombran
   en la nota. */

export function lineasArbolRoe(filas) {
  const lineas = [];
  const omitidas = [];
  for (const r of filas.filter((f) => !f.es_resumen).sort((a, b) => a.orden - b.orden)) {
    if (r.valor == null || r.mediana_grupo == null) omitidas.push(r.nombre);
    else lineas.push({ nombre: r.nombre, banco: r.valor, grupo: r.mediana_grupo });
  }
  return { lineas, omitidas };
}
