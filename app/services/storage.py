from app.db import results_collection

def save_result(answers: list[int], profile: str):
    results_collection.insert_one({
        "answers": answers,
        "profile": profile
    })