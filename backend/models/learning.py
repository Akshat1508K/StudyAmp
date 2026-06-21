from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId


class TopicPerformance(BaseModel):
    topic: str
    accuracy: float
    attempts: int
    status: str  # weak, moderate, strong


class StudyPlanDay(BaseModel):
    day: int
    topic: str
    description: str
    resources: List[str]


class StudyPlanResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    weak_topics: List[TopicPerformance]
    strong_topics: List[TopicPerformance]
    study_plan: List[StudyPlanDay]
    revision_roadmap: Dict[str, List[str]]
    created_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class StudyPlanInDB(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id: str
    weak_topics: List[dict]
    strong_topics: List[dict]
    study_plan: List[dict]
    revision_roadmap: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True
