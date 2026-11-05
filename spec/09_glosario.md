# 09 · Glosario

| Término | Significado |
|---|---|
| **BCB** | Banco Central do Brasil. |
| **IF.Data** | Base del BCB con información financiera trimestral por institución (balance, resultados, cartera, capital). API OLinda. |
| **Escopo** | Nivel de consolidación en IF.Data: 1 prudencial, 2 financiero, 3 individual, 4 cambio. El panel usa el prudencial. |
| **Conglomerado prudencial** | Grupo consolidado para supervisión (incluye instituciones de pago, securitizadoras, etc.). Unidad del panel; código `cod_inst`. |
| **Informe (relatório)** | Tabla de IF.Data: 2 activo, 3 pasivo, 4 resultados, 11 cartera PF por modalidad, 13 cartera PJ por modalidad. |
| **COSIF** | Plan de cuentas contable de las instituciones financieras; renumerado en 2025-03. |
| **Cadastro** | Registro de entidades de IF.Data (qué conglomerado contiene qué). |
| **SGS** | Sistema Gerenciador de Séries Temporais del BCB: series de sistema por código. |
| **SCR / SCR.data** | Sistema de Información de Créditos: cartera y mora agregadas por segmento, porte y UF. |
| **Libre / direccionado** | Crédito con tasas de mercado / crédito con recursos y tasas reguladas (BNDES, rural, inmobiliario con ahorro). |
| **PF / PJ** | Persona física (personas) / persona jurídica (empresas). |
| **Consignado** | Crédito personal con descuento por planilla (privado, público, INSS). |
| **Concesiones** | Flujo de crédito nuevo otorgado en el mes. |
| **Mora / NPL** | Cartera en atraso: panel IF.Data ≥ 15 días (NPL15); SGS > 90 días. |
| **Res. 4.966** | Norma contable vigente desde 2025 (pérdida esperada, activos problemáticos). |
| **Costo del riesgo** | Provisiones (TTM) sobre cartera promedio. |
| **Cobertura (ECL)** | Saldo de provisión de pérdida esperada sobre cartera vencida. |
| **NIM / margen de intermediación** | Resultado de intermediación financiera sobre activos (o cartera) promedio. |
| **ROE / ROA** | Lucro de 4 trimestres sobre patrimonio / activo promedio (t y t−4). |
| **TTM** | Últimos doce meses (cuatro trimestres). |
| **CDI** | Tasa interbancaria de referencia (SGS 4389); proxy de tasa libre de riesgo. |
| **Selic** | Tasa de política monetaria. |
| **Crédito/PIB, brecha** | Crédito sobre PIB (SGS 20622); brecha = desvío contra su tendencia HP unilateral (λ = 400.000). |
| **Óptica / grupo** | Forma de agrupar bancos: modelo de negocio, segmento regulatorio (S1–S4), propiedad, tradicional vs fintech, total panel. |
| **Panel** | Los 34 bancos del universo (`definiciones/bcb_ifdata__bancos_balances.json`). |
| **Gold** | Capa final de parquets `bk_*` que lee el sitio y Power BI. |
| **Lámina** | Una sección del sitio vista en modo Presentar (1920×1080). |
| **Tarjeta** | Un gráfico o tabla dentro de una sección; clave `Bp-nn` (ej. `B3-02`). |
| **Riel** | Columna o franja con número, nombre, pregunta y selectores de la sección. |
| **Franja** | Fila de indicadores con mini serie arriba de algunas páginas (B4, B6, B8). |
| **Canvas** | Tablero de diseño donde se dibuja una página antes de construirla, para aprobación de Pablo. |
