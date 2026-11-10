# 10 · Capital mensual (sección 04 de la Portada)

Estado: cerrado el 9-nov-2026 (Pablo): la opción B se descarta (no pasa 0,3 pp) y la A pasa al frente 11
(`11_fuente_balancetes.md`). Canvas: https://claude.ai/artifact/Prgu2BygZtvCDWBTF52ag8, láminas 12–14.

## Problema
El capital regulatorio (CET1, Nivel I, Basilea, RWA, requerimiento) solo existe trimestral: IF.Data informe 5
(`bk_capital`, `bk_capital_grupo`) y el Pilar 3 de cada banco. La sección 04 queda con corte 2T26 mientras el resto
de la Portada corta en sep-26. Se busca una señal mensual que acompañe a la holgura trimestral, sin presentarla como
capital regulatorio.

## Opciones
### A. Balancetes mensuales de los conglomerados (BCB, documento 4060)
> La fuente se construye en el frente 11 (`tareas/11_fuente_balancetes.md`).
- Qué dan: patrimonio, activo total, cartera de crédito y resultado del mes, por conglomerado prudencial.
- Métricas posibles: patrimonio / activo (apalancamiento contable); crecimiento a/a del patrimonio contra el de la
  cartera (generación contra consumo, versión mensual); utilidad acumulada del trimestre en curso.
- Límites: sin RWA ni ajustes prudenciales; el nivel no es comparable con el CET1.
- Costo: fuente nueva (`pipeline/balancetes.py`), descarga mensual desde la PC de Pablo; mapear las cuentas COSIF
  por época (Res. 4.966 cambia el plan de cuentas desde ene-25). Sirve también para rentabilidad mensual por banco.

### B. Estimación mensual de la holgura (nowcast)
- holgura_est(t) = CP(q) / [RWA(q) × saldo_crédito(t) / saldo_crédito(q)] − requerimiento(q), con q = último
  trimestre publicado y saldo_crédito del SGS (20539, o por segmento).
- Se puede armar hoy, sin datos nuevos.
- Supone densidad de RWA constante dentro del trimestre y no suma la utilidad del mes (subestima la holgura). Con A,
  se le suma la utilidad acumulada de los balancetes.
- Siempre rotulado «estimación», línea punteada, nunca en la tabla de datos publicados.

## Validación (antes de publicar cualquiera)
- Backtest de B: estimar cada trimestre desde el anterior y comparar con el dato publicado; error medio y máximo
  en pp. Si el error típico supera 0,3 pp, no se publica.
- Para A: el patrimonio de fin de trimestre debe calzar con el de IF.Data (informe 1) del mismo conglomerado.

## Recomendación
La página sigue trimestral (16 trimestres por defecto). Si la validación de B pasa, va solo en el Agrandar B como
línea punteada junto a la holgura trimestral. A queda como fuente nueva a evaluar junto con la página de rentabilidad.

## Terminado cuando
Pablo elige A, B o ninguna; si B, el backtest está en `tareas/borradores/` y la línea aparece rotulada en el canvas.
