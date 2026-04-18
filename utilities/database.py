import os
from dotenv import load_dotenv 
from motor.motor_asyncio import AsyncIOMotorClient
from utilities.logger import get_logger

load_dotenv()
MONGO_DETAILS = os.getenv("MONGO_URI")
DB_NAME = "BookScraperDB"
COLLECTION_NAME = "books"
COLLECTION_NAME_LOGS = "change_log_detection"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client[DB_NAME]
book_collection = database.get_collection(COLLECTION_NAME)
change_log_detection = database.get_collection(COLLECTION_NAME_LOGS)

logger = get_logger("database")

async def ping_server():
    try: 
        await client.admin.command('ping')
        return True
    except Exception: 
        return False
    
async def setup_database():
    await book_collection.create_index("source_url", unique=True)
    await change_log_detection.create_index("timestamp")
    logger.info("Connecting to the database....")

async def run_setup():
    if await ping_server():
        logger.info("Database is ready....")
        await setup_database()
    else:
        logger.info("Could not connect to database....")

