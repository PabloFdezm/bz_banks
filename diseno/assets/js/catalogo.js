import { activarComponentes, icono, nombresIconos, anunciar, estadoBoton } from './sistema.js';

activarComponentes();
document.querySelectorAll('[data-icon]').forEach(n => n.innerHTML = icono(n.dataset.icon));
const css = getComputedStyle(document.documentElement);
const token = nombre => css.getPropertyValue(nombre).trim();
const toast = document.getElementById('toast');
let toastTimer;
function avisar(texto) {
  toast.textContent = texto;
  toast.hidden = false;
  anunciar(texto);
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.hidden = true; }, 3600);
}
async function copiar(texto) {
  try {
    if (navigator.clipboard?.writeText && window.isSecureContext) await navigator.clipboard.writeText(texto);
    else {
      const area = document.createElement('textarea');
      area.value = texto; area.className = 'solo-lector';
      document.body.append(area); area.select();
      const ok = document.execCommand('copy'); area.remove();
      if (!ok) throw new Error('clipboard');
    }
    avisar('Copiado al portapapeles.');
  } catch {
    const dialogo = document.getElementById('copia-manual');
    document.getElementById('texto-copia').value = texto;
    dialogo._mbOrigen = document.activeElement;
    dialogo.showModal();
    document.getElementById('texto-copia').select();
  }
}

const TOKENS_COLOR = [
  ['--mb-interactive', 'Acción', 'interfaz'],
  ['--mb-text-primary', 'Texto principal', 'interfaz'],
  ['--mb-text-secondary', 'Texto secundario', 'interfaz'],
  ['--mb-text-helper', 'Ayuda', 'interfaz'],
  ['--mb-background', 'Fondo', 'interfaz'],
  ['--mb-layer', 'Superficie', 'interfaz'],
  ['--mb-layer-selected', 'Selección', 'interfaz'],
  ['--mb-border-control', 'Borde de control', 'interfaz'],
  ['--mb-data-01', 'Azul', 'datos'],
  ['--mb-data-02', 'Petróleo', 'datos'],
  ['--mb-data-03', 'Acero', 'datos'],
  ['--mb-data-04', 'Ciruela', 'datos'],
  ['--mb-data-05', 'Acero claro', 'datos'],
  ['--mb-data-worse', 'Deterioro · texto', 'datos'],
  ['--mb-data-gap', 'Brecha · relleno', 'datos'],
  ['--mb-data-reference', 'Referencia', 'datos'],
];
function luminancia(hex) {
  const rgb = hex.replace('#', '').match(/.{2}/g).map(c => parseInt(c, 16) / 255).map(c => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4);
  return .2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2];
}
TOKENS_COLOR.forEach(([nombre, titulo, tipo]) => {
  const valor = token(nombre);
  const boton = document.createElement('button');
  boton.type = 'button'; boton.className = 'ds-swatch';
  boton.setAttribute('aria-label', `Copiar ${nombre}: ${valor}`);
  const color = document.createElement('span');
  color.className = 'ds-swatch-color'; color.style.background = valor;
  const info = document.createElement('span'); info.className = 'ds-swatch-info';
  const name = document.createElement('span'); name.className = 'ds-swatch-name'; name.textContent = titulo;
  const code = document.createElement('span'); code.className = 'ds-swatch-code'; code.textContent = `${nombre} · ${valor}`;
  info.append(name, code);
  if (/^#[0-9a-f]{6}$/i.test(valor)) {
    const ratio = 1.05 / (luminancia(valor) + .05);
    const r = document.createElement('span'); r.className = 'ds-swatch-ratio';
    r.textContent = `${ratio.toFixed(2)}:1 sobre blanco · ${ratio >= 4.5 ? 'apto para texto' : 'uso gráfico o superficie'}`;
    info.append(r);
  }
  boton.append(color, info); boton.addEventListener('click', () => copiar(`${nombre}: ${valor};`));
  document.getElementById(`paleta-${tipo}`).append(boton);
});

