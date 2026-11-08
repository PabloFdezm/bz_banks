/* B6 · Rentabilidad. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec macro).
   Transcrito de ESQUELETO_BANCOS_v0.1.md §B6: títulos, preguntas, anchos, altos, marcas [banco]
   y estados son los del esqueleto, salvo el título de B6-02-0 (encargo 74, 2026-11-03).
   Segunda pasada (encargo 77d, 2026-11-03): tienen dato real en data/ B6-01-0 (bk_grupo),
   B6-02-0 (bk_roe_arbol), B6-03-0 (particiones metrica/<metrica>/bk_panel), B6-04-0 (bk_sensibilidad),
   B6-04-1 (bk_cre_contexto) y B6-05-0 (metrica/eficiencia_ttm/bk_panel). Lo demás va «en preparación»
   con su motivo: la función armar() no calcula nada que no esté ya en una tabla.
   Este archivo no importa nada: contar_tarjetas.mjs y verificar_f1.py lo leen como texto (new Function),
   así que no lleva import ni la palabra de exportación por defecto dentro de un comentario. */
const IFDATA = 'BCB, IF.Data (conglomerado prudencial)';
const SGS = 'BCB, SGS';
const CALC = 'cálculo propio';

/* Colores fijos de grupo: copia de COLOR_GRUPO (estado.js). */
const COLOR_GRUPO = {
  Grandes: '#2E5C8A',
  Digitales: '#2F7A86',
  'Medianos y nicho': '#6C819B',
  Pagos: '#7B5E8C',
  Desarrollo: '#A9B8CB',
  Panel: '#24324A',
};
const GRUPOS = ['Grandes', 'Digitales', 'Medianos y nicho', 'Pagos', 'Desarrollo'];

/* Líneas del árbol del ROE en el orden del esqueleto (bk_roe_arbol, orden 1 a 10). */
const LINEAS_ROE = [
  ['margen_antes_provisiones', 'Margen antes de provisiones'],
  ['provisiones', 'Provisiones'],
  ['tarifas_servicios', 'Tarifas y servicios'],
  ['transacciones_pago', 'Transacciones de pago'],
  ['personal', 'Personal'],
  ['administrativos', 'Administrativos'],
  ['tributarios', 'Tributarios'],
  ['no_operacional', 'No operacional'],
  ['otros', 'Otros'],
  ['impuesto_participaciones', 'Impuesto y participaciones'],
];

const NUMERO_TRIMESTRE = { '03': 1, '06': 2, '09': 3, '12': 4 };
const FIN_TRIMESTRE = { '03': '03-31', '06': '06-30', '09': '09-30', '12': '12-31' };
const maxPeriodo = (filas) => filas.reduce((m, f) => (f.periodo > m ? f.periodo : m), '');
const porPeriodo = (a, b) => (a.periodo < b.periodo ? -1 : a.periodo > b.periodo ? 1 : 0);
const etiquetaTrimestre = (p) => `${NUMERO_TRIMESTRE[p.slice(4)]}T${p.slice(2, 4)}`; // 202606 → 2T26
const fechaDe = (p) => `${p.slice(0, 4)}-${FIN_TRIMESTRE[p.slice(4)]}`; // 202606 → 2026-06-30
const bancoPorSlug = (d, slug) => d.bk_banco.find((b) => b.slug === slug) || null;
const pendiente = (texto) => () => ({ enPreparacion: texto });
const pctTxt = (v) => (v == null || Number.isNaN(v) ? '—' : `${(v * 100).toFixed(1).replace('.', ',')} %`);
const numTxt = (v) => (v == null || Number.isNaN(v) ? '—' : v.toFixed(1).replace('.', ','));
/* Quiebre COSIF 2025 y Res. 4.966 (esqueleto §0.7), visible en las series del panel que lo cruzan. */
const BANDA_COSIF = [{ desde: '2025-01-01', hasta: '2025-03-31', nombre: 'COSIF 2025 · Res. 4.966' }];

