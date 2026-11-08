/* B2 · Estructura y competencia. Config de la página (SPEC_WEB_BANCOS_00_GENERAL.md §2 y §3 del
   spec macro). Transcrito de ESQUELETO_BANCOS_v0.1.md §B2: títulos, preguntas, anchos, altos,
   marcas [banco] y estados son los del esqueleto. Ninguna tarjeta tiene `armar` todavía.
   Tablas que pide el esqueleto para cada tarjeta:
     B2-01-0  bk_grupo (hhi_*, top5_*)                B2-03-0  bk_cartera (banco × modalidad)
     B2-01-1  bk_panel: share_credito                 B2-03-1  bk_cartera
     B2-02-0  cre_panorama (apilar = Institución, participacion)
     B2-02-1  bk_panel: share_credito, share_depositos
     B2-04-0  bk_scr (segmento × mes) — hoy 6 meses, falta la historia
     B2-04-1  cre_panorama (aa4) · cre_calidad (NPL)
     B2-05-0  bk_conducta — hay un corte; FALTA la serie    B2-05-2  bk_sistema_m (medios de pago)
     B2-05-1  bk_conducta (tarifas Olinda)
   Riel del esqueleto: 01 «Dato de la sección»: cuota de crédito de los cinco mayores ·
   02 selectores de óptica y de medida (Crédito / Depósitos) · 03 selector Personas / Empresas ·
   04 «Dato de la sección»: inadimplencia de fintechs menos la de bancos (pp, SCR) · 05 sin riel.
   Reclamos y tarifas (B2-05-0 y B2-05-1) llevan prefijo «BCB ·»: no son un universo nuevo, es la
   decisión del 2026-11-02. Pix sigue «Sistema BCB ·». */
import { FUENTE } from '../comun.js';

const { IFDATA, SGS, SCR: SCRDATA, OLINDA, CALC } = FUENTE;

export default {
  rotulo: '2 · ESTRUCTURA Y COMPETENCIA',
  usaBanco: true,

  secciones: [
    {
      numero: '01',
      nombre: 'Concentración',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: '¿el sistema se concentra o se abre?',
      filas: [
        [{ clave: 'B2-01-0', ancho: 5, alto: 372 }, { clave: 'B2-01-1', ancho: 4, alto: 372 }],
      ],
    },
    {
      numero: '02',
      nombre: 'Cuota por grupo',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: '¿qué tipo de banco gana cuota?',
      filas: [
        [{ clave: 'B2-02-0', ancho: 5, alto: 372 }, { clave: 'B2-02-1', ancho: 4, alto: 372 }],
      ],
    },
    {
      numero: '03',
      nombre: 'Dónde compiten',
      frecuencia: 'Trimestral · Panel IF.Data',
      pregunta: '¿en qué carteras están ganando los digitales?',
      filas: [
        [{ clave: 'B2-03-0', ancho: 9, alto: 520 }],
        [{ clave: 'B2-03-1', ancho: 9, alto: 372 }],
      ],
    },
    {
      numero: '04',
      nombre: 'Riesgo según el tipo de institución',
      frecuencia: 'Mensual · SCR',
      pregunta: '¿crecer cuota les está costando mora?',
      filas: [
        [{ clave: 'B2-04-0', ancho: 5, alto: 372 }, { clave: 'B2-04-1', ancho: 4, alto: 372 }],
      ],
    },
    {
      numero: '05',
      nombre: 'Precio y servicio',
      frecuencia: 'Trimestral · Olinda y Sistema BCB',
      pregunta: '¿compiten en precio o en servicio?',
      filas: [
        [{ clave: 'B2-05-0', ancho: 4, alto: 372 }, { clave: 'B2-05-1', ancho: 5, alto: 372 }],
        [{ clave: 'B2-05-2', ancho: 9, alto: 372 }],
      ],
    },
  ],

  tarjetas: {
    'B2-01-0': {
      titulo: 'HHI y cuota top 5',
      sub: 'Panel IF.Data · HHI y cuota top 5 en crédito, depósitos y activo',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'linea',
      datos: [],
      estado: 'DERIVAR',
    },
    'B2-01-1': {
      titulo: 'Ranking de cuota de crédito con movimiento',
      sub: 'Panel IF.Data · cuota de crédito · puestos ganados o perdidos en 4 trimestres',
      fuente: IFDATA,
      componente: 'tabla',
      datos: [],
      banco: true,
      estado: 'LISTO',
    },
    'B2-02-0': {
      titulo: 'Cuota por grupo, 100 %',
      sub: 'Panel IF.Data · cuota por grupo · apilado al 100 %',
      fuente: IFDATA,
      componente: 'area_apilada',
      datos: [],
      estado: 'LISTO',
    },
    'B2-02-1': {
      titulo: 'Cuota por banco, hace dos años y hoy',
      sub: 'Panel IF.Data · cuota de crédito y de depósitos · hace dos años y hoy',
      fuente: IFDATA,
      componente: 'pesas',
      datos: [],
      banco: true,
      estado: 'LISTO',
    },
    'B2-03-0': {
      titulo: 'Cuota de cada banco en cada modalidad',
      sub: 'Panel IF.Data · cuota por modalidad · filas ordenadas por tamaño',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'heatmap',
      datos: [],
      banco: true,
      estado: 'DERIVAR',
    },
    'B2-03-1': {
      titulo: 'Cambio de cuota en 4T por modalidad y grupo',
      sub: 'Panel IF.Data · cambio de cuota en 4 trimestres · modalidad × grupo',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'heatmap',
      datos: [],
      estado: 'DERIVAR',
    },
    'B2-04-0': {
      titulo: 'Inadimplencia por tipo de institución',
      sub: 'SCR · mora por tipo de institución · PF y PJ en dos paneles',
      fuente: `${SCRDATA}; ${CALC}`,
      componente: 'linea',
      datos: [],
      estado: 'DERIVAR',
    },
    'B2-04-1': {
      titulo: 'Crecimiento vs. mora por grupo',
      sub: 'Panel IF.Data · crecimiento (media de 4T) vs. NPL · trayectoria de 8 trimestres',
      fuente: `${IFDATA}; ${CALC}`,
      componente: 'burbujas_trayectoria',
      datos: [],
      estado: 'LISTO',
    },
    'B2-05-0': {
      titulo: 'Reclamos por millón de clientes, último trimestre',
      sub: 'BCB · reclamos por millón de clientes · último trimestre',
      fuente: OLINDA,
      componente: 'barras_h',
      datos: [],
      banco: true,
      estado: 'DERIVAR',
    },
    'B2-05-1': {
      titulo: 'Tarifas de un paquete estándar por grupo',
      sub: 'BCB · tarifas del paquete estándar · por grupo',
      fuente: `${OLINDA}; ${CALC}`,
      componente: 'tabla',
      datos: [],
      estado: 'DERIVAR',
    },
    'B2-05-2': {
      titulo: 'Pix como % de los pagos minoristas',
      sub: 'Sistema BCB · Pix como % de los pagos minoristas',
      fuente: SGS,
      componente: 'linea',
      datos: [],
      estado: 'DERIVAR',
    },
  },
};
