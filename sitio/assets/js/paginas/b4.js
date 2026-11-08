/* B4 · Calidad. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec macro).
   Transcrito de ESQUELETO_BANCOS_v0.1.md §B4: títulos, preguntas, anchos, altos, marcas [banco]
   y estados son los del esqueleto.
   armar() solo filtra, ordena, elige columnas y pasa de fracción a % o a pp en la
   presentación. Ningún agregado ni derivación en JS. Lo que exige algo que no está en data/ queda
   «en preparación» con su motivo, y se lista en NO HECHO del resultado.
   Columnas reales usadas:
     B4-01-0           bk_sistema_m: mora90_total, mora90_pf_livre, mora90_pj_livre; p10 y p90 de PF libre
     B4-03-0           bk_cre_calidad: medida_cal NPL, tipo total, ver Institución, inst_key panel y modelo|*
     B4-03-1           bk_panel: costo_riesgo_ttm y cobertura_ecl (fracción, mismo trimestre)
     B4-04-0           bk_exposicion: mora_implicita (null si cobertura < 50 %) y npl_observado
     B4-04-1           bk_exposicion: d_mora_implicita_aa_pp
   Quiebres del esqueleto §0.7 en esta página: 2024-T4 vacío (se conserva el hueco en la escala),
   cambio de cobertura en 2025 (quiebre_2025, marcado con *) y Res. 4.966 / baja a pérdida 2025. */
import { FUENTE, COLOR_GRUPO, GRUPOS, INST_PANEL, ROTULO_PANEL, instGrupo, tablaMetrica, indicadorSistema, indicadorPanel, enPreparacion } from '../comun.js';
import { COLOR } from '../tokens.js';
import { finDeTrimestre, trimestresHasta, trimestresEntre, porFecha } from '../formato.js';

const { IFDATA, SGS, CALC } = FUENTE;
const EJE_PCT = { unidad: 'pct', decimales: 1 };

/* Filas de una serie de bk_sistema_m, ordenadas por fecha. */
const serieSistema = (filas, id) => filas.filter((f) => f.serie_id === id).sort(porFecha);

/* Asterisco en el nombre del banco con cambio de cobertura en 2025 (quiebre_2025). */
const marcaQuiebre = (fila) => (fila && fila.quiebre_2025 ? ' *' : '');

/* B4-01-0 · mora > 90 días del sistema */
function armarMoraSistema(d) {
  const filas = d.bk_sistema_m;
  const puntos = (id, col = 'valor') => serieSistema(filas, id)
    .filter((f) => f[col] != null)
    .map((f) => [f.fecha, f[col]]);
  if (!puntos('mora90_pf_livre').length) return enPreparacion('sin serie de mora mayor a 90 días');
  return {
    series: [
      { nombre: 'Total', puntos: puntos('mora90_total'), color: COLOR.navy, ancho: 2.5 },
      { nombre: 'PF libre', puntos: puntos('mora90_pf_livre'), color: COLOR.petroleo },
      { nombre: 'PJ libre', puntos: puntos('mora90_pj_livre'), color: COLOR.acero },
      { nombre: 'p10 de PF libre', puntos: puntos('mora90_pf_livre', 'p10'), color: COLOR.referencia, discontinua: true, ancho: 1 },
      { nombre: 'p90 de PF libre', puntos: puntos('mora90_pf_livre', 'p90'), color: COLOR.referencia, discontinua: true, ancho: 1 },
    ],
    eje: EJE_PCT,
    ariaLabel: 'Mora mayor a 90 días: total, PF libre y PJ libre, con banda p10 a p90 de PF libre',
  };
}

/* B4-03-0 · calidad por grupo (NPL ≥ 15 días, panel y cinco grupos) */
function armarCalidadGrupos(d) {
  const filas = d.bk_cre_calidad.filter((f) => f.medida_cal === 'NPL' && f.tipo_key === 'total' && f.ver === 'Institución');
  if (!filas.length) return enPreparacion('sin calidad de cartera por grupo');
  const periodos = filas.map((f) => f.periodo).sort();
  const escala = trimestresHasta(periodos[periodos.length - 1], trimestresEntre(periodos[0], periodos[periodos.length - 1]));
  // cada grupo trae también su fila «Panel» (comparador): se toma solo la serie propia del grupo
  const puntos = (clave, serie) => {
    const porP = new Map(filas.filter((f) => f.inst_key === clave && f.serie === serie).map((f) => [f.periodo, f.valor]));
    return escala.map((p) => [finDeTrimestre(p), porP.has(p) ? porP.get(p) : null]); // el hueco (2024-T4) queda como null
  };
  return {
    series: [
      { nombre: 'Panel (todos los bancos)', puntos: puntos(INST_PANEL, ROTULO_PANEL), color: COLOR.referencia, discontinua: true, ancho: 2 },
      ...GRUPOS.map((g) => ({ nombre: g, puntos: puntos(instGrupo(g), g), color: COLOR_GRUPO[g] })),
    ],
    eje: EJE_PCT,
    ariaLabel: 'Mora de 15 días o más sobre cartera, por grupo de bancos y panel, trimestral',
  };
}

