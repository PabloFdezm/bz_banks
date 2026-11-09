# Capital (IF.Data informe 5) → `bk_capital` — informe del 9-nov-2026

Frente 8 (`tareas/08_fuente_capital.md`). Construido hasta la capa gold, sin tocar el sitio: la página B7 sigue
«en preparación» y se conecta después del rediseño.

**Resumen.** `bk_capital` tiene 1.390 filas: los 34 bancos del panel de 2015-03 a 2026-06. `bk_capital_grupo` tiene
806 filas, con los índices calculados como Σ capital / Σ RWA. En 2T26 los cinco grandes calzan con su KM1 o su nota
de capital dentro de 0,1 pp en CP, Nivel I y Basilea, y el capital principal en R$ coincide al millón. Desde 2023-03
el requerimiento de CP de cada banco lo publica el propio BCB en el informe, como «Adicional de Capital Principal» en
R$. Para 2015–2016 sale de las normas. Para 2017–2022 queda vacío: el colchón sistémico de cada banco en esos años
no está verificado.

## 1. Qué se hizo

| Capa | Qué hay | Dónde |
|---|---|---|
| Crudo | Informe 5, escopo prudencial, de 2014-03 a 2026-06. Lo bajó la sesión worker la madrugada del 9-nov con `ifdata.py colectar`; 2014 viene vacío | `datos/crudo/bcb_ifdata/valores/actual/valores_<AAAAMM>_1_r5.parquet` |
| Definiciones | Mapeo por nombre sin la letra de la época, con la `Conta` esperada para auditar | `definiciones/bcb_ifdata__capital.json` |
| | Mínimos y ACP por vigencia, cada fila con su norma y su URL | `definiciones/minimos_regulatorios.json` |
| | 10 métricas de la familia `capital` (con `"tabla": "bk_capital"`) | `definiciones/metricas_bancos.json` |
| Gold | `bk_capital` (banco × trimestre) y `bk_capital_grupo` (óptica × grupo × trimestre), en el contrato | `datos/gold/`, `definiciones/contrato_gold.json` |
| Huecos | 248 casos banco × trimestre del panel sin capital, cada uno con su motivo | `datos/derivado/bcb_ifdata/capital/huecos_capital.csv` |
| Código | `pipeline/capital.py`, paso `capital` en `actualizar.py` (después de `cvm`; usa `bk_panel`) | |
| Tests | 20 pruebas: unitarias sin red más integración sobre `datos/`, incluido el contraste 2T26 | `tests/test_capital.py` |

Cómo se corre:

```powershell
Set-Location C:\dev\bz_banks
# colecta trimestral a mano (cuando el BCB publique 3T26):
.venv\Scripts\python.exe -X utf8 pipeline\ifdata.py colectar --escopo prudencial --informe 5 --periodo 202609
.venv\Scripts\python.exe -X utf8 pipeline\capital.py --resumen   # cobertura y avisos, sin publicar
.venv\Scripts\python.exe -X utf8 pipeline\capital.py             # publica bk_capital y bk_capital_grupo
```

## 2. Desde cuándo hay datos

- **Bancos tradicionales:** desde 2015-03. El panel de 2014 (99 casos) es `INFORME_5_VACIO`.
- **Instituciones de pago y digitales** (Nubank, Stone, PagSeguro, Mercado Pago, Neon, CloudWalk): sin capital
  principal hasta 2023-06. Cielo informa solo Basilea y RWA. XP le falta en 2015-09 a 2016-09; a BRB, en 4 trimestres
  desde 2022-09; a Original, en 2026-06. En total son 149 casos `SIN_CAPITAL_PRINCIPAL_O_RWA`, todos en
  `huecos_capital.csv`.
- **Requerimiento de CP:**
  - desde el ACP del BCB: 451 filas (2023-03 en adelante);
  - desde las normas: 200 filas (2015–2016);
  - vacío: 739 filas (2017–2022, y las filas sin CP).

## 3. Mapeo por época

Las Conta son estables salvo una: el RWA de crédito pasa de 79650 a 138232 en 2023-03. Lo que cambia son las letras:

| Época | RWA total | Exposición | Mercado | Columnas que aparecen |
|---|---|---|---|---|
| 2015-03 – 2022-12 | (i) = f+g+h | (j) | g1–g4 | — |
| 2023-03 – 2023-06 | (j) = f+g+h+i | (k) | g1–g4 | RWAsp (i), ACP. Índice CP **sin salto de línea** |
| 2023-09 – 2024-09 | (j) | (k) | g1–g5 (CVA) | |
| 2024-12 en adelante | (j) | (k) | g1–g6 (DRC) | IRRBB |

## 4. Contraste 2T26 (tolerancia 0,1 pp)

