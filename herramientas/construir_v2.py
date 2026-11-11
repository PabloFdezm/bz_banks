# -*- coding: utf-8 -*-
"""Construye el sitio v2 (rediseño) desde las hojas del canvas.

Entrada:
- `diseno/canvas/*.dc.html`: hojas del canvas «Rediseño de gráficos v3» (plantilla x-dc + clase Component). Los datos
  que el canvas lleva incrustados (`const X = {...};`) se ignoran: la página los lee de `sitio/data/v2/<slug>.json`.
- `diseno/canvas/paginas.json`: páginas del sitio (ruta, título, grupo del menú) y las hojas que monta cada una.
- Datos: `tareas/borradores/_salida/v2/<hoja>.json` (fuera de git: los datos de cada hoja tal como están en el canvas
  aprobado) → `sitio/data/v2/<hoja>.json`. Las hojas de la Portada traen sus datos dentro (const D) y no usan JSON.

Salida (todo dentro de `sitio/`, que publica `publicar.bat`; el sitio entero es esto desde el 10-nov):
- `assets/v2/componentes/<Nombre>.js` y `assets/v2/paginas/<Nombre>.js`: módulos ES con la plantilla y la clase.
- `<ruta>/index.html` para cada página, `index.html` (la Portada) y `404.html`.
- `data/v2/<slug>.json`.

    Set-Location C:\\dev\\bz_banks; python -X utf8 herramientas/construir_v2.py
"""
import json, re, shutil, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CANVAS = RAIZ / 'diseno' / 'canvas'
SITIO = RAIZ / 'sitio'
SALIDA_DATOS = RAIZ / 'tareas' / 'borradores' / '_salida' / 'v2'
LIMITE = 25 * 1024 * 1024


def partes(html: str):
    i = html.index('<script type="text/x-dc"')
    plantilla = html[:i]
    j = html.index('>', i) + 1
    codigo = html[j:html.rindex('</script>')]
    return plantilla, codigo


def sin_datos(codigo: str) -> str:
    """Reemplaza `const X = {...};` (una línea) por los datos que entrega la página."""
    lineas = codigo.split('\n')
    out = [('    const X = DATOS;' if l.lstrip().startswith('const X = {') else l) for l in lineas]
    return '\n'.join(out)


EXCEL = ('<button class="btn v2-excel" type="button" title="Descargar en Excel los datos de este gráfico" aria-label="Descargar en Excel">'
         '<svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
         '<path d="M8 2v8M4.5 6.5 8 10l3.5-3.5M3 13h10"/></svg></button>')


def parches_sitio(plantilla: str, codigo: str):
    """Solo en el sitio: botón Excel en cada gráfico y nombre e historia completa de cada serie en la configuración
    del gráfico (para exportar). El canvas no cambia."""
    plantilla = plantilla.replace('<button class="btn" type="button" onClick="{{s.abrir}}"', EXCEL + '<button class="btn" type="button" onClick="{{s.abrir}}"')
    plantilla = re.sub(r'(<button class="btn" type="button" style="\{\{[od]\.\w+\}\}" aria-pressed="\{\{[od]\.[^>]*>[^<]*</button>)', lambda m: '<div style="display: flex; gap: 8px; align-items: center;">' + EXCEL + m.group(1) + '</div>', plantilla)
    codigo = codigo.replace('({ id: s.id, color: s.color', '({ id: s.id, nombre: s.nombre, todo: s.datos, color: s.color')
    # Gráfico y período al ancho real de su contenedor (dc.js mide el contenedor y guarda __ancho).
    codigo = codigo.replace('const w = c.w, h = c.h, n = c.n,', 'const w = this.__ancho || c.w, h = c.h, n = c.n,')
    codigo = codigo.replace('const w = c.w, n = c.n, min =', 'const w = this.__ancho || c.w, n = c.n, min =')
    codigo = codigo.replace('{ id: s.id, color: s.color, ancho: 0', '{ id: s.id, nombre: s.nombre, todo: s.datos, color: s.color, ancho: 0')
    codigo = re.sub(r'etiquetas: (\([^()]*\)|[\w.]+)\.slice\((\w+), (\w+) \+ 1\)', r'etiquetasTodas: \1, etiquetas: \1.slice(\2, \3 + 1)', codigo)
    return plantilla, codigo


