from http.client import responses

from fastapi import APIRouter, HTTPException, Query, status

from .schemas import PaymentResponse
from ..models.payment_model import Payment
from ..database.database import payments_collection
from bson import ObjectId
import logging


router = APIRouter()

# Configure logging
logging .basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/payments", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK)
async def get_payments(payment_status: str = Query(None), page: int = 1, limit: int = 10):
    query = {}
    if payment_status:
        query["payee_payment_status"] = payment_status

    skip = (page - 1) * limit
    payments_cursor = payments_collection.find(query).skip(skip).limit(limit)

    # Convert each document's _id to a string
    payments = await payments_cursor.to_list(length=limit)
    for payment in payments:
        if "_id" in payment:
            payment["_id"] = str(payment["_id"])  # Convert ObjectId to string

    return payments

@router.post("/payments")
async def create_payment(payment: Payment):
    payment_dict = payment.model_dump()
    payments_collection.insert_one(payment_dict)
    return {"message": "Payment created successfully", "id": str(payment_dict["_id"])}

@router.put("/payments/{payment_id}")
async def update_payment(payment_id: str, payment: Payment):
    updated = payments_collection.update_one({"_id": payment_id}, {"$set": payment.dict()})
    if not updated.matched_count:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment updated successfully"}

@router.delete("/payments/{payment_id}")
async def delete_payment(payment_id: str):
    deleted = payments_collection.delete_one({"_id": payment_id})
    if not deleted.deleted_count:
        raise HTTPException(status_code=404, detail="Payement not found")
    return {"message": "Payment deleted successfully"}