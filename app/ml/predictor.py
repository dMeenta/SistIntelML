import pickle
import os

model_path = os.path.join("app", "models", "riasec_model.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

def predict_riasec(answers: list[int]) -> str:
    return model.predict([answers])[0]