/* B4-03-1 · costo del riesgo y cobertura por banco */
function armarCostoRiesgo(d, est) {
  const cr = d[tablaMetrica('costo_riesgo_ttm')].filter((f) => f.valor != null);
  const cob = d[tablaMetrica('cobertura_ecl')].filter((f) => f.valor != null);
  const t = est.periodoActivo;
  if (!cr.some((f) => f.periodo === t)) return enPreparacion('sin costo del riesgo publicado');
  const valorCr = new Map(cr.filter((f) => f.periodo === t).map((f) => [f.cod_inst, f.valor]));
  const valorCob = new Map(cob.filter((f) => f.periodo === t).map((f) => [f.cod_inst, f.valor]));
  const items = d.bk_banco.map((b) => ({
    b,
    cr: valorCr.has(b.cod_inst) ? valorCr.get(b.cod_inst) : null,
    cob: valorCob.has(b.cod_inst) ? valorCob.get(b.cod_inst) : null,
  }));
  items.sort((x, y) => {
    if (x.cr == null || y.cr == null) {
      return (x.cr == null) - (y.cr == null) || x.b.nombre_corto.localeCompare(y.b.nombre_corto, 'es');
    }
    return y.cr - x.cr;
  });
  // 34 bancos con dos barras no se leen; con banco activo se muestran los de su grupo,
  // sin banco los 15 de mayor costo del riesgo. Solo filtra, no calcula.
  const activo = est.bancoActivo;
  const visibles = activo
    ? items.filter((x) => x.b.modelo === activo.modelo)
    : items.filter((x) => x.cr != null).slice(0, 15);
  return {
    filas: visibles.map(({ b, cr: v, cob: c }) => ({
      nombre: `${b.nombre_corto}${v == null ? ' (sin dato)' : ''}`,
      slug: b.slug,
      valores: [v, c],
    })),
    series: [
      { nombre: 'Costo del riesgo (12 meses)', color: COLOR.navy },
      { nombre: 'Cobertura de pérdida esperada', color: COLOR.acero },
    ],
    formato: 'pct',
    activo: est.banco || null,
    ariaLabel: 'Costo del riesgo de 12 meses y cobertura de pérdida esperada por banco, en porcentaje',
  };
}

/* B4-04-0 · mora implícita del mix vs. NPL observado */
function armarMixVsNpl(d, est) {
  const exp = d.bk_exposicion;
  const t = est.periodoActivo;
  const porCod = new Map(d.bk_banco.map((b) => [b.cod_inst, b]));
  const puntos = exp
    .filter((f) => f.periodo === t && f.mora_implicita != null && f.npl_observado != null
      && f.cobertura >= 0.5 && porCod.has(f.cod_inst))
    .map((f) => {
      const b = porCod.get(f.cod_inst);
      return {
        x: f.mora_implicita,
        y: f.npl_observado,
        nombre: `${b.nombre_corto}${marcaQuiebre(f)}`,
        banco: b.slug,
        destacado: b.slug === est.banco,
      };
    });
  if (!puntos.length) return enPreparacion('sin bancos con cobertura de al menos 50 %');
  return {
    puntos,
    diagonal: true,
    ejeX: { titulo: 'Mora implícita del mix', formato: 'pct' },
    ejeY: { titulo: 'NPL observado (≥ 15 días)', formato: 'pct' },
    cuadrantes: { tl: 'Peor que su mix', br: 'Mejor que su mix' },
    ariaLabel: 'Dispersión: mora implícita del mix contra NPL observado por banco, con diagonal',
  };
}

/* B4-04-1 · cambio de la mora implícita en 12 meses */
function armarCambioMoraImplicita(d, est) {
  const exp = d.bk_exposicion;
  const t = est.periodoActivo;
  const porCod = new Map(d.bk_banco.map((b) => [b.cod_inst, b]));
  const items = exp
    .filter((f) => f.periodo === t && f.d_mora_implicita_aa_pp != null && porCod.has(f.cod_inst))
    .map((f) => ({ nombre: `${porCod.get(f.cod_inst).nombre_corto}${marcaQuiebre(f)}`, v: f.d_mora_implicita_aa_pp }))
    .sort((x, y) => y.v - x.v);
  if (!items.length) return enPreparacion('sin cambio de mora implícita en el trimestre');
  return {
    filas: items.map((x) => ({ nombre: x.nombre })),
    series: [{ nombre: 'Cambio a 12 meses de la mora implícita (pp)', valores: items.map((x) => x.v), color: COLOR.navy }],
    apilar: false,
    mostrarValores: true,
    ariaLabel: 'Cambio a 12 meses de la mora implícita por banco, en puntos porcentuales',
  };
}

