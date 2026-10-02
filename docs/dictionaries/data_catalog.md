# Catálogo de Datos y Diccionario de Metadatos (DAMA-DMBOK 2)
**Plataforma**: AgroStats Intelligence Platform | **Fecha**: 2026-10-01 20:02:21
**Entidades Gobernadas**: 12 tablas y marts

---
## 1. Inventario General de Entidades Lakehouse

| Tabla / Entidad | Capa | Dominio | Granularidad | Registros | Frecuencia |
|---|:---:|---|---|---:|:---:|
| `sipsa_abastecimientos` | **SILVER** | Abastecimiento Agroalimentario | Año x Mes x Municipio Origen (DIVIPOLA) x Central Destino | 59,500 | Periódica / Eventos |
| `sipsa_precios` | **SILVER** | Precios Mayoristas | Fecha x Mercado Mayorista x Producto | 36 | Periódica / Eventos |
| `sipsa_insumos` | **SILVER** | Costos e Insumos | Mes x Insumo Químico | 92 | Periódica / Eventos |
| `dane_ipc` | **SILVER** | Macroeconomía Agraria | Año x Mes (Longitudinal) | 284 | Periódica / Eventos |
| `ideam_pluviometria` | **SILVER** | Hidrometeorología Agrícola | Fecha x Estación x Código DIVIPOLA | 100 | Periódica / Eventos |
| `ideam_telemetria_realtime` | **SILVER** | Telemetría en Tiempo Real | Timestamp x Código Sensor x DIVIPOLA | 1,000 | Periódica / Eventos |
| `dane_csaa` | **SILVER** | Cuentas Nacionales | Código Cuadro x Cadena Agropecuaria | 22 | Periódica / Eventos |
| `doc_webservice_chunks` | **SILVER** | Documentación No Estructurada | Documento x Chunk ID | 39 | Periódica / Eventos |
| `landing_leads` | **SILVER** | Customer & Commercial Analytics | ID Lead x Timestamp Registro | 1 | Periódica / Eventos |
| `dim_municipio_divipola` | **GOLD** | Analytics & Reporting | Agregada / Dimensional | 8 | Batch / Demanda |
| `dim_producto_agro` | **GOLD** | Analytics & Reporting | Agregada / Dimensional | 8 | Batch / Demanda |
| `mart_business_questions` | **GOLD** | Analytics & Reporting | Agregada / Dimensional | 9 | Batch / Demanda |

---
## 2. Diccionario de Datos por Entidad

### Entidad: `sipsa_abastecimientos`
- **Capa Medallion**: SILVER
- **Descripción**: Serie multi-anual consolidada (2025-2019) de flujos de carga origen-destino (DANE SIPSA).
- **Granularidad**: `Año x Mes x Municipio Origen (DIVIPOLA) x Central Destino`
- **Clave Primaria**: `anio, fecha, codigo_divipola_origen, producto`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `anio` | `int64` | Numeric | No | `PUBLIC` | `2025` |
| `periodo` | `str` | DateTime | No | `PUBLIC` | `Cuatrimestre III` |
| `fecha` | `datetime64[us]` | DateTime | No | `PUBLIC` | `2025-09-01 00:00:00` |
| `fuente_destino` | `str` | DateTime | No | `PUBLIC` | `Armenia, Mercar` |
| `codigo_departamento_origen` | `str` | DateTime | No | `PUBLIC` | `'63` |
| `codigo_divipola_origen` | `str` | DateTime | No | `PUBLIC` | `'63190` |
| `departamento_origen` | `str` | DateTime | No | `PUBLIC` | `QUINDÍO` |
| `municipio_origen` | `str` | DateTime | No | `PUBLIC` | `CIRCASIA` |
| `grupo_alimento` | `str` | DateTime | No | `PUBLIC` | `VERDURAS Y HORTALIZAS` |
| `producto` | `str` | DateTime | No | `PUBLIC` | `Tomate chonto` |
| `cantidad_kg` | `float64` | Numeric | No | `INTERNAL` | `4.4` |

