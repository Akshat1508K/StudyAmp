from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)

# Global Qdrant client
qdrant_client: Optional[QdrantClient] = None


async def init_qdrant_client():
    """Initialize Qdrant Cloud client"""
    global qdrant_client
    try:
        # Check if already connected
        if qdrant_client is not None:
            try:
                qdrant_client.get_collections()
                logger.info("Qdrant already connected")
                return
            except:
                qdrant_client = None
        
        # Connect to Qdrant Cloud
        qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=60
        )
        
        logger.info("Connected to Qdrant Cloud")
        
        # Create collection if not exists
        collections = qdrant_client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if settings.QDRANT_COLLECTION_NAME not in collection_names:
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {settings.QDRANT_COLLECTION_NAME}")
            
            # Create payload indexes for filtering
            qdrant_client.create_payload_index(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                field_name="document_id",
                field_schema="keyword"
            )
            qdrant_client.create_payload_index(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                field_name="user_id",
                field_schema="keyword"
            )
            qdrant_client.create_payload_index(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                field_name="subject",
                field_schema="keyword"
            )
            logger.info("Created Qdrant payload indexes")
        else:
            logger.info(f"Qdrant collection already exists: {settings.QDRANT_COLLECTION_NAME}")
            
            # Ensure indexes exist (for existing collections)
            try:
                qdrant_client.create_payload_index(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    field_name="document_id",
                    field_schema="keyword"
                )
                qdrant_client.create_payload_index(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    field_name="user_id",
                    field_schema="keyword"
                )
                qdrant_client.create_payload_index(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    field_name="subject",
                    field_schema="keyword"
                )
                logger.info("Ensured Qdrant payload indexes exist")
            except Exception as idx_error:
                # Indexes might already exist, which is fine
                logger.info(f"Payload indexes check: {idx_error}")
            
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant Cloud client: {e}")
        raise


async def close_qdrant_client():
    """Close Qdrant client connection"""
    global qdrant_client
    if qdrant_client:
        qdrant_client.close()
        logger.info("Qdrant connection closed")


def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client instance"""
    if qdrant_client is None:
        raise RuntimeError("Qdrant client not initialized")
    return qdrant_client


async def store_embeddings(
    points: List[PointStruct]
) -> bool:
    """Store embeddings in Qdrant"""
    try:
        client = get_qdrant_client()
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points
        )
        return True
    except Exception as e:
        logger.error(f"Failed to store embeddings: {e}")
        return False


async def search_similar(
    query_vector: List[float],
    user_id: str,
    document_id: Optional[str] = None,
    subject: Optional[str] = None,
    top_k: int = 5
) -> List[Dict]:
    """Search for similar vectors"""
    try:
        client = get_qdrant_client()
        
        # Build filter
        filter_conditions = {"user_id": user_id}
        if document_id:
            filter_conditions["document_id"] = document_id
        if subject:
            filter_conditions["subject"] = subject
        
        search_result = client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            query_filter={
                "must": [
                    {"key": key, "match": {"value": value}}
                    for key, value in filter_conditions.items()
                ]
            },
            limit=top_k
            # No score_threshold - let RAG service filter based on scores
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in search_result
        ]
    except Exception as e:
        logger.error(f"Failed to search similar vectors: {e}")
        return []


async def delete_document_embeddings(document_id: str) -> bool:
    """Delete all embeddings for a document"""
    try:
        client = get_qdrant_client()
        client.delete(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points_selector={
                "filter": {
                    "must": [
                        {"key": "document_id", "match": {"value": document_id}}
                    ]
                }
            }
        )
        return True
    except Exception as e:
        logger.error(f"Failed to delete document embeddings: {e}")
        return False
