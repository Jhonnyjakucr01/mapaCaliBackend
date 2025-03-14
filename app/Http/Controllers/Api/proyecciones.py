import sys
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Leer el archivo de Excel desde Laravel
archivo_excel = sys.argv[1]
df = pd.read_excel(archivo_excel)

# Limpiar nombres de columnas
df.columns = df.columns.str.strip()

# Años de entrenamiento y predicción
X_años = np.array([2017, 2018, 2019, 2020, 2022, 2023]).reshape(-1, 1)
df["homicidios 2024 predicho"] = 0

# Modelo Polinómico
poly = PolynomialFeatures(degree=3)
X_poly = poly.fit_transform(X_años)

for i in range(len(df)):
    y = np.array([
        df.loc[i, "homicidios 2017"],
        df.loc[i, "homicidios 2018"],
        df.loc[i, "homicidios 2019"],
        df.loc[i, "homicidios 2020"],
        df.loc[i, "homicidios 2022"],
        df.loc[i, "homicidios 2023"]
    ])

    # Entrenar modelo polinómico
    model_poly = LinearRegression()
    model_poly.fit(X_poly, y)

    # Entrenar modelo Random Forest
    model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
    model_rf.fit(X_años, y)

    # Predecir para 2024
    X_pred = np.array([2017, 2018, 2019, 2020, 2022, 2023, 2024]).reshape(-1, 1)
    X_pred_poly = poly.transform(X_pred)

    pred_2024_poly = model_poly.predict(X_pred_poly)[-1]
    pred_2024_rf = model_rf.predict(np.array([[2024]]))[0]

    # Promedio de ambos modelos
    df.loc[i, "homicidios 2024 predicho"] = round((pred_2024_poly + pred_2024_rf) / 2)

# Convertir a JSON para enviar a Laravel
print(df.to_json(orient="records"))
