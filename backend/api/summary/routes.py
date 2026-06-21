from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List

from api.auth.routes import get_current_user
from services.summary.summary_service import SummaryService
from models.summary import SummaryRequest, SummaryResponse

router = APIRouter()


@router.post("/generate", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def generate_summary(
    request: SummaryRequest,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Generate summary for a document"""
    summary_service = SummaryService()
    summary = await summary_service.generate_summary(
        document_id=request.document_id,
        summary_type=request.summary_type,
        user_id=current_user_id
    )
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary"
        )
    
    return summary


@router.get("/document/{document_id}", response_model=List[SummaryResponse])
async def get_document_summaries(
    document_id: str,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get all summaries for a document"""
    summary_service = SummaryService()
    summaries = await summary_service.get_document_summaries(
        document_id=document_id,
        user_id=current_user_id
    )
    return summaries


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: str,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get a specific summary"""
    summary_service = SummaryService()
    summary = await summary_service.get_summary(summary_id, current_user_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    return summary
