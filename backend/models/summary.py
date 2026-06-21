from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class SummaryRequest(BaseModel):
    document_id: str
    summary_type: str  # short, detailed, exam_day


class SummaryResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    document_id: str
    summary_type: str
    content: str
    generated_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class SummaryInDB(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id: str
    document_id: str
    summary_type: str
    content: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True
