from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, Dict

from api.auth.routes import get_current_user
from services.learning.learning_service import LearningService
from models.learning import StudyPlanResponse

router = APIRouter()


@router.post("/study-plan", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_study_plan(
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Generate personalized study plan based on quiz performance"""
    learning_service = LearningService()
    study_plan = await learning_service.generate_study_plan(current_user_id)
    
    if not study_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No quiz results available to generate study plan"
        )
    
    return study_plan


@router.get("/study-plan", response_model=StudyPlanResponse)
async def get_study_plan(
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get latest study plan"""
    learning_service = LearningService()
    study_plan = await learning_service.get_latest_study_plan(current_user_id)
    
    if not study_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No study plan found. Generate one first."
        )
    
    return study_plan


@router.get("/progress", response_model=Dict)
async def get_progress(
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get user's learning progress"""
    learning_service = LearningService()
    progress = await learning_service.get_user_progress(current_user_id)
    return progress
