from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Annotated, List
import logging

from api.auth.routes import get_current_user
from services.documents.document_service import DocumentService
from models.document import DocumentResponse, DocumentList

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    subject_name: str = Form(...),
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Upload a PDF document"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    document_service = DocumentService()
    document = await document_service.upload_document(
        file=file,
        subject_name=subject_name,
        user_id=current_user_id
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )
    
    return document


@router.get("/", response_model=DocumentList)
async def get_documents(
    skip: int = 0,
    limit: int = 20,
    subject: str = None,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get all documents for the current user"""
    document_service = DocumentService()
    documents = await document_service.get_user_documents(
        user_id=current_user_id,
        skip=skip,
        limit=limit,
        subject=subject
    )
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Get a specific document"""
    document_service = DocumentService()
    document = await document_service.get_document(document_id, current_user_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user_id: Annotated[str, Depends(get_current_user)] = None
):
    """Delete a document"""
    document_service = DocumentService()
    success = await document_service.delete_document(document_id, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return None