| Banco | CP bk / publ. | Nivel I bk / publ. | Basilea bk / publ. | CP R$ mm bk / publ. | Fuente |
|---|---|---|---|---|---|
| Itaú | 12,31 / 12,3 | 13,97 / 14,0 | 15,35 / 15,4 | 194.742 / 194.742 | KM1, Pilar 3 2T26 p. 3 (https://api.mziq.com/mzfilemanager/v2/d/42787847-4cf6-4461-94a5-40ed237dca33/c89a30a1-418e-ec1a-acdf-a08040a1fd6e?origin=2) |
| Banco do Brasil | 11,27 / 11,27 | 13,27 / 13,27 | 13,91 / 13,91 | 154.715 / 154.715 | KM1 v2, datos abiertos BB (https://api.externo.bb.com.br/dadosabertos/v1/relatorios/km1/v2/2026-2) |
| Bradesco | 11,28 / 11,3 | 12,85 / 12,8 | 15,56 / 15,5 | 134.658 / 134.658 | Nota de capital de las DF y release 2T26 p. 23 (https://api.mziq.com/mzfilemanager/v2/d/80f2e993-0a30-421a-9470-a4d5c8ad5e9f/b7c34f8d-92f6-7ba4-f408-d518a7211a7a?origin=2) |
| Santander | 11,17 / 11,17 | 12,22 / 12,22 | 15,34 / 15,34 | 86.475 / 86.475 | Nota de capital, DF BRGAAP 2T26 (6-K: https://www.sec.gov/Archives/edgar/data/1471055/000162828026059844/a6k-2t26.htm) |
| BTG Pactual | 11,59 / 11,59 | 12,60 / 12,60 | 16,04 / 16,04 | 74.276 / 74.276 | KM1 v2, datos abiertos BTG (https://ri.btgpactual.com/api/dadosabertos/pillar3/km1/v2/2026-2) |

- Los RWA difieren menos de 0,02 %.
- Las diferencias en el segundo decimal son redondeos: Itaú y Bradesco publican con un decimal.
- El pro forma de Bradesco (aumento de capital y Bradsaúde) no es regulatorio y no se compara.

**Agregado.** El REF de oct-26 (Gráfico 1.2.4.1) da 14,2 % de ICP y 17,0 % de Basilea para el sistema a jun-26.
Sumando los 440 conglomerados prudenciales del informe 5 da 13,9 % y 16,8 %. La diferencia de 0,3 pp es de universo:
el REF no define qué consolida y calcula con el DLO. El panel da **12,9 %**, con el 85 % del RWA del sistema: los
grandes bancos están algo más ajustados que el resto.

## 5. Fuentes de los mínimos

Todo está en `definiciones/minimos_regulatorios.json`, cada fila con su norma y su URL:

- CP 4,5 % y Nivel I 6 % en todo el período.
- PR: 11 % en 2015, 9,875 % en 2016, 9,25 % en 2017, 8,625 % en 2018 y 8 % desde 2019 (Res. 4.193 art. 4; desde el
  3-ene-2022, Res. 4.958).
- Conservación:
  - 0 % en 2015, 0,625 % en 2016, 1,25 % en 2017, 1,875 % en 2018 y 2,5 % desde 2019 (Res. 4.443);
  - durante el COVID: 1,25 % del 1-abr-2020 al 31-mar-2021, 1,625 % hasta el 30-sep-2021 y 2,0 % hasta el
    31-mar-2022 (Res. 4.783). Vuelve a 2,5 % desde abr-2022 (Res. 4.958).
- Contracíclico brasileño: 0 % siempre (Circ. 3.769 art. 3; Comef, Ata 65 de may-2026). El de exposiciones en el
  exterior es propio de cada banco (Itaú 0,1 %, BTG 0,036 %) y antes de 2023 no se conoce.
- Sistémico (Circ. 3.768): no existía antes de 2017. Desde 2019 es 1 % o 2 % según la exposición total sobre el PIB.
  En 2T26 lo tienen al 1 % Itaú, BB, Bradesco y Santander; BTG tiene 0 %.

## 6. Decisiones que quedan para Pablo

1. **Requerimiento 2017–2022.** Falta el ACP sistémico por banco en esos años. Hay tres opciones:
   - (a) dejarlo vacío, como está ahora;
   - (b) cargar a mano el FIS de los grandes desde sus Pilar 3 históricos, que es lo correcto pero lleva trabajo;
   - (c) publicarlo «sin sistémico» como cota inferior, rotulado.
   Recomiendo (b) solo para los cinco grandes y (a) para el resto, porque los medianos casi seguro tenían 0 %, pero
   eso no está verificado.
2. **Dividendos en el puente del CP (B7-02-0).** El informe 5 no los separa. Hoy `bk_capital` publica `var_cp_4t`,
   `lucro_ttm` y `otros_var_cp_4t` como residuo. El residuo mezcla dividendos y JCP, ajustes prudenciales, OCI y
   emisiones. Separar los dividendos exigiría la DRE o la DMPL de la CVM (`bk_publicado`), y solo para 15 bancos.
3. **`holgura_crecimiento`.** Lo implementé como «cuánto pueden crecer los RWA con el CP de hoy» (CP / req − 1). Si
   se mantiene la densidad, equivale a crecer el activo. La tarea decía «en % de la cartera actual»; expresarlo
   sobre la cartera de crédito exige suponer la densidad del crédito, que no se publica.
4. **Trimestres repetidos** (Agibank 2015-06 a 2016-06; PagSeguro 4T25 = 2T25). Hoy se publican con la columna
   `alerta`. Alternativa: vaciarlos.
5. **Pagos y digitales antes de 2023.** Quedan sin dato, de modo que en los gráficos de grupo «Pagos» y «Digitales»
   arrancan en 2023-09 y el `n_bancos` del panel salta de 26 a 31. El diseño de B7 tendría que mostrarlo.
6. **Fuera de este frente:** B7-03-1 (estrés, del REF) y conectar la página B7.
