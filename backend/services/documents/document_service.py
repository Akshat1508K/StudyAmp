from fastapi import UploadFile
from typing import Optional, List
import os
import uuid
import logging
from bson import ObjectId
from datetime import datetime

from models.document import DocumentResponse, DocumentInDB, DocumentList
from database.mongodb import get_database
from services.pdf.pdf_processor import PDFProcessor
from config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self):
        self.db = get_database()
        self.documents_collection = self.db.documents
        self.pdf_processor = PDFProcessor()
        
        # Create upload directory if not exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    async def upload_document(
        self,
        file: UploadFile,
        subject_name: str,
        user_id: str
    ) -> Optional[DocumentResponse]:
        """Upload and process a PDF document"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"File saved: {file_path}")
            
            # Create document record
            document_dict = {
                "user_id": user_id,
                "file_name": file.filename,
                "subject_name": subject_name,
                "upload_date": datetime.utcnow(),
                "file_path": file_path,
                "processing_status": "processing"
            }
            
            result = await self.documents_collection.insert_one(document_dict)
            document_id = str(result.inserted_id)
            document_dict["_id"] = document_id
            
            logger.info(f"Document record created: {document_id}")
            
            # Process PDF in background
            try:
                # Process PDF with FastEmbed embeddings
                processing_result = await self.pdf_processor.process_pdf(
                    file_path=file_path,
                    document_id=document_id,
                    user_id=user_id,
                    subject_name=subject_name
                )
                
                # Update document with processing results
                await self.documents_collection.update_one(
                    {"_id": ObjectId(document_id)},
                    {
                        "$set": {
                            "total_pages": processing_result["total_pages"],
                            "total_chunks": processing_result["total_chunks"],
                            "processing_status": "completed"
                        }
                    }
                )
                
                logger.info(f"Document processed successfully: {document_id}")
                
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                await self.documents_collection.update_one(
                    {"_id": ObjectId(document_id)},
                    {"$set": {"processing_status": "failed"}}
                )
            
            # Get updated document
            updated_doc = await self.documents_collection.find_one({"_id": ObjectId(document_id)})
            updated_doc["_id"] = str(updated_doc["_id"])
            
            return DocumentResponse(**updated_doc)
            
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return None
    
    async def get_user_documents(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        subject: Optional[str] = None
    ) -> DocumentList:
        """Get all documents for a user"""
        try:
            query = {"user_id": user_id}
            if subject:
                query["subject_name"] = subject
            
            cursor = self.documents_collection.find(query).sort("upload_date", -1).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            total = await self.documents_collection.count_documents(query)
            
            # Convert ObjectId to string
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            return DocumentList(
                documents=[DocumentResponse(**doc) for doc in documents],
                total=total
            )
            
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return DocumentList(documents=[], total=0)
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[DocumentResponse]:
        """Get a specific document"""
        try:
            document = await self.documents_collection.find_one({
                "_id": ObjectId(document_id),
                "user_id": user_id
            })
            
            if not document:
                return None
            
            document["_id"] = str(document["_id"])
            return DocumentResponse(**document)
            
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document"""
        try:
            # Get document
            document = await self.documents_collection.find_one({
                "_id": ObjectId(document_id),
                "user_id": user_id
            })
            
            if not document:
                return False
            
            # Delete file
            if os.path.exists(document["file_path"]):
                os.remove(document["file_path"])
            
            # Delete from database
            await self.documents_collection.delete_one({"_id": ObjectId(document_id)})
            
            # Delete embeddings from Qdrant
            from database.qdrant_client import delete_document_embeddings
            await delete_document_embeddings(document_id)
            
            logger.info(f"Document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
