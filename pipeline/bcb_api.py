#!/usr/bin/env python3
"""
Descarga de DATOS (valores) de las series del SGS/BCB via la API oficial.

Endpoints usados (documentados en https://dadosabertos.bcb.gov.br/):
  GET https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados
      ?formato=json|csv&dataInicial=DD/MM/AAAA&dataFinal=DD/MM/AAAA
  GET https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/{n}

Nota: la API limita las series diarias a ventanas de 10 anios (3652 dias);
el script lo gestiona automaticamente. Metadatos: usar bcb_scraper.py
(no hay endpoint de metadatos en la API actual).

OJO con los errores: una serie inexistente NO da 404. La API contesta una pagina
HTML, con un status que varia (visto 200 y 502), asi que el status code no alcanza
para saber si la respuesta sirve. Ver RespuestaNoJSON mas abajo.

Ejemplos:
  python3 bcb_api.py datos 432                       # serie completa (JSON->CSV)
  python3 bcb_api.py datos 432 11 433 -o tasas.csv   # varias series a un CSV
  python3 bcb_api.py datos 433 --desde 01/01/2024    # rango de fechas
  python3 bcb_api.py datos 11 432 --ancho -o x.csv   # una columna por serie
  python3 bcb_api.py ultimos 432 -n 5                # ultimas 5 observaciones
  # varias series en paralelo: se descargan una a una automaticamente
"""

import argparse
import csv
import datetime as dt
import json
import sys
import time
from pathlib import Path

import certificados  # noqa: F401  parchea ssl para la CA corporativa; ver certificados.py
import requests

API = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/{recurso}"
SESION = requests.Session()
SESION.headers["User-Agent"] = "bcb-scraper/1.0"


def _url(codigo, recurso="dados"):
    return API.format(codigo=codigo, recurso=recurso)


LIMITE_VENTANA = dt.timedelta(days=3652)
PRIMER_DIA_SERIES_DIARIAS = dt.date(1980, 1, 1)


class VentanaDemasiadoLarga(ValueError):
    """La API rechazo un rango diario de mas de 3652 dias."""


class RespuestaNoJSON(requests.RequestException):
    """La API contesto algo que no es JSON (en la practica, una pagina HTML de error).

    POR QUE EXISTE ESTA CLASE
    -------------------------
    La API del SGS NO usa 404 para una serie inexistente: devuelve una pagina HTML, y el
    status code que la acompana varia. Verificado el 27/08/2026 contra la API viva: la
    serie 99999999 contesto HTTP 502 con content-type text/html, mientras la 432
    contestaba 200 con JSON; ~/brasil-macro-dashboard registro el mismo caso como
    HTTP 200 con text/html, o sea con response.ok en True.

    Un cliente que solo mire el status code da por buena esa respuesta y despues revienta
    al parsear, o peor: la interpreta como serie vacia. Lo unico estable es que el error
    llega como HTML, asi que la deteccion correcta es el content-type.

    Un HTML tambien puede ser el cortafuegos frenando el ritmo de peticiones. Hereda de
    RequestException para que el lazo lo reintente con una espera mayor que la usada
    ante un error de red comun.
    """

    def __init__(self, codigo, status, content_type):
        self.codigo, self.status, self.content_type = codigo, status, content_type
        super().__init__(f"la API respondio {status} con content-type "
                         f"'{content_type or 'desconocido'}' (no JSON)")


def _asegurar_json(r, codigo):
    if "json" not in r.headers.get("content-type", "").lower():
        raise RespuestaNoJSON(codigo, r.status_code, r.headers.get("content-type"))
    return r


def _fecha(texto, por_defecto=None):
    """Convierte DD/MM/AAAA a date; devuelve por_defecto si no se puede."""
    try:
        return dt.datetime.strptime(texto, "%d/%m/%Y").date()
    except (TypeError, ValueError):
        return por_defecto


def _texto(fecha):
    return fecha.strftime("%d/%m/%Y")


