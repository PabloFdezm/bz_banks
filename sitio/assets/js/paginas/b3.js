/* B3 · Crédito — v3 (3-nov), tablero 06 del canvas. Cuatro láminas con el gráfico a la izquierda y la
   tabla estándar a la derecha (misma proporción y alto en todas, para que al presentar nada salte).
   Todo viene de preparar_gold_bancos_pag_credito.py (bk_cred_tablas, bk_cred_series).
   Versiones anteriores: b3_v1.js.txt, b3_v2.js.txt. Sin imports: contar_tarjetas.mjs lee este archivo. */
const SGS = 'BCB, SGS';
const AZUL = '#2E5C8A', ACERO = '#8FA3BC', TINTA = '#24324A', COBRE = '#A85E24', ARENA = '#E7CDB6';
const MESES = 36;
const etiquetaMes = (f) => `${f.slice(5, 7)}/${f.slice(2, 4)}`;
const etiquetaTrim = (f) => `${Math.ceil(Number(f.slice(5, 7)) / 3)}T${f.slice(2, 4)}`;

const bloque = (d, b) => (d.bk_cred_tablas || []).filter((f) => f.bloque === b).sort((x, y) => x.orden - y.orden);
const serie = (d, s) => (d.bk_cred_series || []).filter((f) => f.serie === s).sort((x, y) => (x.fecha < y.fecha ? -1 : 1));

// 3-nov: vista Barras (último a/a) o Líneas (historia del a/a); el Total va siempre, en cobre, para contrastar.
// En Líneas la leyenda es la de ECharts: clic en un tipo lo oculta o lo muestra (como en Power BI).
const PALETA = { 'Tarjeta': '#2E5C8A', 'Consignado': '#5B8DB8', 'Personal no consignado': '#9DBBDB', 'Vehículos': '#24324A',
  'Inmobiliario (personas)': '#2F7A86', 'Rural (personas)': '#7FB5B9', 'Empresas libre': '#6F7884', 'BNDES (empresas)': '#8FA3BC',
  'Rural (empresas)': '#B79C6A', 'Inmobiliario (empresas)': '#5C4B8A' };
