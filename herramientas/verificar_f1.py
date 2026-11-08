"""Verifica el sitio de bancos sobre todas las páginas de config.js (PAGINAS), con y sin ?banco=itau.

Qué comprueba, con un Chromium real sobre un servidor propio (python -m http.server, que se cierra
al terminar con su mismo PID; no se usa ningún servidor que ya estuviera corriendo):
  1. cada página responde 200 y carga sin errores de consola ni de página;
  2. el número de secciones y de tarjetas es el de la config y el del esqueleto (esqueleto_tarjetas.json);
  3. cada tarjeta lleva el título de su config; si la config NO tiene armar(), la tarjeta está
     «en preparación» (esa exigencia no aplica a las tarjetas con armar());
  4. ninguna tarjeta con armar() muestra error de carga o de cálculo, y ninguna queda cargando: se espera a
     <html data-pagina="lista"> y a que ningún nodo siga en data-estado cargando/actualizando (ciclo de vida
     explícito de pagina.js; el estado se lee de data-estado, no del texto visible);
  5. ningún «[» visible en el texto de la página;
  6. la cabecera tiene una pestaña por página visible (las de config.js sin oculta: true) y la marca de config.js;
  7. en cada ancho de --anchos, la página no tiene scroll horizontal;
  8. cada color de tokens.js (COLOR) es igual a su token de tokens.css (navy → --navy, texto2 → --texto-2).
Las configs, el esqueleto y los colores salen de herramientas/inventario_paginas.mjs (Node).
Captura de página completa solo si se pide con --captura DIR.

Con --url BASE (p. ej. https://banks-bz.pages.dev) revisa el sitio publicado en vez del local, con las fuentes
reales de Google (en local se cortan, para no depender de la red) y reporta si cargaron.

Uso: python -X utf8 herramientas/verificar_f1.py [--puerto 8080] [--url BASE] [--anchos 1920,1280,390] [--captura DIR]
"""
import argparse
import json
import signal
import socket
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
SITIO = RAIZ / "sitio"


