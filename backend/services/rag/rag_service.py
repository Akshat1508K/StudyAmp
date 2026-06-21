from typing import Optional, Dict, List
import logging
from langchain_groq import ChatGroq
from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from services.rag.embedding_service import EmbeddingService
from database.qdrant_client import search_similar
from config import settings

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        # Initialize ChatGroq LLM
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.3,
            max_tokens=2048  # Increased from 1024 for more detailed answers
        )
        
        # Create RAG prompt template
        self.rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful study assistant. Answer the student's question based on the provided context from their uploaded notes.

Context from uploaded notes (multiple relevant sections):
{context}

Student's Question: {question}

Instructions:
1. Carefully read ALL the context sections provided above
2. Synthesize information from multiple sections if needed to give a complete answer
3. Answer the question comprehensively using the information from the context
4. If the context doesn't contain enough information, say "I don't have enough information in the uploaded notes to fully answer this question."
5. Be clear, detailed, and educational
6. Use examples from the context when relevant
7. Structure your answer with clear explanations

Answer:"""
        )
        
        # Create LLMChain for RAG
        self.rag_chain = LLMChain(
            llm=self.llm,
            prompt=self.rag_prompt,
            verbose=False
        )
    
    async def answer_question(
        self,
        question: str,
        user_id: str,
        document_id: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Optional[Dict]:
        """Answer a question using RAG pipeline with LangChain"""
        try:
            logger.info(f"Processing question: {question}")
            
            # Generate question embedding
            question_embedding = await self.embedding_service.get_embedding(question)
            logger.info(f"Generated embedding with {len(question_embedding)} dimensions")
            
            # Search for similar chunks
            similar_chunks = await search_similar(
                query_vector=question_embedding,
                user_id=user_id,
                document_id=document_id,
                subject=subject,
                top_k=settings.TOP_K_RETRIEVAL
            )
            
            logger.info(f"Found {len(similar_chunks)} similar chunks")
            if similar_chunks:
                logger.info(f"Top match score: {similar_chunks[0]['score']:.4f}")
                logger.info(f"Lowest match score: {similar_chunks[-1]['score']:.4f}")
            
            if not similar_chunks:
                return {
                    "answer": "Information not found in uploaded notes.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Filter out very low-scoring results (below 0.15 for FastEmbed)
            # FastEmbed with cosine similarity: 0.4+ = highly relevant, 0.2-0.4 = relevant, <0.2 = weak
            filtered_chunks = [chunk for chunk in similar_chunks if chunk['score'] >= 0.15]
            
            if not filtered_chunks:
                return {
                    "answer": "Information not found in uploaded notes. The question might not be related to the uploaded content.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Prepare context from retrieved chunks with better formatting
            context_parts = []
            sources = []
            
            for idx, chunk in enumerate(filtered_chunks):
                # Add section headers for clarity
                section = f"""
[Section {idx+1}] (Relevance: {chunk['score']:.3f})
{chunk['payload']['text']}
---"""
                context_parts.append(section)
                sources.append({
                    "document_id": chunk['payload']['document_id'],
                    "chunk_id": chunk['payload']['chunk_id'],
                    "subject": chunk['payload']['subject'],
                    "score": chunk['score'],
                    "page_numbers": chunk['payload'].get('page_numbers', [])
                })
            
            context = "\n".join(context_parts)
            
            # Use LangChain to generate answer
            answer = self.rag_chain.run(
                context=context,
                question=question
            )
            
            # Calculate confidence based on retrieval scores
            avg_score = sum(chunk['score'] for chunk in filtered_chunks) / len(filtered_chunks)
            
            logger.info(f"Generated answer with confidence: {avg_score:.3f}")
            
            return {
                "answer": answer.strip(),
                "sources": sources,
                "confidence": round(avg_score, 3)
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return None
