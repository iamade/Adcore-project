from http.client import responses
from datetime import datetime, date, time
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pymongo import ReturnDocument
from .schemas import PaymentResponse, PaymentCreate, PaymentUpdate
from ..database.database import payments_collection
from bson import ObjectId
import logging


router = APIRouter()

# Configure logging
logging .basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Payments with Pagination and Filtering
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
        payment["id"] = str(payment["_id"])
        del payment["_id"]
    # for payment in payments:
    #     if "_id" in payment:
    #         payment["_id"] = str(payment["_id"])  # Convert ObjectId to string

    return payments

def convert_dates(payment_dict):
    # Convert date fields to datetime before inserting into MongoDB
    for field in ["payee_due_date"]:
        if isinstance(payment_dict.get(field), date):
            payment_dict[field] = datetime.combine(payment_dict[field], time(0, 0))
    return payment_dict


# Create New Payment
@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate):
    try:
        payment_dict = payment.model_dump()

        payment_dict = convert_dates(payment_dict)

        payment_dict["due_amount"] = round(payment_dict["due_amount"], 2)

        payment_dict["total_due"] = round(
            payment_dict["due_amount"] * (1 + payment_dict["tax_percent"] / 100) -
            (payment_dict["due_amount"] * payment_dict["discount_percent"] / 100), 2
        )

        result = await payments_collection.insert_one(payment_dict)

        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Payment insertion failed")

        payment_dict["id"] = str(result.inserted_id)
        return PaymentResponse(**payment_dict)

    except Exception as e:
        logger.error(f"Payment creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")


# Update Payment
@router.put("/payments/{payment_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def update_payment(payment_id: str, payment: PaymentUpdate):
    # Only update provided fields
    update_data = {k: v for k, v in payment.model_dump().items() if v is not None}

    # Convert date to datetime if necessary
    for field in ["payee_due_date", "payee_added_date_utc"]:
        if field in update_data and isinstance(update_data[field], date):
            update_data[field] = datetime.combine(update_data[field], time(0, 0))

    # Calculate total_due if necessary
    if "due_amount" in update_data:
        update_data["due_amount"] = round(update_data["due_amount"], 2)
        update_data["total_due"] = round(
            update_data["due_amount"] * (1 + update_data.get("tax_percent", 0) / 100) -
            (update_data["due_amount"] * update_data.get("discount_percent", 0) / 100), 2
        )

    updated_payment = await payments_collection.find_one_and_update(
        {"_id": ObjectId(payment_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if not updated_payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    updated_payment["id"] = str(updated_payment["_id"])
    del updated_payment["_id"]

    return PaymentResponse(**updated_payment)

# Delete Payment
@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(payment_id: str):
    result = await payments_collection.delete_one({"_id": ObjectId(payment_id)})
    if not result.deleted_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    return {"message": "Payment deleted successfully"}


@router.get("/payments/by-id/{payment_id}", response_model=PaymentResponse)
async def get_payment_by_id(payment_id: str):
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(payment_id):
            raise HTTPException(status_code=400, detail="Invalid payment ID format")

        payment = await payments_collection.find_one({"_id": ObjectId(payment_id)})

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # Convert ObjectId to string
        payment["id"] = str(payment["_id"])
        del payment["_id"]

        return PaymentResponse(**payment)

    except Exception as e:
        logger.error(f"Error fetching payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment")


@router.get("/payments/search", response_model=list[PaymentResponse])
async def search_payments(
        payee_first_name: Optional[str] = None,
        payee_last_name: Optional[str] = None
):
    query = {}

    if payee_first_name:
        query["payee_first_name"] = {"$regex": payee_first_name, "$options": "i"}  # Case-insensitive search

    if payee_last_name:
        query["payee_last_name"] = {"$regex": payee_last_name, "$options": "i"}

    payments_cursor = payments_collection.find(query)
    payments = await payments_cursor.to_list(length=None)

    # Convert _id to id
    for payment in payments:
        payment["id"] = str(payment["_id"])
        del payment["_id"]

    if not payments:
        raise HTTPException(status_code=404, detail="No matching payments found")

    return payments