# -*- coding: utf-8 -*-
"""Valida las series de sgs.CODIGOS contra el catálogo oficial del SGS (nombre, unidad, periodicidad).

Consulta el servicio web público del SGS (FachadaWSSGS.getUltimoValorXML), que devuelve el nombre oficial de cada
código, y lo compara con definiciones/bcb_sgs__catalogo.json. Sirve para no volver a identificar una serie solo
porque «los montos cuadran» (spec/08 punto 5, cerrado el 9-nov-2026).

Uso:
    python -X utf8 herramientas/validar_sgs.py            compara y avisa diferencias (no escribe)
    python -X utf8 herramientas/validar_sgs.py --escribir   reescribe el catálogo con lo que dice hoy el SGS
Después de --escribir, revisar a mano que cada nombre oficial corresponda a la clave que lo usa.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "pipeline"))

import almacen as A  # noqa: E402
import red  # noqa: E402
import sgs  # noqa: E402

DEF = "bcb_sgs__catalogo"
URL = "https://www3.bcb.gov.br/wssgs/services/FachadaWSSGS"
SOBRE = ('<?xml version="1.0" encoding="utf-8"?><soapenv:Envelope '
         'xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
         'xmlns:pub="http://publico.ws.casosdeuso.sgs.pec.bcb.gov.br"><soapenv:Body><pub:getUltimoValorXML>'
         '<in0>{codigo}</in0></pub:getUltimoValorXML></soapenv:Body></soapenv:Envelope>')


def consultar(codigo: int) -> dict:
    """Nombre, unidad y periodicidad oficiales de una serie SGS."""
    red.exigir_red(f"el catálogo SGS de la serie {codigo}")
    import certificados  # noqa: F401  CA del proxy corporativo; antes de requests
    import requests

    r = requests.post(URL, data=SOBRE.format(codigo=codigo).encode(), timeout=60,
                      headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": '""'})
    r.raise_for_status()
    texto = html.unescape(html.unescape(r.text))      # el XML de la serie viene escapado dentro del SOAP

    def campo(tag: str) -> str:
        m = re.search(f"<{tag}>(.*?)</{tag}>", texto, re.S)
        return m[1].strip() if m else ""

    if not campo("NOME"):
        raise ValueError(f"SGS {codigo}: el servicio no devolvió nombre (¿código inexistente?)")
    return {"nombre": campo("NOME"), "unidad": campo("UNIDADE"), "periodicidad": campo("PERIODICIDADE")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--escribir", action="store_true", help="reescribe definiciones/bcb_sgs__catalogo.json")
    args = ap.parse_args(argv)

    ruta = A.DEFINICIONES / f"{DEF}.json"
    actual = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {"series": {}}
    nuevas, diferencias = {}, []
    for clave, codigo in sgs.CODIGOS.items():
        oficial = {"codigo": codigo, **consultar(codigo)}
        nuevas[clave] = oficial
        antes = actual["series"].get(clave)
        if antes is None:
            diferencias.append(f"{clave} ({codigo}): no está en el catálogo → «{oficial['nombre']}»")
        elif {k: antes.get(k) for k in oficial} != oficial:
            diferencias.append(f"{clave} ({codigo}): «{antes.get('nombre')}» → «{oficial['nombre']}» "
                               f"[{antes.get('unidad')}|{antes.get('periodicidad')} → "
                               f"{oficial['unidad']}|{oficial['periodicidad']}]")
    for clave in sorted(set(actual["series"]) - set(nuevas)):
        diferencias.append(f"{clave}: está en el catálogo pero ya no en sgs.CODIGOS")

    for d in diferencias:
        print(f"[!] {d}")
    if args.escribir:
        salida = {"fuente": "Servicio web público del SGS (FachadaWSSGS.getUltimoValorXML)",
                  "descripcion": "Nombre, unidad y periodicidad oficiales de cada serie de sgs.CODIGOS. Lo escribe "
                                 "herramientas/validar_sgs.py --escribir; la correspondencia clave ↔ nombre se revisa "
                                 "a mano.",
                  "validado": date.today().isoformat(), "series": nuevas}
        ruta.write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"[+] {ruta.relative_to(RAIZ)}: {len(nuevas)} series")
        return 0
    print(f"{'OK' if not diferencias else 'DIFERENCIAS'}: {len(nuevas)} series contra el catálogo oficial")
    return 1 if diferencias else 0


if __name__ == "__main__":
    sys.exit(main())