### Entidad: `sipsa_precios`
- **Capa Medallion**: SILVER
- **Descripción**: Cotizaciones mayoristas diarias desenrolladas por central de abastos (DANE SIPSA).
- **Granularidad**: `Fecha x Mercado Mayorista x Producto`
- **Clave Primaria**: `producto`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `producto` | `str` | DateTime | No | `PUBLIC` | `Ahuyama` |
| `armenia_mercar_precio` | `float64` | Numeric | Sí | `PUBLIC` | `1033.0` |
| `armenia_mercar_var` | `float64` | Numeric | Sí | `PUBLIC` | `0.0` |
| `bogota_corabastos_precio` | `float64` | Numeric | Sí | `PUBLIC` | `2200.0` |
| `bogota_corabastos_var` | `float64` | Numeric | Sí | `PUBLIC` | `-0.03` |
| `bucaramanga_centroabastos_precio` | `float64` | Numeric | Sí | `PUBLIC` | `1350.0` |
| `bucaramanga_centroabastos_var` | `float64` | Numeric | Sí | `PUBLIC` | `0.0` |
| `cali_cavasa_precio` | `str` | DateTime | No | `PUBLIC` | `1600` |
| `cali_cavasa_var` | `str` | DateTime | No | `PUBLIC` | `0.14` |
| `cucuta_cenabastos_precio` | `float64` | Numeric | Sí | `PUBLIC` | `1917.0` |
| `cucuta_cenabastos_var` | `float64` | Numeric | Sí | `PUBLIC` | `0.0` |
| `ibague_plaza_la_21_precio` | `str` | DateTime | No | `PUBLIC` | `1800` |
| `ibague_plaza_la_21_var` | `str` | DateTime | No | `PUBLIC` | `0` |
| `manizales_centro_galerias_precio` | `float64` | Numeric | Sí | `PUBLIC` | `2000.0` |
| `manizales_centro_galerias_var` | `float64` | Numeric | Sí | `PUBLIC` | `0.0` |
| `medellin_cma_precio` | `int64` | Numeric | No | `PUBLIC` | `1250` |
| `medellin_cma_var` | `float64` | Numeric | No | `PUBLIC` | `0.0` |
| `neiva_surabastos_precio` | `str` | DateTime | No | `PUBLIC` | `n.d.` |
| `neiva_surabastos_var` | `str` | DateTime | No | `PUBLIC` | `n.d.` |
| `pasto_el_potrerillo_precio` | `str` | DateTime | No | `PUBLIC` | `n.d.` |
| `pasto_el_potrerillo_var` | `str` | DateTime | No | `PUBLIC` | `n.d.` |
| `pereira_la_41impala_precio` | `float64` | Numeric | Sí | `PUBLIC` | `1700.0` |
| `pereira_la_41impala_var` | `float64` | Numeric | Sí | `PUBLIC` | `-0.04` |
| `pereira_mercasa_precio` | `float64` | Numeric | Sí | `PUBLIC` | `1700.0` |
| `pereira_mercasa_var` | `float64` | Numeric | Sí | `PUBLIC` | `-0.04` |
| `santa_marta_precio` | `str` | DateTime | No | `PUBLIC` | `n.d.` |
| `santa_marta_var` | `str` | DateTime | No | `PUBLIC` | `n.d.` |
| `tunja_precio` | `float64` | Numeric | Sí | `PUBLIC` | `958.0` |
| `tunja_var` | `float64` | Numeric | Sí | `PUBLIC` | `-0.03` |

