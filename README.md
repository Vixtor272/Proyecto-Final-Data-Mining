# Proyecto-Final-Data-Mining

## Primera Parte

### Pipeline de Datos para Trading Algorítmico

Este proyecto implementa un pipeline de Ingeniería de Datos completo para la ingesta, almacenamiento y procesamiento de datos financieros. El objetivo es preparar un dataset robusto para el entrenamiento de modelos de Machine Learning.

#### 1. Cómo levantar el Entorno

El proyecto está contenerizado utilizando Docker. Para iniciar todos los servicios (Base de datos Postgres, Jupyter Notebook y el entorno de Python), primero ejecutamos el siguiente comandopara levantar el proyecto:

```
docker compose up -d --build
```

Esto levantará:

- Postgres (Puerto: 5432): Almacenamiento de datos (Esquemas raw y analytics).

- Jupyter (Puerto: 8888): Entorno para ejecutar notebooks de ingesta y exploración.

- Feature-Builder: Servicio listo para ejecutar transformaciones de datos.

#### 2. Ingesta de Datos (Capa Raw)

El primer paso es descargar los datos históricos (OHLCV) desde Yahoo Finance y guardarlos en el esquema raw de la base de datos.

1. Abrir el navegador en: http://localhost:8888

2. Navegar a la carpeta _notebooks/_.

3. Abrir el archivo _01_ingesta_prices_raw.ipynb_.

4. Ejecutar todas las celdas.

**Resultado:**
Se poblará la tabla raw.prices_daily con datos de los últimos 3 años para los activos configurados (SPY, QQQ, GLD).

_¿Por qué se escogieron estos activos?_

Se escogieron estos tres activos: ETFs (Exchange Traded Funds), por ser altamente líquidos, representativos y tener comportamientos distintos, ideales para entrenar modelos de Machine Learning (buscamos correlaciones y patrones):

- **SPY (SPDR S&P 500 ETF Trust):** Representa al mercado general de EE. UU. Es el "benchmark" por excelencia.

- **QQQ (Invesco QQQ Trust):** Representa al sector tecnológico (Nasdaq 100). Tiene mayor volatilidad que el SPY.

- **GLD (SPDR Gold Shares):** Representa al oro. Funciona como activo de refugio y suele tener baja correlación con las acciones, lo cual es vital para que el modelo aprenda sobre diversificación.

#### 3. Construcción de Features (Capa Analytics)

Una vez que los datos crudos están cargados, utilizamos el servicio feature-builder para limpiar los datos, calcular métricas financieras y generar la tabla final _analytics.daily_features_.

Se deben ejecutar los siguientes comandos en la terminal para procesar cada activo:

- **Para SPY (S&P 500):**
```
docker compose run --rm feature-builder python src/build_features.py --mode full --ticker SPY --run-id batch_001 --overwrite true
```
- **Para QQQ (Nasdaq 100 - Tech):**
```
docker compose run --rm feature-builder python src/build_features.py --mode full --ticker QQQ --run-id batch_001 --overwrite true
```
- **Para GLD (Oro):**
```
docker compose run --rm feature-builder python src/build_features.py --mode full --ticker GLD --run-id batch_001 --overwrite true
```

#### 4. Diccionario de Datos: analytics.daily_features

| Columna              | Tipo    | Descripción                                        |
| -------------------- | ------- | -------------------------------------------------- |
| `date`               | Date    | Fecha de la sesión bursátil (PK).                  |
| `ticker`             | String  | Símbolo del activo (ej. SPY) (PK).                 |
| `open`               | Numeric | Precio de apertura del día.                        |
| `close`              | Numeric | Precio de cierre del día.                          |
| `high`               | Numeric | Precio máximo alcanzado en el día.                 |
| `low`                | Numeric | Precio mínimo alcanzado en el día.                 |
| `volume`             | BigInt  | Cantidad de acciones/unidades negociadas.          |
| `return_close_open`  | Numeric | Retorno Intradía: $(Close - Open) / Open$.           |
| `return_prev_close`  | Numeric | Retorno Diario: $(Close_t - Close_{t-1}) / Close_{t-1}$. |
| `volatility_20_days` | Numeric | Desviación estándar de retornos diarios (20 días). |
| `year` / `month`     | Int     | Features temporales.                               |
| `day_of_week`        | Int     | Día de la semana _(0=Lunes, 4=Viernes)_.             |

