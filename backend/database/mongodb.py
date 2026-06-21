from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

# Global MongoDB client
mongodb_client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongodb():
    """Connect to MongoDB"""
    global mongodb_client
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGO_DB_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance"""
    if mongodb_client is None:
        raise RuntimeError("MongoDB client not initialized")
    return mongodb_client[settings.MONGO_DB_NAME]


async def create_indexes():
    """Create necessary indexes (only if they don't exist)"""
    db = get_database()
    
    try:
        # Users collection indexes
        existing_indexes = await db.users.index_information()
        if "email_1" not in existing_indexes:
            await db.users.create_index([("email", ASCENDING)], unique=True, background=True)
            await db.users.create_index([("created_at", DESCENDING)], background=True)
            logger.info("Created users indexes")
        
        # Documents collection indexes
        existing_indexes = await db.documents.index_information()
        if "user_id_1" not in existing_indexes:
            await db.documents.create_index([("user_id", ASCENDING)], background=True)
            await db.documents.create_index([("upload_date", DESCENDING)], background=True)
            await db.documents.create_index([("subject_name", ASCENDING)], background=True)
            logger.info("Created documents indexes")
        
        # Quizzes collection indexes
        existing_indexes = await db.quizzes.index_information()
        if "user_id_1" not in existing_indexes:
            await db.quizzes.create_index([("user_id", ASCENDING)], background=True)
            await db.quizzes.create_index([("document_id", ASCENDING)], background=True)
            await db.quizzes.create_index([("generated_at", DESCENDING)], background=True)
            logger.info("Created quizzes indexes")
        
        # Results collection indexes
        existing_indexes = await db.results.index_information()
        if "user_id_1" not in existing_indexes:
            await db.results.create_index([("user_id", ASCENDING)], background=True)
            await db.results.create_index([("quiz_id", ASCENDING)], background=True)
            await db.results.create_index([("attempted_at", DESCENDING)], background=True)
            logger.info("Created results indexes")
        
        # Summaries collection indexes
        existing_indexes = await db.summaries.index_information()
        if "user_id_1" not in existing_indexes:
            await db.summaries.create_index([("user_id", ASCENDING)], background=True)
            await db.summaries.create_index([("document_id", ASCENDING)], background=True)
            logger.info("Created summaries indexes")
        
        # Flashcards collection indexes
        existing_indexes = await db.flashcards.index_information()
        if "user_id_1" not in existing_indexes:
            await db.flashcards.create_index([("user_id", ASCENDING)], background=True)
            await db.flashcards.create_index([("document_id", ASCENDING)], background=True)
            logger.info("Created flashcards indexes")
        
        # Study plans collection indexes
        existing_indexes = await db.study_plans.index_information()
        if "user_id_1" not in existing_indexes:
            await db.study_plans.create_index([("user_id", ASCENDING)], background=True)
            await db.study_plans.create_index([("created_at", DESCENDING)], background=True)
            logger.info("Created study plans indexes")
        
        logger.info("MongoDB indexes verified")
    except Exception as e:
        logger.warning(f"Index creation skipped or failed: {e}")