def _error_de_la_api(cuerpo):
    """Conserva la diferencia entre una ventana larga y los demas errores JSON."""
    detalle = " ".join(str(cuerpo.get(c, "")) for c in ("error", "message"))
    mensaje = str(cuerpo.get("message") or cuerpo["error"])[:160]
    if "janela" in detalle.lower():
        return VentanaDemasiadoLarga(mensaje)
    return requests.RequestException(mensaje)


def _descargar_tramo(codigo, desde, hasta, reintentos, pausa):
    """Hace una peticion por un rango que se supone dentro del limite."""
    params = {"formato": "json"}
    if desde:
        params["dataInicial"] = desde
    if hasta:
        params["dataFinal"] = hasta

    ultimo_error = None
    for intento in range(1, reintentos + 1):
        try:
            time.sleep(pausa)
            r = SESION.get(_url(codigo), params=params, timeout=60)
            if r.status_code == 404:
                raise ValueError(
                    f"la API respondio 404 a la serie {codigo}: o el codigo no existe, "
                    f"o el rango pedido es imposible ({desde or 'sin inicio'} a "
                    f"{hasta or 'sin fin'})"
                )
            if r.status_code in (429, 503):
                raise requests.RequestException(f"{r.status_code}")

            _asegurar_json(r, codigo)
            datos = r.json()
            if isinstance(datos, dict) and "error" in datos:
                raise _error_de_la_api(datos)
            r.raise_for_status()
            for fila in datos:
                fila["fecha"] = fila.pop("data")
            return datos
        except VentanaDemasiadoLarga:
            raise
        except requests.RequestException as e:
            ultimo_error = e
            if intento < reintentos:
                if isinstance(e, RespuestaNoJSON):
                    espera = min(60, 10 * 3 ** (intento - 1))
                else:
                    espera = 2 * intento
                print(f"  [!] reintento {intento} ({e})", file=sys.stderr)
                time.sleep(espera)

    if isinstance(ultimo_error, RespuestaNoJSON):
        raise ValueError(
            f"la serie {codigo} no devolvio datos: {ultimo_error} en {reintentos} "
            f"intentos. La API del SGS contesta HTML cuando el codigo de serie no "
            f"existe, cuando el cortafuegos esta frenando las peticiones y cuando el "
            f"servidor esta caido, y no las distingue. Reintenta con pausa mayor "
            f"(descargar_serie(..., pausa=5)). Para descartar el codigo: "
            f"python3 bcb_scraper.py metadatos --codigos {codigo}"
        )
    raise RuntimeError(
        f"no se pudo descargar la serie {codigo}"
        + (f": {ultimo_error}" if ultimo_error else "")
    )


def descargar_serie(codigo, desde=None, hasta=None, reintentos=3, pausa=1.0):
    """Descarga una serie y devuelve una lista de {fecha, valor}.

    La API limita las series diarias a 3652 dias. Si el servidor identifica una
    ventana demasiado larga, el rango se parte y se descarga completo. Las series
    mensuales y anuales salen en una sola peticion.
    """
    fechas = {}
    for etiqueta, valor in (("desde", desde), ("hasta", hasta)):
        if valor is None:
            continue
        fecha = _fecha(valor)
        if fecha is None:
            raise ValueError(f"{etiqueta}={valor!r} no es una fecha DD/MM/AAAA")
        fechas[etiqueta] = fecha

    if "desde" in fechas and "hasta" in fechas and fechas["desde"] > fechas["hasta"]:
        raise ValueError(
            f"el rango esta al reves: desde={desde} es posterior a hasta={hasta}"
        )

    try:
        return _descargar_tramo(codigo, desde, hasta, reintentos, pausa)
    except VentanaDemasiadoLarga:
        pass

    inicio = fechas.get("desde", PRIMER_DIA_SERIES_DIARIAS)
    fin = fechas.get("hasta", dt.date.today())
    if inicio > fin:
        return []

    tramos = []
    tramo_inicio = inicio
    while tramo_inicio <= fin:
        tramo_fin = min(tramo_inicio + LIMITE_VENTANA, fin)
        tramos.append((tramo_inicio, tramo_fin))
        tramo_inicio = tramo_fin + dt.timedelta(days=1)

    print(
        f"    [i] serie {codigo} diaria: {_texto(inicio)}-{_texto(fin)} pasa de los "
        f"10 anios, se baja en {len(tramos)} tramos",
        file=sys.stderr,
    )
    filas = []
    for tramo_inicio, tramo_fin in tramos:
        filas += _descargar_tramo(
            codigo,
            _texto(tramo_inicio),
            _texto(tramo_fin),
            reintentos,
            pausa,
        )
    return filas