function armarTipos(d, est) {
  const f = bloque(d, 'tipos');
  if (!f.length) return { enPreparacion: 'falta bk_cred_tablas' };
  const tot = f.find((x) => x.fila === 'Total');
  const mods = f.filter((x) => x.fila !== 'Total');
  if ((est.seleccion?.grafico || 'barras') === 'barras') {
    const filas = mods.map((x) => ({ nombre: x.fila, valor: x.d12 * 100, color: x.grupo === 'Empresas' ? ACERO : AZUL })).sort((a, b) => b.valor - a.valor);
    if (tot) filas.unshift({ nombre: 'Total', valor: tot.d12 * 100, color: COBRE });
    return { componente: 'barras_signo', filas, unidad: '%', decimales: 1,
      leyenda: [{ nombre: 'Total', color: COBRE }, { nombre: 'Personas', color: AZUL }, { nombre: 'Empresas', color: ACERO }] };
  }
  const fechas = [...new Set(serie(d, 'aa|Total').map((x) => x.fecha))].slice(-MESES);
  const val = (n) => { const m = new Map(serie(d, `aa|${n}`).map((x) => [x.fecha, x.valor * 100])); return fechas.map((q) => m.get(q) ?? null); };
  const lineas = mods.map((x) => ({ nombre: x.fila, color: PALETA[x.fila] || ACERO, valores: val(x.fila), grosor: 1.6 }));
  lineas.unshift({ nombre: 'Total', color: COBRE, valores: val('Total'), grosor: 3, z: 9 });
  return { componente: 'barras_linea', categorias: fechas.map(etiquetaMes), barras: [], lineas, leyendaInteractiva: true, leyenda: [],
    formatoIzq: (v) => `${v} %`, intervalo: 5 };
}
function armarContrib(d) {
  const f = bloque(d, 'contrib').filter((x) => x.fila !== 'Total');
  if (!f.length) return { enPreparacion: 'falta bk_cred_tablas' };
  return { filas: f.map((x) => ({ nombre: x.fila, valor: x.d1 })).sort((a, b) => b.valor - a.valor), unidad: 'pp', decimales: 2, colorPos: AZUL, colorNeg: COBRE };
}
function armarConc(d) {
  const c = serie(d, 'conc12_aa'), s = serie(d, 'stock_aa');
  if (!c.length) return { enPreparacion: 'falta bk_cred_series' };
  const fechas = [...new Set(s.map((x) => x.fecha))].slice(-MESES);
  const val = (arr) => { const m = new Map(arr.map((x) => [x.fecha, x.valor * 100])); return fechas.map((f) => m.get(f) ?? null); };
  return { categorias: fechas.map(etiquetaMes), barras: [], lineas: [{ nombre: 'Concesiones libres 12m, a/a', color: AZUL, valores: val(c) }, { nombre: 'Saldo total, a/a', color: TINTA, valores: val(s) }], formatoIzq: (v) => `${v} %`, intervalo: 5 };
}
function armarCiclo(d) {
  const n = serie(d, 'cpib_nivel').slice(-16);
  if (!n.length) return { enPreparacion: 'falta bk_cred_series' };
  const fechas = n.map((x) => x.fecha);
  const val = (s) => { const m = new Map(serie(d, s).map((x) => [x.fecha, x.valor])); return fechas.map((f) => m.get(f) ?? null); };
  return { categorias: fechas.map(etiquetaTrim), barras: [{ nombre: 'Brecha (pp, eje der.)', color: ARENA, valores: val('cpib_brecha') }],
    lineas: [{ nombre: 'Crédito/PIB', color: TINTA, valores: val('cpib_nivel') }, { nombre: 'Tendencia HP', color: ACERO, valores: val('cpib_tendencia'), discontinua: true }],
    // Nivel con escala propia; brecha simétrica en torno a cero para que las barras no cuelguen del borde
    rangoIzq: { escala: true }, rangoDer: (() => { const m = Math.ceil(Math.max(...val('cpib_brecha').map((v) => Math.abs(v ?? 0)), 1)); return { min: -m, max: m }; })(),
    ejeBarras: 'der', formatoIzq: (v) => `${v} %`, formatoDer: (v) => `${v} pp`, intervalo: 1 };
}
const tabla = (b, total = 'Total') => (d) => {
  const f = bloque(d, b).map((x) => ({ ...x, destacar: x.fila === total }));
  return f.length ? { filas: f } : { enPreparacion: 'falta bk_cred_tablas' };
};
const fila2 = (a, b, alto = 420) => [[{ clave: a, ancho: 4, alto }, { clave: b, ancho: 5, alto }]]; // alto mayor donde la tabla tiene 11–12 filas // 4-nov: la tabla va en el lado ancho

