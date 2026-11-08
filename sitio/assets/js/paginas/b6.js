/* B6 · Rentabilidad. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec macro).
   Transcrito de ESQUELETO_BANCOS_v0.1.md §B6: títulos, preguntas, anchos, altos, marcas [banco]
   y estados son los del esqueleto, salvo el título de B6-02-0.
   Datos: B6-01-0 bk_grupo (óptica modelo), B6-02-0 bk_roe_arbol, B6-03-0 particiones metrica/<metrica>/bk_panel,
   B6-04-0 bk_sensibilidad y B6-05-0 metrica/eficiencia_ttm/bk_panel. armar() no calcula nada que no esté
   ya en una tabla. */
import { FUENTE, COLOR_GRUPO, GRUPOS, GRUPO_PANEL, OPTICA_MODELO, ROTULO_PANEL, BANDA_2025, tablaMetrica, tablaOptica, indicadorPanel, lineasArbolRoe, enPreparacion, requiereBanco } from '../comun.js';
import { numero, pctRotulo, trimestreDePeriodo, porPeriodo, periodosHasta, ROTULO } from '../formato.js';

const { IFDATA, CALC } = FUENTE;

const decimal = (v) => numero(v, 1, ROTULO);
/* Sin banco activo, el gráfico de riesgo y rentabilidad muestra la trayectoria de este grupo. */
const GRUPO_TRAYECTORIAS = 'Grandes';
/* Eficiencias sobre este tope (CloudWalk 2025: 184 %) aplastan la escala: quedan fuera del gráfico. */
const TOPE_EFICIENCIA = 1.2;