## Segunda Parte

### ML Trading Classifier & Investment Simulation

Proyecto Final: Modelado de Machine Learning para la predicción de dirección de activos financieros (S&P 500, Oro, Nasdaq), simulación de inversión (Backtesting) y despliegue de API REST.

---

### Descripción de la Segunda Parte del Proyecto

Este proyecto aborda el desafío de predecir la dirección diaria del mercado bursátil (Clasificación Binaria: Subir vs Bajar) utilizando algoritmos de aprendizaje supervisado.

A diferencia de los enfoques tradicionales de regresión de precios, este sistema se centra en la clasificación de tendencias para alimentar una estrategia de inversión automatizada.

#### Características Principales:

- **Ingeniería de Características:** Indicadores técnicos (RSI, MACD, Bollinger Bands) y retardos temporales para evitar look-ahead bias.
- **Comparación de Modelos:** Se evaluaron 7 familias de clasificadores, incluyendo XGBoost, CatBoost, SVM (RBF) y Random Forest.
- **Backtesting Financiero:** Simulación de una cartera de USD 10,000 durante el año 2025.
- **Despliegue:** API REST contenerizada con Docker para inferencia en tiempo real.

---

### Arquitectura y Estructura

```text
.
├── analytics/                  # Datos generados (daily_features)
├── src/                        # Código fuente de ingestión
├── ml_trading_classifier.py    # Script principal: ETL, entrenamiento, validación y backtest
├── app.py                      # API REST con FastAPI
├── Dockerfile                  # Imagen de la API
├── docker-compose.yml          # Orquestación de servicios
├── requirements.txt            # Dependencias
├── trading_model.pkl           # Artefacto del modelo entrenado
└── README.md                   # Documentación
```
---

### Instalación y Configuración

#### Prerrequisitos

- Docker y Docker Compose  
- Python 3.9+  

#### 1. Preparar los datos 

Usamos la tabla _analytics.daily_features_ creada en la primera parte del proyecto.

#### 2. Configurar archivo .env

Crear un archivo .env en la raíz:
```
PG_HOST=localhost
PG_DB=trading_db
PG_USER=postgres
PG_PASSWORD=password
MODEL_PATH=trading_model.pkl
```

### Pipeline de Entrenamiento (MLOps)

El script _ml_trading_classifier.py_ maneja el ciclo de vida completo del modelo.

#### 1. Ejecutar Entrenamiento
```
python ml_trading_classifier.py
```

Este proceso:

- Descarga datos

- Genera indicadores técnicos (RSI, MACD, Bandas de Bollinger)

- Ejecuta búsqueda de hiperparámetros (RandomizedSearchCV)

- Entrena y selecciona el mejor modelo

#### 2. Guardado del Modelo

El mejor modelo según F1-Score se serializa automáticamente con joblib.

Salida:

- trading_model.pkl

- equity_curve_2025.png con el rendimiento financiero del backtest

---

### Justificación Matemática de Métricas

Para problemas financieros de clasificación desbalanceada, se emplean métricas rigurosas basadas en la matriz de confusión:

**Matriz de Confusión**

$$
\begin{array}{l|cc}
 & \textbf{Predicción: Sube} & \textbf{Predicción: Baja} \\
\hline
\textbf{Real: Sube} & TP (Ganancia) & FN (\text{Oportunidad Perdida}) \\
\textbf{Real: Baja} & FP (Pérdida) & TN (\text{Evitamos Caída}) \\
\end{array}
$$