def inventario():
    r = subprocess.run(["node", str(RAIZ / "herramientas" / "inventario_paginas.mjs")],
                       capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(r.stdout)


INV = inventario()
PAGINAS = [(f"/{p['ruta']}/" if p["ruta"] else "/", p["clave"]) for p in INV["paginas"]]
VISIBLES = sum(1 for p in INV["paginas"] if not p.get("oculta"))
ESPERADO = INV["ESPERADO"]

# Ciclo de vida de una tarjeta (comun.js, ESTADOS): se lee de data-estado, no del texto visible.
TRANSITORIOS = set(INV["TRANSITORIOS"])
EN_PREPARACION = {"en-preparacion", "requiere-banco"} & set(INV["ESTADOS"])

# La página terminó cuando montar() marcó <html data-pagina="lista"> y ningún nodo sigue cargando.
PAGINA_LISTA = """() => document.documentElement.dataset.pagina === 'lista'
  && !document.querySelector('[data-estado="cargando"], [data-estado="actualizando"]')"""

ESTADO_DOM = """() => {
  const tarjetas = [...document.querySelectorAll('figure.tarjeta')].map((f) => ({
    titulo: (f.querySelector('.tarjeta-titulo')?.textContent || '').trim(),
    estado: f.dataset.estado || '',
    mensaje: (f.querySelector('.estado-datos strong')?.textContent || '').trim(),
  }));
  const otros = [...document.querySelectorAll('[data-estado]:not(figure.tarjeta)')]
    .map((n) => ({ nodo: n.id || n.className, estado: n.dataset.estado }));
  return {
    pagina: document.documentElement.dataset.pagina || '',
    secciones: document.querySelectorAll('section.seccion').length,
    tarjetas,
    otros,
    pestanas: document.querySelectorAll('.pestana').length,
    marca: (document.querySelector('.cabecera-marca')?.textContent || '').trim(),
    texto: document.body.innerText,
    desborde: document.documentElement.scrollWidth - window.innerWidth,
    fuentes: [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family.replace(/"/g, '')),
  };
}"""


def configs_del_sitio():
    """Por página: número de secciones y tarjetas en el orden en que se colocan (título y si tiene armar)."""
    salida = {}
    for p in INV["paginas"]:
        t = p.get("tarjetas", {})
        salida[p["clave"]] = {
            "secciones": len(p.get("secciones", [])),
            "tarjetas": [{"clave": k, "titulo": (t.get(k) or {}).get("titulo") or "", "armar": bool((t.get(k) or {}).get("armar"))}
                         for k in p.get("orden", [])],
        }
    return salida


# kebab de la clave JS: aceroClaro → --acero-claro, texto2 → --texto-2
TOKENS = """(colores) => Object.entries(colores).filter(([clave, valor]) => {
  const token = '--' + clave.replace(/([A-Z0-9])/g, '-$1').toLowerCase();
  return getComputedStyle(document.documentElement).getPropertyValue(token).trim().toUpperCase() !== valor.toUpperCase();
}).map(([clave, valor]) => `${clave} ${valor}`)"""


def puerto_libre(puerto):
    try:
        with socket.create_connection(("127.0.0.1", puerto), timeout=0.3):
            return False
    except OSError:
        return True


def levantar_servidor(puerto):
    if not puerto_libre(puerto):
        raise SystemExit(f"el puerto {puerto} ya está en uso; elige otro con --puerto")
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(puerto), "--bind", "127.0.0.1", "-d", str(SITIO)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(100):
        if not puerto_libre(puerto):
            return proc
        time.sleep(0.1)
    proc.kill()
    raise SystemExit("el servidor de prueba no arrancó")


def revisar(contexto, base, ruta, clave, cfg, banco, captura, fallos, ancho=1920, fuentes_reales=False):
    etiqueta = f"{clave:4} {ruta:15} {'?banco=itau' if banco else 'sin banco':12} {ancho:>5}px"
    errores = []
    pagina = contexto.new_page()
    pagina.set_viewport_size({"width": ancho, "height": 1080})
    if not fuentes_reales:
        # v2: las fuentes de Google se piden a fonts.googleapis.com; sin red (o tras un proxy) fallan y no son error del sitio.
        pagina.route("**/fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=""))
        pagina.route("**/fonts.gstatic.com/**", lambda r: r.fulfill(status=200, body=""))
    pagina.on("console", lambda m: errores.append(f"consola {m.type}: {m.text}") if m.type == "error" else None)
    pagina.on("pageerror", lambda e: errores.append(f"excepción: {e}"))
    url = base + ruta + (("?banco=itau") if banco else "")
    respuesta = pagina.goto(url, wait_until="networkidle")
    if ruta == "/" and not banco:
        fallos.extend(f"color de tokens.js distinto de su token en tokens.css: {c}" for c in pagina.evaluate(TOKENS, INV["COLOR"]))
    pagina.evaluate("() => document.fonts.ready")
    antes = len(fallos)
    try:
        pagina.wait_for_function(PAGINA_LISTA, timeout=60_000)
    except Exception:  # noqa: BLE001 — se reporta abajo con el estado en que quedó cada nodo
        pass
    datos = pagina.evaluate(ESTADO_DOM)

    if datos["pagina"] != "lista":
        fallos.append(f"{clave}: la página no terminó de montar (data-pagina «{datos['pagina']}»)")
    for o in datos["otros"]:
        if o["estado"] in TRANSITORIOS or o["estado"] == "error":
            fallos.append(f"{clave}: «{o['nodo']}» quedó en estado {o['estado']}")
    if respuesta.status != 200:
        fallos.append(f"{clave}{' ?banco=itau' if banco else ''}: HTTP {respuesta.status}")
    fallos.extend(f"{clave}{' ?banco=itau' if banco else ''}: {e}" for e in errores)

    esperadas = cfg["tarjetas"]
    if len(datos["tarjetas"]) != ESPERADO[clave] or len(datos["tarjetas"]) != len(esperadas):
        fallos.append(f"{clave}: {len(datos['tarjetas'])} tarjetas en pantalla, {len(esperadas)} en la config, {ESPERADO[clave]} en el esqueleto")
    if datos["secciones"] != cfg["secciones"]:
        fallos.append(f"{clave}: {datos['secciones']} secciones en pantalla, {cfg['secciones']} en la config")
    for dom, conf in zip(datos["tarjetas"], esperadas):
        titulo_conf = (conf["titulo"] or "").strip()
        if dom["titulo"] != titulo_conf:
            fallos.append(f"{clave}: tarjeta «{dom['titulo']}» donde la config dice «{titulo_conf}»")
        if dom["estado"] == "error":
            fallos.append(f"{clave}: «{dom['titulo']}» muestra error de carga o de cálculo ({dom['mensaje']})")
        if dom["estado"] in TRANSITORIOS or not dom["estado"]:
            fallos.append(f"{clave}: «{dom['titulo']}» no terminó de dibujarse (estado «{dom['estado']}»)")
        if not conf["armar"] and dom["estado"] not in EN_PREPARACION:
            fallos.append(f"{clave}: «{dom['titulo']}» sin armar() debe estar en preparación")
    if datos["pestanas"] != VISIBLES:
        fallos.append(f"{clave}: {datos['pestanas']} pestañas en la cabecera")
    if datos["marca"] != INV["MARCA"]:
        fallos.append(f"{clave}: marca «{datos['marca']}»")
    if "[" in datos["texto"]:
        i = datos["texto"].index("[")
        fallos.append(f"{clave}: «[» visible: …{datos['texto'][max(0, i - 30):i + 30]}…")

    if datos["desborde"] > 1:
        fallos.append(f"{clave} {ancho}px: scroll horizontal de {datos['desborde']} px")
    if fuentes_reales and not datos["fuentes"]:
        fallos.append(f"{clave} {ancho}px: no cargó ninguna fuente web")

    nuevos = len(fallos) - antes
    con_armar = sum(1 for c in esperadas if c["armar"])
    estados = Counter(t["estado"] or "—" for t in datos["tarjetas"])
    print(f"{etiqueta} HTTP {respuesta.status} · {datos['secciones']} secciones · {len(datos['tarjetas'])} tarjetas "
          f"({con_armar} con armar; {', '.join(f'{k} {v}' for k, v in sorted(estados.items())) or 'sin tarjetas'}) · {len(errores)} errores de consola"
          f"{' · fuentes: ' + ', '.join(sorted(set(datos['fuentes']))) if fuentes_reales else ''}"
          f" · {'OK' if nuevos == 0 else f'{nuevos} fallos'}")
    if captura:
        captura.mkdir(parents=True, exist_ok=True)
        nombre = f"{clave.lower()}{'_itau' if banco else ''}_{ancho}.png"
        pagina.screenshot(path=str(captura / nombre), full_page=True)
    pagina.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8080)
    ap.add_argument("--captura", type=Path, default=None)
    ap.add_argument("--url", default=None, help="sitio publicado (sin / final); si falta, levanta uno local")
    ap.add_argument("--anchos", default="1920", help="anchos en px separados por coma, p. ej. 1920,1280,390")
    args = ap.parse_args()
    anchos = [int(a) for a in args.anchos.split(",")]

    # SIGTERM cierra el servidor propio (el bloque finally corre), en vez de dejarlo huérfano
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(1))
    configs = configs_del_sitio()
    fallos = []
    servidor = None if args.url else levantar_servidor(args.puerto)
    base = args.url.rstrip("/") if args.url else f"http://127.0.0.1:{args.puerto}"
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            contexto = navegador.new_context(viewport={"width": 1920, "height": 1080})
            for ancho in anchos:
                for ruta, clave in PAGINAS:
                    for banco in (False, True):
                        revisar(contexto, base, ruta, clave, configs[clave], banco, args.captura, fallos,
                                ancho, fuentes_reales=bool(args.url))
            navegador.close()
    finally:
        if servidor:
            servidor.terminate()
            try:
                servidor.wait(timeout=5)
            except subprocess.TimeoutExpired:
                servidor.kill()

    if fallos:
        print("\nFALLOS:")
        for f in fallos:
            print(" -", f)
        return 1
    print(f"\nOK ({base}, {args.anchos} px): las {len(PAGINAS)} páginas, con y sin ?banco=itau, cargan sin errores; sin scroll horizontal; conteos del esqueleto; «en preparación» solo sin armar()")
    return 0


if __name__ == "__main__":
    sys.exit(main())