def modulo(nombre: str, html: str, con_datos: bool) -> str:
    plantilla, codigo = partes(html)
    plantilla, codigo = parches_sitio(plantilla, codigo)
    plantilla = plantilla.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    if con_datos:
        codigo = sin_datos(codigo)
    cab = "import { DCLogic, registrar } from '/assets/v2/dc.js';\n"
    if con_datos:
        cab += 'let DATOS = null;\nexport function datos(d) { DATOS = d; }\n'
    return f"{cab}const PLANTILLA = `{plantilla}`;\n{codigo.strip()}\nregistrar('{nombre}', PLANTILLA, Component);\n"


def menu(paginas, actual):
    grupos = {}
    for p in paginas:
        grupos.setdefault(p['grupo'], []).append(p)
    out = []
    for g, ps in grupos.items():
        items = []
        for p in ps:
            if p['ruta'] == actual:
                items.append('<li><a href="/' + p['ruta'] + '/" aria-current="page">' + p['menu'] + '</a><ol class="v2-secs" id="v2-secs"></ol></li>')
            else:
                items.append('<li><a href="/' + p['ruta'] + '/">' + p['menu'] + '</a></li>')
        out.append('<div class="v2-grupo"><p class="v2-g">' + g + '</p><ul>' + ''.join(items) + '</ul></div>')
    return ''.join(out)


def leer_contextual(hojas: list[str], fuentes: str) -> dict[str, str]:
    """Entradas de «Cómo leer» que dependen de la página: solo lo que la página muestra."""
    uso = ''
    if 'Seccion01' in hojas:
        uso = ('    <dt>Franja de entrada</dt><dd>Cinco cifras del último mes, con su cambio a/a; cada una lleva a su '
               'sección.</dd>\n'
               '    <dt>Segmentos</dt><dd>En los pares con selector, elige qué se compara: personas y empresas, libre y '
               'dirigido, personas por libre y dirigido, o todos. «En preparación»: ese corte todavía no tiene '
               'datos.</dd>\n')
    z = ('    <dt>Z 10 años</dt><dd>A cuántos desvíos está el último dato del promedio de los últimos 10 años.</dd>\n'
         if 'Z 10 años' in fuentes else '')
    banda = ('    <dt>Banda gris</dt><dd>Período con un cambio de norma o de método que afecta la lectura; el rótulo dice '
             'cuál (p. ej. Res. CMN 4.966, que desde ene-25 cambia la medición de la mora).</dd>\n'
             if 'bandas' in fuentes else '')
    return {'uso_extra': uso, 'glos_z': z, 'glos_banda': banda}


SHELL = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="data:,">
<title>{titulo} · Bancos Brasil</title>
<link rel="stylesheet" href="/assets/v2/v2.css">
<script>(function () {{ let v = null; try {{ v = localStorage.getItem('v2-lateral'); }} catch (e) {{}} if (v === 'cerrado' || (v === null && innerWidth < 1400)) document.documentElement.classList.add('v2-plegado'); }})();</script>
</head>
<body>
<a class="v2-saltar" href="#contenido-principal">Saltar al contenido</a>
<aside class="v2-lateral" id="v2-lateral">
  <div class="v2-lat-cab">
    <a class="v2-marca" href="/">Bancos Brasil</a>
    <button class="v2-plegar" id="v2-plegar" type="button" aria-controls="v2-lateral" aria-expanded="true" title="Ocultar el menú"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M11 4 6 9l5 5"/></svg><span class="v2-sr">Ocultar el menú</span></button>
  </div>
  <nav class="v2-nav" aria-label="Páginas">{menu}</nav>
