from app.db import collection

def save_result(answers, profile, student_info):
    doc = {
        "student": student_info.dict(),
        "answers": answers,
        "profile": profile
    }
    collection.insert_one(doc)
