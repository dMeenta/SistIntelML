from app.db import collection
from app.model import VocationalModel
from app.schemas import TestResult, RIASEC, FeedbackInput
from typing import Dict, Any
import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from datetime import datetime, timezone

# Configuraciones
CSV_PATH = "data/answers_log.csv"
MODEL_PATH = "ml_models/riasec_model.pkl"
LOG_PATH = "training_log.txt"
MIN_SAMPLES_TO_RETRAIN = 50  # Mínimo de muestras nuevas para reentrenar

CAREERS_MAPPING = {
    "R": ["Ingeniería Mecánica", "Arquitectura", "Piloto", "Agricultura"],
    "I": ["Medicina", "Física", "Química", "Investigación Científica"],
    "A": ["Diseño Gráfico", "Música", "Artes Escénicas", "Literatura"],
    "S": ["Psicología", "Docencia", "Trabajo Social", "Medicina"],
    "E": ["Administración", "Marketing", "Derecho", "Negocios Internacionales"],
    "C": ["Contabilidad", "Secretariado", "Auditoría", "Bibliotecología"]
}

class ModelService:
    def __init__(self):
        self.model = VocationalModel(MODEL_PATH)
        self.last_retrain_date = None
        self._initialize_directories()

    def _initialize_directories(self):
        """Asegura que los directorios existan"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("ml_models", exist_ok=True)

    def predict_and_store(self, input_data: Dict[str, Any]) -> TestResult:
        """Realiza predicción y almacena resultados"""
        answers = input_data.answers
        student_info = input_data.student_info.model_dump()
        
        # Validación de respuestas
        if len(answers) != 48:
            raise ValueError("Se requieren exactamente 48 respuestas")

        # Predicción
        prediction = self.model.predict(answers)
        recommended_careers = CAREERS_MAPPING.get(prediction["profile"], [])
        
        # Almacenamiento
        self._store_record(answers, student_info, prediction)
        
        return TestResult(
            profile=prediction["profile"],
            probabilities=prediction["probabilities"],
            dominant_traits=prediction["dominant_traits"],
            recommended_careers=recommended_careers
        )

    def _store_record(self, answers, student_info, prediction):
        """Almacena registro en MongoDB y CSV"""
        record = {
            "student": student_info,
            "answers": answers,
            "profile": prediction["profile"],
            "probabilities": prediction["probabilities"],
            "dominant_traits": prediction["dominant_traits"],
            "timestamp": datetime.now(timezone.utc)
        }
        
        # MongoDB
        collection.insert_one(record)
        
        # CSV para entrenamiento
        self._append_to_csv(record)

    def _append_to_csv(self, record):
        """Añade registro al CSV de entrenamiento"""
        row = {f"answer_{i+1}": v for i, v in enumerate(record["answers"])}
        row.update(record["student"])
        row["profile"] = record["profile"]
        
        df = pd.DataFrame([row])
        df.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False)

    def should_retrain(self) -> bool:
        """Determina si se debe reentrenar el modelo"""
        if not os.path.exists(CSV_PATH):
            return False
            
        df = pd.read_csv(CSV_PATH)
        if len(df) < MIN_SAMPLES_TO_RETRAIN:
            return False
            
        # Solo reentrenar si hay suficientes datos nuevos desde el último entrenamiento
        if self.last_retrain_date:
            last_record_date = pd.to_datetime(df['timestamp'].iloc[-1])
            return last_record_date > self.last_retrain_date
        return True

    def retrain_model(self) -> Dict[str, Any]:
        """Reentrena el modelo si hay suficientes datos nuevos"""
        if not self.should_retrain():
            return {"status": "not_retrained", "reason": "not_enough_data"}
        
        df = pd.read_csv(CSV_PATH)
        answer_cols = [col for col in df.columns if col.startswith("answer_")]
        X = df[answer_cols].values
        y = df["profile"].values
        
        # Mejores hiperparámetros encontrados empíricamente
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluación
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        
        # Guardar modelo
        joblib.dump(model, MODEL_PATH)
        self.model = VocationalModel(MODEL_PATH)
        self.last_retrain_date = datetime.now(timezone.utc)
        
        # Log
        log_entry = (
            f"{datetime.now(timezone.utc).isoformat()} - "
            f"Accuracy: {acc:.4f} - F1: {f1:.4f} - "
            f"Samples: {len(X)}\n"
        )
        with open(LOG_PATH, "a") as f:
            f.write(log_entry)
        
        return {
            "status": "retrained",
            "accuracy": acc,
            "f1_score": f1,
            "samples": len(X)
        }

    def submit_feedback(self, feedback: FeedbackInput, test_id: str) -> Dict[str, str]:
        """Procesa feedback y actualiza registros"""
        feedback_data = feedback.model_dump()
        feedback_data["timestamp"] = datetime.now(timezone.utc)
        
        update_data = {"$set": {"feedback": feedback_data}}
        
        if feedback.actual_profile:
            update_data["$set"]["verified_profile"] = feedback.actual_profile
        
        collection.update_one({"_id": test_id}, update_data)
        
        return {"status": "feedback_received"}


# Instancia singleton del servicio
model_service = ModelService()