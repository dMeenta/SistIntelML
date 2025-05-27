from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.mongo_uri)
db = client[settings.database_name]
results_collection = db["test_results"]
