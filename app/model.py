import joblib
import os

model_path = os.path.join("models", "riasec_model.pkl")
model = joblib.load(model_path)

def predict_profile(answers: list[int]) -> str:
    return model.predict([answers])[0]