document.getElementById('descargar-tokens').addEventListener('click', () => {
  const nombres = [...new Set([...TOKENS_COLOR.map(t => t[0]), '--mb-text-on-color', '--mb-border-subtle', '--mb-border-strong', '--mb-focus', '--mb-support-error', '--mb-support-success', '--mb-font-body', '--mb-font-display', '--mb-font-mono', '--mb-control-height', '--mb-radius-control', '--mb-motion-in', '--mb-motion-out', '--mb-motion-feedback', ...Array.from({ length: 9 }, (_, i) => `--mb-space-0${i + 1}`)])];
  const datos = { name: 'Monitor Brasil', version: '1.0', theme: 'light', source: 'assets/css/tokens.css', tokens: Object.fromEntries(nombres.map(n => [n, token(n)])) };
  const url = URL.createObjectURL(new Blob([JSON.stringify(datos, null, 2)], { type: 'application/json;charset=utf-8' }));
  const a = document.createElement('a'); a.href = url; a.download = 'monitor-brasil-tokens.json';
  a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); avisar('Se descargaron los tokens del tema claro.');
});
document.querySelectorAll('[data-copy-code]').forEach(b => b.addEventListener('click', () => copiar(b.closest('.ds-code').querySelector('code').textContent)));
nombresIconos.forEach(nombre => {
  const b = document.createElement('button'); b.type = 'button'; b.className = 'ds-icon-tile';
  b.setAttribute('aria-label', `Copiar icono ${nombre}`);
  b.innerHTML = icono(nombre);
  const label = document.createElement('span'); label.textContent = nombre; b.append(label);
  b.addEventListener('click', () => copiar(`icono('${nombre}')`));
  document.getElementById('iconos-grid').append(b);
});
document.querySelectorAll('[data-demo-action]').forEach(b => b.addEventListener('click', () => avisar(b.dataset.demoAction)));

const buscar = document.getElementById('buscar');
const bloques = [...document.querySelectorAll('[data-search]')];
const normalizar = v => v.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
function filtrar() {
  const q = normalizar(buscar.value.trim()); let visibles = 0;
  bloques.forEach(n => {
    n.hidden = !!q && !normalizar(`${n.dataset.search} ${n.textContent}`).includes(q);
    if (!n.hidden) visibles++;
  });
  document.getElementById('sin-resultados').hidden = visibles > 0;
  document.getElementById('resultados').textContent = q ? `${visibles} secciones coinciden con la búsqueda.` : 'Busca por componente, token o patrón.';
  document.getElementById('limpiar').hidden = !q;
}
buscar.addEventListener('input', filtrar);
document.getElementById('limpiar').addEventListener('click', () => { buscar.value = ''; filtrar(); buscar.focus(); });
document.querySelectorAll('.ds-sidebar a').forEach(a => a.addEventListener('click', () => {
  if (buscar.value) { buscar.value = ''; filtrar(); }
}));
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    const actual = entries.filter(e => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (!actual) return;
    document.querySelectorAll('.ds-sidebar a').forEach(a => {
      if (a.hash === `#${actual.target.id}`) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    });
  }, { rootMargin: '-10% 0px -65% 0px' });
  bloques.forEach(n => observer.observe(n));
}

document.getElementById('filtro-ejemplo').addEventListener('mb:seleccion', e => {
  document.getElementById('filtro-lectura').textContent = `Vista seleccionada: ${e.detail.value}.`;
  anunciar(`Vista ${e.detail.value} seleccionada.`);
});
const multi = document.getElementById('multi-ejemplo');
multi.addEventListener('change', () => {
  const cantidad = multi.querySelectorAll('input:checked').length;
  document.getElementById('multi-cantidad').textContent = `${cantidad} seleccionadas`;
});

