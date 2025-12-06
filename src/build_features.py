import argparse
import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime

def get_db_connection():
    """Crea la conexión a base de datos usando variables de entorno."""
    user = os.getenv('PG_USER')
    password = os.getenv('PG_PASSWORD')
    host = os.getenv('PG_HOST')
    port = os.getenv('PG_PORT', '5432')
    db = os.getenv('PG_DB')
    
    if not all([user, password, host, db]):
        raise ValueError("Faltan variables de entorno de base de datos.")
    
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)

def calculate_features(df):
    """Lógica de negocio para crear features."""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 1. Features Temporales
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    
    # 2. Retornos
    # Retorno Intradía: (Close - Open) / Open
    df['return_close_open'] = (df['close'] - df['open']) / df['open']
    
    # Retorno Diario: (Close_t - Close_t-1) / Close_t-1
    df['return_prev_close'] = df['close'].pct_change()
    
    # 3. Volatilidad (Desviación estándar de los últimos 20 días del retorno diario)
    df['volatility_20_days'] = df['return_prev_close'].rolling(window=20).std()
    
    # Limpieza de NaN generados por lag/rolling
    df = df.fillna(0)
    
    return df

def run_pipeline(mode, ticker, start_date, end_date, run_id, overwrite):
    engine = get_db_connection()
    raw_schema = os.getenv('PG_SCHEMA_RAW', 'raw')
    analytics_schema = os.getenv('PG_SCHEMA_ANALYTICS', 'analytics')
    
    print(f"--- Iniciando Feature Builder ---")
    print(f"Modo: {mode}, Ticker: {ticker}, RunID: {run_id}")
    
    # 1. Leer datos RAW
    query = f"""
        SELECT date, ticker, open, high, low, close, volume 
        FROM {raw_schema}.prices_daily 
        WHERE ticker = '{ticker}'
    """
    
    # Filtrado por fecha si aplica
    if mode == 'by-date-range' and start_date and end_date:
        query += f" AND date >= '{start_date}' AND date <= '{end_date}'"
    
    print("Leyendo datos raw...")
    df_raw = pd.read_sql(query, engine)
    
    if df_raw.empty:
        print(f"No se encontraron datos para {ticker}")
        return

    # 2. Calcular Features
    print("Calculando features...")
    df_features = calculate_features(df_raw)
    
    # Añadir metadatos
    df_features['run_id'] = run_id
    df_features['ingested_at_utc'] = datetime.utcnow()
    
    # Seleccionar columnas finales
    cols_to_keep = [
        'date', 'ticker', 'year', 'month', 'day_of_week',
        'open', 'close', 'high', 'low', 'volume',
        'return_close_open', 'return_prev_close', 'volatility_20_days',
        'run_id', 'ingested_at_utc'
    ]
    df_final = df_features[cols_to_keep]
    
    # 3. Cargar a Analytics (Idempotencia)
    print("Escribiendo en base de datos...")
    
    with engine.begin() as conn:
        # Estrategia de Idempotencia: Borrar rango existente e insertar
        # Para simplificar, borramos por ticker y rango de fechas procesado
        min_date = df_final['date'].min().strftime('%Y-%m-%d')
        max_date = df_final['date'].max().strftime('%Y-%m-%d')
        
        if overwrite == 'true':
            delete_stmt = text(f"""
                DELETE FROM {analytics_schema}.daily_features 
                WHERE ticker = :ticker 
                AND date >= :min_date AND date <= :max_date
            """)
            conn.execute(delete_stmt, {'ticker': ticker, 'min_date': min_date, 'max_date': max_date})
            print(f"Registros previos eliminados para {ticker} entre {min_date} y {max_date}.")

        # Insertar
        df_final.to_sql(
            'daily_features', 
            con=conn, 
            schema=analytics_schema, 
            if_exists='append', 
            index=False
        )
    
    print(f"Éxito. {len(df_final)} filas procesadas.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Feature Builder CLI')
    parser.add_argument('--mode', choices=['full', 'by-date-range'], required=True)
    parser.add_argument('--ticker', required=True)
    parser.add_argument('--start-date', help='YYYY-MM-DD')
    parser.add_argument('--end-date', help='YYYY-MM-DD')
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--overwrite', choices=['true', 'false'], default='true')
    
    args = parser.parse_args()
    
    run_pipeline(args.mode, args.ticker, args.start_date, args.end_date, args.run_id, args.overwrite)