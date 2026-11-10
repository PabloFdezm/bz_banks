# Frente 9 · Portada mensual: completar los segmentos «en preparación» y llevar a gold lo del canvas

Estado al 10-nov-2026: **en curso**. A1 hecha el 9-nov (commit e8d4654: `bk_concesiones`, `bk_concesiones_tablas`);
falta el resto. Encargo pensado para que lo ejecute otra sesión u otra LLM sin contexto previo.
Leer antes `CLAUDE.md`, `spec/README.md`, `spec/08_estado_pendientes_y_riesgos.md` y `tareas/README.md`.
Reemplaza a la versión anterior de este frente (solo concesiones libres).

## Contexto y decisión de Pablo (9-nov)
- La **Portada** queda con tres secciones mensuales del SGS, aprobadas en el canvas
  https://claude.ai/artifact/Prgu2BygZtvCDWBTF52ag8:
  - 01 · Crédito: colocaciones y ciclo (láminas 06–08)
  - 02 · Precio del crédito (láminas 27–29)
  - 03 · NPL: mora y atraso temprano (láminas 09–11)
- Capital, ROE, NIM, Eficiencia y Depósitos (láminas 12–26) **no van en la Portada**: serán páginas propias (frente 5).
- Cada sección tiene un desplegable de segmentos: Personas / Empresas · Libre / Dirigido · Personas: libre / dirigido ·
  Todos (personas libre, personas dirigido, empresas libre, empresas dirigido). Hoy varias opciones muestran
  «en preparación» porque faltan series. Este frente las completa y deja en gold todas las cifras que el canvas
  calculó a mano (scripts en `tareas/borradores/_salida/*.json`, solo como referencia).

## Regla para identificar series (obligatoria)
No adivinar códigos ni identificarlos «porque los montos cuadran». Usar `herramientas/validar_sgs.py`
(`consultar(codigo)` devuelve el nombre oficial, la unidad y la periodicidad del SGS). Procedimiento:
1. Barrer los rangos candidatos indicados abajo con `consultar` y guardar la tabla código → nombre oficial en
   `tareas/borradores/portada_sgs_barrido.md`.
2. Elegir cada serie por su nombre oficial exacto. Si un corte no existe en el SGS, decirlo: esa opción sale del
   desplegable (no queda «en preparación» para siempre).
3. Agregar cada código a `CODIGOS` de `pipeline/sgs.py` y a `definiciones/bcb_sgs__catalogo.json`
   (`python -X utf8 herramientas/validar_sgs.py --escribir` y revisión a mano); si no, falla
   `tests/test_sgs_catalogo.py`.

## Parte A · Series que faltan
### A1 · Concesiones (sección 01) · hecha el 9-nov (commit e8d4654)
- Ya en el catálogo pero no en `CODIGOS` ni en el crudo: 20634 (libres total) y 20635 (libres personas jurídicas).
- Segmentos: tot = 20631; pf = 20633; pj = 20632; li = 20634; di = 20631 − 20634; pfli = 20662;
  pfdi = 20633 − 20662; pjli = 20635; pjdi = 20632 − 20635. Identidad: 20634 = 20635 + 20662 (diferencia < 1).
- Si el SGS publica las concesiones dirigidas por cliente, usarlas en lugar de la resta y comparar.

### A2 · Precio (sección 02)
- Hoy: tasa media de las operaciones, total (20714); spread de recursos libres, total (20786); ICC total (25351).
- Buscar, por nombre oficial: tasa media, spread e ICC por personas / empresas, por recursos libres / dirigidos y
  sus cruces. Rangos candidatos para el barrido: 20714–20830 y 25351–25370 (ampliar si hace falta).
- Ojo: el spread publicado es de recursos libres; si no hay spread dirigido, la opción Libre / Dirigido del par B
  muestra solo libre y se dice en los metadatos.

### A3 · NPL (sección 03)
- Mora > 90 días: ya están 21082–21086, 21112 y 21132. Personas dirigido y empresas dirigido hoy se despejan con los
  saldos: (mora del segmento × saldo − mora libre × saldo libre) / saldo dirigido. Buscar las series oficiales de
  mora dirigida por cliente (rango candidato 21130–21160); si existen, usarlas y verificar que la derivación calce
  a < 0,03 pp.
