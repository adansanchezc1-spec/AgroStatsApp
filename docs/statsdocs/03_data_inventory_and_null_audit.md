# Inspección Estadística — Parte III: Inventario de Fuentes Agroindustriales y Auditoría de Nulos
**Proyecto**: AgroData Intelligence Platform (`AgroStatsApp`)  
**Versión**: 2.1.0  
**Fecha**: 2026-10-07  
**Fase PDCO**: PLAN → DEVELOPMENT  
**Enfoque**: Mercadeo Agroindustrial, Inteligencia de Mercados y Minería de Datos  
**Alcance**: Exclusivamente Agrícola y Agroindustrial (Sin sector pecuario)  

---

## 1. Punto 7: Inventario Maestro de Fuentes y Enlaces Agroindustriales

A continuación se consolida el inventario exhaustivo de fuentes de información oficiales para el mercadeo agroindustrial, depurado de toda referencia pecuaria:

| # | Entidad Emisora | Recurso / Dataset | Periodo | Granularidad de Datos | Variables Clave | Frecuencia | Análisis de Mercadeo Posible | Enlace Oficial / Acceso |
|:---:|---|---|---|---|---|:---:|---|---|
| **1** | **UPRA** | Evaluaciones Agropecuarias Municipales (EVA Agrícola) | 2019–2025 | Municipio $\times$ Cultivo Agrícola $\times$ Periodo | Área sembrada, área cosechada, producción (t), rendimiento (t/ha) | Semestral / Anual | Identificación del núcleo de oferta agrícola, concentración municipal ($CR_5$, $HHI$), rendimientos y estabilidad física. | [Datos Abiertos - EVA Agrícola](https://www.datos.gov.co/Agricultura-y-Desarrollo-Rural/Evaluaciones-Agropecuarias-Municipales-EVA/2pn8-ywxr) |
| **2** | **DANE** | SIPSA – Abastecimiento de Alimentos | 2018–2025 | Fecha $\times$ Municipio Origen $\times$ Mercado Mayorista $\times$ Producto | Cantidad abastecida (kg), municipio procedencia, central mayorista destino, grupo de cultivo | Diaria continua | Minería de flujos origen-destino, identificación de despensas agrícolas de grandes ciudades, estacionalidad y cuotas de mercado. | [DANE - SIPSA Abastecimiento](https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa) |
| **3** | **DANE** | SIPSA – Precios Mayoristas de Mercado | 2019–2026 | Fecha $\times$ Plaza Mayorista $\times$ Producto Agrícola | Precio mínimo, precio máximo, cotización promedio, variación porcentual diaria | Diaria / Mensual | Volatilidad de precios, matrices de dispersión inter-mercados, ventanas de cotización pico y márgenes de arbitraje espacial. | [Datos Abiertos - SIPSA Precios Mayoristas](https://www.datos.gov.co/Agricultura-y-Desarrollo-Rural/Precios-Mayoristas-SIPSA/gwbi-fnzs) |
| **4** | **DANE** | Cuenta Satélite de la Agroindustria (CSAA) | 2022–2024 preliminar | Cadena Agroindustrial $\times$ Fase Económica $\times$ Año | Valor de producción, consumo intermedio, Valor Agregado Bruto (VAB) | Anual | Tamaño económico del sector, ratios de transformación agroindustrial y productividad del valor agregado por cultivo. | [DANE - Cuenta Satélite Agroindustria](https://www.dane.gov.co/index.php/estadisticas-por-tema/cuentas-nacionales/cuentas-satelite/cuenta-satelite-de-la-agroindustria) |
| **5** | **DANE / DIAN** | Estadísticas de Exportaciones Agroindustriales (EXPO) | 2019–2026 | Mes $\times$ Subpartida Arancelaria $\times$ Depto Origen $\times$ País Destino | Valor FOB (USD), masa neta (kg), país comprador, vía de transporte | Mensual | Análisis de inserción internacional, dinamismo de destinos, tasa CAGR de exportaciones y valor unitario FOB/kg. | [DANE - Comercio Exterior Exportaciones](https://www.dane.gov.co/index.php/estadisticas-por-tema/comercio-internacional/exportaciones) |
| **6** | **AgroNET** | Índice de Precios de Insumos Agrícolas | 2020–2026 | Mes $\times$ Categoría Insumo (Fertilizantes, Plaguicidas, Semillas) | Índice de precios, cotización promedio por presentación comercial | Mensual | Presión de costos de producción sobre el productor agrícola y elasticidad de transmisión hacia precios finales de mercado. | [AgroNET - Insumos Agropecuarios](https://www.agronet.gov.co/estadistica/Paginas/default.aspx) |
| **7** | **UPRA** | SIPRA – Aptitud de Tierras para CULTIVOS | Actual | Territorio $\times$ Cadena Agrícola $\times$ Capa Geográfica | Aptitud biofísica (Alta, Media, Baja), zonificación de cultivos comerciales | Continua | Especialización territorial, potencial de expansión de oferta y cruce con demanda de mercados mayoristas. | [UPRA - Geoportal SIPRA](https://sipra.upra.gov.co/) |
| **8** | **IDEAM** | Climatología y Pluviometría (Red Nacional) | 2020–2026 | Estación Meteorológica $\times$ Fecha | Precipitación diaria (mm), anomalías de lluvia, días con lluvia | Diaria / Mensual | Impacto de shocks climáticos sobre la estacionalidad de cosechas y predicción de caídas de abastecimiento en plazas. | [IDEAM - Catálogo de Datos Meteorológicos](http://dhime.ideam.gov.co/) |

---

## 2. Auditoría Empírica de Datos y Diagnóstico Celda por Celda de Nulos

Se llevó a cabo una verificación técnica directa sobre las tablas persistidas en la base de datos [`agrostats_lakehouse.db`](file:///c:/Users/ADAN/OneDrive/Documentos/App_agro/AgroStatsApp/data/processed/agrostats_lakehouse.db) (13.68 MB). Los resultados confirman plenamente que existen valores faltantes concentrados en tablas específicas:

```
Resultados de Completitud en Base de Datos:
--------------------------------------------------------------------------------
1. sipsa_abastecimientos:       59,500 filas | 11 cols | 0 nulos (100.0% completitud)
2. sipsa_precios:                   36 filas | 29 cols | 16 columnas con nulos (MAR)
3. sipsa_insumos:                   92 filas | 58 cols | 1 columna con 27.2% nulos (MNAR)
4. dane_ipc:                       284 filas |  7 cols | 2 columnas con nulos por frontera t-12
5. ideam_telemetria_realtime:    1,000 filas | 14 cols | 2 cadenas vacías en sensores (MCAR)
6. ideam_pluviometria:             100 filas | 13 cols | 0 nulos (100.0% completitud)
7. dane_csaa:                       22 filas |  3 cols | 0 nulos (100.0% completitud)
8. doc_webservice_chunks:           39 filas |  5 cols | 0 nulos (100.0% completitud)
9. dim_municipio_divipola:           8 filas |  5 cols | 0 nulos (100.0% completitud)
10. dim_producto_agro:               8 filas |  5 cols | 0 nulos (100.0% completitud)
11. mart_business_questions:         9 filas |  7 cols | 1 nulo (pregunta G3 denominador cero)
--------------------------------------------------------------------------------
```

---

### 2.1 Detalle Exhaustivo por Tabla y Columna Afectada

#### A. Tabla `sipsa_precios` (36 filas, 29 columnas)
La tabla estructura las cotizaciones en una matriz ancha donde cada columna representa una plaza mayorista. Se identificaron **16 columnas con valores nulos** correspondientes a ausencias de cotización:

| Columna Afectada | Nulos / Total | % Faltante | Tipo de Dato | Justificación del Fenómeno de Mercado |
|---|:---:|:---:|:---:|---|
| `pereira_la_41impala_var` | 10 / 36 | **27.78%** | `float64` | Ausencia de variación por falta de cotización previa en plaza La 41. |
| `pereira_la_41impala_precio` | 9 / 36 | **25.00%** | `float64` | El producto evaluado no fue transado en la plaza La 41 de Pereira. |
| `tunja_precio` | 8 / 36 | **22.22%** | `float64` | Sin reporte de cotización mayorista en la plaza de Tunja. |
| `tunja_var` | 8 / 36 | **22.22%** | `float64` | Variación no calculable en Tunja por ausencia de precio base. |
| `cucuta_cenabastos_precio` | 6 / 36 | **16.67%** | `float64` | Ausencia de reporte comercial en Cenabastos Cúcuta. |
| `cucuta_cenabastos_var` | 6 / 36 | **16.67%** | `float64` | Variación no calculable en Cenabastos Cúcuta. |
| `manizales_centro_galerias_precio` | 5 / 36 | **13.89%** | `float64` | Sin cotización en Centro Galerías Manizales. |
| `manizales_centro_galerias_var` | 5 / 36 | **13.89%** | `float64` | Sin variación calculable en Manizales. |
| `armenia_mercar_var` | 5 / 36 | **13.89%** | `float64` | Sin variación calculable en Mercar Armenia. |
| `armenia_mercar_precio` | 4 / 36 | **11.11%** | `float64` | Sin cotización registrada en Mercar Armenia. |
| `bucaramanga_centroabastos_precio` | 3 / 36 | **8.33%** | `float64` | Sin cotización en Centroabastos Bucaramanga. |
| `bucaramanga_centroabastos_var` | 3 / 36 | **8.33%** | `float64` | Sin variación en Bucaramanga. |
| `pereira_mercasa_precio` | 3 / 36 | **8.33%** | `float64` | Sin cotización en Mercasa Pereira. |
| `pereira_mercasa_var` | 3 / 36 | **8.33%** | `float64` | Sin variación en Mercasa Pereira. |
| `bogota_corabastos_precio` | 1 / 36 | **2.78%** | `float64` | Cotización puntual no reportada en Corabastos Bogotá. |
| `bogota_corabastos_var` | 1 / 36 | **2.78%** | `float64` | Sin variación en Bogotá. |

#### B. Tabla `sipsa_insumos` (92 filas, 58 columnas)
- Columna `total_otros`: **25 nulos sobre 92 filas (27.17%)**, tipo `float64`.
- **Causa**: Corresponde a insumos agrícolas marginales o no clasificados. Su ausencia es de naturaleza estructural (MNAR): el productor no incurrió en gastos clasificados bajo dicho rubro en los meses reportados como nulos.

#### C. Tabla `dane_ipc` (284 filas, 7 columnas)
- `variacion_mensual_pct`: **1 nulo (0.35%)** en $t_0$ (enero de 1999).
- `variacion_anual_pct`: **12 nulos (4.23%)** en las primeras 12 observaciones ($t_0 \dots t_{11}$).
- **Causa**: **Condición de frontera matemática intrínseca** de operadores en diferencias temporales ($\Delta_{12} X_t$). Para evaluar la variación respecto a hace 12 meses, se requiere obligatoriamente una historia previa de 12 observaciones que no existe en el inicio de la serie.

#### D. Tabla `ideam_telemetria_realtime` (1,000 filas, 14 columnas)
- `descripcionsensor`: **2 cadenas vacías `""` (0.20%)**.
- `unidadmedida`: **2 cadenas vacías `""` (0.20%)**.
- **Causa**: Truncamiento aleatorio de paquetes en la transmisión IoT de 2 estaciones meteorológicas (mecanismo MCAR).

#### E. Tabla `sipsa_abastecimientos` (59,500 filas, 11 columnas)
- **Cero nulos detectados (100.0% completitud)** en volumen abastecido (kg), fecha, departamento origen, municipio origen y central de abasto destino. Representa el núcleo analítico de mayor solidez estadística del sistema.
