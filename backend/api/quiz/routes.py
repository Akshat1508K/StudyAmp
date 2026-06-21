from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, List, Optional

from api.auth.routes import get_current_user
from services.quiz.quiz_service import QuizService
from models.quiz import (
    QuizGenerateRequest, QuizResponse,
    QuizSubmission, QuizResult
)

router = APIRouter()


@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    request: QuizGenerateRequest,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Generate a quiz from a document"""
    quiz_service = QuizService()
    quiz = await quiz_service.generate_quiz(request, current_user_id)
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz"
        )
    
    return quiz


@router.post("/submit", response_model=QuizResult, status_code=status.HTTP_201_CREATED)
async def submit_quiz(
    submission: QuizSubmission,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Submit quiz answers and get evaluation"""
    quiz_service = QuizService()
    result = await quiz_service.submit_quiz(submission, current_user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return result


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get a specific quiz"""
    quiz_service = QuizService()
    quiz = await quiz_service.get_user_quiz(quiz_id, current_user_id)
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return quiz


@router.get("/result/{result_id}", response_model=QuizResult)
async def get_quiz_result(
    result_id: str,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get quiz result"""
    quiz_service = QuizService()
    result = await quiz_service.get_quiz_result(result_id, current_user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    return result


@router.get("/", response_model=List[QuizResponse])
async def get_user_quizzes(
    document_id: Optional[str] = Query(None, description="Filter by document ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get all quizzes for the current user"""
    quiz_service = QuizService()
    quizzes = await quiz_service.get_user_quizzes(
        user_id=current_user_id,
        document_id=document_id,
        skip=skip,
        limit=limit
    )
    return quizzes


@router.get("/results/list", response_model=List[QuizResult])
async def get_user_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get all quiz results for the current user"""
    quiz_service = QuizService()
    results = await quiz_service.get_user_results(
        user_id=current_user_id,
        skip=skip,
        limit=limit
    )
    return results