Interpretación:

TP: Se predijo SUBIDA y subió.

TN: Se predijo BAJADA y bajó.

FP: Se predijo SUBIDA y bajó.

FN: Se predijo BAJADA y subió.

**Métricas Principales**

| Métrica   | Fórmula                      | Interpretación                                                      |
| --------- | ---------------------------- | ------------------------------------------------------------------- |
| Accuracy  | $(\frac{TP+TN}{TP+TN+FP+FN})$  | Medida global; puede ser engañosa en mercados tendenciales.         |
| Precision | $(\frac{TP}{TP+FP})$           | De las compras, cuántas fueron correctas. Reduce pérdidas directas. |
| Recall    | $(\frac{TP}{TP+FN})$           | Cuántas subidas reales capturó el modelo.                           |
| F1-Score  | $(2\cdot\frac{P\cdot R}{P+R})$ | Métrica principal por equilibrar oportunidad y riesgo.              |
| ROC-AUC   | Integral del TPR vs FPR      | Evalúa separabilidad de clases independiente del umbral.            |

--- 
### Simulación de Inversión (Backtesting)

El sistema ejecuta un Backtest en datos fuera de muestra (Año 2025).

### Parámetros

- Capital Inicial: 10,000 USD

- Estrategia: Compra-Venta Intradía durante un año

- Reglas:

  - Si $\hat{y} = 1:$ Comprar en _Open_, vender en _Close_
  - Si $\hat{y} = 0:$ Mantener efectivo

### Interpretación de Resultados

Una alta precisión prediciendo caídas mejora el rendimiento respecto a un enfoque pasivo, principalmente por evitar drawdowns y preservar capital.

### Justificación del modelo

XGBoost se consolidó como el mejor modelo debido a su capacidad superior para manejar la **no linealidad** inherente a los datos financieros. A diferencia de modelos lineales (como la Regresión Logística) que buscan una línea recta para separar las clases, XGBoost utiliza un ensamblaje de árboles de decisión secuenciales (Gradient Boosting) que le permite aprender interacciones complejas entre indicadores técnicos, como detectar que un RSI alto solo es bajista si coincide con una divergencia en el MACD, capturando matices que otros modelos ignoran.



Además, su éxito radica en su **equilibrio entre sesgo y varianza**. Mientras que un Árbol de Decisión simple tiende a memorizar el ruido (overfitting) y una SVM puede ser demasiado rígida, XGBoost incorpora mecanismos de regularización internos que penalizan la complejidad innecesaria. Esto le permitió "ignorar" el ruido aleatorio del mercado en el set de entrenamiento y generalizar mejor en el año 2025, resultando en una estrategia más selectiva y rentable que evitó operar en días de baja probabilidad de éxito.

---

### Despliegue de API y Uso

Una vez generado trading_model.pkl, se puede servir predicciones vía API.

#### 1. Levantar con Docker

docker-compose up --build -d

#### 2. Probar endpoint /predict

Ejemplo usando cURL:

```
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "volume_rel_prev": 1.2,
    "return_prev": 0.015,
    "gap_open": 0.002,
    "rsi_14_prev": 65.5,
    "macd_diff_prev": 0.5,
    "bb_position_prev": 0.8,
    "dist_ma_10": 0.01,
    "dist_ma_50": 0.03,
    "volatility_5d": 0.012,
    "volatility_20d": 0.015,
    "volatility_30d": 0.010,
    "day_of_week": 2,
    "month": 10
  }'
```
Finalmente, también se ha incluído en el proyecto un archivo llamado _test_api_script.py_ el cual una vez haya sido levantado el docker y se haya conectado a la API entonces basta con correr directamente este _.py_ e ir modificando los parámetros que uno desea probar, el modelo te dará la predicción y te recomendará si comprar o no.

