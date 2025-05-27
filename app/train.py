import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# Cargar dataset real
df = pd.read_csv("data/students_responses.csv")  # asegúrate que exista

# Separar features y etiquetas
X = df.drop(columns=["profile"]).values  # respuestas
y = df["profile"].values  # etiquetas RIASEC

# División
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y)

# Entrenamiento
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluación
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Guardar modelo
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/riasec_model.pkl")
print("✅ Modelo entrenado y guardado con joblib.")