- Atraso de 15 a 90 días: hoy solo personas (21005) y empresas (21004); el Total se pondera por saldo. Buscar
  atraso total y por libre / dirigido (rango candidato 21000–21060). Lo que no exista sale del desplegable del par B.

### A4 · Actividad
- IBC-Br desestacionalizado (24364): está en el catálogo y en el crudo del dashboard macro, no en `CODIGOS`.

## Parte B · Gold
Una tabla nueva `bk_portada_m` (registrar en `definiciones/contrato_gold.json` y en el manifiesto), formato largo:
`seccion, par, serie, segmento, fecha, valor`, más una tabla de resumen `bk_portada_m_tablas` con
`seccion, par, bloque, fila, corte, ultimo, share, d1, d3, d12, dventana, z10, p25, p50, p75, minimo, maximo`.
Convenciones de cálculo (las mismas del canvas):
- m/m y a/a: punta contra punta; 3m/3m y 12m/12m: promedio de la ventana contra la anterior. Para tasas y
  porcentajes, en pp; para saldos y flujos, en %.
- Z 10 años: (último − promedio de los últimos 120 meses) / desvío muestral de esos 120 meses (40 trimestres en
  series trimestrales).
- Historia (box plot): percentiles 25, 50 y 75, mínimo y máximo desde ene-14 (desde mar-12 en los Δ a/a de mora y
  atraso).

Contenido por sección:
- **01 · Par A:** concesiones sumadas en 12 meses por segmento y su a/a; tabla con Último (R$ mil millones), Share
  del total, m/m, 3m/3m, a/a, 12m/12m.
- **01 · Par B · Impulso del crédito:** índice = concesiones reales de 12 meses (cada mes deflactado por IPCA, 433) /
  promedio de 12 meses del IBC-Br desestacionalizado (24364), promedio 2014 = 100; su a/a por segmento; Z de 120
  meses sobre el índice. Bloque inferior: crédito/PIB, tendencia HP y brecha desde 1T05 (ya están en
  `bk_cred_series`), con Δ a/a y Z de 40 trimestres (la tendencia sin Z).
- **02 · Par A:** tasa media por segmento y Selic meta a fin de mes (432); bloque: tasa media contra ICC y su
  diferencia en pp.
- **02 · Par B:** spread por segmento; bloque: spread de recursos libres contra mora > 90 días de la cartera libre
  (21085).
- **03 · Par A:** mora > 90 días por los nueve segmentos; bloque: Δ a/a de la mora (total, personas, empresas)
  desde mar-12 con marca de la Res. CMN 4.966 en ene-25 (la mora total sube 0,26 pp entre dic-24 y ene-25).
- **03 · Par B:** atraso de 15 a 90 días por segmento; bloque: Δ a/a del atraso (total, personas, empresas).

## Contraste (cifras del canvas; deben salir iguales al redondeo)
| Serie | Corte | Valor |
|---|---|---|
| Concesiones 12m total | sep-26 | 8.507,8 R$ mil millones, a/a +10,5 %, m/m +0,6 %, 3m/3m +3,0 %, 12m/12m +9,4 % |
| Concesiones 12m personas / empresas | sep-26 | 4.613,7 (+9,3 %) / 3.894,1 (+12,0 %) |
| Concesiones 12m personas libre / dirigido | sep-26 | 4.097,1 (+10,1 %) / 516,5 (+2,8 %) |
| Impulso (concesiones reales / IBC-Br), total | ago-26 | índice 121,3, a/a +4,57 % |
| Mora > 90 días total | sep-26 | 4,98 %, a/a +0,89 pp, Z +2,60 |
| Mora personas dirigido / empresas dirigido (derivada) | sep-26 | 3,41 % / 2,06 % |
| Δ a/a mora total | sep-26 | +0,89 pp; máximo +1,23 (feb-26); mínimo −1,12 (abr-21) |
| Atraso 15–90 personas / total ponderado | sep-26 | 6,45 % / 4,86 % |
| Tasa media total / Selic meta | sep-26 | 32,36 % (a/a +0,89 pp) / 13,75 % |
| ICC total / diferencia tasa − ICC | sep-26 | 24,28 % / 8,08 pp |
| Spread recursos libres | sep-26 | 35,52 pp, a/a +3,42 pp, Z +1,16 |

