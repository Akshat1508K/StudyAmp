from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel

from api.auth.routes import get_current_user
from services.rag.rag_service import RAGService

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    document_id: str = None
    subject: str = None


class AnswerResponse(BaseModel):
    answer: str
    sources: list
    confidence: float


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Ask a question using RAG"""
    rag_service = RAGService()
    result = await rag_service.answer_question(
        question=request.question,
        user_id=current_user_id,
        document_id=request.document_id,
        subject=request.subject
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate answer"
        )
    
    return result
