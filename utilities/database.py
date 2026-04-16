import asyncio
import os 
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "BookScraperDB"
COLLECTION_NAME = "books"
COLLECTION_NAME_LOGS = "change_log_detection"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client[DB_NAME]
book_collection = database.get_collection(COLLECTION_NAME)
change_log_detection = database.get_collection(COLLECTION_NAME_LOGS)

async def ping_server():
    try: 
        await client.admin.command('ping')
        return True
    except Exception: 
        return False
    
async def setup_database():
    await book_collection.create_index("source_url", unique=True)
    await change_log_detection.create_index("timestamp")
    print("Database is ready")

async def run_setup():
    if await ping_server():
        print("Connecting to the database...")
        await setup_database()
    else:
        print("Could not connect to the database")

