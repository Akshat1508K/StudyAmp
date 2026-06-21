"""
Verify FastEmbed embeddings and Qdrant collection status.
This script helps diagnose RAG issues by checking:
1. Qdrant collection exists and has correct vector size
2. Documents in Qdrant and their embedding dimensions
3. Test embedding generation
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.qdrant_client import get_qdrant_client, init_qdrant_client
from services.rag.embedding_service import EmbeddingService
from config import settings
from qdrant_client.models import FieldCondition, MatchValue


async def verify_system():
    """Verify the FastEmbed + Qdrant setup"""
    print("=" * 70)
    print("FastEmbed + Qdrant Verification Tool")
    print("=" * 70)
    
    try:
        # Initialize Qdrant
        print("\n[1/5] Initializing Qdrant connection...")
        await init_qdrant_client()
        client = get_qdrant_client()
        print("✓ Connected to Qdrant Cloud")
        
        # Check collection
        print(f"\n[2/5] Checking collection '{settings.QDRANT_COLLECTION_NAME}'...")
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if settings.QDRANT_COLLECTION_NAME not in collection_names:
            print(f"✗ Collection '{settings.QDRANT_COLLECTION_NAME}' does not exist!")
            print("  Run 'python reset_qdrant.py' to create it.")
            return
        
        # Get collection info
        collection_info = client.get_collection(settings.QDRANT_COLLECTION_NAME)
        vector_size = collection_info.config.params.vectors.size
        print(f"✓ Collection exists")
        print(f"  Vector size: {vector_size} dimensions")
        print(f"  Expected size: {settings.QDRANT_VECTOR_SIZE} dimensions")
        
        if vector_size != settings.QDRANT_VECTOR_SIZE:
            print(f"\n⚠ WARNING: Vector size mismatch!")
            print(f"  Collection has {vector_size}-dim vectors")
            print(f"  FastEmbed generates {settings.QDRANT_VECTOR_SIZE}-dim vectors")
            print(f"\n  SOLUTION: Run 'python reset_qdrant.py' to recreate collection")
            print(f"  Then re-upload all documents from the frontend.")
            return
        else:
            print("✓ Vector dimensions match!")
        
        # Count documents
        print(f"\n[3/5] Counting stored documents...")
        count_result = client.count(
            collection_name=settings.QDRANT_COLLECTION_NAME
        )
        total_chunks = count_result.count
        print(f"✓ Total chunks in Qdrant: {total_chunks}")
        
        if total_chunks == 0:
            print("\n⚠ No documents found in Qdrant.")
            print("  Upload a PDF from the frontend to test the system.")
            return
        
        # Get sample document
        print(f"\n[4/5] Fetching sample chunks...")
        scroll_result = client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            limit=3
        )
        
        if scroll_result[0]:
            print(f"✓ Retrieved {len(scroll_result[0])} sample chunks")
            for i, point in enumerate(scroll_result[0], 1):
                payload = point.payload
                text_preview = payload.get('text', '')[:100]
                print(f"\n  Chunk {i}:")
                print(f"    Document ID: {payload.get('document_id', 'N/A')}")
                print(f"    Subject: {payload.get('subject', 'N/A')}")
                print(f"    Text preview: {text_preview}...")
        
        # Test embedding generation
        print(f"\n[5/5] Testing embedding generation...")
        embedding_service = EmbeddingService()
        test_text = "What is machine learning?"
        test_embedding = await embedding_service.get_embedding(test_text)
        print(f"✓ Generated test embedding")
        print(f"  Dimensions: {len(test_embedding)}")
        print(f"  Sample values: {test_embedding[:5]}")
        
        if len(test_embedding) != settings.QDRANT_VECTOR_SIZE:
            print(f"\n✗ ERROR: Embedding dimension mismatch!")
            return
        
        # Test search
        print(f"\n[BONUS] Testing similarity search...")
        
        # Get a user_id from existing data
        if scroll_result[0]:
            test_user_id = scroll_result[0][0].payload.get('user_id')
            
            search_result = client.search(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query_vector=test_embedding,
                query_filter={
                    "must": [
                        {"key": "user_id", "match": {"value": test_user_id}}
                    ]
                },
                limit=5
            )
            
            print(f"✓ Search returned {len(search_result)} results")
            if search_result:
                print(f"  Top score: {search_result[0].score:.4f}")
                print(f"  Lowest score: {search_result[-1].score:.4f}")
                
                if search_result[0].score < 0.15:
                    print(f"\n⚠ WARNING: Low similarity scores detected")
                    print(f"  This might indicate:")
                    print(f"  1. Test query doesn't match document content")
                    print(f"  2. Documents need re-embedding")
            else:
                print(f"  ✗ No results found (this might be normal if content doesn't match)")
        
        print("\n" + "=" * 70)
        print("VERIFICATION COMPLETE")
        print("=" * 70)
        print("\nSYSTEM STATUS:")
        
        if vector_size == settings.QDRANT_VECTOR_SIZE and total_chunks > 0:
            print("✓ System is properly configured!")
            print("✓ Documents are embedded with FastEmbed")
            print("\nYou can now:")
            print("  1. Upload new documents from the frontend")
            print("  2. Ask questions in the RAG chatbot")
        else:
            print("⚠ System needs attention - see warnings above")
        
        print("\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(verify_system())
