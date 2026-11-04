/* B4 · Calidad. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec macro).
   Transcrito de ESQUELETO_BANCOS_v0.1.md §B4: títulos, preguntas, anchos, altos, marcas [banco]
   y estados son los del esqueleto.
   armar (encargos 74 y 77c): solo filtra, ordena, elige columnas y pasa de fracción a % o a pp en la
   presentación. Ningún agregado ni derivación en JS. Lo que exige algo que no está en data/ queda
   «en preparación» con su motivo, y se lista en NO HECHO del resultado.
   Columnas reales usadas:
     B4-01-0           bk_sistema_m: mora90_total, mora90_pf_livre, mora90_pj_livre; p10 y p90 de PF libre
     B4-02-0           bk_sistema_m: mora90_* por modalidad PF (sin atrasos tempranos por modalidad)
     B4-03-0           bk_cre_calidad: medida_cal NPL, tipo total, ver Institución, inst_key panel y modelo|*
     B4-03-1           bk_panel: costo_riesgo_ttm y cobertura_ecl (fracción, mismo trimestre)
     B4-03-2           bk_exposicion: npl_observado (igual a Σ vencido ≥ 15 días / Σ saldo de bk_cartera)
     B4-04-0           bk_exposicion: mora_implicita (null si cobertura < 50 %) y npl_observado
     B4-04-1           bk_exposicion: d_mora_implicita_aa_pp
     B4-05-0           bk_scr: corte porte_pj, tasa_ap por porte_es (Sin dato fuera)
   Quiebres del esqueleto §0.7 en esta página: 2024-T4 vacío (se conserva el hueco en la escala),
   cambio de cobertura en 2025 (quiebre_2025, marcado con *) y Res. 4.966 / baja a pérdida 2025. */
/* Sin imports: contar_tarjetas.mjs lee este archivo como texto. Colores copiados de tokens.css
   y orden de grupos copiado de estado.js (GRUPOS). */
const C = { navy: '#2E5C8A', petroleo: '#2F7A86', acero: '#6C819B', ciruela: '#7B5E8C', aceroClaro: '#A9B8CB', referencia: '#8A8F96' };
const GRUPOS = ['Grandes', 'Digitales', 'Medianos y nicho', 'Pagos', 'Desarrollo'];
const pctEs = (v) => `${(v * 100).toFixed(1).replace('.', ',')} %`;

const IFDATA = 'BCB, IF.Data (conglomerado prudencial)';
const SGS = 'BCB, SGS';
const SCRDATA = 'BCB, SCR.data';
const CALC = 'cálculo propio';

const FIN_DE_TRIMESTRE = { '03': '31', '06': '30', '09': '30', '12': '31' };

/* AAAAMM de fin de trimestre → fecha ISO de cierre. */
const fechaDeTrimestre = (p) => `${p.slice(0, 4)}-${p.slice(4, 6)}-${FIN_DE_TRIMESTRE[p.slice(4, 6)]}`;

/* Los n trimestres calendario que terminan en `ultimo` (AAAAMM), del más antiguo al más reciente.
   Un trimestre sin datos (2024-T4) se conserva como hueco y no desaparece de la escala. */
function trimestresHasta(ultimo, n) {
  let anio = Number(ultimo.slice(0, 4));
  let mes = Number(ultimo.slice(4, 6));
  const salida = [];
  for (let i = 0; i < n; i += 1) {
    salida.unshift(`${anio}${String(mes).padStart(2, '0')}`);
    mes -= 3;
    if (mes <= 0) { mes += 12; anio -= 1; }
  }
  return salida;
}

/* Trimestre activo: el de la URL si tiene datos; si no, el último con datos. */
function trimestreActivo(est, periodos) {
  if (est && est.trimestre && periodos.has(est.trimestre)) return est.trimestre;
  const lista = [...periodos].sort();
  return lista.length ? lista[lista.length - 1] : null;
}

/* Filas de una serie de bk_sistema_m, ordenadas por fecha. */
function serieSistema(filas, id) {
  return filas
    .filter((f) => f.serie_id === id)
    .sort((a, b) => (a.fecha < b.fecha ? -1 : a.fecha > b.fecha ? 1 : 0));
}