const formulario = document.getElementById('formulario-vista');
const nombre = document.getElementById('nombre-vista');
const error = document.getElementById('nombre-error');
function validar() {
  const valor = nombre.value.trim();
  const mensaje = !valor ? 'Escribe un nombre para identificar la vista.' : valor.length < 3 ? 'Usa al menos 3 caracteres.' : valor.length > 60 ? 'Usa un máximo de 60 caracteres.' : '';
  error.textContent = mensaje; error.hidden = !mensaje;
  nombre.setAttribute('aria-invalid', String(!!mensaje));
  return !mensaje;
}
nombre.addEventListener('blur', validar);
formulario.addEventListener('submit', async ev => {
  ev.preventDefault();
  const mensaje = document.getElementById('formulario-resultado');
  mensaje.hidden = true;
  if (!validar()) { nombre.focus(); anunciar(error.textContent); return; }
  const restaurar = estadoBoton(document.getElementById('guardar-vista'));
  await new Promise(resolve => setTimeout(resolve, 600));
  try {
    sessionStorage.setItem('mb:catalogo:vista', nombre.value.trim());
    mensaje.className = 'mb-notice mb-notice--success';
    mensaje.textContent = `Vista «${nombre.value.trim()}» guardada en esta pestaña de ejemplo.`;
  } catch {
    mensaje.className = 'mb-notice mb-notice--error';
    mensaje.textContent = 'El navegador bloqueó el almacenamiento. Habilita el almacenamiento de la sesión y vuelve a guardar.';
  } finally { restaurar(); mensaje.hidden = false; }
});

const estado = document.getElementById('estado-ejemplo');
const estados = {
  listo: ['correcto', 'Lectura disponible', 'Selecciona una serie o amplía el gráfico para consultar el detalle.', ''],
  carga: ['ayuda', 'Cargando la lectura', 'Consultando las series. El espacio del gráfico se conserva.', ''],
  vacio: ['buscar', 'No hay series seleccionadas', 'Selecciona al menos una serie para construir la comparación.', ''],
  error: ['error', 'No se pudo cargar la lectura', 'La consulta de ejemplo falló. Vuelve a intentarlo.', 'mb-notice--error'],
  exito: ['correcto', 'Vista actualizada', 'La selección de ejemplo se aplicó a la lectura.', 'mb-notice--success'],
};
function mostrarEstado(valor) {
  const [ic, titulo, texto, clase] = estados[valor];
  estado.setAttribute('aria-busy', String(valor === 'carga'));
  const notice = document.createElement('div'); notice.className = `mb-notice ${clase}`;
  const icon = document.createElement('span'); icon.innerHTML = icono(ic);
  const contenido = document.createElement('div');
  const t = document.createElement('strong'); t.className = 'mb-notice-title'; t.textContent = titulo;
  const p = document.createElement('p'); p.textContent = texto;
  contenido.append(t, p);
  if (valor === 'error') {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'mb-button mb-button--compact'; b.textContent = 'Reintentar';
    b.style.marginTop = 'var(--mb-space-03)';
    b.addEventListener('click', () => {
      document.getElementById('selector-estado').value = 'carga'; mostrarEstado('carga');
      setTimeout(() => { document.getElementById('selector-estado').value = 'exito'; mostrarEstado('exito'); }, 900);
    });
    contenido.append(b);
  }
  notice.append(icon, contenido); estado.replaceChildren(notice);
}
document.getElementById('selector-estado').addEventListener('change', e => mostrarEstado(e.target.value));
mostrarEstado('listo');

