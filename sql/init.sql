-- Crear esquemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Tabla RAW: Precios diarios tal cual vienen de la fuente
CREATE TABLE IF NOT EXISTS raw.prices_daily (
    date DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    adj_close NUMERIC,
    volume BIGINT,
    run_id VARCHAR(50),
    ingested_at_utc TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),
    source_name VARCHAR(50),
    PRIMARY KEY (date, ticker)
);

-- Tabla ANALYTICS: Features procesados para ML
CREATE TABLE IF NOT EXISTS analytics.daily_features (
    date DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    
    -- Identificación temporal
    year INT,
    month INT,
    day_of_week INT,
    
    -- Datos de mercado base
    open NUMERIC,
    close NUMERIC,
    high NUMERIC,
    low NUMERIC,
    volume BIGINT,
    
    -- Derivadas / Features
    return_close_open NUMERIC, -- Retorno intradía
    return_prev_close NUMERIC, -- Retorno diario (vs cierre ayer)
    volatility_20_days NUMERIC, -- Volatilidad 20 días (desviación estándar del retorno diario)
    
    -- Metadatos
    run_id VARCHAR(50),
    ingested_at_utc TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),
    
    PRIMARY KEY (date, ticker)
);