/* Bancos en el orden de los grupos del sitio y, dentro de cada grupo, alfabético. */
function bancosOrdenados(bancos) {
  const rango = (m) => (GRUPOS.indexOf(m) < 0 ? GRUPOS.length : GRUPOS.indexOf(m));
  return [...bancos].sort((a, b) => rango(a.modelo) - rango(b.modelo)
    || a.nombre_corto.localeCompare(b.nombre_corto, 'es'));
}

/* Asterisco en el nombre del banco con cambio de cobertura en 2025 (quiebre_2025). */
const marcaQuiebre = (fila) => (fila && fila.quiebre_2025 ? ' *' : '');

const MODALIDADES_PF = [
  ['mora90_cartao_total', 'Tarjeta, total'],
  ['mora90_rotativo', 'Tarjeta rotativo'],
  ['mora90_parcelado', 'Tarjeta parcelado'],
  ['mora90_personal', 'Personal'],
  ['mora90_consignado_privado', 'Consignado privado'],
  ['mora90_consignado_publico', 'Consignado público'],
  ['mora90_consignado_inss', 'Consignado INSS'],
  ['mora90_vehiculos', 'Vehículos'],
  ['mora90_inmobiliario_total', 'Inmobiliario, total'],
];

/* Grupos de bk_cre_calidad (inst_key = modelo|<grupo>), en el orden de GRUPOS. */
const COLOR_GRUPO = [C.navy, C.petroleo, C.acero, C.ciruela, C.aceroClaro];

/* ---------- armar: B4-01-0 · mora > 90 días del sistema ---------- */
function armarMoraSistema(d) {
  const filas = d.bk_sistema_m;
  const puntos = (id, col = 'valor') => serieSistema(filas, id)
    .filter((f) => f[col] != null)
    .map((f) => [f.fecha, f[col]]);
  if (!puntos('mora90_pf_livre').length) return { enPreparacion: 'sin serie de mora mayor a 90 días' };
  return {
    series: [
      { nombre: 'Total', puntos: puntos('mora90_total'), color: C.navy, ancho: 2.5 },
      { nombre: 'PF libre', puntos: puntos('mora90_pf_livre'), color: C.petroleo },
      { nombre: 'PJ libre', puntos: puntos('mora90_pj_livre'), color: C.acero },
      { nombre: 'p10 de PF libre', puntos: puntos('mora90_pf_livre', 'p10'), color: C.referencia, discontinua: true, ancho: 1 },
      { nombre: 'p90 de PF libre', puntos: puntos('mora90_pf_livre', 'p90'), color: C.referencia, discontinua: true, ancho: 1 },
    ],
    formatear: (v) => pctEs(v),
    ariaLabel: 'Mora mayor a 90 días: total, PF libre y PJ libre, con banda p10 a p90 de PF libre',
  };
}

/* ---------- armar: B4-02-0 · mora por modalidad PF ---------- */
function armarModalidades(d) {
  const filas = d.bk_sistema_m;
  const paneles = MODALIDADES_PF.map(([id, nombre]) => ({
    nombre,
    puntos: serieSistema(filas, id).filter((f) => f.valor != null).map((f) => [f.fecha, f.valor]),
  }));
  if (paneles.every((p) => !p.puntos.length)) return { enPreparacion: 'sin mora por modalidad' };
  return {
    paneles,
    columnas: 3,
    formato: 'pct',
    ariaLabel: 'Mora mayor a 90 días por modalidad de crédito a personas, con escala común',
  };
}

