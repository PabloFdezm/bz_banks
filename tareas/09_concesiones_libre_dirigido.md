> Reemplazado el 9-nov por `09_portada_mensual_segmentos.md` (se puede borrar con el visto bueno de Pablo).

# 9 · Concesiones libre / dirigido (sección 01 de la Portada)

Estado: pendiente (Pablo, 9-nov-2026). Canvas: https://claude.ai/artifact/Prgu2BygZtvCDWBTF52ag8, láminas 06–08.
Resumen de decisiones de la sección: proyecto claude.ai, `claude/58_seccion01_colocaciones_2026-11-09.md`.

## Qué falta
La sección 01 («Crédito: colocaciones y ciclo») usa concesiones. Hoy se arman Personas/Empresas (20633/20632),
el Total (20631) y personas libre/dirigido (20662 y 20633 − 20662). Faltan, y el canvas las muestra «en preparación»:
- Libre / Dirigido total: libre = SGS 20634; dirigido = 20631 − 20634.
- Empresas libre = SGS 20635; empresas dirigido = 20632 − 20635.
- Con eso queda el 2×2 (opción «Todos» del desplegable).

## Pasos
1. Agregar a `CODIGOS` de `pipeline/sgs.py`: `"concesiones_libre": 20634, "concesiones_pj_libre": 20635`
   (y su entrada en `definiciones/bcb_sgs__catalogo.json`, o falla `tests/test_sgs_catalogo.py`).
2. Correr la descarga y cuadrar: 20634 = 20635 + 20662 (ya validado contra la API el 8-nov).
3. Construir en gold, por segmento (tot, pf, pj, li, di, pfli, pfdi, pjli, pjdi):
   - concesiones 12m (suma móvil) y su a/a; tabla con Último · Share · m/m · 3m/3m · a/a · 12m/12m;
   - índice concesiones reales 12m (IPCA 433) / IBC-Br desestacionalizado promedio 12m (24364), promedio 2014 = 100,
     su a/a y su Z de 120 meses.
   El IBC-Br 24364 también hay que sumarlo a `CODIGOS` (hoy está solo en el crudo `actividad_mensual`).
4. Reemplazar los «—» del canvas por las cifras y quitar la marca «en preparación».

## Terminado cuando
Las cuatro opciones del desplegable muestran datos, las identidades cuadran (diferencia < 1 en R$ millones) y el
Total de la sección calza con «Concesiones totales» de `bk_cred_tablas`.

## Ampliación (9-nov): tasas y spreads por segmento para la sección 02 «Precio del crédito»
La sección 02 del canvas usa solo totales: tasa media de las operaciones (20714), spread de recursos libres (20786)
e ICC (25351). Personas, empresas, libre, dirigido y sus cruces quedan «en preparación». Agregar a `CODIGOS` de
`pipeline/sgs.py` (y al catálogo) las series del SGS de tasa media, spread e ICC por personas y empresas y por recursos
libres y dirigidos. Los códigos exactos hay que tomarlos del catálogo oficial del SGS con `herramientas/validar_sgs.py`;
no adivinarlos. Mismo criterio de «terminado»: cada opción del desplegable con datos y el Total igual a la serie total.
