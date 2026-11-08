#!/usr/bin/env python3
"""
Hace que Python confie en los certificados que ya confia el sistema operativo.

POR QUE EXISTE ESTE MODULO
--------------------------
En una red corporativa el trafico HTTPS suele pasar por un proxy que lo inspecciona
(Zscaler, Netskope, Fortinet, Palo Alto, o el antivirus con "escaneo HTTPS" activado).
Ese proxy corta la conexion y la vuelve a firmar con una CA propia de la empresa, asi
que el certificado que llega NO es el de olinda.bcb.gov.br: es uno emitido por la CA
corporativa.

Windows y el navegador confian en esa CA porque el equipo la tiene instalada por
politica de dominio; por eso las paginas del BCB abren bien en Chrome. Python NO la ve:
requests valida contra el bundle de certifi, que solo trae las CA publicas. El resultado
es que TODOS los hosts fallan a la vez con:

    SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED]
    certificate verify failed: self-signed certificate in certificate chain'))

envuelto en un "Max retries exceeded with url: ...", que es lo que urllib3 imprime
cuando agota sus intentos. El "max retries" despista: no es que el BCB este caido ni que
nos esten limitando el ritmo. Si el error fuese del servidor, fallarian unos hosts y
otros no; que fallen cvm.gov.br, bndes.gov.br y olinda.bcb.gov.br a la vez, y siempre
por certificado, es la firma del proxy.

truststore resuelve el caso parcheando ssl.SSLContext para que valide contra el almacen
del sistema (el de Windows en el equipo del proyecto, el de OpenSSL en Linux/WSL). Eso
arregla de una sola vez requests y urllib.request, porque los dos terminan en el mismo
ssl del stdlib.

Si truststore no esta instalado, se respeta REQUESTS_CA_BUNDLE / SSL_CERT_FILE por si
alguien exporto la CA de la empresa a mano, y si tampoco hay nada se sigue adelante en
silencio: en una red sin proxy no hace falta nada de esto y no queremos ruido.

USO
---
    import certificados   # basta con importarlo, se activa solo

Va como primer import de cada modulo que salga a la red (bcb_api, ifdata, sgs, scr_zip), ANTES de requests.
"""

import os
import ssl
import sys

# Se activa una sola vez aunque varios modulos importen este archivo.
_activado = False
_metodo = None


def activar(verboso=False):
    """Instala el almacen de certificados del sistema. Devuelve el metodo usado."""
    global _activado, _metodo
    if _activado:
        return _metodo

    # 1) El almacen del sistema. Es lo que queremos: la CA corporativa ya esta ahi,
    #    instalada por politica de dominio, sin exportar ni copiar nada a mano.
    try:
        import truststore
        truststore.inject_into_ssl()
        _activado = True
        if verboso:
            print("[certificados] usando el almacen del sistema (truststore)",
                  file=sys.stderr)
        _metodo = "truststore"
        return _metodo
    except ImportError:
        pass
    except Exception as e:
        # Un fallo de truststore no puede tumbar el pipeline: seguimos a la alternativa.
        print(f"[certificados] truststore no pudo activarse ({e}); "
              f"se sigue con el bundle por omision", file=sys.stderr)

    # 2) Una CA exportada a mano. requests ya lee REQUESTS_CA_BUNDLE por su cuenta, pero
    #    urllib.request no, asi que aqui se lo damos tambien al ssl del stdlib.
    for var in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE"):
        ruta = os.environ.get(var)
        if ruta and os.path.exists(ruta):
            ssl._create_default_https_context = (
                lambda *a, _r=ruta, **kw: ssl.create_default_context(cafile=_r))
            _activado = True
            if verboso:
                print(f"[certificados] usando {var}={ruta}", file=sys.stderr)
            _metodo = var
            return _metodo

    # 3) Sin proxy que inspeccione, el bundle de certifi alcanza. No es un error.
    if verboso:
        print("[certificados] sin truststore ni CA propia; bundle por omision",
              file=sys.stderr)
    _metodo = "certifi"
    return _metodo


def diagnosticar(host="olinda.bcb.gov.br", puerto=443):
    """Dice si la conexion TLS a un host la esta firmando una CA que no es publica.

    Pensado para cuando aparece el "Max retries exceeded ... CERTIFICATE_VERIFY_FAILED"
    y hay que decidir si el problema es el proxy de la empresa o de verdad el servidor.
    """
    import socket

    print(f"Probando TLS contra {host}:{puerto}\n")

    # Primero SIN validar: no se descarga nada.
    bruto = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    bruto.check_hostname = False
    bruto.verify_mode = ssl.CERT_NONE
    emisor = None
    try:
        with socket.create_connection((host, puerto), timeout=15) as s:
            with bruto.wrap_socket(s, server_hostname=host) as ts:
                der = ts.getpeercert(binary_form=True)
                # El emisor legible solo esta disponible tras validar; sin validar, la
                # huella al menos confirma que hubo handshake y con que cert.
                import hashlib
                print(f"  handshake OK, huella SHA256 del cert servido: "
                      f"{hashlib.sha256(der).hexdigest()[:32]}...")
    except Exception as e:
        print(f"  no se pudo ni abrir el socket: {type(e).__name__}: {e}")
        print("  -> esto ya no es un problema de certificados; mira red/DNS/firewall.")
        return

    try:
        val = ssl.create_default_context()
        with socket.create_connection((host, puerto), timeout=15) as s:
            with val.wrap_socket(s, server_hostname=host) as ts:
                emisor = dict(x[0] for x in ts.getpeercert()["issuer"])
        print(f"  validacion OK. Emisor: {emisor.get('organizationName', emisor)}")
        print("\n  Los certificados estan bien. El fallo, si lo hay, es de otra cosa.")
    except ssl.SSLCertVerificationError as e:
        print(f"  validacion FALLA: {e.verify_message}")
        print("\n  -> Hay un proxy corporativo (o el antivirus) inspeccionando el HTTPS.")
        print("     Solucion: pip install truststore  y  import certificados")
    except Exception as e:
        print(f"  validacion FALLA con {type(e).__name__}: {e}")


activar()


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "olinda.bcb.gov.br"
    print(f"[certificados] metodo activo: {activar(verboso=True)}\n")
    diagnosticar(destino)
