from typing import Optional, List
import logging
from bson import ObjectId
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from models.summary import SummaryResponse, SummaryInDB
from database.mongodb import get_database
from database.qdrant_client import get_qdrant_client
from config import settings

logger = logging.getLogger(__name__)


class SummaryService:
    def __init__(self):
        self.db = get_database()
        self.summaries_collection = self.db.summaries
        self.documents_collection = self.db.documents
        
        # Initialize ChatGroq LLM
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.3,
            max_tokens=2048
        )
        
        # Setup LangChain chains for different summary types
        self._setup_summary_chains()
    
    def _setup_summary_chains(self):
        """Setup LangChain chains for summary generation"""
        
        # Short Summary Chain
        short_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Provide a concise summary of the following study material in 3-5 bullet points. Focus on the main concepts and key takeaways.

Material:
{text}

Short Summary:"""
        )
        self.short_chain = LLMChain(llm=self.llm, prompt=short_prompt, verbose=False)
        
        # Detailed Summary Chain
        detailed_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Provide a comprehensive and detailed summary of the following study material. Include all major topics, concepts, definitions, and important details. Organize the summary with clear sections and subsections.

Material:
{text}

Detailed Summary:"""
        )
        self.detailed_chain = LLMChain(llm=self.llm, prompt=detailed_prompt, verbose=False)
        
        # Exam Day Summary Chain
        exam_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Create an exam day quick revision summary of the following study material. Focus on:
- Key formulas and definitions
- Important concepts to remember
- Common mistakes to avoid
- Quick facts and figures
- Critical points that often appear in exams

Material:
{text}

Exam Day Summary:"""
        )
        self.exam_chain = LLMChain(llm=self.llm, prompt=exam_prompt, verbose=False)
    
    async def generate_summary(
        self,
        document_id: str,
        summary_type: str,
        user_id: str
    ) -> Optional[SummaryResponse]:
        """Generate summary for a document"""
        try:
            # Verify document ownership
            document = await self.documents_collection.find_one({
                "_id": ObjectId(document_id),
                "user_id": user_id
            })
            
            if not document:
                logger.warning(f"Document not found: {document_id}")
                return None
            
            # Check if summary already exists
            existing_summary = await self.summaries_collection.find_one({
                "document_id": document_id,
                "user_id": user_id,
                "summary_type": summary_type
            })
            
            if existing_summary:
                existing_summary["_id"] = str(existing_summary["_id"])
                return SummaryResponse(**existing_summary)
            
            # Get document chunks from Qdrant
            client = get_qdrant_client()
            chunks = client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter={
                    "must": [
                        {"key": "document_id", "match": {"value": document_id}},
                        {"key": "user_id", "match": {"value": user_id}}
                    ]
                },
                limit=1000
            )
            
            if not chunks[0]:
                logger.warning(f"No chunks found for document: {document_id}")
                return None
            
            # Extract text from chunks
            texts = [chunk.payload["text"] for chunk in chunks[0]]
            full_text = "\n\n".join(texts)
            
            # Generate summary using appropriate LangChain chain
            if summary_type == "short":
                summary_content = self.short_chain.run(text=full_text)
            elif summary_type == "detailed":
                summary_content = self.detailed_chain.run(text=full_text)
            elif summary_type == "exam_day":
                summary_content = self.exam_chain.run(text=full_text)
            else:
                # Default to short summary
                summary_content = self.short_chain.run(text=full_text)
            
            # Save summary
            summary_dict = {
                "user_id": user_id,
                "document_id": document_id,
                "summary_type": summary_type,
                "content": summary_content.strip(),
                "generated_at": datetime.utcnow()
            }
            
            result = await self.summaries_collection.insert_one(summary_dict)
            summary_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"Summary generated: {summary_type} for document {document_id}")
            
            return SummaryResponse(**summary_dict)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def _create_summary_prompt(self, text: str, summary_type: str) -> str:
        """Create prompt for summary generation"""
        if summary_type == "short":
            prompt = f"""Provide a concise summary of the following study material in 3-5 bullet points. Focus on the main concepts and key takeaways.

Material:
{text}

Short Summary:"""
        
        elif summary_type == "detailed":
            prompt = f"""Provide a comprehensive and detailed summary of the following study material. Include all major topics, concepts, definitions, and important details. Organize the summary with clear sections and subsections.

Material:
{text}

Detailed Summary:"""
        
        elif summary_type == "exam_day":
            prompt = f"""Create an exam day quick revision summary of the following study material. Focus on:
- Key formulas and definitions
- Important concepts to remember
- Common mistakes to avoid
- Quick facts and figures
- Critical points that often appear in exams

Material:
{text}

Exam Day Summary:"""
        
        else:
            prompt = f"""Summarize the following study material:

Material:
{text}

Summary:"""
        
        return prompt
    
    async def get_document_summaries(
        self,
        document_id: str,
        user_id: str
    ) -> List[SummaryResponse]:
        """Get all summaries for a document"""
        try:
            cursor = self.summaries_collection.find({
                "document_id": document_id,
                "user_id": user_id
            }).sort("generated_at", -1)
            
            summaries = await cursor.to_list(length=100)
            
            for summary in summaries:
                summary["_id"] = str(summary["_id"])
            
            return [SummaryResponse(**summary) for summary in summaries]
            
        except Exception as e:
            logger.error(f"Error getting document summaries: {e}")
            return []
    
    async def get_summary(
        self,
        summary_id: str,
        user_id: str
    ) -> Optional[SummaryResponse]:
        """Get a specific summary"""
        try:
            summary = await self.summaries_collection.find_one({
                "_id": ObjectId(summary_id),
                "user_id": user_id
            })
            
            if not summary:
                return None
            
            summary["_id"] = str(summary["_id"])
            return SummaryResponse(**summary)
            
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return None
