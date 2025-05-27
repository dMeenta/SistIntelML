import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score
import joblib
import os

# Ruta del dataset
CSV_PATH = "data/answers_log.csv"

if not os.path.exists(CSV_PATH):
    print("⚠️ No hay datos para entrenar. Usa POST /predict primero.")
    exit()

# Cargar datos
df = pd.read_csv(CSV_PATH)

# Verifica que haya al menos una columna de respuesta
answer_cols = [col for col in df.columns if col.startswith("answer_")]
if len(answer_cols) < 60:
    raise ValueError("El dataset no contiene al menos 60 respuestas.")

# Simular etiquetas si aún no las tienes
# ⚠️ Reemplaza esto cuando ya tengas 'profile' real etiquetado
if "profile" not in df.columns:
    df["profile"] = np.random.choice(["R", "I", "A", "S", "E", "C"], size=len(df))

# Separar features y etiquetas
X = df[answer_cols].values
y = df["profile"].values

# División en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2)

# Entrenar el modelo
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluar el modelo
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="macro")
print("📊 Reporte:")
print(classification_report(y_test, y_pred))

# Guardar modelo
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/riasec_model.pkl")

# Registrar resultados
with open("training_log.txt", "a") as log:
    log.write(f"Accuracy: {accuracy:.4f} - F1: {f1:.4f} - Samples: {len(X)}\n")

print("✅ Modelo entrenado y guardado.")
