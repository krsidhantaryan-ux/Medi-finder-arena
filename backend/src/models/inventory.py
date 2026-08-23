"""
Medicine and Pharmacy Inventory schema models.
"""
from typing import Optional
from pydantic import BaseModel, Field


class InventoryItemCreateSchema(BaseModel):
    med_name: str = Field(..., min_length=1, max_length=200)
    salt_composition: Optional[str] = ""
    category_slug: Optional[str] = "tablets"
    manufacturer: Optional[str] = ""
    batch_no: Optional[str] = ""
    expiry_date: Optional[str] = None
    price: float = Field(..., ge=0)
    mrp: Optional[float] = Field(0.0, ge=0)
    stock_quantity: int = Field(..., ge=0)
    dosage: Optional[str] = ""
    prescription: bool = False
    is_active: bool = True


class InventoryItemUpdateSchema(BaseModel):
    med_name: Optional[str] = None
    salt_composition: Optional[str] = None
    category_slug: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_no: Optional[str] = None
    expiry_date: Optional[str] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    stock_quantity: Optional[int] = None
    dosage: Optional[str] = None
    prescription: Optional[bool] = None
    is_active: Optional[bool] = None


class InventoryItemResponseSchema(BaseModel):
    id: str
    pharmacy_id: str
    med_name: str
    salt_composition: str
    category_slug: Optional[str] = None
    manufacturer: Optional[str] = ""
    batch_no: Optional[str] = ""
    expiry_date: Optional[str] = None
    price: float
    mrp: float
    stock_quantity: int
    dosage: str
    prescription: bool
    is_active: bool
    pharmacy_name: Optional[str] = None
    pharmacy_address: Optional[str] = None
    pharmacy_phone: Optional[str] = None
    pharmacy_open_24h: Optional[bool] = False
    pharmacy_delivery: Optional[bool] = False
    distance_km: Optional[float] = None