### Entidad: `sipsa_insumos`
- **Capa Medallion**: SILVER
- **Descripción**: Índices y precios mayoristas de fertilizantes y plaguicidas agrícolas.
- **Granularidad**: `Mes x Insumo Químico`
- **Clave Primaria**: `fecha`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `fecha` | `str` | DateTime | No | `PUBLIC` | `2026-07-01T00:00:00.000` |
| `indice_total` | `float64` | Numeric | No | `PUBLIC` | `170.35` |
| `total_fertilizantes` | `float64` | Numeric | No | `PUBLIC` | `203.72` |
| `total_plaguicidas` | `float64` | Numeric | No | `INTERNAL` | `116.96` |
| `total_otros` | `float64` | Numeric | Sí | `PUBLIC` | `133.51` |
| `total_simples` | `float64` | Numeric | No | `PUBLIC` | `205.64` |
| `total_compuestos` | `float64` | Numeric | No | `PUBLIC` | `201.78` |
| `total_herbicidas` | `float64` | Numeric | No | `INTERNAL` | `118.06` |
| `total_fungicidas` | `float64` | Numeric | No | `INTERNAL` | `113.88` |
| `total_insecticidas` | `float64` | Numeric | No | `INTERNAL` | `114.43` |
| `urea_46` | `float64` | Numeric | No | `PUBLIC` | `223.5` |
| `urea_sulfato` | `float64` | Numeric | No | `PUBLIC` | `206.53` |
| `dap_18_46` | `float64` | Numeric | No | `PUBLIC` | `239.94` |
| `kcl_0_0_60` | `float64` | Numeric | No | `PUBLIC` | `164.4` |
| `sam` | `float64` | Numeric | No | `PUBLIC` | `163.47` |
| `_15_15_15` | `float64` | Numeric | No | `PUBLIC` | `186.05` |
| `_25_4_24` | `float64` | Numeric | No | `PUBLIC` | `211.23` |
| `_17_6_18_2` | `float64` | Numeric | No | `PUBLIC` | `200.18` |
| `_18_18_18` | `float64` | Numeric | No | `PUBLIC` | `214.04` |
| `_31_8_8` | `float64` | Numeric | No | `PUBLIC` | `217.52` |
| `_12_24_12` | `float64` | Numeric | No | `PUBLIC` | `204.67` |
| `_13_26_6` | `float64` | Numeric | No | `PUBLIC` | `212.35` |
| `_15_4_23` | `float64` | Numeric | No | `PUBLIC` | `204.82` |
| `_10_20_30` | `float64` | Numeric | No | `PUBLIC` | `177.78` |
| `_28_4_0_6` | `float64` | Numeric | No | `PUBLIC` | `159.38` |
| `glifosato` | `float64` | Numeric | No | `PUBLIC` | `124.74` |
| `paraquat` | `float64` | Numeric | No | `PUBLIC` | `107.54` |
| `propanil` | `float64` | Numeric | No | `PUBLIC` | `138.51` |
| `_2_4_d_picloram` | `float64` | Numeric | No | `PUBLIC` | `118.73` |
| `_2_4_d` | `float64` | Numeric | No | `PUBLIC` | `123.84` |
| `aminopiralid_2_4_d` | `float64` | Numeric | No | `INTERNAL` | `145.9` |
| `diuron` | `float64` | Numeric | No | `PUBLIC` | `119.79` |
| `glufosinato_de_amonio` | `float64` | Numeric | No | `PUBLIC` | `74.21` |
| `picloram` | `float64` | Numeric | No | `PUBLIC` | `104.76` |
| `oxadiazon` | `float64` | Numeric | No | `PUBLIC` | `84.08` |
| `metsulfuron_metil` | `float64` | Numeric | No | `PUBLIC` | `70.07` |
| `pendimetalin` | `float64` | Numeric | No | `PUBLIC` | `109.59` |
| `clorotalonil` | `float64` | Numeric | No | `PUBLIC` | `91.59` |
| `difenoconazol` | `float64` | Numeric | No | `PUBLIC` | `92.29` |
| `mancozeb` | `float64` | Numeric | No | `PUBLIC` | `151.92` |
| `mancozeb_cimoxanil` | `float64` | Numeric | No | `PUBLIC` | `120.03` |
| `azoxistrobin_difenoconazol` | `float64` | Numeric | No | `PUBLIC` | `128.24` |
| `dimetomorf` | `float64` | Numeric | No | `PUBLIC` | `89.1` |
| `tebuconazol_trifloxistrobin` | `float64` | Numeric | No | `PUBLIC` | `122.58` |
| `propineb_fluopicolide` | `float64` | Numeric | No | `INTERNAL` | `139.88` |
| `mancozeb_metalaxil_m` | `float64` | Numeric | No | `PUBLIC` | `127.79` |
| `clorpirifos` | `float64` | Numeric | No | `PUBLIC` | `0.0` |
| `fipronil` | `float64` | Numeric | No | `PUBLIC` | `0.0` |
| `metomil` | `float64` | Numeric | No | `PUBLIC` | `121.88` |
| `tiametoxam_lambdacihalotrina` | `float64` | Numeric | No | `PUBLIC` | `73.93` |
| `abamectina` | `float64` | Numeric | No | `PUBLIC` | `98.82` |
| `imidacloprid` | `float64` | Numeric | No | `INTERNAL` | `82.51` |
| `profenofos_cipermetrina` | `float64` | Numeric | No | `PUBLIC` | `125.91` |
| `cipermetrina` | `float64` | Numeric | No | `PUBLIC` | `123.91` |
| `profenofos` | `float64` | Numeric | No | `PUBLIC` | `130.71` |
| `total_coadyuvantes` | `float64` | Numeric | No | `PUBLIC` | `134.81` |
| `total_reguladores` | `float64` | Numeric | No | `PUBLIC` | `126.69` |
| `total_molusquicidas` | `float64` | Numeric | No | `INTERNAL` | `205.89` |

