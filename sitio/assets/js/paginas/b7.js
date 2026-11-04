/* B7 · Capital. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del spec macro).
   Transcrito de ESQUELETO_BANCOS_v0.1.md §B7: títulos, preguntas, anchos, altos, marcas [banco]
   y estados son los del esqueleto. En la F0 ninguna tarjeta tiene `armar`.
   La página entera depende de colectar el informe de capital de IF.Data: hoy solo hay cinco
   cortes sueltos en `datos/derivado/bcb_ifdata/valores/ifdata_capital_*.csv`, así que cinco de
   sus seis tarjetas son FALTA.
   Tablas que pide el esqueleto para cada tarjeta (las necesita la ola 2):
     B7-01-0  bk_capital + FIJO de mínimos (manual/minimos_regulatorios.csv)
     B7-01-1  bk_capital                              B7-03-0  bk_capital
     B7-02-0  bk_capital · bk_panel (lucro)           B7-03-1  bk_ref
     B7-02-1  bk_capital
   Riel del esqueleto: 01 «Dato de la sección»: Basilea del panel · 02 sin riel · 03 sin riel. */
const IFDATA = 'BCB, IF.Data (conglomerado prudencial)';
const REFBCB = 'BCB, Relatório de Estabilidade Financeira';
const CALC = 'cálculo propio';

export default {
  clave: 'B7',
  ruta: 'capital',
  nombre: 'Capital',
  rotulo: '7 · CAPITAL',
  signo: 'bancos',
  usaBanco: true,
  optica: 'Modelo de negocio',

  secciones: [
    {
      numero: '01',
      nombre: 'Niveles',
      frecuencia: 'Trimestral · Panel IF.Data',
      preguntaClave: 'B7.01',
      pregunta: '¿dónde está cada banco contra su mínimo?',
      filas: [
        [{ clave: 'B7-01-0', ancho: 5, alto: 520 }, { clave: 'B7-01-1', ancho: 4, alto: 520 }],
      ],
    },
    {
      numero: '02',
      nombre: 'Generación y consumo',
      frecuencia: 'Trimestral · Panel IF.Data',
      preguntaClave: 'B7.02',
      pregunta: '¿el capital crece por resultados y cuánto consume cada real de crédito?',
      filas: [
        [{ clave: 'B7-02-0', ancho: 5, alto: 372 }, { clave: 'B7-02-1', ancho: 4, alto: 372 }],
      ],
    },
    {
      numero: '03',
      nombre: 'Holgura y estrés',
      frecuencia: 'Trimestral y semestral · Panel y REF',
      preguntaClave: 'B7.03',
      pregunta: '¿cuánto puede crecer la cartera sin capital nuevo, y aguanta un escenario adverso?',
      filas: [
        [{ clave: 'B7-03-0', ancho: 5, alto: 372 }, { clave: 'B7-03-1', ancho: 4, alto: 372 }],
      ],
    },
  ],

  tarjetas: {
    'B7-01-0': {
      titulo: 'Basilea, nivel 1 y capital principal por banco, contra el mínimo con colchones',
      sub: 'Panel IF.Data · nivel 1 y capital principal contra el mínimo con colchones',
      fuente: `${IFDATA}; BCB, mínimos regulatorios; ${CALC}`,
      componente: 'barras_h',
      datos: [],
      banco: true,
      estado: 'FALTA',
    },
    'B7-01-1': {
      titulo: 'Capital principal por grupo',
      sub: 'Panel IF.Data · capital principal · por grupo',
      fuente: IFDATA,
      componente: 'linea',
      datos: [],
      estado: 'FALTA',
    },
    'B7-02-0': {
      titulo: 'Variación del capital principal en 4T: resultado, dividendos, otros',
      sub: 'Panel IF.Data · variación del capital principal en 4 trimestres',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'cascada',
      datos: [],
      banco: true,
      estado: 'FALTA',
    },
    'B7-02-1': {
      titulo: 'Densidad de RWA',
      sub: 'Panel IF.Data · RWA sobre activo y RWA por tipo de riesgo · apilado al 100 %',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'apilada_100',
      datos: [],
      banco: true,
      estado: 'FALTA',
    },
    'B7-03-0': {
      titulo: 'Holgura de crecimiento',
      sub: 'Panel IF.Data · % de la cartera actual',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'barras_h',
      datos: [],
      banco: true,
      estado: 'FALTA',
    },
    'B7-03-1': {
      titulo: 'Resultado del test de estrés del BCB',
      sub: 'REF · test de estrés del BCB · agregado',
      fuente: REFBCB,
      componente: 'tabla',
      datos: [],
      estado: 'REF',
    },
  },
};
