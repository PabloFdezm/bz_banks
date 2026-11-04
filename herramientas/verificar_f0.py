"""Verifica la F0 del sitio de bancos contra el encargo 62 (criterios 1 y 2).

Qué comprueba, con un Chromium real sobre `python -m http.server -d sitio_bancos/site`:
  1. las once URLs del spec web de bancos §1 cargan sin errores de consola ni de página;
  2. cada sección muestra número, nombre y pregunta;
  3. cada tarjeta está «en preparación» con el motivo de su estado;
  4. cada tarjeta tiene el alto del esqueleto (a 1 920 px, donde el alto no es responsive) y su
     `width/9` de las 1 388 px del cuerpo.
Y deja la captura de página completa de B8 a 1 920 px en sitio_bancos/capturas/b8_f0_1920.png.

Uso: python -X utf8 sitio_bancos/verificar_f0.py
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
CAPTURAS = RAIZ / "capturas"
BASE = "http://localhost:8080"

# Las once URLs del spec web de bancos §1 y el alto de cada tarjeta del esqueleto.
PAGINAS = [
    ("/", "B0"),
    ("/ciclo/", "B1"),
    ("/competencia/", "B2"),
    ("/credito/", "B3"),
    ("/calidad/", "B4"),
    ("/fondeo/", "B5"),
    ("/rentabilidad/", "B6"),
    ("/capital/", "B7"),
    ("/ficha/", "B8"),
    ("/comparador/", "B9"),
    ("/metodologia/", "B10"),
]


# Huecos del propio esqueleto, declarados en PENDIENTES.md: no son fallos del código, pero se
# informan aparte para que no se confundan con un descuido. Cualquier otro hueco sí es fallo.
# Vacío desde 62b: el arquitecto fijó el nombre y la pregunta de B9 · 01 («Todos los bancos»), así
# que no queda ningún hueco declarado.
HUECOS = {}


def main() -> int:
    CAPTURAS.mkdir(exist_ok=True)
    fallos = []
    huecos = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(viewport={"width": 1920, "height": 1080})

        for ruta, clave in PAGINAS:
            errores = []
            pagina.on("console", lambda m: errores.append(f"consola {m.type}: {m.text}") if m.type == "error" else None)
            pagina.on("pageerror", lambda e: errores.append(f"excepción: {e}"))
            respuesta = pagina.goto(BASE + ruta, wait_until="networkidle")
            datos = pagina.evaluate(
                """() => {
                  const secciones = [...document.querySelectorAll('section.seccion')].map((s) => ({
                    id: s.id,
                    numero: s.querySelector('.riel-numero')?.textContent || '',
                    nombre: s.querySelector('.riel-nombre')?.textContent || '',
                    pregunta: s.querySelector('.riel-pregunta')?.textContent || '',
                    tarjetas: [...s.querySelectorAll('figure.tarjeta')].map((t) => ({
                      titulo: t.querySelector('.tarjeta-titulo')?.textContent || '',
                      preparacion: t.querySelector('.preparacion')?.textContent || '',
                      alto: Math.round(t.getBoundingClientRect().height),
                      ancho: Math.round(t.getBoundingClientRect().width),
                    })),
                  }));
                  return {
                    secciones,
                    titulo: document.title,
                    pestanas: [...document.querySelectorAll('.pestana')].map((a) => a.getAttribute('href')),
                    marca: document.querySelector('.cabecera-marca')?.textContent || '',
                  };
                }"""
            )
            tarjetas = [t for s in datos["secciones"] for t in s["tarjetas"]]
            print(f"{clave:4} {ruta:16} HTTP {respuesta.status} · {len(datos['secciones'])} secciones · "
                  f"{len(tarjetas)} tarjetas · {len(errores)} errores de consola")
            if respuesta.status != 200:
                fallos.append(f"{clave}: HTTP {respuesta.status}")
            fallos.extend(f"{clave}: {e}" for e in errores)
            for s in datos["secciones"]:
                if not s["numero"] or not s["nombre"]:
                    hueco = HUECOS.get((clave, s["id"]))
                    if hueco:
                        huecos.append(f"{clave} {s['id']}: {hueco}")
                    else:
                        fallos.append(f"{clave}: sección {s['id'] or '(sin id)'} sin número o nombre")
                for t in s["tarjetas"]:
                    if not t["preparacion"].startswith("En preparación:"):
                        fallos.append(f"{clave}: «{t['titulo']}» no está en preparación")
                    if not t["titulo"]:
                        fallos.append(f"{clave}: tarjeta sin título en {s['id']}")
            if len(datos["pestanas"]) != 11:
                fallos.append(f"{clave}: {len(datos['pestanas'])} pestañas en la cabecera")
            if datos["marca"] != "BANCOS BRASIL":
                fallos.append(f"{clave}: marca «{datos['marca']}»")

            if clave == "B8":
                for s in datos["secciones"]:
                    print(f"     {s['id']:5} {s['numero']:>3} {s['nombre']}")
                    for t in s["tarjetas"]:
                        print(f"           {t['ancho']:4} × {t['alto']:3} px · {t['preparacion']} · {t['titulo'][:52]}")
                pagina.screenshot(path=str(CAPTURAS / "b8_f0_1920.png"), full_page=True)
                print(f"     captura: {CAPTURAS / 'b8_f0_1920.png'}")

        navegador.close()

    if huecos:
        print("\nHUECOS DEL ESQUELETO (declarados en PENDIENTES.md):")
        for h in huecos:
            print(" -", h)
    if fallos:
        print("\nFALLOS:")
        for f in fallos:
            print(" -", f)
        return 1
    print("\nOK: las 11 páginas cargan sin errores y todas las tarjetas están en preparación")
    return 0


if __name__ == "__main__":
    sys.exit(main())
