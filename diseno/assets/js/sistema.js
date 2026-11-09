/* Monitor Brasil · utilidades compartidas. Sin dependencia de datos ni gráficos. */
export const movimientoReducido = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
export function animar(nodo, cuadros, salida = false) {
  if (!nodo?.animate || movimientoReducido()) return null;
  const css = getComputedStyle(document.documentElement);
  return nodo.animate(cuadros, {
    duration: parseFloat(css.getPropertyValue(salida ? '--motion-out' : '--motion-in')) || 180,
    easing: salida ? 'ease-in' : 'cubic-bezier(.16, 1, .3, 1)',
  });
}

const TRAZOS = Object.freeze({
  menu: 'M4 6h16M4 12h16M4 18h16',
  cerrar: 'm6 6 12 12M18 6 6 18',
  ampliar: 'M14 4h6v6M10 20H4v-6M20 4l-7 7M4 20l7-7',
  flecha: 'M4 12h16m-6-6 6 6-6 6',
  presentar: 'M4 4h16v12H4zM12 16v4m-4 0h8',
  descargar: 'M12 4v11m-5-5 5 5 5-5M5 20h14',
  buscar: 'M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13M16 16l5 5',
  copiar: 'M8 8h12v12H8zM16 8V4H4v12h4',
  ayuda: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18M9.5 9a2.5 2.5 0 1 1 4 2c-1 .7-1.5 1-1.5 2M12 16v.5',
  correcto: 'm5 12 4 4L19 6',
  aviso: 'M12 3 2 21h20L12 3zM12 9v5M12 17v.5',
  error: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18M12 7v6M12 16v.5',
});
export const nombresIconos = Object.freeze(Object.keys(TRAZOS));
export function icono(nombre) {
  return `<svg class="od-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="${TRAZOS[nombre] || TRAZOS.flecha}"/></svg>`;
}

let region;
let avisoTimer;
export function anunciar(texto) {
  if (!region?.isConnected) {
    region = document.createElement('div');
    region.className = 'solo-lector';
    region.setAttribute('role', 'status');
    region.setAttribute('aria-live', 'polite');
    region.setAttribute('aria-atomic', 'true');
    document.body.append(region);
  }
  clearTimeout(avisoTimer);
  avisoTimer = setTimeout(() => { region.textContent = texto; }, 100);
}

/** Cambia un botón durante una operación y devuelve una función de restauración. */
export function estadoBoton(boton, texto = 'Guardando…') {
  const contenido = [...boton.childNodes];
  const disabled = boton.disabled;
  const busy = boton.getAttribute('aria-busy');
  boton.replaceChildren(document.createTextNode(texto));
  boton.disabled = true;
  boton.setAttribute('aria-busy', 'true');
  let restaurado = false;
  return () => {
    if (restaurado) return;
    restaurado = true;
    boton.replaceChildren(...contenido);
    boton.disabled = disabled;
    if (busy === null) boton.removeAttribute('aria-busy');
    else boton.setAttribute('aria-busy', busy);
  };
}

const RAICES = new WeakSet();
/** Inicializa únicamente controles data-mb-*. Es idempotente para una misma raíz. */
export function activarComponentes(raiz = document) {
  if (RAICES.has(raiz)) return;
  RAICES.add(raiz);
  const obtener = id => document.getElementById(id);
  function cerrarAyudas(excepto) {
    raiz.querySelectorAll('[data-mb-help][aria-expanded="true"]').forEach(b => {
      if (b === excepto) return;
      b.setAttribute('aria-expanded', 'false');
      const p = obtener(b.getAttribute('aria-controls'));
      if (p) p.hidden = true;
    });
  }
  raiz.addEventListener('click', ev => {
    const target = ev.target instanceof Element ? ev.target : ev.target.parentElement;
    const segmento = target?.closest('[data-mb-segment] button[data-value]');
    if (segmento && !segmento.disabled) {
      const grupo = segmento.closest('[data-mb-segment]');
      grupo.querySelectorAll('button[data-value]').forEach(b => b.setAttribute('aria-pressed', String(b === segmento)));
      grupo.dispatchEvent(new CustomEvent('mb:seleccion', { bubbles: true, detail: { value: segmento.dataset.value } }));
    }
    const ayuda = target?.closest('[data-mb-help]');
    if (ayuda) {
      const panel = obtener(ayuda.getAttribute('aria-controls'));
      if (!panel) return;
      const abrir = ayuda.getAttribute('aria-expanded') !== 'true';
      cerrarAyudas(ayuda);
      ayuda.setAttribute('aria-expanded', String(abrir));
      panel.hidden = !abrir;
      if (abrir) {
        const rect = ayuda.getBoundingClientRect();
        const ancho = Math.min(288, innerWidth - 32);
        Object.assign(panel.style, { position: 'fixed', width: `${ancho}px`, right: 'auto', left: `${Math.min(Math.max(16, rect.left), innerWidth - ancho - 16)}px`, top: `${rect.bottom + 8}px` });
        if (panel.getBoundingClientRect().bottom > innerHeight - 16) panel.style.top = `${Math.max(16, rect.top - panel.offsetHeight - 8)}px`;
      }
    } else if (!target?.closest('.mb-tooltip-panel')) cerrarAyudas();
    const abrir = target?.closest('[data-mb-dialog-open]');
    if (abrir) {
      const dialogo = obtener(abrir.dataset.mbDialogOpen);
      if (dialogo instanceof HTMLDialogElement && !dialogo.open) {
        dialogo._mbOrigen = abrir;
        dialogo.showModal();
        animar(dialogo, [{ opacity: .4, transform: 'translateY(8px)' }, { opacity: 1, transform: 'translateY(0)' }]);
      }
    }
    const cerrar = target?.closest('[data-mb-dialog-close]');
    if (cerrar) cerrar.closest('dialog')?.close();
  });
  raiz.addEventListener('keydown', ev => {
    if (ev.key !== 'Escape') return;
    const ayuda = raiz.querySelector('[data-mb-help][aria-expanded="true"]');
    if (ayuda) { cerrarAyudas(); ayuda.focus(); ev.preventDefault(); }
  });
  raiz.addEventListener('focusout', ev => {
    if (ev.target.closest?.('.mb-tooltip') && !ev.target.closest('.mb-tooltip').contains(ev.relatedTarget)) cerrarAyudas();
  });
  raiz.addEventListener('close', ev => {
    if (ev.target instanceof HTMLDialogElement) ev.target._mbOrigen?.focus({ preventScroll: true });
  }, true);
  window.addEventListener('resize', () => cerrarAyudas(), { passive: true });
  window.addEventListener('scroll', () => cerrarAyudas(), { passive: true });
}
