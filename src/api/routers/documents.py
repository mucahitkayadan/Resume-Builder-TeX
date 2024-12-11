from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from typing import Dict, Optional, List
from ..schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentType
)
from ..services.document_service import DocumentService
from ..middleware.auth import auth0_middleware

router = APIRouter()

@router.post("/", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        created = await document_service.create_document(user_id, document, file)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    doc_type: Optional[DocumentType] = None,
    document_service: DocumentService = Depends(get_document_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        documents = await document_service.list_documents(user_id, doc_type)
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        file_path = await document_service.get_document_path(user_id, document_id)
        return FileResponse(
            path=file_path,
            media_type='application/pdf',
            filename=f"document_{document_id}.pdf"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        await document_service.delete_document(user_id, document_id)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 