import pickle
from app.db.mongodb import results_collection

with open("app/ml/riasec_model.pkl", "rb") as f:
    model = pickle.load(f)

def predict_riasec(answers: list[int]) -> str:
    profile = model.predict([answers])[0]
    results_collection.insert_one({"answers": answers, "profile": profile})
    return profile