## Entregables y pasos
1. Barrido y tabla de códigos (`tareas/borradores/portada_sgs_barrido.md`); **detenerse y mostrar a Pablo** qué
   cortes existen y cuáles salen del desplegable.
2. `CODIGOS`, catálogo y descarga (`python -X utf8 pipeline/sgs.py` o el paso de `actualizar.bat`).
3. `pipeline/preparar_gold_bancos_portada_m.py` → `bk_portada_m`, `bk_portada_m_tablas`; paso nuevo en
   `pipeline/actualizar.py` y `actualizar.bat` (CRLF).
4. `tests/test_portada_m.py`: identidades de segmentos (concesiones, saldos, mora ponderada), convenciones de cambio
   y Z, y la tabla de contraste.
5. Informe corto en `tareas/borradores/portada_m_informe.md`.

## Fuera de alcance
- El sitio: construir la Portada en `sitio/` es parte del frente 5, después de este frente.
- Las páginas Capital, ROE, NIM, Eficiencia y Depósitos (frentes 5, 10 y 11).
- Reglas de `CLAUDE.md`: no inventar cifras, no borrar archivos ni hacer commit/push sin pedirlo; todo comando que
  se muestre a Pablo lleva `Set-Location C:\dev\bz_banks`.

## Terminado cuando
Cada opción del desplegable de las tres secciones tiene datos o salió con su razón; `bk_portada_m` y
`bk_portada_m_tablas` en gold con tests verdes; la tabla de contraste calza; fila 9 de `tareas/README.md`
actualizada con la fecha.

## Anexo B. Códigos SGS de Personas por producto (página «Crédito por producto»)

Encontrados en el catálogo del repo macro (`Dashboard/definiciones/bcb_sgs__series/*.json`). Validar cada uno con `herramientas/validar_sgs.py` antes de llevarlo a `sgs.py`. Ojo: el catálogo traduce mal 20666 («Total personal credit»): es el personal no consignado; el personal total es 20672.

| Producto | Saldo | Concesiones | Tasa | Mora > 90 |
|---|---|---|---|---|
| Tarjeta | 20590 (rotativo 20587, parcelado 20588, a la vista 20589) | 20682 (20679, 20680, 20681) | 22024 (rotativo 22022, parcelado 22023) | 21129 (21127, 21128) |
| Consignado | 20579 (privado 20576, público 20577, INSS 20578) | 20671 (20668, 20669, 20670) | 20747 (20744–20746) | 21119 (21116–21118) |
| Personal no consignado | 20574 (renegociación 20575) | 20666 (20667) | 20742 (20743) | 21114 (21115) |
| Vehículos | 20581 | 20673 | 20749 | 21121 |
| Inmobiliario | 20612 (mercado 20610, regulado 20611) | 20704 (20702, 20703) | 20774 (20772, 20773) | 21151 (21149, 21150) |
| Rural | 20609 (20607, 20608) | 20701 (20699, 20700) | 20771 (20769, 20770) | 21148 (21146, 21147) |
| Cheque especial | 20573 | 20665 | 20741 | 21113 |
| Total personas | 20541 | 20633 | 20716 | 21084 |

Otros: spread personas 20785; spreads 20783–20787, 20809, 20825, 20826; ICC 25351–25359 (personas 25353); atraso 15–90 días 21003–21010.

Faltan en el crudo hoy (bajar): 20579, 20680, 20681, 22023, 22024, 20744–20746, 20742, 20743, 20610, 20611, 20607, 20608, 20699, 20700, 20769, 20770, 21146, 21147, 20785. Mientras falten, la página los muestra «en preparación»; el consignado total se arma sumando 20576 + 20577 + 20578.
