from pymongo import MongoClient

# URI para conexión local
MONGO_URI = "mongodb://localhost:27017"

# Establecer conexión
client = MongoClient(MONGO_URI)
db = client["vocational_test"]
results_collection = db["test_results"]