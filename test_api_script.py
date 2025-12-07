import requests
import json

# URL de la API local (Docker)
url = "http://localhost:8000/predict"

# Datos de ejemplo (Simulando un día con indicadores técnicos)
# Estos valores representan un día donde el RSI es bajo (sobreventa)
# y hay un gap positivo, lo que podría indicar una subida.
payload = {
    "volume_rel_prev": 1.5, # Mucho volumen ayer
    "return_prev": -0.02, # Ayer cayó un 2%
    "gap_open": 0.005, # Hoy abrió con hueco alcista
    "rsi_14_prev": 25.0, # RSI muy bajo (Sobreventa -> Posible rebote)
    "macd_diff_prev": 0.1, # MACD empezando a girar
    "bb_position_prev": 0.0, # Tocando banda inferior
    "dist_ma_10": -0.02, # Precio bajo la media de 10
    "dist_ma_50": -0.05, # Precio bajo la media de 50
    "volatility_5d": 0.015,
    "volatility_20d": 0.012,
    "volatility_30d": 0.01,
    "day_of_week": 2, # Miércoles (Lunes=0)
    "month": 10
}

try:
    print(f"Enviando datos a {url}...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\nPredicción Exitosa!")
        print("-" * 30)
        print(f"Dirección Predicha: {result['direction']}")
        print(f"Confianza:          {result['confidence']:.2%}")
        print("-" * 30)
        
        if result['prediction'] == 1:
            print("Consejo del Bot: COMPRAR (Long)")
        else:
            print("Consejo del Bot: MANTENER EFECTIVO (Cash)")
            
    else:
        print(f"Error {response.status_code}: {response.text}")

except requests.exceptions.ConnectionError:
    print("Error de Conexión: Asegúrate de que Docker esté corriendo.")
    print("Ejecuta: docker-compose up")
