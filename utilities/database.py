import os 
from motor.motor_asyncio import AsyncIOMotorClient




MONGO_DETAILS = "mongodb://localhost:27017"
DB_NAME = "BookScraperDB"
COLLECTION_NAME = "books"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client[DB_NAME]
book_collection = database.get_collection(COLLECTION_NAME)


async def ping_server():
    try: 
        await client.admin.command('ping')
        return True
    except Exception: 
        return False
    
async def setup_database():
    await book_collection.create_index("source_url", unique=True)
    print("Database is ready")