def descargar_ultimos(codigo, n=10, pausa=0.3):
    """Ultimas n observaciones de una serie (no requiere rango de fechas)."""
    time.sleep(pausa)
    r = SESION.get(_url(codigo) + f"/ultimos/{n}", params={"formato": "json"},
                   timeout=30)
    if r.status_code == 404:
        raise ValueError(f"serie {codigo} no existe en la API (404)")
    _asegurar_json(r, codigo)   # HTML = serie inexistente o servidor caido; ver la clase
    r.raise_for_status()
    return r.json()


def _escribir_csv(filas_series, salida):
    """filas_series: {codigo: [ {data, valor}, ... ]}"""
    todas = []
    for cod, datos in filas_series.items():
        for d in datos:
            todas.append({"codigo": cod, "fecha": d["fecha"], "valor": d["valor"]})
    todas.sort(key=lambda x: (x["fecha"], str(x["codigo"])), reverse=True)
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["codigo", "fecha", "valor"])
        w.writeheader()
        w.writerows(todas)


def _escribir_ancho(filas_series, salida):
    """una columna por codigo (ideal para graficos en Excel)."""
    fechas = sorted({d["fecha"] for datos in filas_series.values() for d in datos})
    codigos = sorted(filas_series)
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fecha"] + [f"serie_{c}" for c in codigos])
        por_fecha = {}
        for cod, datos in filas_series.items():
            for d in datos:
                por_fecha.setdefault(d["fecha"], {})[cod] = d["valor"]
        for fecha in fechas:
            fila = [fecha] + [por_fecha[fecha].get(c, "") for c in codigos]
            w.writerow(fila)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Descarga datos del SGS/BCB via API oficial")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_datos = sub.add_parser("datos", help="descarga los valores de series")
    p_datos.add_argument("codigos", nargs="+", help="codigo(s) de serie")
    p_datos.add_argument("--desde", help="fecha inicial DD/MM/AAAA")
    p_datos.add_argument("--hasta", help="fecha final DD/MM/AAAA")
    p_datos.add_argument("-o", "--salida", default=None, help="CSV de salida")
    p_datos.add_argument("--ancho", action="store_true",
                         help="formato ancho: una columna por serie")

    p_meta = sub.add_parser("ultimos", help="ultimas N observaciones de una serie")
    p_meta.add_argument("codigo")
    p_meta.add_argument("-n", type=int, default=10, help="cantidad (defecto: 10)")


    args = ap.parse_args(argv)

    if args.cmd == "datos":
        salida = args.salida or (
            f"serie_{args.codigos[0]}.csv" if len(args.codigos) == 1 else "series.csv")
        filas_series = {}
        for cod in args.codigos:
            print(f"[~] descargando serie {cod}...", file=sys.stderr)
            try:
                filas_series[cod] = descargar_serie(cod, args.desde, args.hasta)
                print(f"    {len(filas_series[cod])} observaciones", file=sys.stderr)
            except ValueError as e:
                print(f"    ERROR: {e}", file=sys.stderr)
        if not filas_series:
            sys.exit("no se descargo ninguna serie")
        if args.ancho:
            _escribir_ancho(filas_series, salida)
        else:
            _escribir_csv(filas_series, salida)
        print(f"[+] guardado en {salida}")
        for cod, datos in filas_series.items():
            if datos:
                print(f"    serie {cod}: {datos[0]['fecha']} a "
                      f"{datos[-1]['fecha']} ({len(datos)} obs)")

    elif args.cmd == "ultimos":
        datos = descargar_ultimos(args.codigo, args.n)
        if not datos:
            print("(sin datos)")
            return
        print(f"serie {args.codigo} - ultimas {len(datos)} observaciones:")
        for d in datos[-min(args.n, 12):]:
            print(f"  {d['data']}  {d['valor']}")



if __name__ == "__main__":
    main()
