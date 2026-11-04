/* B5 · Fondeo y liquidez. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec
   macro). Transcrito de ESQUELETO_BANCOS_v0.1.md §B5: títulos, preguntas, anchos, altos, marcas
   [banco] y estados son los del esqueleto. En la F0 ninguna tarjeta tiene `armar`.
   Tablas que pide el esqueleto para cada tarjeta (las necesita la ola 2):
     B5-01-0  bk_grupo (componentes del pasivo)       B5-03-0  bk_panel: credito_depositos
     B5-01-1  bk_grupo: depositos_aa                  B5-03-1  bk_panel: costo_captacion_ttm
     B5-02-0  hcs_ahorro                              B5-04-0  bk_ref (gráficos 1.2.1.15, 1.2.1.18)
   B5-03-1 queda FALTA: el DRE del panel no separa gasto de captación (validar en `bank_cuentas`).
   Riel del esqueleto: 01 selector de óptica · 02 sin riel · 03 sin riel · 04 sin riel. */
const IFDATA = 'BCB, IF.Data (conglomerado prudencial)';
const SGS = 'BCB, SGS';
const REFBCB = 'BCB, Relatório de Estabilidade Financeira';
const CALC = 'cálculo propio';

export default {
  clave: 'B5',
  ruta: 'fondeo',
  nombre: 'Fondeo y liquidez',
  rotulo: '5 · FONDEO',
  signo: 'bancos',
  usaBanco: true,
  optica: 'Modelo de negocio',

  secciones: [
    {
      numero: '01',
      nombre: 'Mix de fondeo',
      frecuencia: 'Trimestral · Panel IF.Data',
      preguntaClave: 'B5.01',
      pregunta: '¿depósitos, compromissadas o emisiones?',
      filas: [
        [{ clave: 'B5-01-0', ancho: 5, alto: 372 }, { clave: 'B5-01-1', ancho: 4, alto: 372 }],
      ],
    },
    {
      numero: '02',
      nombre: 'El ahorro',
      frecuencia: 'Mensual · Sistema BCB',
      preguntaClave: 'B5.02',
      pregunta: '¿el ahorro se queda en el balance bancario?',
      filas: [[{ clave: 'B5-02-0', ancho: 9, alto: 372 }]],
    },
    {
      numero: '03',
      nombre: 'Calce y costo',
      frecuencia: 'Trimestral · Panel IF.Data',
      preguntaClave: 'B5.03',
      pregunta: '¿quién depende más del mayorista y quién paga más por fondearse?',
      filas: [
        [{ clave: 'B5-03-0', ancho: 4, alto: 372 }, { clave: 'B5-03-1', ancho: 5, alto: 372 }],
      ],
    },
    {
      numero: '04',
      nombre: 'Liquidez',
      frecuencia: 'Semestral · REF',
      preguntaClave: 'B5.04',
      pregunta: '¿hay holgura de liquidez?',
      filas: [[{ clave: 'B5-04-0', ancho: 9, alto: 372 }]],
    },
  ],

  tarjetas: {
    'B5-01-0': {
      titulo: 'Pasivo + PL por instrumento, por grupo, 100 %',
      sub: 'Panel IF.Data · pasivo y patrimonio por instrumento · apilado al 100 %',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'apilada_100',
      datos: [],
      estado: 'DERIVAR',
    },
    'B5-01-1': {
      titulo: 'Depósitos a/a por grupo',
      sub: 'Panel IF.Data · depósitos a/a · por grupo',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'linea',
      datos: [],
      estado: 'DERIVAR',
    },
    'B5-02-0': {
      titulo: 'CDB vs. poupança vs. Selic',
      sub: 'Sistema BCB · CDB, poupança y Selic',
      fuente: SGS,
      componente: 'linea',
      datos: [],
      estado: 'LISTO',
    },
    'B5-03-0': {
      titulo: 'Crédito / depósitos por banco',
      sub: 'Panel IF.Data · crédito sobre depósitos · por banco',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'barras_h',
      datos: [],
      banco: true,
      estado: 'DERIVAR',
    },
    'B5-03-1': {
      titulo: 'Costo implícito de captación vs. CDI',
      sub: 'Panel IF.Data · gasto de captación TTM sobre pasivo con costo promedio vs. CDI',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'dispersion',
      datos: [],
      banco: true,
      estado: 'FALTA',
    },
    'B5-04-0': {
      titulo: 'LCR y NSFR: agregado, máximo y mínimo',
      sub: 'REF · LCR y NSFR · agregado, máximo y mínimo (S1)',
      fuente: REFBCB,
      componente: 'linea',
      datos: [],
      estado: 'REF',
    },
  },
};
