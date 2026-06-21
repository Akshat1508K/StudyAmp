from typing import Optional, List, Dict
import logging
from bson import ObjectId
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json
import re

from models.flashcard import (
    FlashcardResponse, FlashcardInDB,
    FlashcardGenerateRequest, FlashcardItem
)
from database.mongodb import get_database
from database.qdrant_client import get_qdrant_client
from config import settings

logger = logging.getLogger(__name__)


class FlashcardService:
    def __init__(self):
        self.db = get_database()
        self.flashcards_collection = self.db.flashcards
        self.documents_collection = self.db.documents
        
        # Initialize ChatGroq LLM
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.5,
            max_tokens=4000
        )
        
        # Setup LangChain chains for different flashcard types
        self._setup_flashcard_chains()
    
    def _setup_flashcard_chains(self):
        """Setup LangChain chains for flashcard generation"""
        
        # Key Points Chain
        key_points_prompt = PromptTemplate(
            input_variables=["text", "num_cards"],
            template="""You are creating exam revision flashcards with KEY POINTS from study material.

IMPORTANT: Generate EXACTLY {num_cards} flashcards. Each flashcard must be separated by ===

For each flashcard, follow this EXACT format:

TOPIC: [Short topic name]
POINTS:
• [Key point 1 - max 20 words]
• [Key point 2 - max 20 words]
• [Key point 3 - max 20 words]
• [Optional: Key point 4]
• [Optional: Key point 5]
===

Rules:
1. Generate EXACTLY {num_cards} key point cards
2. Each topic should have 3-5 bullet points
3. Each point MUST be <= 20 words
4. Focus on exam-relevant facts, definitions, formulas
5. NO unnecessary explanations
6. Use simple, concise language

Study Material:
{text}

Now generate EXACTLY {num_cards} key point flashcards:"""
        )
        self.key_points_chain = LLMChain(llm=self.llm, prompt=key_points_prompt, verbose=False)
        
        # Concept Cards Chain
        concept_prompt = PromptTemplate(
            input_variables=["text", "num_cards"],
            template="""You are creating CONCEPT flashcards that explain core concepts simply.

IMPORTANT: Generate EXACTLY {num_cards} concept flashcards. Each must be separated by ===

For each flashcard, follow this EXACT format:

CONCEPT: [What is the concept name?]
EXPLANATION: [Simple explanation in max 40 words]
===

Rules:
1. Generate EXACTLY {num_cards} concept cards
2. Explanation MUST be <= 40 words
3. Use beginner-friendly simple language
4. Focus on "What is..." type concepts
5. Clear and concise

Study Material:
{text}

Now generate EXACTLY {num_cards} concept flashcards:"""
        )
        self.concept_chain = LLMChain(llm=self.llm, prompt=concept_prompt, verbose=False)
        
        # Comparison Cards Chain
        comparison_prompt = PromptTemplate(
            input_variables=["text", "num_cards"],
            template="""You are creating COMPARISON flashcards for commonly confused concepts.

IMPORTANT: Generate EXACTLY {num_cards} comparison flashcards. Each must be separated by ===

For each flashcard, follow this EXACT format:

COMPARE: [Concept A] vs [Concept B]
LEFT:
• [Point about Concept A]
• [Another point about Concept A]
• [One more point about Concept A]
RIGHT:
• [Point about Concept B]
• [Another point about Concept B]
• [One more point about Concept B]
===

Rules:
1. Generate EXACTLY {num_cards} comparison cards
2. Each side should have 2-4 short points
3. Points should be parallel (matching structure)
4. Focus on key differences
5. Keep points concise

Study Material:
{text}

Now generate EXACTLY {num_cards} comparison flashcards:"""
        )
        self.comparison_chain = LLMChain(llm=self.llm, prompt=comparison_prompt, verbose=False)
    
    async def generate_flashcards(
        self,
        request: FlashcardGenerateRequest,
        user_id: str,
        weak_topics: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Generate flashcards from document with adaptive learning support"""
        try:
            logger.info(f"Generating {request.num_cards} flashcards (weak topics: {weak_topics})")
            
            # Verify document ownership
            document = await self.documents_collection.find_one({
                "_id": ObjectId(request.document_id),
                "user_id": user_id
            })
            
            if not document:
                logger.warning(f"Document not found: {request.document_id}")
                return None
            
            # Get document text from Qdrant
            text_content = await self._get_document_text(request.document_id, user_id, weak_topics)
            
            if not text_content:
                logger.warning(f"No content found for document: {request.document_id}")
                return None
            
            # Limit text to prevent token overflow
            if len(text_content) > 6000:
                text_content = text_content[:6000]
            
            logger.info(f"Using {len(text_content)} characters of content")
            
            # Determine flashcard distribution
            total_cards = request.num_cards
            num_key_points = int(total_cards * 0.5)  # 50% key points
            num_concepts = int(total_cards * 0.3)    # 30% concepts
            num_comparisons = total_cards - num_key_points - num_concepts  # 20% comparisons
            
            all_flashcards = []
            
            # Generate Key Points Cards
            if num_key_points > 0:
                logger.info(f"Generating {num_key_points} key point cards...")
                key_cards = await self._generate_key_points(text_content, num_key_points)
                all_flashcards.extend(key_cards)
                logger.info(f"Generated {len(key_cards)} key point cards")
            
            # Generate Concept Cards
            if num_concepts > 0:
                logger.info(f"Generating {num_concepts} concept cards...")
                concept_cards = await self._generate_concepts(text_content, num_concepts)
                all_flashcards.extend(concept_cards)
                logger.info(f"Generated {len(concept_cards)} concept cards")
            
            # Generate Comparison Cards
            if num_comparisons > 0:
                logger.info(f"Generating {num_comparisons} comparison cards...")
                comparison_cards = await self._generate_comparisons(text_content, num_comparisons)
                all_flashcards.extend(comparison_cards)
                logger.info(f"Generated {len(comparison_cards)} comparison cards")
            
            if not all_flashcards:
                logger.error("Failed to generate any flashcards")
                return None
            
            logger.info(f"✓ Total flashcards generated: {len(all_flashcards)}")
            
            # Return flashcards directly without saving (for revision)
            return {
                "flashcards": all_flashcards,
                "total": len(all_flashcards),
                "weak_topics": weak_topics or []
            }
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}", exc_info=True)
            return None
    
    async def _get_document_text(
        self, 
        document_id: str, 
        user_id: str,
        weak_topics: Optional[List[str]] = None
    ) -> Optional[str]:
        """Get document text from Qdrant, prioritizing weak topics"""
        try:
            client = get_qdrant_client()
            
            # If we have weak topics, prioritize those chunks
            if weak_topics:
                # Search for chunks related to weak topics
                from services.rag.embedding_service import EmbeddingService
                embedding_service = EmbeddingService()
                
                # Get embeddings for weak topics
                weak_topics_text = ", ".join(weak_topics)
                weak_embedding = await embedding_service.get_embedding(weak_topics_text)
                
                # Search for relevant chunks
                from database.qdrant_client import search_similar
                similar_chunks = await search_similar(
                    query_vector=weak_embedding,
                    user_id=user_id,
                    document_id=document_id,
                    top_k=50
                )
                
                if similar_chunks:
                    texts = [chunk['payload']['text'] for chunk in similar_chunks[:30]]
                    logger.info(f"Prioritizing {len(texts)} chunks for weak topics: {weak_topics}")
                    return "\n\n".join(texts)
            
            # Otherwise, get all chunks
            chunks, _ = client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter={
                    "must": [
                        {"key": "document_id", "match": {"value": document_id}},
                        {"key": "user_id", "match": {"value": user_id}}
                    ]
                },
                limit=50
            )
            
            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return None
            
            texts = [chunk.payload.get("text", "") for chunk in chunks]
            return "\n\n".join(texts)
            
        except Exception as e:
            logger.error(f"Error retrieving document text: {e}")
            return None
    
    async def _generate_key_points(self, text: str, num_cards: int) -> List[Dict]:
        """Generate key point flashcards"""
        try:
            response = self.key_points_chain.run(text=text, num_cards=num_cards)
            cards = self._parse_key_points(response)
            return cards
        except Exception as e:
            logger.error(f"Error generating key points: {e}")
            return []
    
    def _parse_key_points(self, response: str) -> List[Dict]:
        """Parse key point flashcards"""
        cards = []
        try:
            blocks = [b.strip() for b in response.split("===") if b.strip()]
            
            for idx, block in enumerate(blocks, 1):
                if "TOPIC:" not in block.upper():
                    continue
                
                # Extract topic
                topic_match = re.search(r'TOPIC:\s*(.+?)(?=\nPOINTS:|\n|$)', block, re.IGNORECASE)
                if not topic_match:
                    continue
                topic = topic_match.group(1).strip()
                
                # Extract points (lines starting with • or -)
                points = []
                for line in block.split('\n'):
                    line = line.strip()
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        point = line[1:].strip()
                        if point and len(point.split()) <= 25:  # Allow some flexibility
                            points.append(point)
                
                if topic and len(points) >= 2:
                    cards.append({
                        "type": "key_point",
                        "topic": topic,
                        "points": points[:5]  # Max 5 points
                    })
                    logger.debug(f"Parsed key point card: {topic}")
            
            return cards
        except Exception as e:
            logger.error(f"Error parsing key points: {e}")
            return []
    
    async def _generate_concepts(self, text: str, num_cards: int) -> List[Dict]:
        """Generate concept flashcards"""
        try:
            response = self.concept_chain.run(text=text, num_cards=num_cards)
            cards = self._parse_concepts(response)
            return cards
        except Exception as e:
            logger.error(f"Error generating concepts: {e}")
            return []
    
    def _parse_concepts(self, response: str) -> List[Dict]:
        """Parse concept flashcards"""
        cards = []
        try:
            blocks = [b.strip() for b in response.split("===") if b.strip()]
            
            for idx, block in enumerate(blocks, 1):
                if "CONCEPT:" not in block.upper():
                    continue
                
                # Extract concept
                concept_match = re.search(r'CONCEPT:\s*(.+?)(?=\nEXPLANATION:|\n|$)', block, re.IGNORECASE)
                if not concept_match:
                    continue
                concept = concept_match.group(1).strip()
                
                # Extract explanation
                explanation_match = re.search(r'EXPLANATION:\s*(.+?)(?=\n|$)', block, re.IGNORECASE | re.DOTALL)
                if not explanation_match:
                    continue
                explanation = explanation_match.group(1).strip()
                
                # Clean up
                explanation = ' '.join(explanation.split())
                
                if concept and explanation and len(explanation.split()) <= 50:
                    cards.append({
                        "type": "concept",
                        "question": concept,
                        "answer": explanation
                    })
                    logger.debug(f"Parsed concept card: {concept}")
            
            return cards
        except Exception as e:
            logger.error(f"Error parsing concepts: {e}")
            return []
    
    async def _generate_comparisons(self, text: str, num_cards: int) -> List[Dict]:
        """Generate comparison flashcards"""
        try:
            response = self.comparison_chain.run(text=text, num_cards=num_cards)
            cards = self._parse_comparisons(response)
            return cards
        except Exception as e:
            logger.error(f"Error generating comparisons: {e}")
            return []
    
    def _parse_comparisons(self, response: str) -> List[Dict]:
        """Parse comparison flashcards"""
        cards = []
        try:
            blocks = [b.strip() for b in response.split("===") if b.strip()]
            
            for idx, block in enumerate(blocks, 1):
                if "COMPARE:" not in block.upper():
                    continue
                
                # Extract comparison topic
                compare_match = re.search(r'COMPARE:\s*(.+?)(?=\nLEFT:|\n|$)', block, re.IGNORECASE)
                if not compare_match:
                    continue
                topic = compare_match.group(1).strip()
                
                # Extract LEFT points
                left_points = []
                in_left = False
                for line in block.split('\n'):
                    if 'LEFT:' in line.upper():
                        in_left = True
                        continue
                    if 'RIGHT:' in line.upper():
                        in_left = False
                        continue
                    
                    if in_left:
                        line = line.strip()
                        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                            point = line[1:].strip()
                            if point:
                                left_points.append(point)
                
                # Extract RIGHT points
                right_points = []
                in_right = False
                for line in block.split('\n'):
                    if 'RIGHT:' in line.upper():
                        in_right = True
                        continue
                    if in_right:
                        line = line.strip()
                        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                            point = line[1:].strip()
                            if point:
                                right_points.append(point)
                
                if topic and len(left_points) >= 2 and len(right_points) >= 2:
                    cards.append({
                        "type": "comparison",
                        "topic": topic,
                        "left_points": left_points[:4],
                        "right_points": right_points[:4]
                    })
                    logger.debug(f"Parsed comparison card: {topic}")
            
            return cards
        except Exception as e:
            logger.error(f"Error parsing comparisons: {e}")
            return []