</aside>
<button class="v2-abrir" id="v2-abrir" type="button" aria-controls="v2-lateral" title="Mostrar el menú"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 5h12M3 9h12M3 13h12"/></svg><span>Menú</span></button>
<header class="v2-barra">
  <div class="v2-barra-t"><span class="v2-barra-tit">{titulo}</span><span class="v2-corte" id="v2-corte"></span></div>
  <div class="v2-barra-acc">
    <button class="v2-b" id="v2-leer" type="button" aria-label="Cómo leer" aria-haspopup="dialog" aria-controls="v2-leer-dlg" title="Pistas de uso y glosario"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="8" cy="8" r="6"/><path d="M8 7.5V11M8 5h.01"/></svg><span class="v2-b-txt">Cómo leer</span></button>
    <button class="v2-b" id="v2-excel-pag" type="button" aria-label="Excel de la página" title="Descargar en Excel los datos de todos los gráficos de la página"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M8 2v8M4.5 6.5 8 10l3.5-3.5M3 13h10"/></svg><span class="v2-b-txt">Excel de la página</span></button>
    <button class="v2-b" id="v2-presentar" type="button" title="Una sección por pantalla; flechas para avanzar, Esc para salir"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="2" y="3" width="12" height="8" rx="1"/><path d="M8 11v3M5.5 14h5"/></svg>Presentar</button>
  </div>
</header>
<dialog class="v2-leer-dlg" id="v2-leer-dlg" aria-labelledby="v2-leer-tit">
  <div class="v2-leer-cab"><h2 id="v2-leer-tit">Cómo leer los gráficos</h2><button class="v2-b" id="v2-leer-cerrar" type="button">Cerrar</button></div>
  <h3>Uso</h3>
  <dl>
    <dt>Clic en una serie</dt><dd>En la leyenda, en la línea o en la fila de la tabla: la resalta y atenúa las demás. Otro clic la suelta.</dd>
    <dt>Ctrl + clic</dt><dd>Suma series al resaltado (⌘ + clic en Mac).</dd>
    <dt>Ajustar eje</dt><dd>Lleva la escala a las series resaltadas. Las que quedan fuera marcan su máximo y su mínimo con ▲ ▼.</dd>
    <dt>← →</dt><dd>Con el foco en el gráfico, recorren los períodos; Inicio y Fin van al primero y al último del período que se ve (la historia completa está en Agrandar).</dd>
    <dt>Alt + ↓ ↑</dt><dd>Salta a la sección siguiente o a la anterior.</dd>
    <dt>Agrandar</dt><dd>El gráfico a todo el ancho, con período ajustable, la tabla completa y la metodología.</dd>
    <dt>Presentar</dt><dd>Una sección por pantalla; flechas para avanzar, Esc para salir.</dd>
{uso_extra}  </dl>
  <h3>Glosario</h3>
  <dl>
    <dt>a/a</dt><dd>Contra el mismo mes (o trimestre) del año anterior.</dd>
    <dt>m/m · t/t</dt><dd>Contra el mes (o trimestre) anterior.</dd>
    <dt>3m/3m · 12m/12m</dt><dd>Promedio de la ventana contra el de la ventana anterior; en flujos, suma de 12 meses contra la anterior.</dd>
    <dt>Δ a/a</dt><dd>Cambio a/a de una tasa, en puntos porcentuales (pp).</dd>
    <dt>Share</dt><dd>Peso en el total.</dd>
    <dt>Mora &gt; 90 días (NPL)</dt><dd>Parte de la cartera con más de 90 días de atraso, en %.</dd>
    <dt>Atraso 15–90 días</dt><dd>Mora temprana: suele adelantar a la mora &gt; 90 días.</dd>
{glos_z}    <dt>Corte</dt><dd>Último período con dato de la serie.</dd>
    <dt>Total</dt><dd>En cobre en el gráfico y en negrita en la tabla.</dd>
{glos_banda}  </dl>
</dialog>
<main id="contenido-principal" tabindex="-1"><div id="v2-escala"><div id="v2-raiz"><p class="v2-carga" role="status">Cargando {titulo}…</p></div></div></main>
<div class="v2-pres" id="v2-pres" hidden>
  <span class="v2-pres-t" id="v2-pres-t"></span>
  <button class="v2-b" id="v2-pres-ant" type="button" aria-label="Lámina anterior">‹</button>
  <span class="v2-pres-n" id="v2-pres-n" aria-live="polite"></span>
  <button class="v2-b" id="v2-pres-sig" type="button" aria-label="Lámina siguiente">›</button>
  <button class="v2-b" id="v2-pres-salir" type="button">Salir</button>