export default {
  rotulo: '4 · CALIDAD',
  usaBanco: true,

  franja: [
    indicadorSistema('Mora > 90 días · Sistema', 'mora90_total', 'mejora_baja'),
    indicadorSistema('Mora > 90 · PF libre', 'mora90_pf_livre', 'mejora_baja'),
    indicadorSistema('Mora > 90 · PJ libre', 'mora90_pj_livre', 'mejora_baja'),
    indicadorPanel('NPL ≥ 15 días · Panel', 'npl15_total'),
    indicadorPanel('Costo del riesgo · Panel', 'costo_riesgo_ttm'),
  ],

  secciones: [
    {
      numero: '01',
      nombre: 'Sistema',
      frecuencia: 'Mensual · Sistema BCB',
      pregunta: 'Mora mayor a 90 días: personas, empresas y total.',
      filas: [
        [{ clave: 'B4-01-0', ancho: 9, alto: 320 }],
      ],
    },
    {
      numero: '02',
      nombre: 'Por grupo y por banco',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'NPL por grupo y costo del riesgo con cobertura en el grupo del banco activo.',
      filas: [
        [{ clave: 'B4-03-0', ancho: 5, alto: 380 }, { clave: 'B4-03-1', ancho: 4, alto: 380 }],
      ],
    },
    {
      numero: '03',
      nombre: 'Exposición',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Cuánto NPL predice el mix de cartera de cada banco y cuánto tiene.',
      filas: [
        [{ clave: 'B4-04-0', ancho: 5, alto: 640 }, { clave: 'B4-04-1', ancho: 4, alto: 640 }],
      ],
    },
  ],


  tarjetas: {
    'B4-01-0': {
      plana: true,
      titulo: 'Mora > 90 días: PF libre, PJ libre, total',
      sub: 'Sistema BCB · mora > 90 días · total, PF libre y PJ libre · banda p10–p90 de PF libre, 10 años',
      fuente: SGS,
      componente: 'linea',
      datos: ['bk_sistema_m'],
      leyenda: [
        { nombre: 'Total', color: COLOR.navy },
        { nombre: 'PF libre', color: COLOR.petroleo },
        { nombre: 'PJ libre', color: COLOR.acero },
        { nombre: 'Banda p10–p90 de PF libre', color: COLOR.referencia, discontinua: true },
      ],
      nota: 'Desde 2025, con la Res. 4.966 y el cambio de política de baja a pérdida, la mora > 90 días puede no ser comparable con años anteriores.',
      armar: armarMoraSistema,
      estado: 'LISTO',
    },
    'B4-03-0': {
      plana: true,
      titulo: 'Calidad por grupo',
      sub: 'Panel IF.Data · NPL ≥ 15 días sobre cartera · panel y cinco grupos de modelo de negocio · trimestral',
      fuente: IFDATA,
      componente: 'linea',
      datos: ['bk_cre_calidad'],
      leyenda: [
        { nombre: 'Panel (todos los bancos)', color: COLOR.referencia, discontinua: true },
        ...GRUPOS.map((g) => ({ nombre: g, color: COLOR_GRUPO[g] })),
      ],
      nota: 'Hasta 2024-T3 la medida es la escala E–H; desde 2025-T1 (Res. 4.966) son los activos problemáticos. La línea cambia de definición en 2025-T1. 2024-T4 sin dato en todo el panel.',
      armar: armarCalidadGrupos,
      estado: 'LISTO',
    },
    'B4-03-1': {
      plana: true,
      titulo: 'Costo del riesgo TTM y cobertura, por banco',
      sub: 'Panel IF.Data · costo del riesgo (12 meses) y cobertura de pérdida esperada, por banco',
      fuente: IFDATA,
      componente: 'barras_h_doble',
      datos: [tablaMetrica('costo_riesgo_ttm'), tablaMetrica('cobertura_ecl'), 'bk_banco'], // no los 27 MB de bk_panel
      leyenda: [
        { nombre: 'Costo del riesgo (12 meses)', color: COLOR.navy },
        { nombre: 'Cobertura de pérdida esperada', color: COLOR.acero },
      ],
      nota: 'Con banco activo: los bancos de su grupo, el activo en negrita. Sin banco: los 15 de mayor costo del riesgo. Último trimestre con dato (2T26): 32 de 34 bancos; sin dato BRB y Cielo.',
      banco: true,
      armar: armarCostoRiesgo,
      estado: 'LISTO',
    },
    'B4-04-0': {
      plana: true,
      titulo: 'Mora implícita del mix vs. NPL observado',
      sub: 'Panel IF.Data · NPL observado contra mora implícita del mix · con diagonal',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'dispersion',
      datos: ['bk_exposicion', 'bk_banco'],
      nota: 'Por encima de la diagonal, el banco tiene más NPL del que su mix predice; por debajo, menos. Solo bancos con cobertura de al menos 50 % de la cartera; los demás no tienen punto.',
      banco: true,
      armar: armarMixVsNpl,
      estado: 'DERIVAR',
    },
    'B4-04-1': {
      plana: true,
      titulo: 'Cambio de la mora implícita en 12m, por banco',
      sub: 'Panel IF.Data · cambio de la mora implícita en 12 meses · por banco',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'barras_h',
      datos: ['bk_exposicion', 'bk_banco'],
      nota: '* Cambio de cobertura en 2025. Mora implícita solo con cobertura de al menos 50 %: BNDES, Banco da Amazônia y Cielo sin dato.',
      armar: armarCambioMoraImplicita,
      estado: 'DERIVAR',
    },
  },
};
