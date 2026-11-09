# -*- coding: utf-8 -*-
"""Pruebas de la fuente CVM (ITR/DFP) y de bk_publicado.

Las unitarias son sintéticas y sin red: reproducen las trampas reales de la fuente (cuentas duplicadas por
ORDEM_EXERC, varias versiones, escala en R$ mil, trimestre contra acumulado en la DRE, códigos que se corren
entre años, bancos que dejan la cuenta en 0) sobre un fixture mínimo. Las marcadas `integracion` leen
datos/ y se omiten si no está.
"""
from __future__ import annotations

import pandas as pd
import pytest

import almacen as A
import cvm
from conftest import GOLD

# Un banco ficticio del panel, para no depender del mapa real en las pruebas unitarias.
COD = "C0080099"
CNPJ = "60.872.504/0001-23"
RAIZ = "60872504"


def _fila(**kw) -> dict:
    """Una fila del derivado con los valores por omisión de un ITR consolidado de 2T26."""
    base = {"cod_inst": COD, "nombre_corto": "Banco de Prueba", "documento": "ITR", "anio_zip": "2026",
            "estado": "BPA", "tipo_estado": "con", "cnpj": CNPJ, "cd_cvm": "019348",
            "denominacion": "BANCO DE PRUEBA S.A.", "dt_refer": "2026-06-30", "versao": "1",
            "ordem_exerc": "ÚLTIMO", "dt_ini_exerc": "", "dt_fim_exerc": "2026-06-30",
            "grupo": "DF Consolidado - Balanço Patrimonial Ativo", "cd_conta": "1", "ds_conta": "Ativo Total",
            "vl_conta": "1000.0000000000", "escala": "MIL", "moeda": "REAL", "st_conta_fixa": "S"}
    base.update(kw)
    return base