### Entidad: `dane_ipc`
- **Capa Medallion**: SILVER
- **Descripción**: Serie longitudinal (2003-2026) del Índice de Precios al Consumidor (IPC Alimentos).
- **Granularidad**: `Año x Mes (Longitudinal)`
- **Clave Primaria**: `anio, mes_num`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `anio` | `int64` | Numeric | No | `PUBLIC` | `2026` |
| `mes_num` | `int64` | Numeric | No | `PUBLIC` | `8` |
| `mes_nombre` | `str` | DateTime | No | `PUBLIC` | `Agosto` |
| `fecha` | `str` | DateTime | No | `PUBLIC` | `2026-08-01` |
| `ipc_alimentos` | `float64` | Numeric | No | `PUBLIC` | `160.42` |
| `variacion_mensual_pct` | `float64` | Numeric | Sí | `PUBLIC` | `0.3942674760623266` |
| `variacion_anual_pct` | `float64` | Numeric | Sí | `PUBLIC` | `6.245446718325698` |

### Entidad: `ideam_pluviometria`
- **Capa Medallion**: SILVER
- **Descripción**: Registros pluviométricos y precipitación acumulada por estación meteorológica.
- **Granularidad**: `Fecha x Estación x Código DIVIPOLA`
- **Clave Primaria**: `codigoestacion, fechaobservacion`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `codigoestacion` | `int64` | Numeric | No | `PUBLIC` | `26125504` |
| `codigosensor` | `int64` | Numeric | No | `PUBLIC` | `240` |
| `fechaobservacion` | `str` | DateTime | No | `PUBLIC` | `2020-03-11T21:05:00.000` |
| `valorobservado` | `float64` | Numeric | No | `PUBLIC` | `0.0` |
| `nombreestacion` | `str` | DateTime | No | `PUBLIC` | `PARAGUAICITO  - AUT` |
| `departamento` | `str` | DateTime | No | `PUBLIC` | `QUINDÍO` |
| `municipio` | `str` | DateTime | No | `PUBLIC` | `BUENAVISTA` |
| `zonahidrografica` | `str` | DateTime | No | `INTERNAL` | `CAUCA` |
| `latitud` | `float64` | Numeric | No | `PUBLIC` | `4.395555556` |
| `longitud` | `float64` | Numeric | No | `PUBLIC` | `-75.73416667` |
| `descripcionsensor` | `str` | DateTime | No | `PUBLIC` | `Precipitacion` |
| `unidadmedida` | `str` | DateTime | No | `INTERNAL` | `mm` |
| `codigo_divipola` | `str` | DateTime | No | `PUBLIC` | `MUN_98430` |