export default {
  clave: 'B3',
  ruta: 'credito',
  nombre: 'Crédito',
  rotulo: 'SISTEMA BCB · MENSUAL',
  usaBanco: false,

  secciones: [
    { numero: '01', nombre: 'Por tipo', frecuencia: 'Mensual · SGS', pregunta: 'Crecimiento a/a del saldo de cada modalidad.',
      riel: [{ tipo: 'selector', clave: 'grafico', rotulo: 'GRÁFICO', defecto: 'barras', opciones: [{ valor: 'barras', nombre: 'Barras · último' }, { valor: 'lineas', nombre: 'Líneas · historia' }] }],
      filas: fila2('B3-01', 'B3-02', 570) },
    { numero: '02', nombre: 'Qué lo movió', frecuencia: 'Mensual · SGS', pregunta: 'Contribución de cada modalidad al crecimiento del total en el último mes.', filas: fila2('B3-03', 'B3-04', 590) },
    { numero: '03', nombre: 'Crédito nuevo', frecuencia: 'Mensual · SGS', pregunta: 'Concesiones contra stock: si lo que se presta crece más que el saldo, el saldo tiende a acelerar.', filas: fila2('B3-05', 'B3-06') },
    { numero: '04', nombre: 'Ciclo', frecuencia: 'Trimestral · SGS 20622', pregunta: 'Crédito/PIB contra su tendencia: la brecha dice si el crédito está sobre o bajo lo sostenible.', filas: fila2('B3-07', 'B3-08') },
  ],

  tarjetas: {
    'B3-01': { titulo: 'Crecimiento a/a por tipo', plana: true,
      fuente: `${SGS}; consignado = privado + público + INSS`, componente: 'barras_signo', datos: ['bk_cred_tablas', 'bk_cred_series'], armar: armarTipos, estado: 'LISTO' },
    'B3-02': { titulo: 'Cartera por tipo', plana: true, nota: 'Último: saldo en R$ mil millones. Share: peso en la cartera total. Cambios en %. 3m/3m y 12m/12m: promedio de la ventana contra la anterior.',
      fuente: SGS, componente: 'tabla_estandar', datos: ['bk_cred_tablas'], armar: tabla('tipos'), estado: 'LISTO' },
    'B3-03': { titulo: 'Contribución al crecimiento m/m', plana: true, leyenda: [{ nombre: 'Suma', color: AZUL }, { nombre: 'Resta', color: COBRE }],
      fuente: `${SGS}; Otros = resto de libre y direccionado`, componente: 'barras_signo', datos: ['bk_cred_tablas'], armar: armarContrib, estado: 'LISTO' },
    'B3-04': { titulo: 'Contribución por tipo', plana: true, nota: 'Último: saldo en R$ mil millones. Share: peso en la cartera total. Cambios: contribución al crecimiento del total, en pp; suman el total.',
      fuente: SGS, componente: 'tabla_estandar', datos: ['bk_cred_tablas'], armar: tabla('contrib', 'Total'), estado: 'LISTO' },
    'B3-05': { titulo: 'Concesiones contra saldo, a/a', plana: true, leyenda: [{ nombre: 'Concesiones libres 12m, a/a', color: AZUL }, { nombre: 'Saldo total, a/a', color: TINTA }],
      fuente: `${SGS} 20631, 20539`, componente: 'barras_linea', datos: ['bk_cred_series'], armar: armarConc, estado: 'LISTO' },
    'B3-06': { titulo: 'Concesiones y saldo', plana: true, nota: 'Último: flujo del mes (concesiones) o saldo, en R$ mil millones. Cambios en %; 12m/12m de concesiones compara sumas de doce meses.',
      fuente: `${SGS} 20631, 20633, 20632, 20539`, componente: 'tabla_estandar', datos: ['bk_cred_tablas'], armar: tabla('conc', 'Saldo total'), estado: 'LISTO' },
    'B3-07': { titulo: 'Crédito/PIB, tendencia y brecha', plana: true, leyenda: [{ nombre: 'Crédito/PIB (%)', color: TINTA }, { nombre: 'Tendencia HP (%)', color: ACERO, discontinua: true }, { nombre: 'Brecha (pp, eje der.)', color: ARENA }],
      fuente: `${SGS} 20622; HP unilateral, λ = 400.000`, componente: 'barras_linea', datos: ['bk_cred_series'], armar: armarCiclo, estado: 'LISTO' },
    'B3-08': { titulo: 'Ciclo del crédito', plana: true, nota: 'Último en % (crédito/PIB, tendencia) y pp (brecha). Cambios en pp. El BIS mide crédito total al sector privado y su brecha difiere.',
      fuente: SGS, componente: 'tabla_estandar', datos: ['bk_cred_tablas'], armar: tabla('ciclo', 'Brecha'), estado: 'LISTO' },
  },
};
