# Portada mensual (frente 9) · barrido de códigos SGS

11-nov-2026. Nombres oficiales con `herramientas/validar_sgs.py` (`consultar`, servicio FachadaWSSGS). Rangos barridos:
20714–20830, 25351–25370, 21000–21081, 21130–21160 (250 códigos). 55 dan error 500 en el servicio (20775, 20781,
20788–20808, 20810–20824, 20827–20830, 25360–25370, 21000, 21158): por los vecinos son spreads y tasas por
modalidad o códigos no publicados; se reintentaron tres veces sin respuesta.

Segmentos: tot · pf · pj · li (libre) · di (dirigido) · pfli · pfdi · pjli · pjdi.

| Indicador | tot | pf | pj | li | pfli | pjli | di | pfdi | pjdi |
|---|---|---|---|---|---|---|---|---|---|
| Concesiones (A1, hecho) | 20631 | 20633 | 20632 | 20634 | 20662 | 20635 | resta | resta | resta |
| Tasa media, % a.a. | 20714 | 20716 | 20715 | 20717 | 20740 | 20718 | 20756 | 20768 | 20757 |
| ICC, % a.a. | 25351 | 25353 | 25352 | 25354 | 25356 | 25355 | 25357 | 25359 | 25358 |
| Spread, p.p. | 20783 | 20785 | 20784 | 20786 | 20809 | 20787 | 20825 | **no publicado** | 20826 |
| Mora > 90 días, % | 21082 | 21084 | 21083 | 21085 | 21112 | 21086 | 21132 | 21145 | 21133 |
| Atraso 15–90 días, % | 21003 | 21005 | 21004 | 21006 | 21033 | 21007 | 21053 | 21066 | 21054 |

Notas:
- **Spread dirigido de personas físicas:** no aparece. La familia del spread dirigido sigue el orden total (20825) y
  PJ (20826); el siguiente, 20827, da error 500 igual que 20828–20830. No se puede derivar sin los saldos y tasas de
  captación por segmento: no se estima.
- **Mora dirigida por cliente:** existe (21145 PF, 21133 PJ). Reemplaza la derivación por saldos del canvas; falta
  verificar que la derivación calce a < 0,03 pp.
- **Atraso por libre / dirigido y cruces:** existe completo (antes solo PF y PJ, con el total ponderado por saldo).
- **Concesiones dirigidas:** el SGS no las publica por separado (se mantienen como total − libres, A1).
