from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


# Schema for Payment (Request Body)
class PaymentCreate(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: str
    payee_added_date_utc: datetime
    payee_due_date: date
    payee_address_line_1: str
    payee_address_line_2: Optional[str]
    payee_city: str
    payee_country: str
    payee_province_or_state: Optional[str]
    payee_postal_code: str
    payee_phone_number: str
    payee_email: str
    currency: str
    discount_percent: Optional[float]
    tax_percent: Optional[float]
    due_amount: float



# Schema for Payment (Response)
class PaymentResponse(PaymentCreate):
    id: str
    total_due: float

# Payment Update Schema (Partial Updates with Optional Fields)
class PaymentUpdate(BaseModel):
    payee_first_name: Optional[str]
    payee_last_name: Optional[str]
    payee_payment_status: Optional[str]
    payee_due_date: Optional[date]
    payee_address_line_1: Optional[str]
    payee_address_line_2: Optional[str]
    payee_city: Optional[str]
    payee_country: Optional[str]
    payee_province_or_state: Optional[str]
    payee_postal_code: Optional[str]
    payee_phone_number: Optional[str]
    payee_email: Optional[str]
    discount_percent: Optional[float]
    tax_percent: Optional[float]
    due_amount: Optional[float]


# Schema for Evidence (Upload and Download)
class EvidenceUpload(BaseModel):
    payment_id: str
    file_name: str
    content: bytes


class EvidenceResponse(BaseModel):
    payment_id: str
    file_name: str
    content: bytes