// Datos deliberadamente ilustrativos: no son las lecturas actuales del monitor.
const ejemplo = [2.4, 2.7, 2.5, 2.9, 3.2, 3.1];
const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'];
const grafico = document.getElementById('grafico-ejemplo');
const linea = document.getElementById('linea-ejemplo');
const cursor = document.getElementById('cursor-ejemplo');
const punto = document.getElementById('punto-ejemplo');
let anchoGrafico = 640;
const margenIzquierdo = 40, margenDerecho = 16;
const x = i => margenIzquierdo + i * (anchoGrafico - margenIzquierdo - margenDerecho) / (ejemplo.length - 1);
const y = v => 188 - (v - 2) * (164 / 1.5);
const rango = document.getElementById('mes-ejemplo');
function mostrarLectura() {
  const i = Number(rango.value);
  document.querySelectorAll('[data-lectura-mes]').forEach(n => n.textContent = `${meses[i]} · ejemplo`);
  document.querySelectorAll('[data-lectura-valor]').forEach(n => n.textContent = `${ejemplo[i].toFixed(1).replace('.', ',')} %`);
  document.getElementById('mes-detalle').value = String(i);
  rango.setAttribute('aria-valuetext', `${meses[i]}: ${ejemplo[i].toFixed(1).replace('.', ',')} por ciento, ejemplo`);
  cursor.setAttribute('x1', x(i)); cursor.setAttribute('x2', x(i));
  punto.setAttribute('cx', x(i)); punto.setAttribute('cy', y(ejemplo[i]));
}
rango.addEventListener('input', mostrarLectura);

// Una unidad SVG equivale a un píxel del contenedor: los ejes conservan 12 px.
// Se redistribuyen los puntos; no se escala la tipografía de un lienzo de 640 px.
function dibujarGrafico() {
  const ancho = Math.round(grafico.getBoundingClientRect().width);
  if (ancho <= 0) return;
  anchoGrafico = ancho;
  grafico.setAttribute('viewBox', `0 0 ${anchoGrafico} 240`);
  grafico.setAttribute('width', anchoGrafico);
  grafico.setAttribute('height', 240);
  const ejes = grafico.querySelector('g');
  const fragmento = document.createDocumentFragment();
  const crear = (tag, attrs, texto) => {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
    if (texto != null) n.textContent = texto;
    fragmento.append(n);
  };
  [2, 2.5, 3, 3.5].forEach(v => {
    crear('line', { class: 'grid-line', x1: x(0), y1: y(v), x2: x(5), y2: y(v) });
    crear('text', { x: margenIzquierdo - 8, y: y(v) + 4, 'text-anchor': 'end' }, v.toFixed(1).replace('.', ','));
  });
  ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'].forEach((mes, i) => crear('text', { x: x(i), y: 220, 'text-anchor': 'middle' }, mes));
  ejes.replaceChildren(fragmento);
  document.getElementById('referencia-ejemplo').setAttribute('d', `M${x(0)} ${y(3)}H${x(5)}`);
  linea.setAttribute('d', ejemplo.map((v, i) => `${i ? 'L' : 'M'}${x(i)} ${y(v)}`).join(' '));
  mostrarLectura();
}
dibujarGrafico();
new ResizeObserver(dibujarGrafico).observe(grafico);
document.querySelectorAll('[data-legend]').forEach(b => b.addEventListener('click', () => {
  const visible = b.getAttribute('aria-pressed') !== 'true';
  b.setAttribute('aria-pressed', String(visible));
  if (b.dataset.legend === 'serie') { [linea, punto, cursor].forEach(n => n.toggleAttribute('hidden', !visible)); rango.disabled = !visible; }
  else document.getElementById('referencia-ejemplo').toggleAttribute('hidden', !visible);
  avisar(`${b.dataset.legend === 'serie' ? 'Serie ilustrativa' : 'Referencia'} ${visible ? 'visible' : 'oculta'}.`);
}));
grafico.addEventListener('click', ev => {
  if (rango.disabled) return;
  const rect = grafico.getBoundingClientRect();
  const puntoX = (ev.clientX - rect.left) * anchoGrafico / rect.width;
  const paso = (anchoGrafico - margenIzquierdo - margenDerecho) / (ejemplo.length - 1);
  rango.value = Math.max(0, Math.min(5, Math.round((puntoX - margenIzquierdo) / paso)));
  mostrarLectura();
});
document.getElementById('mes-detalle').addEventListener('change', e => { rango.value = e.target.value; mostrarLectura(); });
document.getElementById('abrir-detalle').addEventListener('click', () => document.getElementById('mes-detalle').value = rango.value);