/* ---------- armar: B4-03-0 · calidad por grupo (NPL ≥ 15 días, panel y cinco grupos) ---------- */
function armarCalidadGrupos(d) {
  const filas = d.bk_cre_calidad.filter((f) => f.medida_cal === 'NPL' && f.tipo_key === 'total' && f.ver === 'Institución');
  if (!filas.length) return { enPreparacion: 'sin calidad de cartera por grupo' };
  const periodos = filas.map((f) => f.periodo).sort();
  const escala = trimestresHasta(periodos[periodos.length - 1], trimestresEntre(periodos[0], periodos[periodos.length - 1]));
  // cada grupo trae también su fila «Panel» (comparador): se toma solo la serie propia del grupo
  const puntos = (clave, serie) => {
    const porP = new Map(filas.filter((f) => f.inst_key === clave && f.serie === serie).map((f) => [f.periodo, f.valor]));
    return escala.map((p) => [fechaDeTrimestre(p), porP.has(p) ? porP.get(p) : null]); // el hueco (2024-T4) queda como null
  };
  return {
    series: [
      { nombre: 'Panel (todos los bancos)', puntos: puntos('panel|todos', 'Panel'), color: C.referencia, discontinua: true, ancho: 2 },
      ...GRUPOS.map((g, i) => ({ nombre: g, puntos: puntos(`modelo|${g}`, g), color: COLOR_GRUPO[i] })),
    ],
    formatear: (v) => pctEs(v),
    ariaLabel: 'Mora de 15 días o más sobre cartera, por grupo de bancos y panel, trimestral',
  };
}

/* Número de trimestres de `desde` a `hasta` (AAAAMM), ambos incluidos. */
function trimestresEntre(desde, hasta) {
  const a = Number(desde.slice(0, 4)) * 4 + (Number(desde.slice(4, 6)) - 1) / 3;
  const b = Number(hasta.slice(0, 4)) * 4 + (Number(hasta.slice(4, 6)) - 1) / 3;
  return b - a + 1;
}

/* ---------- armar: B4-03-1 · costo del riesgo y cobertura por banco ---------- */
function armarCostoRiesgo(d, est) {
  const panel = d.bk_panel || [...(d['metrica/costo_riesgo_ttm/bk_panel'] || []), ...(d['metrica/cobertura_ecl/bk_panel'] || [])];
  const cr = panel.filter((f) => f.metrica === 'costo_riesgo_ttm' && f.valor != null);
  const cob = panel.filter((f) => f.metrica === 'cobertura_ecl' && f.valor != null);
  const t = trimestreActivo(est, new Set(cr.map((f) => f.periodo)));
  if (!t) return { enPreparacion: 'sin costo del riesgo publicado' };
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
  // arquitecto: 34 bancos con dos barras no se leen; con banco activo se muestran los de su grupo,
  // sin banco los 15 de mayor costo del riesgo. Solo filtra, no calcula.
  const activo = d.bk_banco.find((b) => b.slug === est.banco);
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
      { nombre: 'Costo del riesgo (12 meses)', color: C.navy },
      { nombre: 'Cobertura de pérdida esperada', color: C.acero },
    ],
    formato: 'pct',
    activo: est.banco || null,
    ariaLabel: 'Costo del riesgo de 12 meses y cobertura de pérdida esperada por banco, en porcentaje',
  };
}

/* ---------- armar: B4-03-2 · NPL por banco, ocho trimestres ---------- */
function armarNplBancos(d, est) {
  const exp = d.bk_exposicion;
  const t = trimestreActivo(est, new Set(exp.map((f) => f.periodo)));
  if (!t) return { enPreparacion: 'sin datos de NPL por banco' };
  const trimestres = trimestresHasta(t, 8);
  const porBanco = new Map();
  for (const f of exp) {
    if (!porBanco.has(f.cod_inst)) porBanco.set(f.cod_inst, new Map());
    porBanco.get(f.cod_inst).set(f.periodo, f);
  }
  const paneles = bancosOrdenados(d.bk_banco).map((b) => {
    const porT = porBanco.get(b.cod_inst) || new Map();
    return {
      nombre: `${b.nombre_corto}${marcaQuiebre(porT.get(t))}`,
      banco: b.slug,
      destacado: b.slug === est.banco,
      puntos: trimestres.map((p) => {
        const f = porT.get(p);
        return [fechaDeTrimestre(p), f && f.npl_observado != null ? f.npl_observado : null];
      }),
    };
  });
  if (!paneles.some((p) => p.puntos.some(([, v]) => v != null))) return { enPreparacion: 'sin NPL por banco' };
  return {
    paneles,
    columnas: 6,
    formato: 'pct',
    ariaLabel: 'Mora de 15 días o más sobre saldo, ocho trimestres, por banco, con escala común',
  };
}

