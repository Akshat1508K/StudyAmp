from typing import List
import logging
from fastembed import TextEmbedding
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        """
        Initialize FastEmbed for high-quality semantic embeddings.
        Uses BAAI/bge-small-en-v1.5 model (384 dimensions, fast, accurate)
        """
        logger.info("Initializing FastEmbed embedding service...")
        
        # Initialize FastEmbed with a lightweight but powerful model
        # BAAI/bge-small-en-v1.5: 384 dimensions, great for semantic search
        self.model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            max_length=512  # Max token length for input text
        )
        
        self.embedding_dim = 384  # BGE-small produces 384-dimensional embeddings
        
        logger.info(f"FastEmbed initialized with {self.embedding_dim}-dimensional embeddings")
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate semantic embedding for a text using FastEmbed.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            # FastEmbed returns a generator, get the first (and only) embedding
            embeddings = list(self.model.embed([text]))
            
            if embeddings:
                embedding = embeddings[0].tolist()
                return embedding
            else:
                logger.error("No embedding generated")
                return [0.0] * self.embedding_dim
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * self.embedding_dim
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch (more efficient).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Batch processing is more efficient
            embeddings = list(self.model.embed(texts))
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[0.0] * self.embedding_dim for _ in texts]
    
    # Keep this method for compatibility but it's no longer needed with FastEmbed
    async def fit_corpus(self, texts: List[str]):
        """
        No-op for FastEmbed - pre-trained models don't need fitting.
        Kept for backward compatibility.
        """
        logger.info(f"FastEmbed uses pre-trained model, no fitting needed for {len(texts)} documents")
        pass
