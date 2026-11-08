# -*- coding: utf-8 -*-
"""Tests del verificador de la capa gold (tablas bk_*, encargo 59).

Cada comprobación tiene su prueba «rota a propósito»: un DataFrame pequeño con el
error que la comprobación debe detectar. Las comprobaciones generales (contrato,
claves, fechas, licencias) se prueban por la entrada pública: tablas escritas en
una carpeta temporal y `verificar_gold(gold=...)`.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import verificar_gold as V

HOY = pd.Timestamp("2026-11-02")
MODELOS = ["Grandes", "Digitales", "Medianos y nicho", "Pagos", "Desarrollo"]
C = V.COLUMNAS_GOLD


def _df(columnas: list[str], filas: list[dict]) -> pd.DataFrame:
    """DataFrame con todas las columnas del contrato; lo que no se pasa queda nulo."""
    return pd.DataFrame([{c: f.get(c, np.nan) for c in columnas} for f in filas], columns=columnas)


def _banco(n: int = V.N_BANCOS_GOLD) -> pd.DataFrame:
    filas = [{
        "cod_inst": f"C{i:04d}", "slug": f"banco{i}", "nombre_corto": f"Banco {i}",
        "modelo": MODELOS[i % len(MODELOS)], "segmento_reg": "S1", "propiedad": "2",
        "fintech": "Tradicional", "primer_periodo": "201403", "ultimo_periodo": "202606",
    } for i in range(n)]
    return _df(C["bk_banco"], filas)


def _panel_base(filas: list[dict]) -> pd.DataFrame:
    return _df(C["bk_panel"], filas)


def _gold(tmp_path: Path, nombre: str, df: pd.DataFrame) -> V.Resultado:
    """Escribe una tabla gold en una carpeta temporal y corre el verificador completo sobre ella."""
    df.to_parquet(tmp_path / f"{nombre}.parquet")
    return V.verificar_gold(gold=tmp_path, hoy=HOY)


def test_general_detecta_columna_faltante(tmp_path):
    r = _gold(tmp_path, "bk_banco", _banco().drop(columns=["slug"]))
    assert any("faltan columnas" in e for e in r.errores), r.errores


def test_general_detecta_filas_repetidas(tmp_path):
    panel = _panel_base([{"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.1}])
    panel = pd.concat([panel, panel.iloc[[0]]], ignore_index=True)
    r = _gold(tmp_path, "bk_panel", panel)
    assert any("repetidas" in e for e in r.errores), r.errores


def test_general_detecta_infinito(tmp_path):
    panel = _panel_base([{"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": np.inf}])
    r = _gold(tmp_path, "bk_panel", panel)
    assert any("infinitos" in e for e in r.errores), r.errores


def test_general_detecta_fecha_posterior_a_hoy(tmp_path):
    panel = _panel_base([{"cod_inst": "C0000", "periodo": "202606", "fecha": pd.Timestamp("2026-12-31"),
                          "metrica": "roe_ttm", "valor": 0.1}])
    r = _gold(tmp_path, "bk_panel", panel)
    assert any("posteriores a hoy" in e for e in r.errores), r.errores


def test_general_detecta_periodo_posterior_a_hoy(tmp_path):
    banco = _banco()
    banco.loc[0, "ultimo_periodo"] = "202612"  # 4T26 todavía no cerró al 2-nov-2026
    r = _gold(tmp_path, "bk_banco", banco)
    assert any("posterior a hoy" in e for e in r.errores), r.errores


def test_general_detecta_columna_con_licencia(tmp_path):
    panel = _panel_base([{"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.1}])
    panel["px_last"] = 1.0
    r = _gold(tmp_path, "bk_panel", panel)
    assert any("licencia" in e for e in r.errores), r.errores


def test_general_limpia_no_marca_tablas_validas(tmp_path):
    r = _gold(tmp_path, "bk_banco", _banco())
    assert not r.errores, r.errores


def test_banco_valido_pasa():
    assert not V.verificar_gold_banco(_banco()).errores


def test_banco_detecta_filas_de_menos():
    r = V.verificar_gold_banco(_banco(33))
    assert any("33 filas" in e for e in r.errores), r.errores


def test_banco_detecta_modelo_fuera_de_lista():
    banco = _banco()
    banco.loc[0, "modelo"] = "Otros"
    r = V.verificar_gold_banco(banco)
    assert any("modelo fuera" in e for e in r.errores), r.errores


def test_banco_detecta_slug_repetido():
    banco = _banco()
    banco.loc[1, "slug"] = banco.loc[0, "slug"]
    r = V.verificar_gold_banco(banco)
    assert any("slug repetido" in e for e in r.errores), r.errores


def test_metrica_detecta_signo_fuera_de_lista():
    met = _df(C["bk_metrica"], [{"metrica": "roe_ttm", "unidad": "ratio", "signo": "neutral"}])
    r = V.verificar_gold_metrica(met)
    assert any("signo fuera" in e for e in r.errores), r.errores


def test_metrica_detecta_metrica_del_panel_sin_fila():
    met = _df(C["bk_metrica"], [{"metrica": "roe_ttm", "unidad": "ratio", "signo": "mejora_sube"}])
    panel = _panel_base([{"cod_inst": "C0000", "periodo": "202606", "metrica": "roa_ttm", "valor": 0.01}])
    r = V.verificar_gold_metrica(met, panel)
    assert any("sin fila" in e and "roa_ttm" in e for e in r.errores), r.errores


def test_panel_detecta_pct_fuera_de_0_1():
    panel = _panel_base([{"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm",
                          "valor": 0.1, "pct_grupo": 1.2, "pct_panel": 0.5}])
    r = V.verificar_gold_panel(panel, _banco())
    assert any("fuera de [0, 1]" in e for e in r.errores), r.errores


def test_panel_detecta_percentiles_con_menos_de_tres_bancos():
    # C0000 y C0005 son ambos «Grandes»: dos bancos con dato, menos de 3.
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.1, "p50_grupo": 0.1},
        {"cod_inst": "C0005", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.2, "p50_grupo": 0.2},
    ])
    r = V.verificar_gold_panel(panel, _banco())
    assert any("menos de 3 bancos" in e for e in r.errores), r.errores


def test_panel_percentiles_nulos_con_dos_bancos_pasan():
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.1},
        {"cod_inst": "C0005", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.2},
    ])
    assert not V.verificar_gold_panel(panel, _banco()).errores


def test_panel_valor_t4_coincide_pasa():
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202506", "metrica": "roe_ttm", "valor": 0.10},
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.12, "valor_t4": 0.10},
    ])
    r = V.verificar_gold_panel(panel, None)
    assert not any("valor_t4" in e for e in r.errores), r.errores


def test_panel_detecta_valor_t4_que_no_coincide():
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202506", "metrica": "roe_ttm", "valor": 0.10},
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.12, "valor_t4": 0.99},
    ])
    r = V.verificar_gold_panel(panel, None)
    assert any("valor_t4 no coincide" in e for e in r.errores), r.errores


def _metrica_grupo() -> pd.DataFrame:
    return _df(C["bk_metrica"], [
        {"metrica": "ativo_total", "unidad": "brl", "signo": "neutro"},
        {"metrica": "roe_ttm", "unidad": "ratio", "signo": "mejora_sube"},
    ])


def _panel_grupo() -> pd.DataFrame:
    return _panel_base([
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "ativo_total", "valor": 100.0},
        {"cod_inst": "C0001", "periodo": "202606", "metrica": "ativo_total", "valor": 100.0},
        {"cod_inst": "C0002", "periodo": "202606", "metrica": "ativo_total", "valor": 100.0},
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.10},
        {"cod_inst": "C0001", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.20},
        {"cod_inst": "C0002", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.30},
    ])


def _grupo_filas(total_ativo=300.0, grandes_ativo=100.0, total_roe=0.2) -> list[dict]:
    f = []
    for optica, grupo in [("Modelo de negocio", "Grandes"), ("Modelo de negocio", "Digitales"),
                          ("Modelo de negocio", "Medianos y nicho")]:
        valor_ativo = grandes_ativo if grupo == "Grandes" else 100.0
        roe = {"Grandes": 0.10, "Digitales": 0.20, "Medianos y nicho": 0.30}[grupo]
        f += [{"optica": optica, "grupo": grupo, "periodo": "202606", "metrica": "ativo_total", "valor": valor_ativo},
              {"optica": optica, "grupo": grupo, "periodo": "202606", "metrica": "roe_ttm", "valor": roe}]
    f += [{"optica": "Propiedad", "grupo": "Privado nacional", "periodo": "202606", "metrica": "ativo_total", "valor": 300.0},
          {"optica": "Propiedad", "grupo": "Privado nacional", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.2},
          {"optica": "Segmento regulatorio", "grupo": "S1", "periodo": "202606", "metrica": "ativo_total", "valor": 300.0},
          {"optica": "Segmento regulatorio", "grupo": "S1", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.2},
          {"optica": "Tradicional vs Fintech", "grupo": "Tradicionales", "periodo": "202606", "metrica": "ativo_total", "valor": 300.0},
          {"optica": "Tradicional vs Fintech", "grupo": "Tradicionales", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.2},
          {"optica": V.TOTAL_PANEL, "grupo": "Todos los grupos", "periodo": "202606", "metrica": "ativo_total", "valor": total_ativo},
          {"optica": V.TOTAL_PANEL, "grupo": "Todos los grupos", "periodo": "202606", "metrica": "roe_ttm", "valor": total_roe}]
    return f


def _grupo(**kw) -> pd.DataFrame:
    return _df(C["bk_grupo"], _grupo_filas(**kw))


def test_grupo_valido_pasa():
    r = V.verificar_gold_grupo(_grupo(), _panel_grupo(), _banco().head(3).assign(
        modelo=MODELOS[:3]), _metrica_grupo())
    assert not r.errores, r.errores


def test_grupo_detecta_total_distinto_de_la_suma_de_bancos():
    r = V.verificar_gold_grupo(_grupo(total_ativo=310.0), _panel_grupo(), _banco(), _metrica_grupo())
    assert any("no es igual a la suma de los bancos" in e for e in r.errores), r.errores


def test_grupo_detecta_optica_que_no_suma_el_total():
    r = V.verificar_gold_grupo(_grupo(grandes_ativo=90.0), _panel_grupo(), _banco(), _metrica_grupo())
    assert any("«Modelo de negocio» no suman" in e for e in r.errores), r.errores


def test_grupo_detecta_ratio_fuera_del_rango_de_sus_bancos():
    r = V.verificar_gold_grupo(_grupo(total_roe=0.5), _panel_grupo(), _banco(), _metrica_grupo())
    assert any("fuera del rango" in e for e in r.errores), r.errores


def test_grupo_sin_total_panel_es_error():
    filas = [f for f in _grupo_filas() if f["optica"] != V.TOTAL_PANEL]
    r = V.verificar_gold_grupo(_df(C["bk_grupo"], filas), _panel_grupo(), _banco(), _metrica_grupo())
    assert any("no hay filas de la óptica" in e for e in r.errores), r.errores


LINEAS_ROE = [0.02, -0.01, 0.005, np.nan, -0.008, -0.003, -0.001, 0.0015, -0.002]  # suma 0,0025


def _roe(roa=0.0025, roe=0.025, apal=10.0) -> pd.DataFrame:
    filas = [{"entidad": "C0000", "periodo": "202606", "linea": f"l{i + 1}", "orden": i + 1, "valor": v}
             for i, v in enumerate(LINEAS_ROE)]
    filas += [
        {"entidad": "C0000", "periodo": "202606", "linea": "roa", "orden": 10, "valor": roa},
        {"entidad": "C0000", "periodo": "202606", "linea": "apalancamiento", "orden": 11, "valor": apal},
        {"entidad": "C0000", "periodo": "202606", "linea": "roe", "orden": 12, "valor": roe},
    ]
    return _df(C["bk_roe_arbol"], filas)


def test_roe_arbol_valido_pasa():
    assert not V.verificar_gold_roe_arbol(_roe()).errores


def test_roe_arbol_detecta_suma_de_lineas_distinta_del_roa():
    r = V.verificar_gold_roe_arbol(_roe(roa=0.003))
    assert any("Σ líneas 1–9" in e for e in r.errores), r.errores


def test_roe_arbol_detecta_identidad_roe_rota():
    r = V.verificar_gold_roe_arbol(_roe(roe=0.03))
    assert any("apalancamiento no es igual al ROE" in e for e in r.errores), r.errores


def _cartera(periodo="202606", npl=0.05) -> pd.DataFrame:
    return _df(C["bk_cartera"], [
        {"cod_inst": "C0000", "periodo": periodo, "tipo": "PF", "modalidad": "Cartão", "saldo": 600e6, "vencido15": 30e6, "npl15": npl},
        {"cod_inst": "C0000", "periodo": periodo, "tipo": "PF", "modalidad": "Pessoal", "saldo": 400e6, "vencido15": 10e6, "npl15": npl},
    ])


def _totales_publicados(publicado=1000e6) -> pd.DataFrame:
    return _df(["cod_inst", "periodo", "tipo", "publicado", "exterior"], [
        {"cod_inst": "C0000", "periodo": "202606", "tipo": "PF", "publicado": publicado, "exterior": 0.0}])


def test_cartera_valida_pasa():
    assert not V.verificar_gold_cartera(_cartera(), _totales_publicados()).errores


def test_cartera_detecta_suma_que_no_cuadra_con_el_total():
    r = V.verificar_gold_cartera(_cartera(), _totales_publicados(publicado=1100e6))
    assert any("no cuadra con el total publicado" in e for e in r.errores), r.errores


def test_cartera_detecta_2024_t4_con_filas():
    r = V.verificar_gold_cartera(_cartera(periodo="202412"), None)
    assert any("2024-T4" in e for e in r.errores), r.errores


def test_cartera_detecta_npl_fuera_de_0_1():
    r = V.verificar_gold_cartera(_cartera(npl=1.5), None)
    assert any("npl15 fuera de [0, 1]" in e for e in r.errores), r.errores


def test_cartera_sin_totales_es_aviso_no_error():
    r = V.verificar_gold_cartera(_cartera(), None)
    assert not r.errores
    assert any("no hay totales publicados" in a for a in r.advertencias), r.advertencias


def _serie(serie, valores, unidad="fraccion", fin="2026-09-30") -> list[dict]:
    fechas = pd.date_range(end=fin, periods=len(valores), freq="QE")
    return [{"fecha": f, "serie_id": serie, "unidad": unidad, "valor": v} for f, v in zip(fechas, valores)]


def _sistema(filas: list[dict]) -> pd.DataFrame:
    return _df(C["bk_sistema_q"], filas)


VALS30 = [0.01 + 0.001 * i for i in range(30)]


def test_sistema_valido_pasa_con_excepcion_selic():
    sist = _sistema(_serie("ok", VALS30) + _serie("selic_real_exante", VALS30[:23]))
    r = V.verificar_gold_sistema(sist, "bk_sistema_q", HOY, V.EXCEPCIONES_OBS["bk_sistema_q"])
    assert not r.errores, r.errores


def test_sistema_detecta_serie_corta():
    r = V.verificar_gold_sistema(_sistema(_serie("corta", VALS30[:10])), "bk_sistema_q", HOY)
    assert any("corta tiene 10 observaciones" in e for e in r.errores), r.errores


def test_sistema_excepcion_no_perdona_bajar_del_minimo_documentado():
    sist = _sistema(_serie("selic_real_exante", VALS30[:22]))
    r = V.verificar_gold_sistema(sist, "bk_sistema_q", HOY, V.EXCEPCIONES_OBS["bk_sistema_q"])
    assert any("selic_real_exante tiene 22 observaciones" in e for e in r.errores), r.errores


def test_sistema_detecta_serie_constante():
    r = V.verificar_gold_sistema(_sistema(_serie("plana", [0.05] * 30)), "bk_sistema_q", HOY)
    assert any("plana es constante" in e for e in r.errores), r.errores


def test_sistema_detecta_fraccion_mayor_que_uno():
    vals = VALS30[:]
    vals[5] = 1.5
    r = V.verificar_gold_sistema(_sistema(_serie("grande", vals)), "bk_sistema_q", HOY)
    assert any("|valor| > 1" in e for e in r.errores), r.errores


def test_sistema_detecta_ultimo_dato_futuro():
    r = V.verificar_gold_sistema(_sistema(_serie("futura", VALS30, fin="2027-03-31")), "bk_sistema_q", HOY)
    assert any("posterior a hoy" in e for e in r.errores), r.errores


def test_sistema_unidad_pp_no_se_acota_a_uno():
    sist = _sistema(_serie("impulso_pp", [1.0 + 0.5 * i for i in range(30)], unidad="pp"))
    r = V.verificar_gold_sistema(sist, "bk_sistema_q", HOY)
    assert not r.errores, r.errores


def _scr(tasas: dict[str, float]) -> pd.DataFrame:
    filas = []
    for seg, t in tasas.items():
        for cliente, activa in (("PF", 600.0), ("PJ", 400.0)):
            filas.append({"corte": "segmento_cliente", "fecha": pd.Timestamp("2026-06-30"), "segmento_inst": seg,
                          "cliente": cliente,
                          "carteira_ativa": activa, "inadimplencia_brl": activa * t, "tasa_inad": t})
    return _df(C["bk_scr"], filas)


def test_scr_valida_pasa():
    assert not V.verificar_gold_scr(_scr(dict(V.TASA_JUN26))).errores


def test_scr_detecta_tasa_distinta_de_la_publicada():
    tasas = dict(V.TASA_JUN26)
    tasas["Banco"] = 0.05
    r = V.verificar_gold_scr(_scr(tasas))
    assert any("tasa de Banco" in e for e in r.errores), r.errores


def test_scr_detecta_segmento_sin_corte():
    tasas = {k: v for k, v in V.TASA_JUN26.items() if k != "Fintech"}
    r = V.verificar_gold_scr(_scr(tasas))
    assert any("no hay corte de Fintech" in e for e in r.errores), r.errores


def _manifiesto(tmp_path: Path, sha_ok=True, incluir=True, corte="2026-09-30"):
    ruta = tmp_path / "bk_banco.parquet"
    pd.DataFrame({"cod_inst": ["C0000"]}).to_parquet(ruta)
    sha = hashlib.sha256(ruta.read_bytes()).hexdigest() if sha_ok else "0" * 64
    filas = []
    if incluir:
        filas.append({"tabla": "bk_banco", "filas": 1, "columnas": 1, "rango": "", "sha256": sha,
                      "producido_por": "test"})
    filas.append({"universo": "Panel", "ultimo_corte": corte})
    return _df(C["bk_manifiesto"], filas), {"bk_banco": ruta}


def test_manifiesto_valido_pasa(tmp_path):
    man, presentes = _manifiesto(tmp_path)
    assert not V.verificar_gold_manifiesto(man, presentes, HOY).errores


def test_manifiesto_detecta_sha_que_no_coincide(tmp_path):
    man, presentes = _manifiesto(tmp_path, sha_ok=False)
    r = V.verificar_gold_manifiesto(man, presentes, HOY)
    assert any("sha256 de bk_banco no coincide" in e for e in r.errores), r.errores


def test_manifiesto_detecta_tabla_sin_fila(tmp_path):
    man, presentes = _manifiesto(tmp_path, incluir=False)
    r = V.verificar_gold_manifiesto(man, presentes, HOY)
    assert any("bk_banco no tiene fila" in e for e in r.errores), r.errores


def test_manifiesto_acepta_corte_aaaamm_y_avisa_sin_corte(tmp_path):
    man, presentes = _manifiesto(tmp_path, corte="202606")
    assert not V.verificar_gold_manifiesto(man, presentes, HOY).errores
    extra = _df(C["bk_manifiesto"], [{"universo": "SCR", "ultimo_corte": None}])
    r = V.verificar_gold_manifiesto(pd.concat([man, extra], ignore_index=True), presentes, HOY)
    assert not r.errores, r.errores
    assert any("sin último corte" in a for a in r.advertencias), r.advertencias


def test_manifiesto_detecta_corte_ilegible(tmp_path):
    man, presentes = _manifiesto(tmp_path, corte="no es fecha")
    r = V.verificar_gold_manifiesto(man, presentes, HOY)
    assert any("no se puede leer" in e for e in r.errores), r.errores


def test_manifiesto_detecta_universo_con_corte_futuro(tmp_path):
    man, presentes = _manifiesto(tmp_path, corte="2027-01-31")
    r = V.verificar_gold_manifiesto(man, presentes, HOY)
    assert any("posterior a hoy" in e for e in r.errores), r.errores


def test_grupo_cuotas_son_aditivas_y_no_se_comparan_con_rango():
    met = _df(C["bk_metrica"], [{"metrica": "share_ativo", "unidad": "ratio", "signo": "neutro"}])
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "share_ativo", "valor": 0.6},
        {"cod_inst": "C0001", "periodo": "202606", "metrica": "share_ativo", "valor": 0.4},
    ])
    grupo = _df(C["bk_grupo"], [
        {"optica": V.TOTAL_PANEL, "grupo": "Todos los grupos", "periodo": "202606", "metrica": "share_ativo", "valor": 1.0},
        {"optica": "Modelo de negocio", "grupo": "Todos los grupos", "periodo": "202606", "metrica": "share_ativo", "valor": 1.0},
        {"optica": "Modelo de negocio", "grupo": "Grandes", "periodo": "202606", "metrica": "share_ativo", "valor": 0.6},
        {"optica": "Modelo de negocio", "grupo": "Digitales", "periodo": "202606", "metrica": "share_ativo", "valor": 0.4},
    ])
    r = V.verificar_gold_grupo(grupo, panel, _banco(), met)
    assert not r.errores, r.errores


def test_grupo_detecta_cuota_de_grupo_que_no_suma():
    met = _df(C["bk_metrica"], [{"metrica": "share_ativo", "unidad": "ratio", "signo": "neutro"}])
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "share_ativo", "valor": 0.6},
        {"cod_inst": "C0001", "periodo": "202606", "metrica": "share_ativo", "valor": 0.4},
    ])
    grupo = _df(C["bk_grupo"], [
        {"optica": V.TOTAL_PANEL, "grupo": "Todos los grupos", "periodo": "202606", "metrica": "share_ativo", "valor": 1.0},
        {"optica": "Modelo de negocio", "grupo": "Todos los grupos", "periodo": "202606", "metrica": "share_ativo", "valor": 1.0},
        {"optica": "Modelo de negocio", "grupo": "Grandes", "periodo": "202606", "metrica": "share_ativo", "valor": 0.5},
        {"optica": "Modelo de negocio", "grupo": "Digitales", "periodo": "202606", "metrica": "share_ativo", "valor": 0.4},
    ])
    r = V.verificar_gold_grupo(grupo, panel, _banco(), met)
    assert any("«Modelo de negocio» no suman" in e for e in r.errores), r.errores


def test_grupo_detecta_cuotas_de_optica_que_no_suman_uno():
    # Total y bancos suman 0,9: la partición contra el total cuadra, pero la cuota no suma 1.
    met = _df(C["bk_metrica"], [{"metrica": "share_ativo", "unidad": "ratio", "signo": "neutro"}])
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "share_ativo", "valor": 0.6},
        {"cod_inst": "C0001", "periodo": "202606", "metrica": "share_ativo", "valor": 0.3},
    ])
    grupo = _df(C["bk_grupo"], [
        {"optica": V.TOTAL_PANEL, "grupo": "Todos los grupos", "periodo": "202606", "metrica": "share_ativo", "valor": 0.9},
        {"optica": "Modelo de negocio", "grupo": "Todos los grupos", "periodo": "202606", "metrica": "share_ativo", "valor": 0.9},
        {"optica": "Modelo de negocio", "grupo": "Grandes", "periodo": "202606", "metrica": "share_ativo", "valor": 0.6},
        {"optica": "Modelo de negocio", "grupo": "Digitales", "periodo": "202606", "metrica": "share_ativo", "valor": 0.3},
    ])
    r = V.verificar_gold_grupo(grupo, panel, _banco(), met)
    assert any("cuotas de los grupos de «Modelo de negocio» no suman 1" in e for e in r.errores), r.errores


def test_grupo_hhi_y_top5_no_se_comparan_con_rango():
    met = _df(C["bk_metrica"], [{"metrica": "hhi_credito", "unidad": "indice", "signo": "neutro"}])
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "roe_ttm", "valor": 0.1},
    ])
    grupo = _df(C["bk_grupo"], [
        {"optica": V.TOTAL_PANEL, "grupo": "Todos los grupos", "periodo": "202606", "metrica": "hhi_credito", "valor": 900.0},
    ])
    r = V.verificar_gold_grupo(grupo, panel, _banco(), met)
    assert not any("fuera del rango" in e for e in r.errores), r.errores


def test_grupo_lucro_aa_queda_fuera_del_rango_con_aviso():
    met = _df(C["bk_metrica"], [{"metrica": "lucro_ttm_aa", "unidad": "ratio", "signo": "mejora_sube"}])
    panel = _panel_base([
        {"cod_inst": "C0000", "periodo": "202606", "metrica": "lucro_ttm_aa", "valor": -5.0},
        {"cod_inst": "C0001", "periodo": "202606", "metrica": "lucro_ttm_aa", "valor": 2.0},
    ])
    grupo = _df(C["bk_grupo"], [
        {"optica": V.TOTAL_PANEL, "grupo": "Todos los grupos", "periodo": "202606", "metrica": "lucro_ttm_aa", "valor": 10.0},
    ])
    r = V.verificar_gold_grupo(grupo, panel, _banco(), met)
    assert not any("fuera del rango" in e for e in r.errores), r.errores
    assert any("lucro_ttm_aa" in a for a in r.advertencias), r.advertencias


def test_gold_sin_tablas_solo_avisos(tmp_path):
    r = V.verificar_gold(gold=tmp_path, hoy=HOY)
    assert not r.errores
    assert r.advertencias
    assert r.resumen["gold_tablas"] == []


def test_gold_detecta_banco_de_33_filas_desde_disco(tmp_path):
    _banco(33).to_parquet(tmp_path / "bk_banco.parquet")
    r = V.verificar_gold(gold=tmp_path, hoy=HOY)
    assert any("33 filas" in e for e in r.errores), r.errores


@pytest.mark.integracion
def test_gold_reales_sin_errores():
    r = V.verificar_gold()
    assert not r.errores, "\n".join(r.errores)


def _exposicion(**kw) -> pd.DataFrame:
    fila = {"cod_inst": "C0000", "periodo": "202606", "fecha": pd.Timestamp("2026-06-30"),
            "trimestre": "2T26", "cobertura": 0.8, "mora_implicita": 0.04, "npl_observado": 0.05,
            "brecha_pp": 1.0, "efecto_mix_pp": 0.2, "efecto_mora_pp": 0.3,
            "d_mora_implicita_aa_pp": 0.5, "quiebre_2025": False}
    fila.update(kw)
    return _df(C["bk_exposicion"], [fila])


def test_exposicion_valida_pasa():
    assert not V.verificar_gold_exposicion(_exposicion()).errores
    # Σ de pesos normalizados puede quedar en 1 + 2e-16 (valor real de bk_exposicion)
    assert not V.verificar_gold_exposicion(_exposicion(cobertura=1.0000000000000002)).errores
    # con cobertura < 0,5 todo lo que depende de la mora implícita queda nulo: eso es válido
    vacia = _exposicion(cobertura=0.3, mora_implicita=np.nan, brecha_pp=np.nan, efecto_mix_pp=np.nan,
                        efecto_mora_pp=np.nan, d_mora_implicita_aa_pp=np.nan)
    assert not V.verificar_gold_exposicion(vacia).errores


def test_exposicion_detecta_cobertura_fuera_de_rango():
    r = V.verificar_gold_exposicion(_exposicion(cobertura=1.2))
    assert any("cobertura fuera de [0, 1]" in e for e in r.errores), r.errores


def test_exposicion_detecta_mora_con_cobertura_baja():
    r = V.verificar_gold_exposicion(_exposicion(cobertura=0.3))
    assert any("cobertura < 0,5" in e for e in r.errores), r.errores


def test_exposicion_detecta_efectos_que_no_suman_la_delta():
    r = V.verificar_gold_exposicion(_exposicion(d_mora_implicita_aa_pp=0.6))
    assert any("≠ d_mora_implicita_aa_pp" in e for e in r.errores), r.errores


def test_exposicion_detecta_efecto_con_nulo_parcial():
    r = V.verificar_gold_exposicion(_exposicion(efecto_mora_pp=np.nan))
    assert any("≠ d_mora_implicita_aa_pp" in e for e in r.errores), r.errores


def _sensibilidad(**kw) -> pd.DataFrame:
    fila = {"cod_inst": "C0000", "modelo": "Grandes", "beta_nim_cdi": 0.5, "ic_inf": 0.1,
            "ic_sup": 0.9, "r2": 0.3, "n_trimestres": 30, "excluidos": "202412"}
    fila.update(kw)
    return _df(C["bk_sensibilidad"], [fila])


def test_sensibilidad_valida_pasa():
    assert not V.verificar_gold_sensibilidad(_sensibilidad()).errores
    # con n = 16 la beta se publica; con n = 10 todo queda nulo, y eso es válido
    assert not V.verificar_gold_sensibilidad(_sensibilidad(n_trimestres=16)).errores
    nula = _sensibilidad(n_trimestres=10, beta_nim_cdi=np.nan, ic_inf=np.nan, ic_sup=np.nan, r2=np.nan)
    assert not V.verificar_gold_sensibilidad(nula).errores


def test_sensibilidad_detecta_beta_con_pocos_trimestres():
    r = V.verificar_gold_sensibilidad(_sensibilidad(n_trimestres=10))
    assert any("menos de 16 trimestres" in e for e in r.errores), r.errores


def test_sensibilidad_detecta_beta_fuera_del_intervalo():
    r = V.verificar_gold_sensibilidad(_sensibilidad(ic_inf=0.6))
    assert any("ic_inf ≤ beta ≤ ic_sup" in e for e in r.errores), r.errores


def test_sensibilidad_detecta_r2_fuera_de_rango():
    r = V.verificar_gold_sensibilidad(_sensibilidad(r2=1.2))
    assert any("R² fuera de [0, 1]" in e for e in r.errores), r.errores


def _cartera_totales(**kw) -> pd.DataFrame:
    fila = {"cod_inst": "C0000", "periodo": "202606", "tipo": "PF", "publicado": 100.0,
            "exterior": 10.0, "brasil": 90.0}
    fila.update(kw)
    return _df(C["bk_cartera_totales"], [fila])


def test_totales_valida_pasa():
    assert not V.verificar_gold_cartera_totales(_cartera_totales()).errores
    # exterior nulo cuenta como cero: brasil = publicado
    assert not V.verificar_gold_cartera_totales(_cartera_totales(exterior=np.nan, brasil=100.0)).errores


def test_totales_detecta_brasil_que_no_es_publicado_menos_exterior():
    r = V.verificar_gold_cartera_totales(_cartera_totales(brasil=95.0))
    assert any("brasil ≠ publicado − exterior" in e for e in r.errores), r.errores