/* ---------- armar: B4-04-0 · mora implícita del mix vs. NPL observado ---------- */
function armarMixVsNpl(d, est) {
  const exp = d.bk_exposicion;
  const t = trimestreActivo(est, new Set(exp.map((f) => f.periodo)));
  if (!t) return { enPreparacion: 'sin datos de mora implícita' };
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
  if (!puntos.length) return { enPreparacion: 'sin bancos con cobertura de al menos 50 %' };
  return {
    puntos,
    diagonal: true,
    ejeX: { titulo: 'Mora implícita del mix', formato: 'pct' },
    ejeY: { titulo: 'NPL observado (≥ 15 días)', formato: 'pct' },
    cuadrantes: { tl: 'Peor que su mix', br: 'Mejor que su mix' },
    ariaLabel: 'Dispersión: mora implícita del mix contra NPL observado por banco, con diagonal',
  };
}

/* ---------- armar: B4-04-1 · cambio de la mora implícita en 12 meses ---------- */
function armarCambioMoraImplicita(d, est) {
  const exp = d.bk_exposicion;
  const t = trimestreActivo(est, new Set(exp.map((f) => f.periodo)));
  const porCod = new Map(d.bk_banco.map((b) => [b.cod_inst, b]));
  const items = exp
    .filter((f) => f.periodo === t && f.d_mora_implicita_aa_pp != null && porCod.has(f.cod_inst))
    .map((f) => ({ nombre: `${porCod.get(f.cod_inst).nombre_corto}${marcaQuiebre(f)}`, v: f.d_mora_implicita_aa_pp }))
    .sort((x, y) => y.v - x.v);
  if (!items.length) return { enPreparacion: 'sin cambio de mora implícita en el trimestre' };
  return {
    filas: items.map((x) => ({ nombre: x.nombre })),
    series: [{ nombre: 'Cambio a 12 meses de la mora implícita (pp)', valores: items.map((x) => x.v), color: C.navy }],
    apilar: false,
    mostrarValores: true,
    ariaLabel: 'Cambio a 12 meses de la mora implícita por banco, en puntos porcentuales',
  };
}

/* ---------- armar: B4-05-0 · activos problemáticos PJ por porte ---------- */
const PORTES_PJ = [
  ['Grande', C.navy],
  ['Mediana', C.petroleo],
  ['Pequeña', C.acero],
  ['Micro', C.referencia],
];

function armarPorteEmpresas(d) {
  const filas = d.bk_scr.filter((f) => f.corte === 'porte_pj' && f.tasa_ap != null && f.porte_es && f.porte_es !== 'Sin dato');
  if (!filas.length) return { enPreparacion: 'sin activos problemáticos PJ por porte' };
  return {
    series: PORTES_PJ.map(([porte, color]) => ({
      nombre: porte,
      color,
      puntos: filas
        .filter((f) => f.porte_es === porte)
        .sort((a, b) => (a.fecha < b.fecha ? -1 : a.fecha > b.fecha ? 1 : 0))
        .map((f) => [f.fecha, f.tasa_ap]),
    })),
    formatear: (v) => pctEs(v),
    ariaLabel: 'Activos problemáticos sobre cartera activa de empresas, por porte, mensual',
  };
}

/* En preparación: estas tarjetas no tienen dato utilizable en data/ todavía. */
const EN_PREPARACION = {
  'B4-01-1': 'la mora mayor a 90 días adelantada tres meses requiere desplazar fechas en el navegador; el exportador debe traerla ya adelantada (atraso15_90_pf sí está en bk_sistema_m)',
  'B4-05-1': 'el componente de mosaico por estado todavía no existe en el sitio; los datos por estado sí están en bk_scr',
};

