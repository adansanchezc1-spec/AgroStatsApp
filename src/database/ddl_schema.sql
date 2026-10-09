-- Esquema Estrella Relacional para AgroStatsApp
-- Fase PDCO: DEVELOPMENT | Estándar: Ralph Kimball (Dimensional Modeling) / DAMA-DMBOK 2

PRAGMA foreign_keys = ON;

-- 1. Dimensión Tiempo
CREATE TABLE IF NOT EXISTS dim_tiempo (
    id_tiempo INTEGER PRIMARY KEY,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semestre INTEGER NOT NULL,
    UNIQUE(anio, mes)
);

-- 2. Dimensión Municipio (DIVIPOLA)
CREATE TABLE IF NOT EXISTS dim_municipio (
    cod_municipio TEXT PRIMARY KEY,
    cod_departamento TEXT NOT NULL,
    nombre_municipio TEXT NOT NULL,
    nombre_departamento TEXT NOT NULL
);

-- 3. Dimensión Producto / Cultivo
CREATE TABLE IF NOT EXISTS dim_producto (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_producto TEXT NOT NULL,
    grupo_cultivo TEXT,
    variedad TEXT,
    UNIQUE(nombre_producto, variedad)
);

-- 4. Dimensión Insumo Agropecuario
CREATE TABLE IF NOT EXISTS dim_insumo (
    id_insumo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_insumo TEXT NOT NULL UNIQUE,
    categoria_insumo TEXT
);

-- 5. Tabla de Hechos: Producción Agrícola (EVA / UPRA)
CREATE TABLE IF NOT EXISTS fact_produccion_eva (
    id_fact_eva INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tiempo INTEGER NOT NULL,
    cod_municipio TEXT NOT NULL,
    id_producto INTEGER NOT NULL,
    area_sembrada_ha REAL,
    area_cosechada_ha REAL,
    produccion_ton REAL,
    rendimiento_ton_ha REAL,
    FOREIGN KEY(id_tiempo) REFERENCES dim_tiempo(id_tiempo),
    FOREIGN KEY(cod_municipio) REFERENCES dim_municipio(cod_municipio),
    FOREIGN KEY(id_producto) REFERENCES dim_producto(id_producto)
);

-- 6. Tabla de Hechos: Precios e Insumos (SIPSA / DANE)
CREATE TABLE IF NOT EXISTS fact_precios_sipsa (
    id_fact_sipsa INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tiempo INTEGER NOT NULL,
    cod_municipio TEXT NOT NULL,
    id_insumo INTEGER NOT NULL,
    precio_promedio REAL NOT NULL,
    FOREIGN KEY(id_tiempo) REFERENCES dim_tiempo(id_tiempo),
    FOREIGN KEY(cod_municipio) REFERENCES dim_municipio(cod_municipio),
    FOREIGN KEY(id_insumo) REFERENCES dim_insumo(id_insumo)
);

-- 7. Tabla de Hechos: Clima e Índices Hidrometeorológicos (IDEAM)
CREATE TABLE IF NOT EXISTS fact_clima_ideam (
    id_fact_clima INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tiempo INTEGER NOT NULL,
    cod_municipio TEXT,
    codigo_estacion TEXT NOT NULL,
    precipitacion_mensual_mm REAL,
    temperatura_media_c REAL,
    spi_3 REAL,
    anomalia_termica_z REAL,
    FOREIGN KEY(id_tiempo) REFERENCES dim_tiempo(id_tiempo),
    FOREIGN KEY(cod_municipio) REFERENCES dim_municipio(cod_municipio)
);

-- 8. Vista Analítica Desnormalizada para BI y OLAP
CREATE VIEW IF NOT EXISTS view_indicadores_agroclimaticos AS
SELECT 
    t.anio,
    t.mes,
    t.trimestre,
    m.cod_municipio,
    m.nombre_municipio,
    m.nombre_departamento,
    p.nombre_producto,
    p.variedad,
    eva.area_sembrada_ha,
    eva.area_cosechada_ha,
    eva.produccion_ton,
    eva.rendimiento_ton_ha,
    clima.precipitacion_mensual_mm,
    clima.temperatura_media_c,
    clima.spi_3,
    clima.anomalia_termica_z
FROM fact_produccion_eva eva
JOIN dim_tiempo t ON eva.id_tiempo = t.id_tiempo
JOIN dim_municipio m ON eva.cod_municipio = m.cod_municipio
JOIN dim_producto p ON eva.id_producto = p.id_producto
LEFT JOIN fact_clima_ideam clima ON eva.id_tiempo = clima.id_tiempo AND eva.cod_municipio = clima.cod_municipio;

-- 9. Data Mart de Contrastes Estadísticos e Inferencia (Gold)
CREATE TABLE IF NOT EXISTS mart_hypothesis_tests (
    id_test INTEGER PRIMARY KEY AUTOINCREMENT,
    variable TEXT NOT NULL,
    categoria_prueba TEXT NOT NULL,
    prueba TEXT NOT NULL,
    estadistico REAL,
    p_valor REAL,
    decision TEXT NOT NULL,
    interpretacion TEXT
);

-- 10. Índices de Rendimiento para Consultas OLAP y Cruces Dimensionales
CREATE INDEX IF NOT EXISTS idx_fact_eva_tiempo ON fact_produccion_eva(id_tiempo);
CREATE INDEX IF NOT EXISTS idx_fact_eva_mun ON fact_produccion_eva(cod_municipio);
CREATE INDEX IF NOT EXISTS idx_fact_clima_tiempo_mun ON fact_clima_ideam(id_tiempo, cod_municipio);
CREATE INDEX IF NOT EXISTS idx_fact_sipsa_tiempo_mun ON fact_precios_sipsa(id_tiempo, cod_municipio);
