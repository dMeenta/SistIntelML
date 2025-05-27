from app.db import collection
from app.model import load_model

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

import pandas as pd
import os
import joblib

CSV_PATH = "data/answers_log.csv"
MODEL_PATH = "models/riasec_model.pkl"
LOG_PATH = "training_log.txt"

CSV_PATH = "data/answers_log.csv"

def predict_and_store(input_data):
    answers = input_data.answers
    student = input_data.student_info.dict()

    model = load_model()
    profile = model.predict([answers])[0]

    # Guardar en Mongo
    collection.insert_one({
        "student": student,
        "answers": answers,
        "profile": profile
    })

    # Guardar en CSV
    os.makedirs("data", exist_ok=True)
    row = {f"answer_{i+1}": v for i, v in enumerate(answers)}
    row.update(student)
    row["profile"] = profile
    df = pd.DataFrame([row])
    if os.path.exists(CSV_PATH):
        df.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_PATH, index=False)

    return profile

def retrain_model_background():
    df = pd.read_csv(CSV_PATH)
    answer_cols = [col for col in df.columns if col.startswith("answer_")]
    X = df[answer_cols].values
    y = df["profile"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Guardar modelo
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    # Log
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    with open(LOG_PATH, "a") as f:
        f.write(f"Accuracy: {acc:.4f} - F1: {f1:.4f} - Samples: {len(X)}\n")