export default {
  rotulo: '6 · RENTABILIDAD',
  usaBanco: true,

  franja: [
    indicadorPanel('ROE 12 meses · Panel', 'roe_ttm'),
    indicadorPanel('ROA 12 meses · Panel', 'roa_ttm'),
    // bk_metrica le da mejora_sube; la franja lo muestra sin juicio (decisión de diseño previa, a confirmar por Pablo)
    indicadorPanel('Margen de intermediación', 'margem_intermediacao_ttm', { tono: 'neutro' }),
    indicadorPanel('Costo del riesgo · Panel', 'costo_riesgo_ttm'),
    indicadorPanel('Eficiencia · Panel', 'eficiencia_ttm'),
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
      plana: true,
      titulo: 'ROE TTM por grupo',
      sub: 'Panel IF.Data · ROE TTM · por grupo',
      fuente: IFDATA,
      componente: 'linea',
      datos: [tablaOptica('modelo')], // 2 MB en vez de los 12 MB de bk_grupo completo
      estado: 'LISTO',
      armar: (d) => {
        const filas = d[tablaOptica('modelo')].filter((f) => f.optica === OPTICA_MODELO && f.metrica === 'roe_ttm');
        const series = [...GRUPOS, GRUPO_PANEL].map((g) => {
          const puntos = filas.filter((f) => f.grupo === g).sort(porPeriodo).map((f) => [f.fecha, f.valor]);
          const nombre = g === GRUPO_PANEL ? ROTULO_PANEL : g;
          return { nombre, puntos, color: COLOR_GRUPO[nombre], discontinua: g === GRUPO_PANEL };
        });
        return {
          series,
          leyenda: series.map(({ nombre, color, discontinua }) => ({ nombre, color, discontinua })),
          eje: { unidad: 'pct', decimales: 0 },
          bandas: BANDA_2025,
          ariaLabel: 'ROE TTM por grupo de modelo de negocio, serie trimestral',
        };
      },
    },
    'B6-02-0': {
      plana: true,
      titulo: 'Del margen al ROA, en % del activo promedio',
      sub: 'Panel IF.Data · % del activo promedio · banco vs. mediana del grupo',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'cascada_doble',
      datos: ['bk_roe_arbol'],
      nota: 'Las medianas de cada línea no suman exactamente a la mediana del ROA del grupo.',
      banco: true,
      estado: 'LISTO',
      armar: (d, e) => {
        if (!e.banco) return requiereBanco('elige un banco en la barra: la descomposición compara un banco con su grupo');
        const b = e.bancoActivo;
        const periodo = e.periodoActivo;
        const filas = d.bk_roe_arbol.filter((f) => f.entidad === b.cod_inst && f.periodo === periodo);
        const celda = (linea) => filas.find((f) => f.linea === linea) || null;
        const roa = celda('roa');
        if (!roa || roa.valor == null) return enPreparacion('sin dato del banco en ese trimestre');
        const { lineas, omitidas } = lineasArbolRoe(filas);
        const roe = celda('roe');
        const apal = celda('apalancamiento');
        const notas = [];
        if (roe && roe.valor != null) notas.push(`ROE del banco ${pctRotulo(roe.valor)}; mediana del grupo ${pctRotulo(roe.mediana_grupo)}`);
        if (apal && apal.valor != null) notas.push(`apalancamiento de ${decimal(apal.valor)} veces, contra ${decimal(apal.mediana_grupo)} del grupo`);
        if (omitidas.length) notas.push(`sin dato en ${trimestreDePeriodo(periodo)} para: ${omitidas.join(', ').toLowerCase()}`);
        return {
          lineas,
          total: roa.mediana_grupo == null ? undefined : { nombre: 'ROA', banco: roa.valor, grupo: roa.mediana_grupo },
          nota: notas.length ? `${notas.join('. ')}.` : undefined,
          ariaLabel: `Descomposición del ROA de ${b.nombre_corto} frente a la mediana de su grupo, ${trimestreDePeriodo(periodo)}`,
        };
      },
    },
    'B6-03-0': {
      plana: true,
      titulo: 'ROE TTM vs. costo del riesgo TTM, por banco, con trayectoria de 8 trimestres',
      sub: 'Panel IF.Data · ROE TTM vs. costo del riesgo TTM · tamaño = activo · 8 trimestres',
      fuente: IFDATA,
      componente: 'burbujas_trayectoria',
      datos: [
        'bk_banco',
        tablaMetrica('roe_ttm'),
        tablaMetrica('costo_riesgo_ttm'),
        tablaMetrica('ativo_total'),
      ],
      banco: true,
      estado: 'LISTO',
      armar: (d, e) => {
        const particiones = [['roe', tablaMetrica('roe_ttm')], ['costo', tablaMetrica('costo_riesgo_ttm')], ['activo', tablaMetrica('ativo_total')]];
        const valor = new Map();
        for (const [clave, tabla] of particiones) {
          for (const f of d[tabla] || []) valor.set(`${f.cod_inst}|${f.periodo}|${clave}`, f.valor);
        }
        const v = (cod, p, clave) => valor.get(`${cod}|${p}|${clave}`) ?? null;
        const t = e.periodoActivo;
        const periodos = periodosHasta(d[tablaMetrica('roe_ttm')], t, 8);
        const puntos = [];
        const trayectorias = [];
        for (const b of d.bk_banco) {
          const x = v(b.cod_inst, t, 'costo');
          const y = v(b.cod_inst, t, 'roe');
          const tamano = v(b.cod_inst, t, 'activo');
          if (x != null && y != null && tamano != null) {
            puntos.push({ banco: b.slug, nombre: b.nombre_corto, grupo: b.modelo, x, y, tamaño: tamano });
          }
          // con banco activo, solo su trayectoria; sin banco, las del grupo de referencia
          if (e.banco ? b.slug === e.banco : b.modelo === GRUPO_TRAYECTORIAS) {
            const pts = periodos
              .map((p) => [v(b.cod_inst, p, 'costo'), v(b.cod_inst, p, 'roe'), trimestreDePeriodo(p)])
              .filter(([px, py]) => px != null && py != null);
            trayectorias.push({ banco: b.slug, nombre: b.nombre_corto, grupo: b.modelo, puntos: pts });
          }
        }
        return {
          puntos,
          trayectorias,
          banco: e.banco || null,
          colores: COLOR_GRUPO,
          ejeX: { titulo: 'Costo del riesgo, 12 meses', formato: 'pct' },
          ejeY: { titulo: 'ROE, 12 meses', formato: 'pct' },
          ariaLabel: `ROE TTM frente a costo del riesgo TTM de cada banco, ${trimestreDePeriodo(t)}`,
        };
      },
    },
    'B6-04-0': {
      plana: true,
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
      plana: true,
      titulo: 'Eficiencia TTM por banco, hace un año y hoy',
      sub: 'Panel IF.Data · eficiencia TTM · hace un año y hoy',
      fuente: IFDATA,
      componente: 'pesas',
      datos: ['bk_banco', 'bk_metrica', tablaMetrica('eficiencia_ttm')],
      banco: true,
      estado: 'LISTO',
      armar: (d, e) => {
        const tabla = d[tablaMetrica('eficiencia_ttm')];
        const signo = (d.bk_metrica.find((m) => m.metrica === 'eficiencia_ttm') || {}).signo || 'neutro';
        const t = e.periodoActivo;
        const enT = new Map(tabla.filter((f) => f.periodo === t).map((f) => [f.cod_inst, f]));
        // con banco activo, solo su grupo; siempre fuera las eficiencias sobre el tope
        const grupo = e.bancoActivo?.modelo;
        const filas = d.bk_banco.filter((b) => !grupo || b.modelo === grupo).filter((b) => {
          const f = enT.get(b.cod_inst);
          return f && f.valor != null && f.valor <= TOPE_EFICIENCIA && (f.valor_t4 == null || f.valor_t4 <= TOPE_EFICIENCIA);
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
          ariaLabel: `Eficiencia TTM de cada banco hace un año y en ${trimestreDePeriodo(t)}`,
        };
      },
    },
  },
};
