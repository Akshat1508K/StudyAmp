from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class FlashcardItem(BaseModel):
    question: str
    answer: str
    topic: str


class FlashcardGenerateRequest(BaseModel):
    document_id: str
    num_cards: int = 10
    topics: Optional[List[str]] = None


class FlashcardResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    document_id: str
    cards: List[FlashcardItem]
    generated_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class FlashcardInDB(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id: str
    document_id: str
    cards: List[dict]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True
