# Frente 7 · Fuente CVM (ITR/DFP) → `bk_publicado`

Estado al 10-nov-2026: **construido** (commits 08d1c1e y 5970758, 9-nov; decisiones en `borradores/cvm_informe.md` §7).
Queda conectar la tarjeta B8-06-0 después del rediseño. Lo que sigue era el encargo original.
Pensado para que lo ejecute un worker (otra sesión u otra LLM) sin contexto previo.

## Por qué
La tarjeta B8-06-0 «Último trimestre publicado (CVM)» está «en preparación». El ITR sale semanas antes que el
IF.Data, así que da el último trimestre de los bancos cotizados en Brasil, con la base contable rotulada.

## Lo que ya se sabe (verificado el 8-nov)
- **Acceso:** `https://dados.cvm.gov.br` responde bien desde el `.venv` si se importa antes `pipeline/certificados.py`
  (el proxy corporativo cambia el certificado; `truststore` lo resuelve). No hace falta nada más en la red.
- **Archivos:**
  - ITR: `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_<año>.zip` (2026 pesa unos 22 MB).
  - DFP: `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_<año>.zip`.
  - Registro: `https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv`.
  - Formato de los CSV: `;` y latin1.
  - Dentro de cada ZIP: `itr_cia_aberta_{BPA,BPP,DRE,...}_{con,ind}_<año>.csv`. Se usa `con` (consolidado).
- **Bancos que filtró `SETOR_ATIV` contiene «Banc» y `SIT == 'ATIVO'` en el ITR 2026:**
  - Con sep-26: Itaú, Bradesco, Santander, BMG, Mercantil, BR Partners.
  - Hasta jun-26: BB, BTG, Banrisul, Banestes, Daycoval y Pine.
- **No aparecen:** Nubank, Inter, XP, Stone y PagSeguro, que reportan en EE.UU. con 20-F/6-K. Quedan **fuera de
  alcance** en la v1, con `bk_publicado` vacío para ellos. Pan, ABC y BRB tampoco salieron con ese filtro:
  revisarlos por CNPJ, porque quizá estén en otro `SETOR_ATIV`.
- **Trampas ya documentadas** (ver `definiciones/cvm__dfp_bancos.json`, campo `nota`):
  1. Cada cuenta viene dos veces por `ORDEM_EXERC` («ÚLTIMO» y «PENÚLTIMO»): hay que quedarse con «ÚLTIMO».
  2. Los valores vienen en R$ mil (`ESCALA_MOEDA = 'MIL'`).
  3. En el ITR, la DRE trae el trimestre y el acumulado del año: distinguirlos por `DT_INI_EXERC`.
  4. Cada documento puede tener varias versiones (`VERSAO`): usar la mayor.
- El extractor viejo (`extraer_fuentes.py cvm-dfp`) ya no existe y su filtro estaba mal (72 % de las filas no
  eran bancos). Se empieza de cero.

## Qué construir
1. **`pipeline/cvm.py`**: descarga y extracción, con el patrón de `pipeline/scr_zip.py` y `pipeline/almacen.py`.
   - El ZIP íntegro, sin tocar, va a `datos/crudo/cvm/itr/<año>/` (lo mismo para la DFP y el registro), vía
     `almacen.guardar_crudo` / `registrar_crudo` con su procedencia.
   - Se re-descarga si cambió: la CVM regenera el ZIP del año en curso casi todas las semanas.
   - Lo filtrado a bancos va a `datos/derivado/cvm/...` vía `almacen.guardar_derivado`.
2. **`definiciones/cvm__bancos.json`**: mapa CNPJ CVM → `cod_inst` del panel IF.Data. Usar el universo de
   `pipeline/bancos.py`; la raíz del CNPJ son los 8 primeros dígitos. Cada banco lleva su base contable (IFRS o BR
   GAAP) y una nota si no entrega ITR.
3. **`definiciones/cvm__bancos_lineas.json`**: mapeo de `CD_CONTA`/`DS_CONTA` por banco a las líneas mínimas:
   - activo total
   - cartera de crédito bruta
   - provisiones (PDD)
   - depósitos
   - patrimonio líquido
   - resultado bruto de intermediación
   - lucro líquido atribuible al controlador

   Es la parte laboriosa: los planes de cuentas difieren entre bancos. Cada línea se valida a mano contra un banco
   grande (Itaú 2T26) antes de generalizar. Si una línea no se puede mapear con certeza, se deja vacía con una nota:
   **no se inventa.**
4. **Tabla gold `bk_publicado`**, publicada con `almacen.publicar_gold` y declarada en `definiciones/contrato_gold.json`.
   - Columnas: `cod_inst`, `periodo` (formato de `pipeline/periodos.py`), `linea`, `valor` (en R$, ya multiplicado
     por mil), `base`, `fecha_entrega`, `cd_cvm`, `versao`.
   - ROE anualizado: lucro trimestral × 4 / PL promedio. Se calcula aquí o en la capa de métricas; seguir lo que haga
     el repo para el ROE de IF.Data.
5. **Integración:** un paso en `pipeline/actualizar.py` (mirar cómo están los otros) y un verificador.
   - Para cada banco y trimestre presente en los dos universos, comparar el activo total y el PL CVM contra
     IF.Data. Informar la diferencia en %, sin corregir nada. La diferencia es esperable (conglomerado prudencial vs.
     consolidado contable), pero no puede pasar de ~15 % sin explicación.
   - Revisar si `bk_puente` (lo produce `pipeline/preparar_gold_bancos.py`) puede consumir `bk_publicado`.
6. **Tests** en `tests/test_cvm.py`, con un fixture pequeño y sin red:
   - el filtro `ORDEM_EXERC`/`VERSAO`;
   - la escala ×1000;
   - trimestre vs. acumulado en la DRE;
   - que ningún CNPJ fuera del mapa entra a `bk_publicado`.
7. **Documentación:**
   - actualizar `definiciones/cvm__dfp_bancos.json`, o reemplazarlo por uno del ITR y dejar el viejo marcado como
     obsoleto;
   - correr `python -X utf8 herramientas/generar_spec.py`;
   - anotar en `spec/08_estado_pendientes_y_riesgos.md` las trampas nuevas que aparezcan.

## Fuera de alcance
- Páginas web, tarjetas o CSS: otra sesión está con el diseño. La tarjeta B8-06-0 se conecta después.
- SEC (20-F/6-K) para Nubank, Inter, XP, Stone y PagSeguro.
- Commit, push, publicar o borrar archivos: lo decide Pablo.

## Criterio de «terminado»
- `actualizar.bat` (o el paso nuevo por sí solo) baja ITR 2025–2026 y DFP 2023–2025 y genera `bk_publicado` sin
  errores. `python -m pytest -q` pasa entero.
- Tabla de control con los 12+ bancos × los últimos 4 trimestres × 7 líneas, con huecos explicados. Contraste
  CVM vs. IF.Data del activo y el PL para el 2T26.
- Itaú 2T26, verificado a mano contra su ITR: activo total, PL y lucro coinciden al R$ mil.
- Un informe corto en `tareas/borradores/cvm_informe.md`:
  - qué se hizo;
  - qué bancos y líneas quedaron vacíos y por qué;
  - las diferencias contra IF.Data;
  - decisiones que quedan para Pablo.
