"""Verifica el sitio v2 (páginas de diseno/canvas/paginas.json) con un Chromium real.

Qué comprueba en cada página y cada ancho de --anchos:
  1. responde 200 y carga sin errores de página ni de consola, y el «Cargando…» desaparece;
  2. tiene tarjetas (.card) fuera de los diálogos y ningún «{{» sin reemplazar en el texto visible;
  3. no hay scroll horizontal de la página;
  4. los rótulos del eje horizontal de cada gráfico no se pisan (cajas de texto de la misma fila sin solaparse);
  5. con --url (sitio publicado, fuentes reales de Google): IBM Plex Sans, IBM Plex Mono y Bricolage Grotesque
     quedan en document.fonts con status «loaded». No se usa document.fonts.check: da falso negativo con Plex Mono por
     los subconjuntos unicode. En local las fuentes se cortan (no dependen de la red) y este punto no se mira.
Además, una vez por página a 1920: «Cómo leer» abre y cierra con Esc.

En local levanta su propio servidor (python -m http.server sobre sitio/) y lo cierra al terminar; no usa uno que ya
estuviera corriendo. Con --captura DIR guarda una captura de página completa por página y ancho.

Uso: python -X utf8 herramientas/verificar_f1.py [--puerto 8080] [--url BASE] [--anchos 1920,1280,390] [--captura DIR]
     (p. ej. --url https://banks-bz.pages.dev --anchos 1920,1280,390)
"""
import argparse
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
SITIO = RAIZ / "sitio"
FUENTES = ["IBM Plex Sans", "IBM Plex Mono", "Bricolage Grotesque"]

# Rótulos del eje horizontal: mes («oct-24»), trimestre («1T25») o año («2024»).
JS_REVISION = r"""() => {
  const R = document.getElementById('v2-raiz');
  const visible = (e) => !e.closest('[role=dialog]') && !e.closest('dialog');
  const cards = [...R.querySelectorAll('.card')].filter(visible).length;
  const texto = R.innerText || '';
  const pisados = [];
  R.querySelectorAll('dc-import[name="Grafico"]').forEach((g, k) => {
    if (!visible(g)) return;
    const rot = [...g.querySelectorAll('div')].filter((d) => d.children.length === 0
      && /^([a-z]{3}-\d{2}|\dT\d{2}|\d{4})$/.test(d.textContent.trim()))
      .map((d) => ({ t: d.textContent.trim(), r: d.getBoundingClientRect() })).filter((x) => x.r.width > 0);
    const filas = {};
    rot.forEach((x) => { (filas[Math.round(x.r.top)] ||= []).push(x); });
    Object.values(filas).forEach((f) => {
      f.sort((a, b) => a.r.left - b.r.left);
      for (let i = 1; i < f.length; i++) if (f[i].r.left < f[i - 1].r.right - 0.5) pisados.push(k + ':' + f[i - 1].t + '/' + f[i].t);
    });
  });
  return {
    cards, llaves: (texto.match(/\{\{/g) || []).length, cargando: !!R.querySelector('.v2-carga'),
    scroll: document.documentElement.scrollWidth - document.documentElement.clientWidth, pisados,
    fuentes: [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family.replace(/"/g, '')),
  };
}"""


def paginas() -> list[dict]:
    return json.loads((RAIZ / "diseno" / "canvas" / "paginas.json").read_text(encoding="utf-8"))["paginas"]


