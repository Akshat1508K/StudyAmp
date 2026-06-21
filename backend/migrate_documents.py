"""
Migrate existing documents to FastEmbed embeddings.
This script re-processes all documents in MongoDB and regenerates their embeddings
using FastEmbed instead of TF-IDF.

WARNING: This will:
1. Delete all existing embeddings from Qdrant
2. Re-process all PDFs from the uploads folder
3. Generate new FastEmbed embeddings
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import get_database, init_mongodb
from database.qdrant_client import init_qdrant_client, get_qdrant_client, delete_document_embeddings
from services.pdf.pdf_processor import PDFProcessor
from config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate_documents():
    """Re-embed all documents with FastEmbed"""
    print("=" * 70)
    print("Document Migration Tool - TF-IDF → FastEmbed")
    print("=" * 70)
    print("\nThis will re-process all documents and regenerate embeddings.")
    print("This is necessary after switching from TF-IDF to FastEmbed.")
    print("\n⚠ WARNING: This operation cannot be undone!")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    try:
        # Initialize connections
        print("\n[1/4] Initializing database connections...")
        await init_mongodb()
        await init_qdrant_client()
        db = get_database()
        qdrant_client = get_qdrant_client()
        print("✓ Connections established")
        
        # Get all documents
        print("\n[2/4] Fetching documents from MongoDB...")
        documents_collection = db.documents
        documents = await documents_collection.find(
            {"processing_status": "completed"}
        ).to_list(length=None)
        
        total_docs = len(documents)
        print(f"✓ Found {total_docs} completed documents")
        
        if total_docs == 0:
            print("\nNo documents to migrate.")
            return
        
        # Initialize PDF processor
        pdf_processor = PDFProcessor()
        
        # Process each document
        print(f"\n[3/4] Re-processing documents with FastEmbed...")
        success_count = 0
        fail_count = 0
        
        for idx, doc in enumerate(documents, 1):
            doc_id = str(doc['_id'])
            file_name = doc['file_name']
            file_path = doc['file_path']
            
            print(f"\n[{idx}/{total_docs}] Processing: {file_name}")
            print(f"  Document ID: {doc_id}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"  ✗ File not found: {file_path}")
                fail_count += 1
                continue
            
            try:
                # Delete old embeddings
                print(f"  - Deleting old embeddings...")
                await delete_document_embeddings(doc_id)
                
                # Re-process with FastEmbed
                print(f"  - Generating FastEmbed embeddings...")
                result = await pdf_processor.process_pdf(
                    file_path=file_path,
                    document_id=doc_id,
                    user_id=doc['user_id'],
                    subject_name=doc['subject_name']
                )
                
                if result['success']:
                    print(f"  ✓ Successfully embedded {result['total_chunks']} chunks")
                    success_count += 1
                else:
                    print(f"  ✗ Failed to store embeddings")
                    fail_count += 1
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                fail_count += 1
        
        # Summary
        print("\n[4/4] Migration Summary")
        print("=" * 70)
        print(f"Total documents: {total_docs}")
        print(f"✓ Successful: {success_count}")
        print(f"✗ Failed: {fail_count}")
        
        if success_count > 0:
            # Verify Qdrant
            count_result = qdrant_client.count(
                collection_name=settings.QDRANT_COLLECTION_NAME
            )
            print(f"\nTotal chunks in Qdrant: {count_result.count}")
        
        print("\n✓ Migration complete!")
        print("\nNext steps:")
        print("  1. Run 'python verify_embeddings.py' to verify the migration")
        print("  2. Test RAG queries from the frontend")
        print("  3. If issues persist, try deleting and re-uploading documents")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(migrate_documents())