export default {
  clave: 'B6',
  ruta: 'rentabilidad',
  nombre: 'Rentabilidad',
  rotulo: '6 · RENTABILIDAD',
  signo: 'bancos',
  usaBanco: true,
  optica: 'Modelo de negocio',

  // v3 (3-nov): estructura del canvas; la versión anterior queda en el .v1.txt de este archivo.
  franja: [
    { rotulo: 'ROE 12 meses · Panel', tabla: 'optica/panel/bk_grupo', filtro: { optica: 'Total panel', grupo: 'Todos los grupos', metrica: 'roe_ttm' }, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_sube' },
    { rotulo: 'ROA 12 meses · Panel', tabla: 'optica/panel/bk_grupo', filtro: { optica: 'Total panel', grupo: 'Todos los grupos', metrica: 'roa_ttm' }, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_sube' },
    { rotulo: 'Margen de intermediación', tabla: 'optica/panel/bk_grupo', filtro: { optica: 'Total panel', grupo: 'Todos los grupos', metrica: 'margem_intermediacao_ttm' }, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'neutro' },
    { rotulo: 'Costo del riesgo · Panel', tabla: 'optica/panel/bk_grupo', filtro: { optica: 'Total panel', grupo: 'Todos los grupos', metrica: 'costo_riesgo_ttm' }, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_baja' },
    { rotulo: 'Eficiencia · Panel', tabla: 'optica/panel/bk_grupo', filtro: { optica: 'Total panel', grupo: 'Todos los grupos', metrica: 'eficiencia_ttm' }, orden: 'periodo', delta: 'valor_tt', escalaDelta: 1, tono: 'mejora_baja' },
  ],

  secciones: [
    {
      numero: '01',
      nombre: 'ROE por grupo',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'ROE de 12 meses por modelo de negocio.',
      filas: [
        [{ clave: 'B6-01-0', ancho: 9, alto: 320 }],
      ],
    },
    {
      numero: '02',
      nombre: 'De dónde sale el ROA',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Árbol del ROA del banco activo contra la mediana de su grupo.',
      filas: [
        [{ clave: 'B6-02-0', ancho: 9, alto: 540 }],
      ],
    },
    {
      numero: '03',
      nombre: 'Riesgo y Selic',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Rentabilidad contra costo del riesgo, y sensibilidad del margen a la tasa.',
      filas: [
        [{ clave: 'B6-03-0', ancho: 5, alto: 440 }, { clave: 'B6-04-0', ancho: 4, alto: 440 }],
      ],
    },
    {
      numero: '04',
      nombre: 'Eficiencia',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: 'Gasto sobre ingreso, hace un año y hoy.',
      filas: [
        [{ clave: 'B6-05-0', ancho: 9, alto: 380 }],
      ],
    },
  ],


  tarjetas: {
    'B6-01-0': {
      plana: true, // v3
      titulo: 'ROE TTM por grupo',
      sub: 'Panel IF.Data · ROE TTM · por grupo',
      fuente: IFDATA,
      componente: 'linea',
      leyenda: [...GRUPOS.map((g) => ({ nombre: g, color: COLOR_GRUPO[g] })), { nombre: 'Panel', color: COLOR_GRUPO.Panel, discontinua: true }], // arquitecto
      datos: ['optica/modelo/bk_grupo'], // 4-nov: 2 MB en vez de los 12 MB de bk_grupo completo
      estado: 'LISTO',
      armar: (d) => {
        const filas = d['optica/modelo/bk_grupo'].filter((f) => f.optica === 'Modelo de negocio' && f.metrica === 'roe_ttm');
        const series = [...GRUPOS, 'Todos los grupos'].map((g) => {
          const puntos = filas.filter((f) => f.grupo === g).sort(porPeriodo).map((f) => [f.fecha, f.valor]);
          const nombre = g === 'Todos los grupos' ? 'Panel' : g;
          return { nombre, puntos, color: COLOR_GRUPO[nombre], discontinua: g === 'Todos los grupos' };
        });
        return {
          series,
          formatear: (v) => `${Math.round(v * 100)} %`, // arquitecto: eje en %, no en fracción
          bandas: BANDA_COSIF,
          ariaLabel: 'ROE TTM por grupo de modelo de negocio, serie trimestral',
        };
      },
    },
    'B6-02-0': {
      plana: true, // v3
      titulo: 'Del margen al ROA, en % del activo promedio',
      sub: 'Panel IF.Data · % del activo promedio · banco vs. mediana del grupo',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'cascada_doble',
      datos: ['bk_banco', 'bk_roe_arbol'],
      nota: 'Las medianas de cada línea no suman exactamente a la mediana del ROA del grupo.',
      banco: true,
      estado: 'LISTO',
      armar: (d, e) => {
        if (!e.banco) return { enPreparacion: 'elige un banco en la barra: la descomposición compara un banco con su grupo', requiereBanco: true };
        const b = bancoPorSlug(d, e.banco);
        if (!b) return { enPreparacion: 'el banco activo no está en la lista de bancos' };
        const periodo = e.trimestre || maxPeriodo(d.bk_roe_arbol);
        const filas = d.bk_roe_arbol.filter((f) => f.entidad === b.cod_inst && f.periodo === periodo);
        const celda = (linea) => filas.find((f) => f.linea === linea) || null;
        const roa = celda('roa');
        if (!roa || roa.valor == null) return { enPreparacion: 'sin dato del banco en ese trimestre' };
        const omitidas = [];
        const lineas = LINEAS_ROE.map(([clave, nombre]) => {
          const f = celda(clave);
          if (!f || f.valor == null || f.mediana_grupo == null) { omitidas.push(nombre.toLowerCase()); return null; }
          return { nombre, banco: f.valor, grupo: f.mediana_grupo };
        }).filter(Boolean);
        const roe = celda('roe');
        const apal = celda('apalancamiento');
        const notas = [];
        if (roe && roe.valor != null) notas.push(`ROE del banco ${pctTxt(roe.valor)}; mediana del grupo ${pctTxt(roe.mediana_grupo)}`);
        if (apal && apal.valor != null) notas.push(`apalancamiento de ${numTxt(apal.valor)} veces, contra ${numTxt(apal.mediana_grupo)} del grupo`);
        if (omitidas.length) notas.push(`sin dato en ${etiquetaTrimestre(periodo)} para: ${omitidas.join(', ')}`);
        return {
          lineas,
          total: roa.mediana_grupo == null ? undefined : { nombre: 'ROA', banco: roa.valor, grupo: roa.mediana_grupo },
          nota: notas.length ? `${notas.join('. ')}.` : undefined,
          ariaLabel: `Descomposición del ROA de ${b.nombre_corto} frente a la mediana de su grupo, ${etiquetaTrimestre(periodo)}`,
        };
      },
    },
    'B6-03-0': {
      plana: true, // v3
      titulo: 'ROE TTM vs. costo del riesgo TTM, por banco, con trayectoria de 8 trimestres',
      sub: 'Panel IF.Data · ROE TTM vs. costo del riesgo TTM · tamaño = activo · 8 trimestres',
      fuente: IFDATA,
      componente: 'burbujas_trayectoria',
      datos: [
        'bk_banco',
        'metrica/roe_ttm/bk_panel',
        'metrica/costo_riesgo_ttm/bk_panel',
        'metrica/ativo_total/bk_panel',
      ],
      banco: true,
      estado: 'LISTO',
      armar: (d, e) => {
        const particiones = [['roe', 'metrica/roe_ttm/bk_panel'], ['costo', 'metrica/costo_riesgo_ttm/bk_panel'], ['activo', 'metrica/ativo_total/bk_panel']];
        const valor = new Map();
        for (const [clave, tabla] of particiones) {
          for (const f of d[tabla] || []) valor.set(`${f.cod_inst}|${f.periodo}|${clave}`, f.valor);
        }
        const v = (cod, p, clave) => valor.get(`${cod}|${p}|${clave}`) ?? null;
        const t = e.trimestre || maxPeriodo(d['metrica/roe_ttm/bk_panel']);
        const periodos = [...new Set(d['metrica/roe_ttm/bk_panel'].map((f) => f.periodo))].filter((p) => p <= t).sort().slice(-8);
        const puntos = [];
        const trayectorias = [];
        for (const b of d.bk_banco) {
          const x = v(b.cod_inst, t, 'costo');
          const y = v(b.cod_inst, t, 'roe');
          const tamano = v(b.cod_inst, t, 'activo');
          if (x != null && y != null && tamano != null) {
            puntos.push({ banco: b.slug, nombre: b.nombre_corto, grupo: b.modelo, x, y, tamaño: tamano });
          }
          if (b.slug === e.banco || b.modelo === 'Grandes') {
            const pts = periodos
              .map((p) => [v(b.cod_inst, p, 'costo'), v(b.cod_inst, p, 'roe'), etiquetaTrimestre(p)])
              .filter(([px, py]) => px != null && py != null);
            trayectorias.push({ banco: b.slug, nombre: b.nombre_corto, grupo: b.modelo, puntos: pts });
          }
        }
        return {
          puntos,
          trayectorias,
          banco: e.banco || null,
          ejeX: { titulo: 'Costo del riesgo, 12 meses', formato: 'pct' },
          ejeY: { titulo: 'ROE, 12 meses', formato: 'pct' },
          ariaLabel: `ROE TTM frente a costo del riesgo TTM de cada banco, ${etiquetaTrimestre(t)}`,
        };
      },
    },
    'B6-04-0': {
      plana: true, // v3
      titulo: 'Beta del margen a la Selic',
      sub: 'Panel IF.Data · pendiente del NIM contra el CDI medio desde 2016 · con intervalo',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'barras_ic',
      datos: ['bk_banco', 'bk_sensibilidad'],
      banco: true,
      estado: 'LISTO',
      armar: (d, e) => {
        const bancos = new Map(d.bk_banco.map((b) => [b.cod_inst, b]));
        const filas = d.bk_sensibilidad.map((s) => {
          const b = bancos.get(s.cod_inst);
          return {
            nombre: b ? b.nombre_corto : s.cod_inst,
            slug: b ? b.slug : null,
            valor: s.beta_nim_cdi,
            bajo: s.ic_inf,
            alto: s.ic_sup,
            n: s.n_trimestres,
          };
        }).sort((a, b) => (a.valor == null) - (b.valor == null) || (b.valor ?? 0) - (a.valor ?? 0));
        return {
          filas,
          activo: e.banco || null,
          nota: 'Intervalo de confianza de 90 %. Regresión del NIM trimestral contra el CDI medio desde 2016. Se excluyen 2024-T4 y, en los bancos con cambio de cobertura en 2025, 2025-T1. «Pocos trimestres»: menos de 24 trimestres.',
          ariaLabel: 'Beta del margen a la Selic por banco, con intervalo de confianza de 90 %',
        };
      },
    },
    'B6-05-0': {
      plana: true, // v3
      titulo: 'Eficiencia TTM por banco, hace un año y hoy',
      sub: 'Panel IF.Data · eficiencia TTM · hace un año y hoy',
      fuente: IFDATA,
      componente: 'pesas',
      datos: ['bk_banco', 'bk_metrica', 'metrica/eficiencia_ttm/bk_panel'],
      banco: true,
      estado: 'LISTO',
      armar: (d, e) => {
        const tabla = d['metrica/eficiencia_ttm/bk_panel'];
        const signo = (d.bk_metrica.find((m) => m.metrica === 'eficiencia_ttm') || {}).signo || 'neutro';
        const t = e.trimestre || maxPeriodo(tabla);
        const enT = new Map(tabla.filter((f) => f.periodo === t).map((f) => [f.cod_inst, f]));
        // v3: con banco activo, solo su grupo; siempre fuera los valores > 120 % (CloudWalk 2025: 184 %), que aplastan la escala
        const filas = d.bk_banco.filter((b) => !e.grupoBanco || b.modelo === e.grupoBanco).filter((b) => {
          const f = enT.get(b.cod_inst);
          return f && f.valor != null && f.valor <= 1.2 && (f.valor_t4 == null || f.valor_t4 <= 1.2);
        }).map((b) => {
          const f = enT.get(b.cod_inst);
          return {
            nombre: b.nombre_corto,
            slug: b.slug,
            antes: f ? f.valor_t4 : null,
            ahora: f ? f.valor : null,
            signo,
            destacada: b.slug === e.banco,
          };
        }).sort((a, b) => (a.ahora == null) - (b.ahora == null) || (a.ahora ?? 0) - (b.ahora ?? 0));
        return {
          filas,
          formato: 'pct',
          umbral: 0,
          ariaLabel: `Eficiencia TTM de cada banco hace un año y en ${etiquetaTrimestre(t)}`,
        };
      },
    },
  },
};
