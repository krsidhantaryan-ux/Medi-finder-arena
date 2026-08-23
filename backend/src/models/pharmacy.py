"""
Pharmacy domain schema models.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field


class PharmacyRegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: str = Field(..., min_length=8, max_length=20)
    owner_name: Optional[str] = Field(None, max_length=100)
    license_number: Optional[str] = Field(None, max_length=100)
    address: str = Field(..., min_length=5)
    city: str = Field("Patna", max_length=100)
    state: str = Field("Bihar", max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    open_time: str = Field("08:00", max_length=10)
    close_time: str = Field("22:00", max_length=10)
    is_open_24h: bool = False
    delivery: bool = False
    description: Optional[str] = ""


class PharmacyUpdateSchema(BaseModel):
    phone: Optional[str] = None
    owner_name: Optional[str] = None
    license_number: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    is_open_24h: Optional[bool] = None
    delivery: Optional[bool] = None


class PharmacyResponseSchema(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    owner_name: Optional[str] = None
    license_number: Optional[str] = None
    license_image: Optional[str] = None
    shop_photo: Optional[str] = None
    description: Optional[str] = ""
    address: str
    city: str
    state: str
    pincode: Optional[str] = None
    lat: float
    lng: float
    open_time: str
    close_time: str
    is_open_24h: bool
    delivery: bool
    status: str  # 'Pending', 'Approved', 'Rejected'
    rejection_note: Optional[str] = None
    distance_km: Optional[float] = None
    rating: Optional[float] = None
    total_reviews: Optional[int] = 0
