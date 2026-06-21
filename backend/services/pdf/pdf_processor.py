from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Dict, List
import logging
import uuid

from services.rag.embedding_service import EmbeddingService
from database.qdrant_client import store_embeddings
from qdrant_client.models import PointStruct
from config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        self.embedding_service = EmbeddingService()
    
    async def process_pdf(
        self,
        file_path: str,
        document_id: str,
        user_id: str,
        subject_name: str
    ) -> Dict:
        """Process PDF: extract text, chunk, embed, and store in Qdrant"""
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Load PDF
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            total_pages = len(pages)
            logger.info(f"Loaded {total_pages} pages")
            
            # Extract text from all pages
            full_text = "\n\n".join([page.page_content for page in pages])
            
            # Split into chunks
            chunks = self.text_splitter.split_text(full_text)
            total_chunks = len(chunks)
            
            logger.info(f"Created {total_chunks} chunks")
            
            # Generate embeddings and create points
            points = []
            for idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = await self.embedding_service.get_embedding(chunk)
                
                # Log first few dimensions of first embedding for verification
                if idx == 0:
                    logger.info(f"First embedding dimensions: {len(embedding)}, sample values: {embedding[:5]}")
                
                # Create point
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "user_id": user_id,
                        "document_id": document_id,
                        "chunk_id": idx,
                        "subject": subject_name,
                        "text": chunk,
                        "page_numbers": self._get_page_numbers(idx, total_chunks, total_pages)
                    }
                )
                points.append(point)
            
            # Store in Qdrant
            success = await store_embeddings(points)
            
            if success:
                logger.info(f"Successfully stored {total_chunks} embeddings in Qdrant")
            else:
                logger.error("Failed to store embeddings in Qdrant")
            
            return {
                "total_pages": total_pages,
                "total_chunks": total_chunks,
                "success": success
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def _get_page_numbers(self, chunk_idx: int, total_chunks: int, total_pages: int) -> List[int]:
        """Estimate page numbers for a chunk"""
        chunks_per_page = total_chunks / total_pages
        start_page = int(chunk_idx / chunks_per_page) + 1
        end_page = int((chunk_idx + 1) / chunks_per_page) + 1
        return list(range(start_page, min(end_page + 1, total_pages + 1)))
