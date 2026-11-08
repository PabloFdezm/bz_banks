#!/usr/bin/env python3
"""
Framework de descarga del IFDATA (Informaciones Financieras Trimestrales)
del Banco Central do Brasil: datos financieros de las entidades reguladas
(bancos, financieras, cooperativas, corretoras, distribuidoras,
administradoras de consorcio y conglomerados financieros/prudenciales, que
pueden incluir aseguradoras y otras entidades no bancarias del grupo).

Fuente: API OLinda (OData) de datos abiertos del BCB:
  https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata

  - IfDataValores(AnoMes, TipoInstituicao, Relatorio) -> valores del trimestre
  - IfDataCadastro(AnoMes)                            -> registro de entidades
  - ListaDeRelatorio()                                -> catalogo de informes

Escopos (TipoInstituicao):
  1 = prudencial   conglomerado prudencial (IFs + administradoras de consortium,
                   instituciones de pago, adquirentes de credito/factoring,
                   securitizadoras, holdings puras y fondos con riesgo retenido)
  2 = financeiro   conglomerado financiero (solo entidades autorizadas por el BCB)
  3 = individual   la entidad aislada (por CNPJ, no consolidado)
  4 = cambio       instituciones con operaciones de cambio en el periodo
                   (solo informe 15, 12/2014-06/2023)

Trimestral (mar/jun/sep/dic) desde 2000-03. Valores en R$ (unidades).
Publicacion con ~60 dias de rezago (~90 para la base de diciembre).

Cambios de era a tener en cuenta:
  - 2025-03: el BCB renumero codigos de cuentas y migro los informes de
    credito del escopo financeiro (2) al prudencial (1).
  - Los informes disponibles varian por escopo y epoca.

Flujo y capas (ver almacen.py):

  descarga -> datos/crudo/bcb_ifdata/{catalogo,cadastro,valores}/actual/
                 el CSV tal cual lo sirvio OLinda, con manifiesto (URL + sha256).
                 Hace de cache: una respuesta vacia valida tambien queda registrada
                 por bytes/sha256, y los ultimos trimestres caducan a los 95 dias
                 porque la base de diciembre republica los cuatro trimestres previos.
           -> normalizacion y filtros nuestros
           -> datos/derivado/bcb_ifdata/{cadastro,valores,datos}/
                 CSV tidy con manifiesto que nombra los crudos de los que salio y
                 el comando que lo produjo.

Todo lo que sale de `cadastro`, `valores` y `datos` es DERIVADO aunque cada numero
venga del BCB: esta filtrado por escopo, informe, cuenta, institucion o situacion.
"""

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import certificados  # noqa: F401  parchea ssl para la CA corporativa; ver certificados.py
import requests

import almacen as A
import red
from ifdata_texto import a_valor, limpiar, normalizar, nulo, parsear_periodo



def filas_crudo(archivo):
    """Filas (dict de texto) de un crudo, desde el CSV o, si ya se convirtió, desde su parquet."""
    archivo = Path(archivo)
    if archivo.exists():
        with open(archivo, newline="", encoding="utf-8") as f:
            yield from csv.DictReader(f)
    else:
        yield from A.leer_crudo_tabla(archivo).to_dict("records")

BASE = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) bcb-scraper/ifdata-1.0"
PRIMER_PERIODO = "200003"

TIPOS = {1: "prudencial", 2: "financeiro", 3: "individual", 4: "cambio"}
NOMBRE_TIPO = {v: k for k, v in TIPOS.items()}

CAMPOS_VALORES = ["periodo", "escopo", "cod_inst", "institucion", "informe",
                  "num_informe", "grupo", "cod_cuenta", "cuenta",
                  "composicion", "valor"]
CAMPOS_CADASTRO = ["periodo", "cod_inst", "institucion", "tipo_entidad",
                   "inicio_actividad", "tcb", "td", "tc", "segmento",
                   "actividad", "uf", "municipio", "sr", "cod_congl_fin",
                   "cod_congl_prud", "cnpj_lider", "situacion"]


def tamano(ruta):
    n = Path(ruta).stat().st_size
    for unidad in ("B", "KB", "MB", "GB"):
        if n < 1024 or unidad == "GB":
            return f"{n:.1f} {unidad}" if unidad != "B" else f"{n} B"
        n /= 1024


