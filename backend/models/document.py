from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class DocumentBase(BaseModel):
    file_name: str
    subject_name: str
    total_pages: Optional[int] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: str = Field(alias="_id")
    user_id: str
    upload_date: datetime
    file_path: str
    total_chunks: Optional[int] = None
    processing_status: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class DocumentInDB(DocumentBase):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_path: str
    total_chunks: Optional[int] = None
    processing_status: str = "pending"  # pending, processing, completed, failed
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class DocumentList(BaseModel):
    documents: list[DocumentResponse]
    total: int
