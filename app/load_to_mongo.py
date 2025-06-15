# load_to_mongodb.py
from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017/")
db = client["vocational_test"]

with open("data/answers_log.json") as f:
    data = json.load(f)

db.students.insert_many(data)
print(f"✅ Insertados {len(data)} registros")