def trimestres(desde, hasta):
    d, h = parsear_periodo(desde, "--desde"), parsear_periodo(hasta, "--hasta")
    if d > h:
        raise ValueError(f"--desde ({d}) es posterior a --hasta ({h})")
    salir, anio, mes = [], int(d[:4]), int(d[4:])
    while True:
        p = f"{anio}{mes:02d}"
        if p > h:
            return salir
        salir.append(p)
        mes += 3
        if mes > 12:
            anio, mes = anio + 1, 3


def ultimo_periodo_disponible(hoy=None):
    """
    Trimestre mas reciente que ya debio publicarse: ~60 dias tras el cierre
    de mar/jun/sep y ~90 tras el de dic (con margen de seguridad).
    """
    hoy = hoy or date.today()
    candidatos = []
    for anio in (hoy.year, hoy.year - 1):
        for mes in (12, 9, 6, 3):
            candidatos.append(f"{anio}{mes:02d}")
    for p in sorted(candidatos, reverse=True):
        base = date(int(p[:4]), int(p[4:]), 1)
        fin = date(base.year + (base.month // 12), base.month % 12 + 1, 1) \
            - timedelta(days=1)
        rezago = 95 if base.month == 12 else 65
        if fin + timedelta(days=rezago) <= hoy:
            return p
    return PRIMER_PERIODO


def ultimos_trimestres(n, hoy=None):
    p = ultimo_periodo_disponible(hoy)
    anio, mes, salir = int(p[:4]), int(p[4:]), []
    for _ in range(n):
        salir.append(f"{anio}{mes:02d}")
        mes -= 3
        if mes < 3:
            anio, mes = anio - 1, 12
    return list(reversed(salir))


def tipo_de_codigo(cod, fila=None):
    """Tipo de entidad segun el codigo (C... = conglomerado) y el cadastro."""
    cod = (cod or "").strip()
    if not cod:
        return ""
    if cod.upper().startswith("C"):
        if fila:
            if cod == nulo(fila.get("CodConglomeradoPrudencial")):
                return "conglomerado prudencial"
            if cod == nulo(fila.get("CodConglomeradoFinanceiro")):
                return "conglomerado financeiro"
        return "conglomerado"
    return "individual"


def tipos_de_escopo(escopo):
    if escopo in ("", "todos"):
        return [1, 2, 3]
    return [NOMBRE_TIPO[escopo]]


def clave_orden(x):
    try:
        v = float(x["valor"])
    except (TypeError, ValueError):
        v = float("-inf")
    return (x["periodo"], -v)


def guardar_csv(filas, ruta, campos):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow({k: fila.get(k, "") for k in campos})


def publicar_derivado(api, salida, dataset, como):
    """Mueve la salida del comando a datos/derivado/ con su procedencia.

    Todo lo que producen estos comandos esta filtrado por nosotros — por escopo,
    informe, cuenta, institucion o situacion — asi que es derivado aunque cada
    numero venga del BCB. Confundir eso es lo que dejo un CSV filtrado pasando por
    dato oficial de la CVM, con un filtro que estaba mal y nadie podia auditar.

    `desde` son los crudos que el comando leyo de verdad, no una lista escrita a
    mano: asi el manifiesto dice de que trimestres salio esta tabla.
    """
    out = Path(salida)
    if not out.exists():
        sys.exit(f"[!] {out} no existe; no se escribio nada")
    destino = A.guardar_derivado("bcb_ifdata", dataset, out.name, out.read_bytes(),
                                 desde=list(api.crudos_usados), como=como)
    if out.resolve() != destino.resolve():
        out.unlink()
    print(f"[publicar] {destino.relative_to(A.RAIZ)}")
    return destino


def como_se_invoco(argv=None):
    """El comando tal cual, para que el manifiesto diga que receta produjo el archivo."""
    return "ifdata.py " + " ".join(argv if argv is not None else sys.argv[1:])


class IFData:
    def __init__(self, delay=0.3, verbose=True, refrescar=False, max_edad_dias=95):
        # Los crudos leidos durante esta corrida, para que un derivado pueda decir
        # de que trimestres salio en vez de declarar una procedencia vacia.
        self.crudos_usados = []
        self.s = requests.Session()
        self.s.headers["User-Agent"] = USER_AGENT
        self.delay = delay
        self.verbose = verbose
        self.refrescar = refrescar
        self.max_edad_dias = max_edad_dias
        self._relatorios = None
        self._nombres = {}
        self._refrescables = None

    def log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _descargar(self, url, destino):
        red.bajar_a_disco(self.s.get, url, destino, intentos=3, reintentables=(requests.RequestException,),
                          pausa_previa=self.delay)

    def periodos_refrescables(self):
        """Trimestres recientes que la fuente todavia puede republicar."""
        if self._refrescables is None:
            self._refrescables = set(ultimos_trimestres(5))
        return self._refrescables

    def _registro_crudo(self, d, nombre):
        man = A.leer_manifiesto(d) or {"archivos": {}}
        return man.get("archivos", {}).get(nombre)

    def _crudo_vigente(self, destino, reg):
        """Un crudo ya bajado sigue siendo cache valido si coincide con su manifiesto.

        El tamano basta para los archivos grandes; en los chicos ademas se verifica el
        sha256 porque una respuesta vacia legitima tiene solo cabecera y antes se volvia
        a descargar en cada corrida.
        """
        if self.refrescar:
            return False
        if not destino.exists():
            # convertido a parquet (y CSV borrado): vale si el parquet es el que anotó el manifiesto
            pq = A.ruta_parquet(destino)
            meta = (reg or {}).get("parquet")
            return bool(pq.exists() and meta and meta.get("bytes") == pq.stat().st_size)
        tam = destino.stat().st_size
        if not reg:
            return tam > A.MIN_BYTES_CRUDO
        if reg.get("bytes") != tam:
            return False
        esperado = reg.get("sha256")
        if esperado and tam <= 4096 and A.sha256_archivo(destino) != esperado:
            return False
        return True

    def _crudo_caducado(self, periodo, reg):
        """True si el trimestre es reciente y la descarga ya paso el maximo de dias.

        La base de diciembre republica contabilidad, capital y credito de los cuatro
        trimestres anteriores; sin caducidad, el cache viejo congelaba esas revisiones.
        """
        if not periodo or not reg or not self.max_edad_dias:
            return False
        cuando = reg.get("descargado_en")
        if not cuando:
            return True
        try:
            descargado = datetime.fromisoformat(cuando)
        except ValueError:
            return True
        if descargado.tzinfo is None:
            descargado = descargado.replace(tzinfo=timezone.utc)
        edad = (datetime.now(timezone.utc) - descargado).days
        return periodo in self.periodos_refrescables() and edad > self.max_edad_dias

    def _asegurar(self, dataset, nombre, url, etiqueta, periodo=None):
        """Ruta del archivo crudo, descargandolo si falta. Registra su procedencia.

        El archivo vive en datos/crudo/bcb_ifdata/<dataset>/actual/: es exactamente
        lo que sirvio OLinda, sin filtro nuestro, asi que es capa cruda. Antes esto
        iba a ifdata_cache/ sin manifiesto, y no habia forma de decir de que URL
        salio cada trimestre.
        """
        d = A.ruta_cruda("bcb_ifdata", dataset)
        d.mkdir(parents=True, exist_ok=True)
        destino = d / nombre

        reg = self._registro_crudo(d, nombre)
        vale = self._crudo_vigente(destino, reg)
        if vale and self._crudo_caducado(periodo, reg):
            vale = False

        if not vale:
            self.log(f"[~] Descargando {etiqueta}...")
            self._descargar(url, destino)
            A.registrar_crudo("bcb_ifdata", dataset, destino, url)
            self.log(f"[+] {destino.name} ({tamano(destino)})")
            if destino.suffix == ".csv":   # todo texto, sin pérdida y ~80 veces menos espacio
                pq = A.csv_a_parquet("bcb_ifdata", dataset, destino, borrar_csv=True)
                self.log(f"    -> {pq.name} ({tamano(pq)})")
        elif destino.exists() and not self._registro_crudo(d, nombre):
            mtime = datetime.fromtimestamp(destino.stat().st_mtime, timezone.utc)
            A.registrar_crudo("bcb_ifdata", dataset, destino, url,
                              descargado_en=mtime.isoformat(),
                              nota="archivo existente registrado retroactivamente")

        rel = str(destino.relative_to(A.DATOS))
        if rel not in self.crudos_usados:
            self.crudos_usados.append(rel)
        return destino

    def relatorios(self):
        if self._relatorios is None:
            archivo = self._asegurar(
                "catalogo", "relatorios.json",
                f"{BASE}/ListaDeRelatorio()?$format=json",
                "catalogo de informes")
            datos = json.loads(archivo.read_text(encoding="utf-8"))
            self._relatorios = datos["value"]
        return self._relatorios

    def resolver_informe(self, ref):
        """Nombre o numero de informe -> (numero, nombre) del catalogo."""
        rels = self.relatorios()
        if str(ref).strip().isdigit():
            for r in rels:
                if r["NumeroRelatorio"] == str(int(ref)):
                    return int(r["NumeroRelatorio"]), r["NomeRelatorio"]
            raise SystemExit(f"[!] No existe el informe numero {ref}. "
                             f"Ver: python3 ifdata.py relatorios")
        objetivo = normalizar(ref)
        for r in rels:
            if normalizar(r["NomeRelatorio"]) == objetivo:
                return int(r["NumeroRelatorio"]), r["NomeRelatorio"]
        parciales = [r for r in rels if objetivo in normalizar(r["NomeRelatorio"])]
        if len(parciales) == 1:
            return int(parciales[0]["NumeroRelatorio"]), parciales[0]["NomeRelatorio"]
        if parciales:
            lista = "\n  ".join(f'{r["NumeroRelatorio"]}: {r["NomeRelatorio"]}'
                                for r in parciales)
            raise SystemExit(f"[!] '{ref}' coincide con varios informes:\n  {lista}")
        raise SystemExit(f"[!] Informe no encontrado: {ref}")

    def archivo_cadastro(self, ano_mes):
        url = (f"{BASE}/IfDataCadastro(AnoMes=@AnoMes)"
               f"?@AnoMes={ano_mes}&$format=text/csv")
        return self._asegurar("cadastro", A.ruta_cadastro(ano_mes).name, url,
                              f"cadastro {ano_mes}", periodo=ano_mes)

    def leer_cadastro(self, ano_mes):
        archivo = self.archivo_cadastro(ano_mes)
        for fila in filas_crudo(archivo):
            cod = nulo(fila.get("CodInst"))
            yield {
                "periodo": nulo(fila.get("Data")) or ano_mes,
                "cod_inst": cod,
                "institucion": limpiar(fila.get("NomeInstituicao")),
                "tipo_entidad": tipo_de_codigo(cod, fila),
                "inicio_actividad": nulo(fila.get("DataInicioAtividade")),
                "tcb": nulo(fila.get("Tcb")),
                "td": nulo(fila.get("Td")),
                "tc": nulo(fila.get("Tc")),
                "segmento": nulo(fila.get("SegmentoTb")),
                "actividad": nulo(fila.get("Atividade")),
                "uf": nulo(fila.get("Uf")),
                "municipio": nulo(fila.get("Municipio")),
                "sr": nulo(fila.get("Sr")),
                "cod_congl_fin": nulo(fila.get("CodConglomeradoFinanceiro")),
                "cod_congl_prud": nulo(fila.get("CodConglomeradoPrudencial")),
                "cnpj_lider": nulo(fila.get("CnpjInstituicaoLider")),
                "situacion": nulo(fila.get("Situacao")),
            }

    def nombres(self, ano_mes):
        """Mapa cod_inst -> nombre para el trimestre (memoizado)."""
        if ano_mes not in self._nombres:
            self._nombres[ano_mes] = {
                x["cod_inst"]: x["institucion"]
                for x in self.leer_cadastro(ano_mes)
            }
        return self._nombres[ano_mes]

    def _url_valores(self, ano_mes, tipo, numero=None):
        rel = "T" if numero is None else str(numero)
        return (f"{BASE}/IfDataValores(AnoMes=@AnoMes,"
                f"TipoInstituicao=@TipoInstituicao,Relatorio=@Relatorio)"
                f"?@AnoMes={ano_mes}&@TipoInstituicao={tipo}"
                f"&@Relatorio=%27{rel}%27&$format=text/csv")

    def archivo_valores(self, ano_mes, tipo, numero=None):
        nombre = A.ruta_valores(ano_mes, tipo, numero).name
        if numero is None:
            etiqueta = f"valores {ano_mes} escopo {TIPOS[tipo]} (todos los informes)"
        else:
            etiqueta = f"valores {ano_mes} escopo {TIPOS[tipo]} informe {numero}"
        return self._asegurar("valores", nombre,
                              self._url_valores(ano_mes, tipo, numero), etiqueta,
                              periodo=ano_mes)

    def leer_valores(self, ano_mes, tipo, informe=None):
        """
        Itera las filas CRUDAS de un trimestre/escopo.
        informe: None -> todos; (numero, nombre) -> solo ese informe. Si hay
        cache completo se filtra en local; si no, se descarga solo ese
        informe (mas liviano). Si la numeracion antigua no coincide con el
        nombre pedido, se baja todo y se filtra por nombre.
        """
        numero = informe[0] if informe else None
        nombre = informe[1] if informe else None
        filtro = None
        if numero is None:
            archivo = self.archivo_valores(ano_mes, tipo)
        else:
            completo = A.ruta_valores(ano_mes, tipo)
            if A.existe_crudo(completo) and not self.refrescar and A.crudo_con_datos(completo):
                archivo, filtro = completo, ("num", str(numero))
                rel = str(completo.relative_to(A.DATOS))
                if rel not in self.crudos_usados:
                    self.crudos_usados.append(rel)
            else:
                archivo = self.archivo_valores(ano_mes, tipo, numero)
                if nombre:
                    primera = next(iter(filas_crudo(archivo)), None)
                    if primera and \
                            normalizar(primera.get("NomeRelatorio")) != normalizar(nombre):
                        self.log(f"  [!] En {ano_mes} el informe {numero} no es "
                                 f"'{nombre}' (numeracion antigua); se baja todo "
                                 f"y se filtra por nombre")
                        archivo = self.archivo_valores(ano_mes, tipo)
                        filtro = ("nombre", nombre)
        vistos = set()
        for fila in filas_crudo(archivo):
            if filtro:
                if filtro[0] == "num":
                    if nulo(fila.get("NumeroRelatorio")) != filtro[1]:
                        continue
                elif normalizar(fila.get("NomeRelatorio")) != normalizar(filtro[1]):
                    continue
            # la API a veces devuelve filas exactas repetidas (republicaciones); se descartan
            clave = hash(tuple(fila.values()))
            if clave in vistos:
                continue
            vistos.add(clave)
            yield fila

    def valores(self, ano_mes, tipo, informe=None):
        """Itera filas NORMALIZADAS (tidy) de un trimestre/escopo."""
        nombres = self.nombres(ano_mes)
        for fila in self.leer_valores(ano_mes, tipo, informe):
            cod = nulo(fila.get("CodInst"))
            yield {
                "periodo": nulo(fila.get("AnoMes")) or ano_mes,
                "escopo": TIPOS[tipo],
                "cod_inst": cod,
                "institucion": nombres.get(cod, ""),
                "informe": limpiar(fila.get("NomeRelatorio")),
                "num_informe": nulo(fila.get("NumeroRelatorio")),
                "grupo": nulo(fila.get("Grupo")),
                "cod_cuenta": nulo(fila.get("Conta")),
                "cuenta": limpiar(fila.get("NomeColuna")),
                "composicion": nulo(fila.get("DescricaoColuna")),
                "valor": a_valor(fila.get("Saldo")),
            }

    def resolver_institucion(self, ref, periodo):
        """
        ref: codigo (C0080099 o 60394079) o texto del nombre.
        Devuelve (cod_inst, nombre, tipos_a_consultar).
        """
        ref = str(ref).strip()
        if re.fullmatch(r"\d{8}|[Cc]\d{7}", ref):
            ref = ref.upper()
            for x in self.leer_cadastro(periodo):
                if x["cod_inst"] == ref:
                    return ref, x["institucion"], _tipos_de(x)
            tipos = [1, 2] if ref.startswith("C") else [3]
            return ref, "", tipos
        objetivo = normalizar(ref)
        candidatas = [x for x in self.leer_cadastro(periodo)
                      if objetivo in normalizar(x["institucion"])]
        if not candidatas:
            raise SystemExit(f"[!] Ninguna entidad contiene '{ref}' en {periodo}. "
                             f"Prueba: python3 ifdata.py instituciones "
                             f"--periodo {periodo} --texto ...")
        exactas = [x for x in candidatas
                   if normalizar(x["institucion"]) == objetivo
                   and x["situacion"] == "A"]
        if len(exactas) == 1:
            candidatas = exactas
        if len(candidatas) > 1:
            print("[!] Varias entidades coinciden; se mas especifico o usa "
                  "el codigo:", file=sys.stderr)
            for x in candidatas[:15]:
                print(f"    {x['cod_inst']:>9}  {x['institucion']}"
                      f"  ({x['tipo_entidad']}, {x['situacion']})",
                      file=sys.stderr)
            raise SystemExit(1)
        x = candidatas[0]
        return x["cod_inst"], x["institucion"], _tipos_de(x)


def _tipos_de(entidad_cadastro):
    cod = entidad_cadastro["cod_inst"]
    if cod.upper().startswith("C"):
        if cod == entidad_cadastro["cod_congl_prud"]:
            return [1]
        if cod == entidad_cadastro["cod_congl_fin"]:
            return [2]
        return [1, 2]
    return [3]


def add_periodos(sp):
    sp.add_argument("--periodo", default="",
                    help="un trimestre AAAAMM (ej. 202603)")
    sp.add_argument("--desde", default="",
                    help="trimestre inicial del rango (AAAAMM)")
    sp.add_argument("--hasta", default="",
                    help="trimestre final del rango (AAAAMM)")


def resolver_periodos(args, defecto_ultimos=0):
    if args.periodo:
        if args.desde or args.hasta:
            raise SystemExit("[>] Usa --periodo O --desde/--hasta, no ambos")
        return [parsear_periodo(args.periodo)]
    if args.desde or args.hasta:
        if not (args.desde and args.hasta):
            raise SystemExit("[>] --desde y --hasta van juntos")
        return trimestres(args.desde, args.hasta)
    if defecto_ultimos:
        return ultimos_trimestres(defecto_ultimos)
    raise SystemExit("[>] Falta --periodo o --desde/--hasta "
                     "(ej. --periodo 202603 o --desde 202403 --hasta 202603)")


def resolver_informes(api, refs):
    """Lista de referencias de informe -> numeros de catalogo, o [None] para todos."""
    if not refs:
        return [None]
    numeros = []
    for ref in refs:
        for parte in str(ref).split(","):
            parte = parte.strip()
            if parte:
                numeros.append(api.resolver_informe(parte)[0])
    return sorted(set(numeros)) or [None]


def cmd_valores(api, args):
    periodos = resolver_periodos(args)
    tipos = tipos_de_escopo(args.escopo)
    informe = api.resolver_informe(args.informe) if args.informe else None
    cuenta = normalizar(args.cuenta) if args.cuenta else ""
    if not informe and len(periodos) > 4:
        api.log("[i] Tip: --informe y/o --cuenta reducen mucho la descarga")
    filas = []
    for p in periodos:
        for t in tipos:
            n0 = len(filas)
            for x in api.valores(p, t, informe):
                if cuenta and cuenta not in normalizar(x["cuenta"]):
                    continue
                filas.append(x)
            api.log(f"[~] {p} {TIPOS[t]}: {len(filas) - n0} filas")
    if cuenta:
        filas.sort(key=clave_orden)
    guardar_csv(filas, args.salida, CAMPOS_VALORES)
    ninst = len({x["cod_inst"] for x in filas})
    print(f"[+] {len(filas)} filas, {ninst} entidades, "
          f"{len(periodos)} trimestre(s)")
    publicar_derivado(api, args.salida, "valores", api.invocacion)


def cmd_datos(api, args):
    explicito = bool(args.periodo or args.desde or args.hasta)
    periodos = resolver_periodos(args, defecto_ultimos=4)
    if not explicito:
        api.log(f"[i] Sin --periodo/--desde: ultimos 4 trimestres "
                f"({periodos[0]}..{periodos[-1]})")
    cod, nombre, tipos_auto = api.resolver_institucion(args.institucion,
                                                       periodos[0])
    tipos = tipos_de_escopo(args.escopo) if args.escopo else tipos_auto
    informe = api.resolver_informe(args.informe) if args.informe else None
    cuenta = normalizar(args.cuenta) if args.cuenta else ""
    api.log(f"[+] {nombre or cod} ({cod}) escopo(s): "
            f"{', '.join(TIPOS[t] for t in tipos)}")
    if not informe and len(periodos) > 4:
        api.log("[i] Tip: --informe y/o --cuenta reducen mucho la descarga")
    filas = []
    for p in periodos:
        for t in tipos:
            n0 = len(filas)
            for x in api.valores(p, t, informe):
                if x["cod_inst"] != cod:
                    continue
                if cuenta and cuenta not in normalizar(x["cuenta"]):
                    continue
                if not x["institucion"]:
                    x["institucion"] = nombre
                filas.append(x)
            api.log(f"[~] {p} {TIPOS[t]}: {len(filas) - n0} filas")
    if cuenta:
        filas.sort(key=clave_orden)
    guardar_csv(filas, args.salida, CAMPOS_VALORES)
    print(f"[+] {len(filas)} filas de {nombre or cod} en "
          f"{len(periodos)} trimestre(s)")
    publicar_derivado(api, args.salida, "datos", api.invocacion)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Framework de descarga del IFDATA del BCB (API OLinda). "
                    "Lo que sirve OLinda queda en datos/crudo/bcb_ifdata/ (y hace "
                    "de cache); lo que producen los comandos, en "
                    "datos/derivado/bcb_ifdata/.")
    ap.add_argument("--delay", type=float, default=0.3,
                    help="pausa entre peticiones en segundos (defecto: 0.3)")
    ap.add_argument("--refrescar", action="store_true",
                    help="ignorar el cache y volver a descargar")
    ap.add_argument("--max-edad-dias", type=int, default=95,
                    help="dias tras los cuales un trimestre reciente se vuelve a bajar "
                         "(defecto: 95; 0 desactiva la caducidad)")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="silenciar el progreso")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("relatorios",
                   help="catalogo de informes disponibles (numero y nombre)")

    sp = sub.add_parser("instituciones",
                        help="buscar entidades en el registro del trimestre")
    sp.add_argument("--periodo", required=True, help="trimestre AAAAMM")
    sp.add_argument("--texto", default="",
                    help="texto a buscar en nombre/codigo/UF/municipio")
    sp.add_argument("--todos", action="store_true",
                    help="incluir entidades inactivas o en liquidacion")
    sp.add_argument("--limite", type=int, default=40,
                    help="maximo de resultados a listar (defecto: 40)")

    sp = sub.add_parser("cadastro",
                        help="exportar el registro de entidades")
    add_periodos(sp)
    sp.add_argument("-o", "--salida", default="ifdata_cadastro.csv")
    sp.add_argument("--texto", default="", help="filtrar por texto")
    sp.add_argument("--situacion", default="",
                    help="filtrar por situacion (A=activa, I=inactiva, "
                         "LO/LE=liquidacion, F)")

    sp = sub.add_parser("valores",
                        help="exportar valores (todas las entidades)")
    add_periodos(sp)
    sp.add_argument("--escopo", default="todos",
                    choices=["prudencial", "financeiro", "individual", "cambio", "todos"])
    sp.add_argument("--informe", default="",
                    help="nombre o numero de informe (ej. Resumo o 1); vacio = todos")
    sp.add_argument("--cuenta", default="",
                    help="filtrar cuentas por texto (ej. 'Ativo Total')")
    sp.add_argument("-o", "--salida", default="ifdata_valores.csv")

    sp = sub.add_parser("datos",
                        help="datos de UNA entidad a lo largo del tiempo "
                             "(serie: agrega --cuenta, ej. 'Ativo Total')")
    sp.add_argument("--institucion", required=True,
                    help="codigo (C0080099 / 60394079) o nombre (ej. 'itau')")
    add_periodos(sp)
    sp.add_argument("--escopo", default="",
                    choices=["", "prudencial", "financeiro", "individual", "cambio"])
    sp.add_argument("--informe", default="",
                    help="nombre o numero de informe (reduce la descarga)")
    sp.add_argument("--cuenta", default="",
                    help="filtrar cuentas por texto (ej. 'Ativo Total')")
    sp.add_argument("-o", "--salida", default="ifdata_datos.csv")

    sp = sub.add_parser("colectar",
                        help="descarga masiva al cache (valores completos + "
                             "cadastro), sin generar CSV")
    add_periodos(sp)
    sp.add_argument("--escopo", default="todos",
                    choices=["prudencial", "financeiro", "individual", "cambio", "todos"])
    sp.add_argument("--informe", action="append", default=[],
                    help="nombre o numero de informe a descargar; se puede repetir o "
                         "separar por comas (vacio = todos los informes)")
    sp.add_argument("--sin-cadastro", action="store_true",
                    help="no descargar los registros de entidades")

    args = ap.parse_args(argv)
    api = IFData(delay=args.delay, verbose=not args.quiet,
                 refrescar=args.refrescar, max_edad_dias=args.max_edad_dias)
    api.invocacion = como_se_invoco(argv)

    if args.cmd == "relatorios":
        print(f"{'N.o':>4}  Informe")
        for r in api.relatorios():
            print(f"{r['NumeroRelatorio']:>4}  {r['NomeRelatorio']}")
        print("\nEscopos: 1=prudencial 2=financeiro 3=individual 4=cambio. La "
              "disponibilidad varia por escopo y epoca (ej. credito: "
              "financeiro hasta 2024-12, prudencial desde 2025-03; "
              "cambio: 12/2014-06/2023, solo informe 15).")

    elif args.cmd == "instituciones":
        texto = normalizar(args.texto)
        n = 0
        for x in api.leer_cadastro(args.periodo):
            if not args.todos and x["situacion"] != "A":
                continue
            if texto:
                blob = normalizar(" ".join((x["institucion"], x["cod_inst"],
                                            x["uf"], x["municipio"])))
                if texto not in blob:
                    continue
            n += 1
            if n <= args.limite:
                print(f"{x['cod_inst']:>9}  {x['institucion'][:46]:<46}"
                      f"  {x['tipo_entidad'][:24]:<24}"
                      f"  {x['tcb'] or '-':<4} {x['uf'] or '-':<2}"
                      f"  {x['situacion']}")
        if n > args.limite:
            print(f"... y {n - args.limite} mas (usa --texto o --limite)")
        api.log(f"[+] {n} entidades (situacion "
                f"{'todas' if args.todos else 'A'}) en {args.periodo}")

    elif args.cmd == "cadastro":
        periodos = resolver_periodos(args)
        texto = normalizar(args.texto)
        filas = []
        for p in periodos:
            for x in api.leer_cadastro(p):
                if args.situacion and x["situacion"] != args.situacion:
                    continue
                if texto and texto not in normalizar(" ".join(x.values())):
                    continue
                filas.append(x)
        guardar_csv(filas, args.salida, CAMPOS_CADASTRO)
        activas = sum(1 for x in filas if x["situacion"] == "A")
        print(f"[+] {len(filas)} entidades ({activas} activas) en "
              f"{len(periodos)} trimestre(s)")
        publicar_derivado(api, args.salida, "cadastro", api.invocacion)

    elif args.cmd == "valores":
        cmd_valores(api, args)

    elif args.cmd == "datos":
        cmd_datos(api, args)

    elif args.cmd == "colectar":
        periodos = resolver_periodos(args, defecto_ultimos=1)
        tipos = tipos_de_escopo(args.escopo)
        informes = resolver_informes(api, args.informe)
        for p in periodos:
            if not args.sin_cadastro:
                api.archivo_cadastro(p)
            for t in tipos:
                for numero in informes:
                    api.archivo_valores(p, t, numero)
        etiqueta_informes = "todos los informes" if informes == [None] else \
            ", ".join(str(n) for n in informes)
        print(f"[+] Cache actualizado: {len(periodos)} trimestre(s) x "
              f"{len(tipos)} escopo(s) x {etiqueta_informes} en "
              f"{A.ruta_cruda('bcb_ifdata', 'valores').parent.relative_to(A.RAIZ)}")


if __name__ == "__main__":
    main()