### Entidad: `ideam_telemetria_realtime`
- **Capa Medallion**: SILVER
- **Descripción**: Observaciones sensoricas continuas de estaciones IDEAM (API 57sv-p2fu).
- **Granularidad**: `Timestamp x Código Sensor x DIVIPOLA`
- **Clave Primaria**: `codigoestacion, fechaobservacion`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `codigoestacion` | `int64` | Numeric | No | `PUBLIC` | `21206810` |
| `codigosensor` | `int64` | Numeric | No | `PUBLIC` | `243` |
| `fechaobservacion` | `str` | DateTime | No | `PUBLIC` | `2026-10-01T12:06:00.000` |
| `valorobservado` | `float64` | Numeric | No | `PUBLIC` | `21.98` |
| `nombreestacion` | `str` | DateTime | No | `PUBLIC` | `SAN BENITO  - AUT  [21206810]` |
| `departamento` | `str` | DateTime | No | `PUBLIC` | `Bogotá` |
| `municipio` | `str` | DateTime | No | `PUBLIC` | `Bogotá, D.C` |
| `zonahidrografica` | `str` | DateTime | No | `INTERNAL` | `Alto Magdalena` |
| `latitud` | `float64` | Numeric | No | `PUBLIC` | `4.56365303` |
| `longitud` | `float64` | Numeric | No | `PUBLIC` | `-74.13845` |
| `descripcionsensor` | `str` | DateTime | Sí | `PUBLIC` | `Temperatura del suelo a 50 cm` |
| `unidadmedida` | `str` | DateTime | Sí | `INTERNAL` | `°C` |
| `entidad` | `str` | DateTime | No | `INTERNAL` | `ESTACIONES PARTICULARES` |
| `codigo_divipola` | `str` | DateTime | No | `PUBLIC` | `MUN_71987` |

### Entidad: `dane_csaa`
- **Capa Medallion**: SILVER
- **Descripción**: Cuenta Satélite de la Agroindustria: Valor Agregado Bruto (VAB) por fase productiva.
- **Granularidad**: `Código Cuadro x Cadena Agropecuaria`
- **Clave Primaria**: `codigo_cuadro`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `codigo_cuadro` | `str` | DateTime | No | `PUBLIC` | `Cuadro 1` |
| `descripcion_indicador` | `str` | DateTime | No | `PUBLIC` | `Área sembrada de arroz paddy verde me...` |
| `fase_cadena` | `str` | DateTime | No | `PUBLIC` | `Fase Agrícola / Agroindustrial` |

### Entidad: `doc_webservice_chunks`
- **Capa Medallion**: SILVER
- **Descripción**: Fragmentos procesados de la especificación técnica DANE WebService SIPSA.
- **Granularidad**: `Documento x Chunk ID`
- **Clave Primaria**: `chunk_id`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `chunk_id` | `int64` | Numeric | No | `INTERNAL` | `1` |
| `source_file` | `str` | DateTime | No | `PUBLIC` | `DANE-webservice-SIPSA.pdf` |
| `page_number` | `int64` | Numeric | No | `PUBLIC` | `1` |
| `chunk_text` | `str` | DateTime | No | `PUBLIC` | `OFICINA DE SISTEMAS DOCUMENTACION WEB...` |
| `char_length` | `int64` | Numeric | No | `PUBLIC` | `65` |

