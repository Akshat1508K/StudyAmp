from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, List, Optional, Dict

from api.auth.routes import get_current_user
from services.flashcard.flashcard_service import FlashcardService
from models.flashcard import FlashcardGenerateRequest

router = APIRouter()


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_flashcards(
    request: FlashcardGenerateRequest,
    weak_topics: Optional[List[str]] = Query(None, description="Weak topics from quiz results"),
    current_user_id: Annotated[str, Depends(get_current_user)] = None
) -> Dict:
    """Generate flashcards from a document for revision (not saved)"""
    flashcard_service = FlashcardService()
    result = await flashcard_service.generate_flashcards(
        request=request,
        user_id=current_user_id,
        weak_topics=weak_topics
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate flashcards"
        )
    
    return result
