import joblib
import os
from typing import Dict, Any
from sklearn.base import BaseEstimator
from app.schemas import RIASEC

class VocationalModel:
    def __init__(self, model_path: str = "ml_models/riasec_model.pkl"):
        self.model_path = model_path
        self.model = self._load_model()
        
    def _load_model(self) -> BaseEstimator:
        """Carga el modelo desde el archivo .pkl"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        return joblib.load(self.model_path)
    
    def predict(self, answers: list) -> Dict[str, Any]:
        """Realiza una predicción y devuelve el perfil con metadatos"""
        if len(answers) != 60:
            raise ValueError("Se requieren exactamente 60 respuestas")
            
        prediction = self.model.predict([answers])[0]
        probabilities = self.model.predict_proba([answers])[0]
        
        return {
            "profile": prediction,
            "probabilities": {
                RIASEC.R: float(probabilities[0]),
                RIASEC.I: float(probabilities[1]),
                RIASEC.A: float(probabilities[2]),
                RIASEC.S: float(probabilities[3]),
                RIASEC.E: float(probabilities[4]),
                RIASEC.C: float(probabilities[5]),
            },
            "dominant_traits": self._get_dominant_traits(answers)
        }
    
    def _get_dominant_traits(self, answers: list) -> Dict[str, float]:
        """Calcula los rasgos dominantes basados en las respuestas"""
        # Agrupar respuestas por categoría RIASEC (6 categorías, 10 preguntas cada una)
        categories = {
            "R": sum(answers[i] for i in [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]),
            "I": sum(answers[i] for i in [1, 7, 13, 19, 25, 31, 37, 43, 49, 55]),
            "A": sum(answers[i] for i in [2, 8, 14, 20, 26, 32, 38, 44, 50, 56]),
            "S": sum(answers[i] for i in [3, 9, 15, 21, 27, 33, 39, 45, 51, 57]),
            "E": sum(answers[i] for i in [4, 10, 16, 22, 28, 34, 40, 46, 52, 58]),
            "C": sum(answers[i] for i in [5, 11, 17, 23, 29, 35, 41, 47, 53, 59]),
        }
        return categories