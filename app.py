# API REST PARA MODELO DE TRADING
import joblib
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# 1. Inicializamos App
app = FastAPI(title="Trading Prediction API", version="1.0")

# 2. Cargamos el Modelo
MODEL_PATH = os.getenv("MODEL_PATH", "trading_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print(f"Modelo cargado correctamente desde {MODEL_PATH}")
except Exception as e:
    print(f"Error cargando modelo: {e}")
    model = None

# 3. Esquema de los datos (Inputs)
class MarketFeatures(BaseModel):
    volume_rel_prev: float
    return_prev: float
    gap_open: float
    rsi_14_prev: float
    macd_diff_prev: float
    bb_position_prev: float
    dist_ma_10: float
    dist_ma_50: float
    volatility_5d: float
    volatility_20d: float
    volatility_30d: float
    day_of_week: int
    month: int

# 4. Endpoints
@app.get("/")
def home():
    return {"message": "API de Predicción de Trading Activa. Usa /predict para obtener señales."}

@app.post("/predict")
def predict_direction(features: MarketFeatures):
    if not model:
        raise HTTPException(status_code=500, detail="El modelo no está cargado.")
    
    input_data = pd.DataFrame([features.dict()])
    
    try:
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0][1]
        
        direction = "SUBIR" if prediction == 1 else "BAJAR"
        
        return {
            "prediction": int(prediction),
            "direction": direction,
            "confidence": float(probability)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