def _derivado(filas: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(filas, columns=cvm.COLUMNAS_DERIVADO)


@pytest.fixture
def mapa_falso(monkeypatch):
    """Un mapa de un solo banco que entrega consolidado."""
    df = pd.DataFrame([{
        "cod_inst": COD, "nombre_corto": "Banco de Prueba", "cnpj_raiz": RAIZ, "cnpj_ifdata": RAIZ,
        "cd_cvm": "019348", "denominacion_cvm": "BANCO DE PRUEBA S.A.", "tipo_estado": "con",
        "usar_individual_si_falta": False, "base": "CPC", "entrega": True, "registro_cvm": "Bancos",
        "nota": "fixture",
    }])
    monkeypatch.setattr(cvm, "mapa_bancos", lambda: df)
    return df


@pytest.fixture
def derivado_en_disco(monkeypatch, tmp_path):
    """Escribe un derivado sintético y hace que cvm lo lea de ahí."""
    def _escribir(filas: list[dict]) -> None:
        tmp_path.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(filas, columns=cvm.COLUMNAS_DERIVADO).to_parquet(tmp_path / "estados_itr_2026.parquet")
        monkeypatch.setattr(cvm.A, "ruta_derivada", lambda fuente, dataset: tmp_path)
    return _escribir


# --- utilidades ----------------------------------------------------------------------------------------- #

def test_raiz_cnpj():
    assert cvm.raiz_cnpj("60.872.504/0001-23") == "60872504"
    assert cvm.raiz_cnpj("00000000000191") == "00000000"
    assert cvm.raiz_cnpj(12345678901234) == "12345678"


def test_numero_cvm_punto_y_coma():
    assert cvm.numero_cvm("3202125000.0000000000") == 3202125000.0
    assert cvm.numero_cvm("-49896000.0000000000") == -49896000.0
    assert cvm.numero_cvm("1.234,56") == 1234.56          # formato brasileño
    with pytest.raises(ValueError):
        cvm.numero_cvm("")
    with pytest.raises(ValueError):
        cvm.numero_cvm("n/d")


def test_periodo_de_referencia():
    assert cvm.periodo_de_referencia("2026-06-30") == "202606"
    assert cvm.periodo_de_referencia("2026-12-31") == "202612"
    assert cvm.periodo_de_referencia("2026-02-28") is None     # no es fin de trimestre
    assert cvm.periodo_de_referencia("2026-06-29") is None     # fin de trimestre mal escrito
    assert cvm.periodo_de_referencia("basura") is None


def test_normalizar_descripciones():
    assert cvm.normalizar("(-) Provisão para Perda Esperada") == "provisao para perda esperada"
    assert cvm.normalizar("Atribuído aos Sócios da Empresa Controladora").startswith("atribuido aos socios")
    assert "controladora" in cvm.normalizar("Atribuído a Sócios da Empresa Controladora")


# --- trampas de la fuente ------------------------------------------------------------------------------- #

def test_ordem_exerc_deja_solo_el_ultimo(mapa_falso, derivado_en_disco):
    """Trampa 1: cada cuenta viene dos veces (ÚLTIMO y PENÚLTIMO); sin filtrar se duplica y se mezcla el año."""
    derivado_en_disco([
        _fila(vl_conta="2000.0"),                                             # ÚLTIMO 2026-06-30
        _fila(ordem_exerc="PENÚLTIMO", dt_fim_exerc="2025-12-31", vl_conta="1500.0"),
    ])
    d, avisos = cvm.estados_preparados(mapa_falso)
    assert len(d) == 1                       # la fila PENÚLTIMO (2025-12-31) no entra
    assert d.iloc[0]["periodo"] == "202606"
    assert d.iloc[0]["valor"] == 2_000_000.0
    assert avisos == []


def test_version_mayor_gana(mapa_falso, derivado_en_disco):
    """Trampa 4: una compañía puede reentregar; se usa la VERSAO mayor."""
    derivado_en_disco([
        _fila(versao="1", vl_conta="1000.0"),
        _fila(versao="3", vl_conta="1200.0"),
        _fila(versao="2", vl_conta="1100.0"),
    ])
    d, avisos = cvm.estados_preparados(mapa_falso)
    assert len(d) == 1
    assert d.iloc[0]["valor"] == 1_200_000.0
    assert any("VERSAO" in a for a in avisos)


def test_escala_mil_multiplica_por_mil(mapa_falso, derivado_en_disco):
    """Trampa 2: los valores vienen en R$ mil; bk_publicado tiene que estar en R$."""
    derivado_en_disco([_fila(vl_conta="2854475.0000000000", escala="MIL")])
    d, _ = cvm.estados_preparados(mapa_falso)
    assert d.iloc[0]["valor"] == pytest.approx(2_854_475_000.0)


def test_escala_unidad_no_multiplica(mapa_falso, derivado_en_disco):
    derivado_en_disco([_fila(vl_conta="42.0", escala="UNIDADE")])
    d, _ = cvm.estados_preparados(mapa_falso)
    assert d.iloc[0]["valor"] == pytest.approx(42.0)


def test_escala_desconocida_falla(mapa_falso, derivado_en_disco):
    derivado_en_disco([_fila(escala="MILLONES")])
    with pytest.raises(ValueError, match="ESCALA_MOEDA"):
        cvm.estados_preparados(mapa_falso)


def test_moneda_distinta_de_real_falla(mapa_falso, derivado_en_disco):
    derivado_en_disco([_fila(moeda="DOLAR")])
    with pytest.raises(ValueError, match="moneda"):
        cvm.estados_preparados(mapa_falso)


def test_dre_trimestre_contra_acumulado(mapa_falso, derivado_en_disco):
    """Trampa 3: la DRE del ITR trae el trimestre y el acumulado; se distinguen por DT_INI_EXERC."""
    derivado_en_disco([
        _fila(estado="DRE", dt_ini_exerc="2026-01-01", cd_conta="3.03", vl_conta="71756.0"),
        _fila(estado="DRE", dt_ini_exerc="2026-04-01", cd_conta="3.03", vl_conta="37059.0"),
    ])
    d, avisos = cvm.estados_preparados(mapa_falso)
    assert avisos == []
    medidas = dict(zip(d["medida"], d["valor"]))
    assert medidas["acumulado"] == pytest.approx(71_756_000.0)
    assert medidas["trimestre"] == pytest.approx(37_059_000.0)


def test_dre_de_primer_trimestre_va_tambien_como_trimestre(mapa_falso, derivado_en_disco):
    """En el 1T el acumulado y el trimestre son la misma cifra y la CVM entrega una sola fila."""
    derivado_en_disco([
        _fila(estado="DRE", dt_refer="2026-03-31", dt_fim_exerc="2026-03-31",
              dt_ini_exerc="2026-01-01", cd_conta="3.03", vl_conta="100.0"),
    ])
    d, _ = cvm.estados_preparados(mapa_falso)
    assert sorted(d["medida"]) == ["acumulado", "trimestre"]
    assert d["periodo"].tolist() == ["202603", "202603"]


def test_dre_con_periodo_raro_se_descarta_y_avisa(mapa_falso, derivado_en_disco):
    """Caso real: BRB entrega en la DFP una DRE que cubre solo diciembre (dt_ini 2023-12-01)."""
    derivado_en_disco([
        _fila(estado="DRE", documento="DFP", anio_zip="2023", dt_refer="2023-12-31",
              dt_fim_exerc="2023-12-31", dt_ini_exerc="2023-12-01", cd_conta="3.11", vl_conta="204880.0"),
    ])
    d, avisos = cvm.estados_preparados(mapa_falso)
    assert d.empty
    assert any("2023-12-01" in a for a in avisos)


def test_cnpj_fuera_del_mapa_rompe_la_corrida(derivado_en_disco, mapa_falso):
    """Ningún CNPJ que no esté en definiciones/cvm__bancos.json puede llegar a bk_publicado."""
    derivado_en_disco([_fila(cod_inst="C0099999", cnpj="99.999.999/0001-99")])
    with pytest.raises(ValueError, match="fuera del mapa"):
        cvm.estados_preparados(mapa_falso)


def test_dt_refer_que_no_es_fin_de_trimestre_se_descarta(mapa_falso, derivado_en_disco):
    derivado_en_disco([_fila(dt_refer="2026-05-31", dt_fim_exerc="2026-05-31")])
    d, avisos = cvm.estados_preparados(mapa_falso)
    assert d.empty
    assert any("fin de trimestre" in a for a in avisos)


# --- resolución de líneas ------------------------------------------------------------------------------- #

def _cuentas(filas: list[dict]) -> pd.DataFrame:
    d = _derivado(filas)
    d["valor"] = [cvm.numero_cvm(v) * cvm.ESCALAS[e] for v, e in zip(d["vl_conta"], d["escala"])]
    d["ds_norm"] = d["ds_conta"].map(cvm.normalizar)
    d["medida"] = ["saldo"] * len(d)
    return d


def test_resolver_por_codigo_y_descripcion():
    cuentas = _cuentas([_fila(cd_conta="1.02.03.05", ds_conta="Operações de Crédito e Arrendamento Mercantil "
                                                              "Financeiro", estado="BPA", vl_conta="1082266.0")])
    spec = {"estado": "BPA", "alternativas": [
        {"suma": [{"cd": ["1.02.03.05", "1.02.03.04"], "ds": ["operacoes de credito"]}]}]}
    r = cvm.resolver(cuentas, spec, "saldo", "2026-06-30")
    assert r["valor"] == pytest.approx(1_082_266_000.0)
    assert r["cd_conta"] == "1.02.03.05"


def test_resolver_el_codigo_se_corre_entre_anios():
    """Itaú: la cartera era 1.02.03.04 hasta el DFP 2023 y es 1.02.03.05 desde 2024."""
    spec = {"estado": "BPA", "alternativas": [
        {"suma": [{"cd": ["1.02.03.05", "1.02.03.04"], "ds": ["operacoes de credito"]}]}]}
    vieja = _cuentas([_fila(cd_conta="1.02.03.04", ds_conta="Operações de Crédito e Arrendamento Mercantil "
                                                            "Financeiro", vl_conta="910590.0")])
    assert cvm.resolver(vieja, spec, "saldo", "2023-12-31")["valor"] == pytest.approx(910_590_000.0)


def test_resolver_la_descripcion_evita_un_codigo_que_cambio_de_significado():
    """Pine: 2.07 fue «Patrimônio Líquido Consolidado» hasta 2024 y «Passivos sobre Ativos...» desde 2025."""
    spec = {"estado": "BPP", "alternativas": [
        {"suma": [{"cd": ["2.07", "2.08"], "ds": ["patrimonio liquido", "consolidado"]}]}]}
    pine_2025 = _cuentas([
        _fila(estado="BPP", cd_conta="2.07", ds_conta="Passivos sobre Ativos Não Correntes a Venda e "
                                                      "Descontinuados", vl_conta="0.0"),
        _fila(estado="BPP", cd_conta="2.08", ds_conta="Patrimônio Líquido Consolidado", vl_conta="1830889.0"),
    ])
    r = cvm.resolver(pine_2025, spec, "saldo", "2026-06-30")
    assert r["valor"] == pytest.approx(1_830_889_000.0)
    assert r["cd_conta"] == "2.08"


def test_resolver_suma_y_resta():
    """PL del controlador = PL consolidado − participación de los no controladores."""
    cuentas = _cuentas([
        _fila(estado="BPP", cd_conta="2.08", ds_conta="Patrimônio Líquido Consolidado", vl_conta="228026000.0"),
        _fila(estado="BPP", cd_conta="2.08.09", ds_conta="Participação dos Acionistas Não Controladores",
              vl_conta="10247000.0"),
    ])
    spec = {"estado": "BPP", "alternativas": [
        {"suma": [{"cd": ["2.08"], "ds": ["patrimonio liquido"]}],
         "resta": [{"cd": ["2.08.09"], "ds": ["nao controladores"]}]}]}
    r = cvm.resolver(cuentas, spec, "saldo", "2026-06-30")
    assert r["valor"] == pytest.approx((228_026_000 - 10_247_000) * 1000)
    assert r["cd_conta"] == "2.08 + 2.08.09"


def test_resolver_alternativas_en_orden():
    cuentas = _cuentas([_fila(estado="BPP", cd_conta="2.07", ds_conta="Patrimônio Líquido", vl_conta="7258915.0")])
    spec = {"estado": "BPP", "alternativas": [
        {"suma": [{"cd": ["2.07"], "ds": ["patrimonio liquido", "consolidado"]}]},   # no casa
        {"suma": [{"cd": ["2.07"], "ds": ["patrimonio liquido"]}]},                  # casa
    ]}
    r = cvm.resolver(cuentas, spec, "saldo", "2026-06-30")
    assert r["alternativa"] == 2
    assert r["valor"] == pytest.approx(7_258_915_000.0)


def test_resolver_ventana_desde_hasta():
    """ABC y Mercantil publican la provisión solo desde el 1T25: antes el saldo de crédito es neto."""
    spec = {"estado": "BPA", "alternativas": [
        {"suma": [{"cd": ["1.02.04.04"], "ds": ["operacoes de credito"], "desde": "2025-03-31"}]}]}
    cuentas = _cuentas([_fila(cd_conta="1.02.04.04", ds_conta="Operações de Crédito", vl_conta="22755080.0")])
    assert cvm.resolver(cuentas, spec, "saldo", "2024-12-31")["problema"] == "FUERA_DE_VENTANA"
    assert cvm.resolver(cuentas, spec, "saldo", "2025-03-31")["valor"] == pytest.approx(22_755_080_000.0)


def test_resolver_cero_es_vacio():
    """Banco do Brasil deja la provisión en 0: no es un dato, es que no la divulga."""
    spec = {"estado": "BPA", "signo": "positivo", "cero_es_vacio": True, "alternativas": [
        {"suma": [{"cd": ["1.02.04.05"], "ds": ["perdas esperadas"]}]}]}
    cuentas = _cuentas([_fila(cd_conta="1.02.04.05",
                              ds_conta="Provisão para Perdas Esperadas Associadas ao Risco de Crédito",
                              vl_conta="0.0")])
    r = cvm.resolver(cuentas, spec, "saldo", "2026-06-30")
    assert r["valor"] is None
    assert "0" in r["problema"]


def test_resolver_signo_positivo_en_la_provision():
    """La provisión viene negativa (contra-activo) y se publica en positivo."""
    spec = {"estado": "BPA", "signo": "positivo", "alternativas": [
        {"suma": [{"cd": ["1.02.04.05"], "ds": ["perdas esperadas"]}]}]}
    cuentas = _cuentas([_fila(cd_conta="1.02.04.05",
                              ds_conta="Provisão para Perdas Esperadas Associadas ao Risco de Crédito",
                              vl_conta="-46378851.0")])
    assert cvm.resolver(cuentas, spec, "saldo", "2026-06-30")["valor"] == pytest.approx(46_378_851_000.0)


def test_resolver_duplicada_en_cero_toma_la_no_nula():
    """BB llenó en el ITR 3T25 las cuentas del esqueleto nuevo con 0 además de las suyas."""
    spec = {"estado": "DRE", "alternativas": [
        {"suma": [{"cd": ["3.11.01", "3.09.01"], "ds": ["atribuido", "controladora"]}]}]}
    cuentas = _cuentas([
        _fila(estado="DRE", cd_conta="3.09.01", ds_conta="Atribuído a Sócios da Empresa Controladora",
              vl_conta="0.0"),
        _fila(estado="DRE", cd_conta="3.11.01", ds_conta="Atribuído aos Sócios da Empresa Controladora",
              vl_conta="8458188.0"),
    ])
    r = cvm.resolver(cuentas, spec, "saldo", "2025-09-30")
    assert r["valor"] == pytest.approx(8_458_188_000.0)


def test_resolver_ambiguedad_real_no_adivina():
    spec = {"estado": "BPP", "alternativas": [{"suma": [{"cd": ["2.03.01", "2.03.02"], "ds": ["depositos"]}]}]}
    cuentas = _cuentas([
        _fila(estado="BPP", cd_conta="2.03.01", ds_conta="Depósitos", vl_conta="100.0"),
        _fila(estado="BPP", cd_conta="2.03.02", ds_conta="Depósitos", vl_conta="200.0"),
    ])
    r = cvm.resolver(cuentas, spec, "saldo", "2026-06-30")
    assert r["valor"] is None
    assert "ambigua" in r["problema"]


def test_resolver_ds_no_excluye():
    """«Lucro ou Prejuízo antes das Participações» no es el lucro líquido del período."""
    spec = {"estado": "DRE", "alternativas": [
        {"suma": [{"cd": ["3.09", "3.11"], "ds": ["lucro", "periodo"],
                   "ds_no": ["antes das participacoes"]}]}]}
    cuentas = _cuentas([
        _fila(estado="DRE", cd_conta="3.09", ds_conta="Lucro ou Prejuízo antes das Participações e "
                                                      "Contribuições Estatutárias", vl_conta="500.0"),
        _fila(estado="DRE", cd_conta="3.11", ds_conta="Lucro ou Prejuízo Líquido Consolidado do Período",
              vl_conta="480.0"),
    ])
    assert cvm.resolver(cuentas, spec, "saldo", "2026-06-30")["valor"] == pytest.approx(480_000.0)


def test_resolver_atribucion_en_cero_cae_al_total_menos_no_controladores():
    """Caso real de Banestes: deja 3.11.01 en 0 en los ITR de 1T y 3T; vale el total menos los minoritarios."""
    spec = cvm.especificaciones("C0080147")["lucro_liquido_controlador"]     # Banestes usa la plantilla
    cuentas = _cuentas([
        _fila(estado="DRE", cd_conta="3.11", ds_conta="Lucro ou Prejuízo Líquido Consolidado do Período",
              vl_conta="111655.0"),
        _fila(estado="DRE", cd_conta="3.11.01", ds_conta="Atribuído aos Sócios da Empresa Controladora",
              vl_conta="0.0"),
        _fila(estado="DRE", cd_conta="3.11.02", ds_conta="Atribuído aos Sócios não Controladores",
              vl_conta="1072.0"),
    ])
    r = cvm.resolver(cuentas, spec, "saldo", "2025-03-31")
    assert r["alternativa"] == 2
    assert r["valor"] == pytest.approx((111_655.0 - 1_072.0) * 1000)


def test_santander_reconstruye_el_lucro_con_la_atribucion():
    """Santander entrega el impuesto en 0 y su 3.09 queda antes de impuestos: el total se reconstruye sumando
    la atribución a controladores y minoritarios. La regla está en la definición, no en el código."""
    spec = cvm.especificaciones("C0080185")["lucro_liquido"]
    cuentas = _cuentas([
        _fila(estado="DRE", cd_conta="3.09", ds_conta="Lucro/Prejuízo Consolidado do Período",
              vl_conta="8104038.0"),          # antes de impuestos: NO se usa
        _fila(estado="DRE", cd_conta="3.09.01", ds_conta="Atribuído a Sócios da Empresa Controladora",
              vl_conta="6111748.0"),
        _fila(estado="DRE", cd_conta="3.09.02", ds_conta="Atribuído a Sócios Não Controladores",
              vl_conta="132485.0"),
    ])
    r = cvm.resolver(cuentas, spec, "saldo", "2026-06-30")
    assert r["valor"] == pytest.approx((6_111_748.0 + 132_485.0) * 1000)
    assert r["cd_conta"] == "3.09.01 + 3.09.02"


# --- definición y mapa ---------------------------------------------------------------------------------- #

def test_definicion_de_lineas_cubre_las_minimas():
    defn = cvm.definicion_lineas()
    minimas = {"ativo_total", "credito_bruto", "provisao_perda", "depositos", "patrimonio_liquido",
               "resultado_intermediacion", "lucro_liquido_controlador"}
    assert minimas <= set(defn["lineas"])
    for nombre, linea in defn["lineas"].items():
        assert linea.get("definicion"), f"{nombre} sin definición"
        assert linea.get("unidad") in {"R$", "ratio"}


def test_todo_banco_que_entrega_tiene_lineas():
    mapa = cvm.mapa_bancos()
    defn = cvm.definicion_lineas()
    for _, b in mapa[mapa["entrega"]].iterrows():
        specs = cvm.especificaciones(b["cod_inst"], defn)
        assert specs, f"{b['nombre_corto']} sin líneas"
        assert "ativo_total" in specs, f"{b['nombre_corto']} sin ativo_total"
        assert specs["ativo_total"]["alternativas"], f"{b['nombre_corto']} sin reglas para ativo_total"


def test_mapa_cubre_el_universo_del_panel():
    import bancos as B
    mapa = cvm.mapa_bancos()
    assert set(mapa["cod_inst"]) == {b["cod_inst"] for b in B.universo()}
    assert mapa.loc[mapa["entrega"], "cnpj_raiz"].ne("").all()
    assert not mapa.loc[mapa["entrega"], "cnpj_raiz"].duplicated().any()


def test_especificaciones_rechaza_linea_desconocida():
    defn = cvm.definicion_lineas()
    defn["bancos"] = {"C0000000": {"nombre_corto": "Fantasma", "lineas": {"linea_inventada": {"alternativas": []}}}}
    with pytest.raises(ValueError, match="desconocida"):
        cvm.especificaciones("C0000000", defn)


# --- bk_publicado (integración) ------------------------------------------------------------------------- #

@pytest.mark.integracion
def test_bk_publicado_cumple_el_contrato():
    ruta = GOLD / "bk_publicado.parquet"
    if not ruta.exists():
        pytest.skip("falta bk_publicado.parquet")
    df = pd.read_parquet(ruta)
    A.validar_contrato("bk_publicado", df)          # columnas y clave única
    assert df["valor"].notna().all()
    assert set(df["medida"]) <= {"saldo", "trimestre", "acumulado"}
    assert set(df["documento"]) <= {"ITR", "DFP", "DFP−ITR"}
    assert set(df["consolidacion"]) <= {"con", "ind"}
    assert df.loc[df["linea"] != "roe_anualizado", "valor"].abs().gt(0).all()


@pytest.mark.integracion
def test_itau_2t26_verificado_contra_el_derivado():
    """El criterio de «terminado»: Itaú 2T26 coincide al R$ mil con su ITR.

    Los valores esperados son los del archivo crudo de la CVM (VL_CONTA en R$ mil, ×1000 aquí):
    ativo 3.202.125.000; crédito 1.082.266.000; provisión −49.896.000; depósitos 1.134.485.000;
    PL 228.026.000; resultado de intermediación 37.059.000 (trimestre) y 71.756.000 (acumulado);
    lucro atribuible 11.979.000 (trimestre) y 23.615.000 (acumulado).
    """
    ruta = GOLD / "bk_publicado.parquet"
    if not ruta.exists():
        pytest.skip("falta bk_publicado.parquet")
    df = pd.read_parquet(ruta)
    it = df[(df["cod_inst"] == "C0080099") & (df["periodo"] == "202606")]
    if it.empty:
        pytest.skip("Itaú no tiene 2T26 en bk_publicado")

    def valor(linea, medida=None):
        f = it[it["linea"] == linea]
        if medida:
            f = f[f["medida"] == medida]
        assert len(f) == 1, f"{linea}/{medida}: {len(f)} filas"
        return float(f["valor"].iloc[0])

    assert valor("ativo_total", "saldo") == pytest.approx(3_202_125_000 * 1000)
    assert valor("credito_bruto", "saldo") == pytest.approx(1_082_266_000 * 1000)
    assert valor("provisao_perda", "saldo") == pytest.approx(49_896_000 * 1000)
    assert valor("depositos", "saldo") == pytest.approx(1_134_485_000 * 1000)
    assert valor("patrimonio_liquido", "saldo") == pytest.approx(228_026_000 * 1000)
    assert valor("patrimonio_liquido_controlador", "saldo") == pytest.approx((228_026_000 - 10_247_000) * 1000)
    assert valor("resultado_intermediacion", "trimestre") == pytest.approx(37_059_000 * 1000)
    assert valor("resultado_intermediacion", "acumulado") == pytest.approx(71_756_000 * 1000)
    assert valor("lucro_liquido_controlador", "trimestre") == pytest.approx(11_979_000 * 1000)
    assert valor("lucro_liquido_controlador", "acumulado") == pytest.approx(23_615_000 * 1000)
    assert it.iloc[0]["documento"] in {"ITR", "DFP", "DFP−ITR"}
    assert it.iloc[0]["consolidacion"] == "con"
    assert it.iloc[0]["base"] == "CPC"
    assert str(it.iloc[0]["fecha_entrega"]).startswith("2026-")


@pytest.mark.integracion
def test_activo_total_suma_sus_partes_en_todas_las_entregas():
    """Aritmética del estado: 1 = Σ 1.0x. Si falla, se leyó otra versión o el crudo cambió."""
    import verificar_cvm as V
    r = V.Resultado()
    V.verificar_balance(pd.read_parquet(GOLD / "bk_publicado.parquet"), r)
    assert not r.errores, r.errores


@pytest.mark.integracion
def test_verificador_cvm_sin_errores():
    import verificar_cvm as V
    r = V.verificar(contraste=False)
    assert not r.errores, "\n".join(r.errores)


@pytest.mark.integracion
def test_roe_anualizado_usa_pl_promedio_del_trimestre():
    """ROE = lucro del trimestre × 4 / ((PL_t + PL_t−1) / 2), con el PL del controlador (convención de los releases)."""
    df = pd.read_parquet(GOLD / "bk_publicado.parquet")
    roe = df[df["linea"] == "roe_anualizado"]
    if roe.empty:
        pytest.skip("sin ROE en bk_publicado")
    import periodos as PER
    for _, f in roe.sample(min(5, len(roe)), random_state=0).iterrows():
        t = df[(df["cod_inst"] == f["cod_inst"]) & (df["periodo"] == f["periodo"])]
        anterior = df[(df["cod_inst"] == f["cod_inst"]) & (df["periodo"] == PER.previo(f["periodo"], 1))]
        lucro = t[(t["linea"] == "lucro_liquido_controlador") & (t["medida"] == "trimestre")]["valor"]
        pl_t = t[(t["linea"] == "patrimonio_liquido_controlador")]["valor"]
        pl_t4 = anterior[(anterior["linea"] == "patrimonio_liquido_controlador")]["valor"]
        assert len(lucro) == 1 and len(pl_t) == 1 and len(pl_t4) == 1
        esperado = float(lucro.iloc[0]) * 4 / ((float(pl_t.iloc[0]) + float(pl_t4.iloc[0])) / 2)
        assert float(f["valor"]) == pytest.approx(esperado, rel=1e-9)


@pytest.mark.integracion
def test_cuarto_trimestre_es_el_anual_menos_nueve_meses():
    """El 4T no lo publica nadie: se deriva restando el acumulado de setiembre del anual de la DFP."""
    df = pd.read_parquet(GOLD / "bk_publicado.parquet")
    q4 = df[(df["documento"] == "DFP−ITR") & (df["medida"] == "trimestre")
            & (df["linea"] != "roe_anualizado")]      # el ROE del 4T hereda el documento, pero es derivado
    if q4.empty:
        pytest.skip("sin 4T derivado")
    for _, f in q4.sample(min(6, len(q4)), random_state=0).iterrows():
        anual = df[(df["cod_inst"] == f["cod_inst"]) & (df["periodo"] == f["periodo"])
                   & (df["linea"] == f["linea"]) & (df["medida"] == "acumulado")
                   & (df["documento"] == "DFP")]
        nueve = df[(df["cod_inst"] == f["cod_inst"]) & (df["periodo"] == f"{f['periodo'][:4]}09")
                   & (df["linea"] == f["linea"]) & (df["medida"] == "acumulado")]
        assert len(anual) == 1 and len(nueve) == 1
        assert float(f["valor"]) == pytest.approx(float(anual["valor"].iloc[0]) - float(nueve["valor"].iloc[0]))