### Entidad: `landing_leads`
- **Capa Medallion**: SILVER
- **Descripción**: Prospectos de productores y clientes con seudonimización SHA-256 (Ley 1581).
- **Granularidad**: `ID Lead x Timestamp Registro`
- **Clave Primaria**: `id`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `id` | `str` | DateTime | No | `INTERNAL` | `LEAD-2026-1001` |
| `ticketid` | `str` | DateTime | No | `INTERNAL` | `LEAD-2026-1001` |
| `companyname` | `str` | DateTime | No | `PUBLIC` | `Fintech Andes Corp.` |
| `contactname` | `str` | DateTime | No | `PUBLIC` | `4390a8a8e554070b734dd36643273a9405972...` |
| `email` | `str` | DateTime | No | `CONFIDENTIAL_PII` | `2042a2b555e377eb9fa482ceb53730e717c71...` |
| `phone` | `str` | DateTime | No | `CONFIDENTIAL_PII` | `c70da8950ae09e2f18461ab76332bfe590169...` |
| `industry` | `str` | DateTime | No | `PUBLIC` | `Finanzas & Banca` |
| `services` | `str` | DateTime | No | `PUBLIC` | `['data-engineering', 'ai-data-science']` |
| `datavolumetb` | `int64` | Numeric | No | `PUBLIC` | `12` |
| `budgetusd` | `int64` | Numeric | No | `PUBLIC` | `45000` |
| `urgency` | `str` | DateTime | No | `PUBLIC` | `alta` |
| `challengedescription` | `str` | DateTime | No | `PUBLIC` | `Modernización de DWH legado hacia Dat...` |
| `score` | `int64` | Numeric | No | `PUBLIC` | `88` |
| `priority` | `str` | DateTime | No | `PUBLIC` | `ALTA` |
| `status` | `str` | DateTime | No | `PUBLIC` | `QUALIFIED_FOR_ARB` |
| `assignedto` | `str` | DateTime | No | `PUBLIC` | `Mateo Arismendi (Jefe de Procesos)` |
| `createdat` | `str` | DateTime | No | `PUBLIC` | `2026-09-05 14:22:10 UTC` |

### Entidad: `dim_municipio_divipola`
- **Capa Medallion**: GOLD
- **Descripción**: Data Mart analítico Gold: dim_municipio_divipola
- **Granularidad**: `Agregada / Dimensional`
- **Clave Primaria**: `codigo_divipola`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `codigo_divipola` | `str` | DateTime | No | `PUBLIC` | `11001` |
| `municipio` | `str` | DateTime | No | `PUBLIC` | `Bogotá, D.C.` |
| `departamento` | `str` | DateTime | No | `PUBLIC` | `Bogotá D.C.` |
| `latitud` | `float64` | Numeric | No | `PUBLIC` | `4.711` |
| `longitud` | `float64` | Numeric | No | `PUBLIC` | `-74.0721` |

### Entidad: `dim_producto_agro`
- **Capa Medallion**: GOLD
- **Descripción**: Data Mart analítico Gold: dim_producto_agro
- **Granularidad**: `Agregada / Dimensional`
- **Clave Primaria**: `producto_id`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `producto_id` | `int64` | Numeric | No | `INTERNAL` | `1` |
| `producto` | `str` | DateTime | No | `PUBLIC` | `PAPA` |
| `cpc_code` | `str` | DateTime | No | `PUBLIC` | `01510` |
| `categoria` | `str` | DateTime | No | `PUBLIC` | `Tubérculos` |
| `unidad_estandar` | `str` | DateTime | No | `INTERNAL` | `Kg` |

### Entidad: `mart_business_questions`
- **Capa Medallion**: GOLD
- **Descripción**: Data Mart analítico Gold: mart_business_questions
- **Granularidad**: `Agregada / Dimensional`
- **Clave Primaria**: `pregunta_id`

| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |
|---|---|---|:---:|:---:|---|
| `pregunta_id` | `str` | DateTime | No | `INTERNAL` | `A1` |
| `dimension` | `str` | DateTime | No | `PUBLIC` | `Demanda y Abastecimiento` |
| `titulo` | `str` | DateTime | No | `PUBLIC` | `Tamaño del mercado de abastecimiento` |
| `metrica_parametrica` | `float64` | Numeric | Sí | `PUBLIC` | `120326500.0` |
| `metrica_no_parametrica` | `float64` | Numeric | Sí | `PUBLIC` | `120309000.0` |
| `unidad` | `str` | DateTime | No | `INTERNAL` | `Kg` |
| `interpretacion` | `str` | DateTime | No | `PUBLIC` | `Volumen total abastecido: 120,326,500 Kg` |