export default {
  clave: 'B4',
  ruta: 'calidad',
  nombre: 'Calidad',
  rotulo: '4 · CALIDAD',
  signo: 'bancos',
  usaBanco: true,
  optica: 'Modelo de negocio',

  // v3 (3-nov): estructura del canvas; la versión anterior queda en el .v1.txt de este archivo.
  franja: [
    { rotulo: 'Mora > 90 días · Sistema', tabla: 'bk_sistema_q', filtro: { serie_id: 'mora90_total' }, delta: 'd_tt', tono: 'mejora_baja' },
    { rotulo: 'Mora > 90 · PF libre', tabla: 'bk_sistema_q', filtro: { serie_id: 'mora90_pf_livre' }, delta: 'd_tt', tono: 'mejora_baja' },
    { rotulo: 'Mora > 90 · PJ libre', tabla: 'bk_sistema_q', filtro: { serie_id: 'mora90_pj_livre' }, delta: 'd_tt', tono: 'mejora_baja' },
    { rotulo: 'NPL ≥ 15 días · Panel', tabla: 'optica/panel/bk_grupo', filtro: { optica: 'Total panel', grupo: 'Todos los grupos', metrica: 'npl15_total' }, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_baja' },
    { rotulo: 'Costo del riesgo · Panel', tabla: 'optica/panel/bk_grupo', filtro: { optica: 'Total panel', grupo: 'Todos los grupos', metrica: 'costo_riesgo_ttm' }, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_baja' },
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
      plana: true, // v3
      titulo: 'Mora > 90 días: PF libre, PJ libre, total',
      sub: 'Sistema BCB · mora > 90 días · total, PF libre y PJ libre · banda p10–p90 de PF libre, 10 años',
      fuente: SGS,
      componente: 'linea',
      datos: ['bk_sistema_m'],
      leyenda: [
        { nombre: 'Total', color: C.navy },
        { nombre: 'PF libre', color: C.petroleo },
        { nombre: 'PJ libre', color: C.acero },
        { nombre: 'Banda p10–p90 de PF libre', color: C.referencia, discontinua: true },
      ],
      nota: 'Desde 2025, con la Res. 4.966 y el cambio de política de baja a pérdida, la mora > 90 días puede no ser comparable con años anteriores.',
      armar: armarMoraSistema,
      estado: 'LISTO',
    },
    'B4-03-0': {
      plana: true, // v3
      titulo: 'Calidad por grupo',
      sub: 'Panel IF.Data · NPL ≥ 15 días sobre cartera · panel y cinco grupos de modelo de negocio · trimestral',
      fuente: IFDATA,
      componente: 'linea',
      datos: ['bk_cre_calidad'],
      leyenda: [
        { nombre: 'Panel (todos los bancos)', color: C.referencia, discontinua: true },
        ...GRUPOS.map((g, i) => ({ nombre: g, color: COLOR_GRUPO[i] })),
      ],
      nota: 'Hasta 2024-T3 la medida es la escala E–H; desde 2025-T1 (Res. 4.966) son los activos problemáticos. La línea cambia de definición en 2025-T1. 2024-T4 sin dato en todo el panel.',
      armar: armarCalidadGrupos,
      estado: 'LISTO',
    },
    'B4-03-1': {
      plana: true, // v3
      titulo: 'Costo del riesgo TTM y cobertura, por banco',
      sub: 'Panel IF.Data · costo del riesgo (12 meses) y cobertura de pérdida esperada, por banco',
      fuente: IFDATA,
      componente: 'barras_h_doble',
      datos: ['metrica/costo_riesgo_ttm/bk_panel', 'metrica/cobertura_ecl/bk_panel', 'bk_banco'], // 4-nov: no los 27 MB de bk_panel
      leyenda: [
        { nombre: 'Costo del riesgo (12 meses)', color: C.navy },
        { nombre: 'Cobertura de pérdida esperada', color: C.acero },
      ],
      nota: 'Con banco activo: los bancos de su grupo, el activo en negrita. Sin banco: los 15 de mayor costo del riesgo. Último trimestre con dato (2T26): 32 de 34 bancos; sin dato BRB y Cielo.',
      banco: true,
      armar: armarCostoRiesgo,
      estado: 'LISTO',
    },
    'B4-04-0': {
      plana: true, // v3
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
      plana: true, // v3
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
