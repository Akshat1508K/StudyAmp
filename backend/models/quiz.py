from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class QuizQuestion(BaseModel):
    question: str
    question_type: str  # mcq, short_answer, long_answer
    options: Optional[List[str]] = None  # For MCQ
    correct_answer: str
    topic: str
    difficulty: Optional[str] = "medium"  # easy, medium, hard


class QuizGenerateRequest(BaseModel):
    document_id: str
    num_mcq: int = 5
    num_short: int = 3
    num_long: int = 2
    topics: Optional[List[str]] = None


class QuizResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    document_id: str
    questions: List[QuizQuestion]
    generated_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class QuizInDB(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id: str
    document_id: str
    questions: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: Dict[int, str]  # question_index: user_answer


class QuizResult(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    quiz_id: str
    score: float
    accuracy: float
    total_questions: int
    correct_answers: int
    weak_topics: List[str]
    strong_topics: List[str]
    attempted_at: datetime
    detailed_results: List[Dict[str, Any]]
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class QuizResultInDB(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id: str
    quiz_id: str
    score: float
    accuracy: float
    total_questions: int
    correct_answers: int
    weak_topics: List[str]
    strong_topics: List[str]
    attempted_at: datetime = Field(default_factory=datetime.utcnow)
    detailed_results: List[Dict[str, Any]]
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True
