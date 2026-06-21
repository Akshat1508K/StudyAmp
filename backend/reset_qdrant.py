"""
Reset Qdrant Collection - Recreate with FastEmbed dimensions

This script will:
1. Delete the existing 'study_documents' collection (if it exists)
2. Create a new collection with 384 dimensions (for FastEmbed)
3. Create payload indexes for efficient filtering

USE CASES:
- Migrating from TF-IDF (1000-dim) to FastEmbed (384-dim)
- Fixing "Vector dimension error" issues
- Starting fresh with a clean collection

WARNING: This will delete ALL embeddings in Qdrant!
         MongoDB document records are NOT affected.
         You will need to re-upload PDFs from the frontend.
"""
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import settings

async def reset_collection():
    print("=" * 70)
    print("Qdrant Collection Reset Tool")
    print("=" * 70)
    print("\n⚠ WARNING: This will DELETE all embeddings in Qdrant!")
    print("MongoDB documents will NOT be affected.\n")
    
    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    print("\n[1/4] Connecting to Qdrant...")
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )
    print("✓ Connected to Qdrant Cloud")
    
    # Delete old collection
    print(f"\n[2/4] Deleting old collection '{settings.QDRANT_COLLECTION_NAME}'...")
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if settings.QDRANT_COLLECTION_NAME in collection_names:
            # Get current collection info
            old_info = client.get_collection(settings.QDRANT_COLLECTION_NAME)
            old_size = old_info.config.params.vectors.size
            old_count = client.count(settings.QDRANT_COLLECTION_NAME).count
            
            print(f"  Old collection info:")
            print(f"    Vector size: {old_size} dimensions")
            print(f"    Total chunks: {old_count}")
            
            client.delete_collection(settings.QDRANT_COLLECTION_NAME)
            print(f"✓ Deleted old collection")
        else:
            print(f"  Collection doesn't exist yet (this is fine)")
    except Exception as e:
        print(f"  Note: {e}")
    
    # Create new collection with 384 dimensions for FastEmbed
    print(f"\n[3/4] Creating new collection...")
    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=settings.QDRANT_VECTOR_SIZE,  # Use config value (384 for FastEmbed)
            distance=Distance.COSINE
        )
    )
    print(f"✓ Created collection: {settings.QDRANT_COLLECTION_NAME}")
    print(f"  Vector size: {settings.QDRANT_VECTOR_SIZE} dimensions (FastEmbed)")
    print(f"  Distance metric: Cosine similarity")
    
    # Create payload indexes
    print(f"\n[4/4] Creating payload indexes...")
    client.create_payload_index(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        field_name="document_id",
        field_schema="keyword"
    )
    print(f"  ✓ Index: document_id")
    
    client.create_payload_index(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        field_name="user_id",
        field_schema="keyword"
    )
    print(f"  ✓ Index: user_id")
    
    client.create_payload_index(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        field_name="subject",
        field_schema="keyword"
    )
    print(f"  ✓ Index: subject")
    
    print("\n" + "=" * 70)
    print("✅ QDRANT COLLECTION RESET COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Start the backend: python start_backend_no_reload.py")
    print("  2. Go to the frontend and upload your PDF documents")
    print("  3. Documents will be automatically embedded with FastEmbed")
    print("\nOr run: python migrate_documents.py to re-embed existing PDFs")
    print()


if __name__ == "__main__":
    asyncio.run(reset_collection())
