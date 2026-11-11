# -*- coding: utf-8 -*-
"""Cada serie de sgs.CODIGOS tiene su nombre oficial anotado (definiciones/bcb_sgs__catalogo.json), sin red.

El catálogo lo escribe herramientas/validar_sgs.py contra el servicio web del SGS. Estas pruebas evitan que vuelva
a entrar un código identificado solo porque «los montos cuadran» (spec/08 punto 5, cerrado el 9-nov-2026).
"""
from __future__ import annotations

import almacen as A
import sgs

CATALOGO = A.leer_definicion("bcb_sgs__catalogo")["series"]


def test_todo_codigo_tiene_nombre_oficial():
    faltan = sorted(set(sgs.CODIGOS) - set(CATALOGO))
    assert not faltan, f"códigos sin nombre oficial (correr herramientas/validar_sgs.py --escribir): {faltan}"
    distintos = {k: (v, CATALOGO[k]["codigo"]) for k, v in sgs.CODIGOS.items() if CATALOGO[k]["codigo"] != v}
    assert not distintos, distintos


def test_nombres_oficiales_coinciden_con_el_uso():
    """Las claves que el sitio rotula de una manera concreta dicen lo mismo que el SGS."""
    def nombre(k):
        return CATALOGO[k]["nombre"].lower()
    assert "não consignado" in nombre("mora90_personal")          # el comentario viejo decía «incluye consignado»
    assert "não consignado" in nombre("credito_pf_personal")
    assert nombre("concesiones_total").endswith("concessões de crédito - total")
    assert "pessoas físicas" in nombre("concesiones_pf") and "pessoas jurídicas" in nombre("concesiones_pj")
    assert "cartão de crédito total" in nombre("mora90_cartao_total")
    assert "cartão de crédito total" in nombre("credito_pf_tarjeta")
    for k in ("credito_pf_consignado_a", "credito_pf_consignado_b", "credito_pf_consignado_c"):
        assert "consignado para" in nombre(k)
    assert all(CATALOGO[k]["unidad"] == "%" for k in sgs.CODIGOS if k.startswith(("mora90_", "atraso15_90_")))
    assert all(CATALOGO[k]["unidad"] == "R$ (milhões)" for k in sgs.CODIGOS
               if k.startswith(("credito_", "conc")) and not k.startswith("credito_pib"))   # crédito/PIB va en %