def puerto_libre(puerto: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", puerto), timeout=0.3):
            return False
    except OSError:
        return True


def levantar_servidor(puerto: int) -> subprocess.Popen:
    if not puerto_libre(puerto):
        raise SystemExit(f"el puerto {puerto} ya está en uso; elige otro con --puerto")
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(puerto), "--bind", "127.0.0.1", "-d", str(SITIO)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        if not puerto_libre(puerto):
            return proc
        time.sleep(0.1)
    proc.kill()
    raise SystemExit("el servidor de prueba no arrancó")


def revisar(navegador, base: str, pag: dict, ancho: int, publicado: bool, captura: Path | None) -> list[str]:
    fallos = []
    alto = 844 if ancho < 600 else 1080
    ctx = navegador.new_context(viewport={"width": ancho, "height": alto}, has_touch=ancho < 600)
    pg = ctx.new_page()
    errores = []
    pg.on("pageerror", lambda e: errores.append(f"página: {e}"))
    pg.on("console", lambda m: m.type == "error" and errores.append(f"consola: {m.text}"))
    if not publicado:
        pg.route("**/fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=""))
        pg.route("**/fonts.gstatic.com/**", lambda r: r.fulfill(status=200, body=""))
    ruta = f"/{pag['ruta']}/"
    r = pg.goto(base + ruta, wait_until="networkidle")
    if r is None or r.status != 200:
        fallos.append(f"HTTP {r.status if r else 'sin respuesta'}")
    try:
        pg.wait_for_selector("#v2-raiz .card", timeout=20000)
    except Exception:
        fallos.append("sin tarjetas a los 20 s")
    pg.evaluate("() => document.fonts.ready")
    pg.wait_for_timeout(400)
    x = pg.evaluate(JS_REVISION)
    if x["cargando"]:
        fallos.append("sigue «Cargando…»")
    if not x["cards"]:
        fallos.append("0 tarjetas")
    if x["llaves"]:
        fallos.append(f"{x['llaves']} «{{{{» sin reemplazar")
    if x["scroll"] > 0:
        fallos.append(f"scroll horizontal de {x['scroll']} px")
    if x["pisados"]:
        fallos.append(f"rótulos del eje X pisados: {x['pisados'][:4]}" + (f" (+{len(x['pisados']) - 4})" if len(x["pisados"]) > 4 else ""))
    if publicado:
        faltan = [f for f in FUENTES if f not in x["fuentes"]]
        if faltan:
            fallos.append(f"fuentes sin cargar: {faltan}")
    if ancho == 1920:
        pg.click("#v2-leer")
        pg.wait_for_timeout(200)
        if not pg.evaluate("() => document.getElementById('v2-leer-dlg').open"):
            fallos.append("«Cómo leer» no abre")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(200)
        if pg.evaluate("() => document.getElementById('v2-leer-dlg').open"):
            fallos.append("«Cómo leer» no cierra con Esc")
    if captura:
        captura.mkdir(parents=True, exist_ok=True)
        pg.screenshot(path=str(captura / f"{pag['ruta']}_{ancho}.png"), full_page=True)
    fallos += errores
    ctx.close()
    estado = "OK " if not fallos else "MAL"
    print(f"  {estado} {ruta:16} {ancho:>5}px  {x['cards']:3} tarjetas" + ("" if not fallos else "  ← " + "; ".join(fallos)))
    return [f"{ruta} {ancho}px: {f}" for f in fallos]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--puerto", type=int, default=8080)
    ap.add_argument("--url", help="revisa el sitio publicado (p. ej. https://banks-bz.pages.dev) en vez del local")
    ap.add_argument("--anchos", default="1920,1280,390")
    ap.add_argument("--captura", type=Path)
    a = ap.parse_args()
    anchos = [int(x) for x in a.anchos.split(",")]
    servidor = None if a.url else levantar_servidor(a.puerto)
    base = (a.url or f"http://127.0.0.1:{a.puerto}").rstrip("/")
    fallos = []
    try:
        with sync_playwright() as pw:
            nav = pw.chromium.launch()
            for pag in paginas():
                for ancho in anchos:
                    fallos += revisar(nav, base, pag, ancho, bool(a.url), a.captura)
            nav.close()
    finally:
        if servidor:
            servidor.kill()
    n = len(paginas()) * len(anchos)
    print(f"\n{n - len({f.split(':')[0] for f in fallos})} de {n} combinaciones página × ancho sin fallos")
    if fallos:
        print("FALLOS:\n  " + "\n  ".join(fallos))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
