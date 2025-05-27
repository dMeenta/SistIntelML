from pymongo import MongoClient
import os

client = MongoClient("mongodb://localhost:27017")
db = client["vocational_system"]
collection = db["test_results"]

def save_result(answers, profile):
    doc = {
        "answers": answers,
        "profile": profile
    }
    collection.insert_one(doc)
