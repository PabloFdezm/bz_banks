/* B1 · Ciclo y condiciones. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del
   spec macro). Transcrito de ESQUELETO_BANCOS_v0.1.md §B1: títulos, preguntas, anchos, altos y
   estados son los del esqueleto. Ninguna tarjeta tiene `armar` todavía.
   Tablas que pide el esqueleto para cada tarjeta:
     B1-01-0  tasa_real_exante (la línea de tasa neutral es FIJO a confirmar: sin confirmación se omite)
     B1-01-1  trayectoria_selic_focus
     B1-02-0  cpib_componentes
     B1-02-1  bk_sistema_m: impulso_credito (SGS 20539 + 4382)
     B1-03-0  hsf_mensual · fh_deuda
     B1-03-1  tasas_pnad · bk_sistema_m (SGS 21112)
     B1-04-0  bk_sistema_m: SGS 27701, 27702          B1-05-0  bk_ref (gráfico 1.2.2.1 del REF)
     B1-04-1  bk_sistema_m: SGS 27703, 27704 · scrdata_pj_agregado   B1-05-1  bk_ref (tabla 1.2.2.1)
     B1-04-2  crudo fgo_pronampe · bndes_fgi
   Riel del esqueleto: 01 KPI K57 «¿Restrictiva o expansiva?» · 02 KPI K58 «El impulso de
   crédito» · 03 «Dato de la sección»: comprometimiento de renta (SGS 29034) · 04 «Dato de la
   sección»: activos problemáticos PJ MPME (SCR) · 05 sin riel. */
import { FUENTE } from '../comun.js';

const { SGS, SCR: SCRDATA, REF: REFBCB, FOCUS, IBGE, CALC } = FUENTE;

export default {
  rotulo: '1 · CICLO Y CONDICIONES',
  usaBanco: false,

  secciones: [
    {
      numero: '01',
      nombre: 'Tasa',
      frecuencia: 'Mensual · Sistema BCB',
      pregunta: '¿qué tan restrictiva es la política y qué espera el mercado?',
      filas: [
        [{ clave: 'B1-01-0', ancho: 5, alto: 372 }, { clave: 'B1-01-1', ancho: 4, alto: 372 }],
      ],
    },
    {
      numero: '02',
      nombre: 'Crédito y economía',
      frecuencia: 'Mensual · Sistema BCB',
      pregunta: '¿el crédito crece más o menos que la economía, y está acelerando?',
      filas: [
        [{ clave: 'B1-02-0', ancho: 5, alto: 372 }, { clave: 'B1-02-1', ancho: 4, alto: 372 }],
      ],
    },
    {
      numero: '03',
      nombre: 'Hogares',
      frecuencia: 'Mensual · Sistema BCB',
      pregunta: '¿los hogares pueden seguir pagando?',
      filas: [
        [{ clave: 'B1-03-0', ancho: 5, alto: 372 }, { clave: 'B1-03-1', ancho: 4, alto: 372 }],
      ],
    },
    {
      numero: '04',
      nombre: 'Empresas',
      frecuencia: 'Mensual · Sistema BCB y SCR',
      pregunta: '¿las empresas pueden pagar, y qué tamaño de empresa preocupa?',
      filas: [
        [{ clave: 'B1-04-0', ancho: 5, alto: 372 }, { clave: 'B1-04-1', ancho: 4, alto: 372 }],
        [{ clave: 'B1-04-2', ancho: 9, alto: 372 }],
      ],
    },
    {
      numero: '05',
      nombre: 'Desintermediación',
      frecuencia: 'Semestral · REF',
      pregunta: '¿cuánto crédito se va del balance de los bancos al mercado de capitales?',
      filas: [
        [{ clave: 'B1-05-0', ancho: 5, alto: 372 }, { clave: 'B1-05-1', ancho: 4, alto: 372 }],
      ],
    },
  ],

  tarjetas: {
    'B1-01-0': {
      titulo: 'Selic real ex ante',
      sub: 'Sistema BCB · tasa real ex ante, con la Selic nominal',
      fuente: `${SGS}; ${FOCUS}; ${CALC}`,
      componente: 'linea',
      datos: [],
      estado: 'LISTO',
    },
    'B1-01-1': {
      titulo: 'Trayectoria de la Selic: Focus vs. mercado',
      sub: 'Sistema BCB · Focus y curva de mercado',
      fuente: `${FOCUS}; B3`,
      componente: 'linea',
      datos: [],
      estado: 'LISTO',
    },
    'B1-02-0': {
      titulo: 'Crédito/PIB y su tendencia',
      sub: 'Sistema BCB · crédito/PIB con aporte PF y PJ',
      fuente: `${SGS}; ${IBGE}; ${CALC}`,
      componente: 'columnas',
      datos: [],
      estado: 'LISTO',
    },
    'B1-02-1': {
      titulo: 'Impulso de crédito',
      sub: 'Sistema BCB · Δ del flujo de 12 meses sobre el PIB de 12 meses',
      fuente: `${SGS}; ${CALC}`,
      componente: 'columnas',
      datos: [],
      estado: 'DERIVAR',
    },
    'B1-03-0': {
      titulo: 'Comprometimiento de renta: intereses y amortización',
      sub: 'Sistema BCB · intereses y amortización, con la línea del total',
      fuente: SGS,
      componente: 'area_apilada',
      datos: [],
      estado: 'LISTO',
    },
    'B1-03-1': {
      titulo: 'Desempleo y mora PF libre',
      sub: 'Sistema BCB · desempleo y mora PF libre · dos paneles con el mismo eje x',
      fuente: `${IBGE}; ${SGS}`,
      componente: 'linea',
      datos: [],
      estado: 'LISTO',
    },
    'B1-04-0': {
      titulo: 'Crédito real a/a por porte',
      sub: 'Sistema BCB · crédito real a/a · MPME vs. grandes',
      fuente: `${SGS}; ${CALC}`,
      componente: 'linea',
      datos: [],
      estado: 'DERIVAR',
    },
    'B1-04-1': {
      titulo: 'Inadimplencia por porte',
      sub: 'Sistema BCB y SCR · inadimplencia por porte',
      fuente: `${SGS}; ${SCRDATA}; ${CALC}`,
      componente: 'linea',
      datos: [],
      estado: 'DERIVAR',
    },
    'B1-04-2': {
      titulo: 'Crédito con garantía pública',
      sub: 'Sistema BCB · garantía pública como % de las concesiones a MPME',
      fuente: `BNDES (FGI); FGO/Pronampe; ${CALC}`,
      componente: 'columnas',
      datos: [],
      estado: 'DERIVAR',
    },
    'B1-05-0': {
      titulo: 'Crédito amplio por fuente',
      sub: 'REF · crédito por fuente, aporte al crecimiento',
      fuente: REFBCB,
      componente: 'columnas',
      datos: [],
      estado: 'REF',
    },
    'B1-05-1': {
      titulo: 'Mercado de capitales por instrumento',
      sub: 'REF · mercado de capitales por instrumento',
      fuente: REFBCB,
      componente: 'barras_h',
      datos: [],
      estado: 'REF',
    },
  },
};
