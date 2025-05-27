import joblib
import os

def load_model():
    return joblib.load("models/riasec_model.pkl")
