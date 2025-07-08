from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import MONGO_URI, MONGO_DB

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]