</div>
<script type="module">
import {{ iniciar }} from '/assets/v2/sitio.js';
iniciar({hojas}, {titulo_js});
</script>
</body>
</html>
"""


NO_ENCONTRADA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Página no encontrada · Bancos Brasil</title>
<link rel="stylesheet" href="/assets/v2/v2.css">
</head>
<body class="v2-404">
<main id="contenido-principal"><p class="v2-marca">Bancos Brasil</p><h1>Esta página no existe</h1><p><a href="/">Ir a la Portada</a></p></main>
</body>
</html>
"""


def main() -> int:
    cfg = json.loads((CANVAS / 'paginas.json').read_text(encoding='utf-8'))
    paginas, componentes = cfg['paginas'], cfg['componentes']
    dest_js = SITIO / 'assets' / 'v2'
    for sub in ('componentes', 'paginas'):
        (dest_js / sub).mkdir(parents=True, exist_ok=True)
    for c in componentes:
        html = (CANVAS / f'{c}.dc.html').read_text(encoding='utf-8')
        (dest_js / 'componentes' / f'{c}.js').write_text(modulo(c, html, False), encoding='utf-8')
    (SITIO / 'data' / 'v2').mkdir(parents=True, exist_ok=True)
    for p in paginas:
        hojas = []
        for h in p['hojas']:
            html = (CANVAS / f'{h}.dc.html').read_text(encoding='utf-8')
            con_datos = '\n    const X = {' in html
            (dest_js / 'paginas' / f'{h}.js').write_text(modulo(h, html, con_datos), encoding='utf-8')
            if con_datos:
                destino = SITIO / 'data' / 'v2' / f'{h}.json'
                shutil.copyfile(SALIDA_DATOS / f'{h}.json', destino)
                if destino.stat().st_size > LIMITE:
                    raise SystemExit(f'{destino} pasa el límite de 25 MiB de Cloudflare Pages')
            hojas.append({'hoja': h, 'datos': h if con_datos else None})
        carpeta = SITIO / p['ruta']
        carpeta.mkdir(parents=True, exist_ok=True)
        fuentes = ''.join((CANVAS / f'{h}.dc.html').read_text(encoding='utf-8') for h in p['hojas'])
        (carpeta / 'index.html').write_text(SHELL.format(titulo=p['titulo'], menu=menu(paginas, p['ruta']), hojas=json.dumps(hojas), titulo_js=json.dumps(p['titulo'], ensure_ascii=False), **leer_contextual(p['hojas'], fuentes)), encoding='utf-8')
        print(f'{p["ruta"]}/  ←  ' + ', '.join(p['hojas']))
    # Raíz del sitio: la primera página (Portada) también en /, y una 404 con el mismo marco.
    p0 = paginas[0]
    (SITIO / 'index.html').write_text((SITIO / p0['ruta'] / 'index.html').read_text(encoding='utf-8'), encoding='utf-8')
    (SITIO / '404.html').write_text(NO_ENCONTRADA, encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
