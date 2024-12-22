from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from bson import ObjectId
from typing import List
import logging

from .schemas import EvidenceResponse, EvidenceUpload
from ..database.database import evidence_collection

router = APIRouter()

logger = logging.getLogger(__name__)

ALLOWED_FILE_TYPES = ["application/pdf", "image/png", "image/jpeg"]


# Helper function to check valid ObjectId
def validate_object_id(payment_id: str):
    if not ObjectId.is_valid(payment_id):
        raise HTTPException(status_code=400, detail="Invalid payment ID format")
    return payment_id

# Upload Evidence for Payment
@router.post("/upload_evidence/", status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    payment_id: str = Depends(validate_object_id),
    file: UploadFile = None
):
    # File presence check
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )

    # File type validation
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed types: PDF, PNG, JPEG"
        )

    # Read file and create evidence document
    file_content = await file.read()
    evidence = EvidenceUpload(
        payment_id=payment_id,
        file_name=file.filename,
        content=file_content
    )

    # Insert evidence into MongoDB
    result = await evidence_collection.insert_one(evidence.dict())

    logger.info(f"Evidence uploaded for payment {payment_id}")

    return {
        "message": "Evidence uploaded successfully",
        "evidence_id": str(result.inserted_id)
    }

# Download Evidence for a Payment
@router.get("/download_evidence/{payment_id}", response_model=EvidenceResponse, status_code=status.HTTP_200_OK)
async def download_evidence(payment_id: str = Depends(validate_object_id)):
    evidence = await evidence_collection.find_one({"payment_id": payment_id})

    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )

    return EvidenceResponse(
        payment_id=evidence["payment_id"],
        file_name=evidence["file_name"],
        content=evidence["content"]
    )

# List All Evidence for a Payment
@router.get("/evidence/{payment_id}", response_model=List[EvidenceResponse])
async def list_evidence(payment_id: str = Depends(validate_object_id)):
    evidence_cursor = evidence_collection.find({"payment_id": payment_id})
    evidence_list = await evidence_cursor.to_list(length=None)

    if not evidence_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No evidence found for this payment"
        )

    return [EvidenceResponse(**evidence) for evidence in evidence_list]
