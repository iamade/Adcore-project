from fastapi import APIRouter, UploadFile, HTTPException
from ..database.database import evidence_collection

router = APIRouter()

@router.post("/upload_evidence/{payment_id}")
async def upload_evidence(payment_id: str, file: UploadFile):
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    evidence = {"payment_id": payment_id, "file_name":file.filename, "content": await file.read()}
    evidence_collection.insert_one(evidence)
    return {"message": "Evidence uploaded Successfully"}

@router.get("/download_evidence/{payment_id}")
async def download_evidence(payment_id: str):
    evidence = evidence_collection.find_one({"payment_id": payment_id})
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"file_name": evidence['file_name'], "content": evidence['content']}