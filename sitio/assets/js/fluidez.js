/* Agrupa el trabajo visual: una ejecución por clave y fotograma. */
export function crearColaVisual({
  solicitar = (fn) => requestAnimationFrame(fn),
  cancelar = (id) => cancelAnimationFrame(id),
} = {}) {
  const pendientes = new Map();
  let frame = null;
  function ejecutar() {
    frame = null;
    const trabajos = [...pendientes.values()];
    pendientes.clear();
    for (const trabajo of trabajos) trabajo();
  }
  return {
    agendar(clave, trabajo) {
      pendientes.set(clave, trabajo);
      if (frame === null) frame = solicitar(ejecutar);
    },
    quitar(clave) {
      pendientes.delete(clave);
      if (!pendientes.size && frame !== null) {
        cancelar(frame);
        frame = null;
      }
    },
  };
}
