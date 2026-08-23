"""
User schema models for Customers, Pharmacists, and Admins.
"""
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class CustomerRegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field("Patna", max_length=100)
    lat: Optional[float] = None
    lng: Optional[float] = None


class CustomerLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    city: Optional[str] = None
    created_at: Optional[str] = None
