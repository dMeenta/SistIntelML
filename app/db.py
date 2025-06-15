from pymongo import MongoClient
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(
            os.getenv("MONGO_URI"),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
        self.db = self.client["vocational_test"]
        self.students = self.db["students"]
        self._create_indexes()
    
    def _create_indexes(self):
        """Crea índices para mejorar el rendimiento de las consultas"""
        self.students.create_index("student.email", unique=True, sparse=True)
        self.students.create_index("profile")
        self.students.create_index("timestamp")

db = Database().students