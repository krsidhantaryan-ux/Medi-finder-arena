"""
Reservation domain schema models.
"""
from typing import Optional
from pydantic import BaseModel, Field


class CreateReservationSchema(BaseModel):
    inventory_id: str
    pharmacy_id: str
    customer_phone: str = Field(..., min_length=8, max_length=20)
    customer_name: Optional[str] = None
    quantity: int = Field(1, ge=1, le=20)
    note: Optional[str] = Field(None, max_length=500)


class ReservationResponseSchema(BaseModel):
    id: str
    inventory_id: str
    pharmacy_id: str
    pharmacy_name: Optional[str] = None
    pharmacy_address: Optional[str] = None
    pharmacy_phone: Optional[str] = None
    med_name: Optional[str] = None
    dosage: Optional[str] = None
    price: Optional[float] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: str
    quantity: int
    status: str  # Pending, Confirmed, Collected, Cancelled, Expired
    note: Optional[str] = None
    held_until: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
