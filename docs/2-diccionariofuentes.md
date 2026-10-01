| # | Fuente | Dataset / recurso | Año / periodo | Granularidad | Variables principales | Frecuencia | Análisis posible | Link |
|---:|---|---|---|---|---|---|---|---|
| 1 | **UPRA** | Evaluaciones Agropecuarias Municipales (EVA) | 2019–2025 | Municipio × producto/actividad × periodo | Área, producción, rendimiento, cultivos, inventarios pecuarios | Semestral / anual | Crecimiento, participación, concentración, rendimiento, tendencias |  |
| 2 | **DANE** | SIPSA – Abastecimiento de alimentos | 2018–2025 | Fecha × origen × municipio × mercado × producto | Cantidad abastecida, origen, destino, producto, grupo | Periódica | Flujos de abastecimiento, concentración, estacionalidad, tendencias |  |
| 3 | **DANE** | SIPSA – Precios mayoristas | 2025–2026 | Fecha × mercado mayorista × producto | Precio, producto, mercado | Diaria / mensual | Tendencia, volatilidad, CV, estacionalidad, variación |  |
| 4 | **DANE** | Cuenta Satélite de la Agroindustria | 2022–2024 preliminar | Cadena × fase × año | Producción, consumo intermedio, VAB, variables económicas | Anual | Crecimiento, participación, productividad, valor agregado |  |
| 5 | **DANE** | Estadísticas de Exportaciones | 2025–2026 | Mes × producto/arancel × departamento × destino | FOB USD, kg, país destino, departamento, subpartida | Mensual | Crecimiento, concentración, diversificación, USD/kg |  |
| 6 | **DANE** | Microdatos de Exportaciones (EXPO) | 2025–2026 | Operación × producto × destino × origen × tiempo | Subpartida, país, departamento, kg, FOB, transporte | Mensual / registro | Panel producto-destino, concentración, crecimiento |  |
| 7 | **ICA** | Estimaciones poblacionales del sector pecuario | 2025–2026 | Municipio × departamento × especie × categoría × año | Bovinos, porcinos, bufalinos, ovinos, caprinos, etc. | Anual | Distribución territorial, crecimiento, concentración, especialización |  |
| 8 | **UPRA** | SIPRA – Sistema de Información para la Planificación Rural Agropecuaria | Actual | Territorio × cadena × capa geográfica | Aptitud, cadenas productivas, EVA, variables territoriales | Variable | Análisis espacial, aptitud, especialización territorial |  |
| 9 | **UPRA** | RECIA – Infraestructura agropecuaria | 2025–2026 | Infraestructura × ubicación | Tipo, ubicación, características y capacidad | Actualización progresiva | Cobertura, concentración, accesibilidad, brechas |  |
| 10 | **AgroNET** | Estadísticas pecuarias | 2025–2026 | Mes × departamento × producto | Precio de leche, volumen recolectado, producto | Mensual | Tendencias, volatilidad, relación precio-volumen |  |
| 11 | **AgroNET** | Índice de precios de insumos agropecuarios | 2025–2026 | Mes × producto/categoría × territorio | Índices y precios de insumos | Mensual | Inflación de insumos, presión de costos, correlaciones |  |



| Dimensión | Granularidad necesaria | Fuente |
|---|---|---|
| **Oferta agrícola** | Producto × municipio × tiempo | EVA |
| **Producción** | Producto × municipio × tiempo | EVA |
| **Rendimiento** | Producto × municipio × tiempo | EVA |
| **Oferta pecuaria** | Especie × municipio × tiempo | ICA |
| **Abastecimiento** | Producto × origen × mercado × tiempo | SIPSA Abastecimiento |
| **Precios** | Producto × mercado × tiempo | SIPSA Precios |
| **Estacionalidad** | Producto × territorio/mercado × tiempo | EVA + SIPSA |
| **Valor agregado** | Cadena × fase × año | Cuenta Satélite |
| **Exportaciones** | Producto × destino × origen × tiempo | DANE EXPO |
| **Mercados internacionales** | Producto × país × tiempo | DANE EXPO |
| **Infraestructura** | Infraestructura × territorio | RECIA |
| **Aptitud territorial** | Territorio × cadena × capa | SIPRA |
| **Costos productivos** | Producto × territorio × tiempo | AgroNET |
| **Demanda interna directa** | Producto × mercado/consumidor × tiempo | **Pendiente de fuente específica** |
| **Demanda internacional directa** | Producto × país comprador × tiempo | **Complementar EXPO con fuentes internacionales** |