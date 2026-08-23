"""
Review and Ratings domain schema.
"""
from typing import Optional
from pydantic import BaseModel, Field


class CreateReviewSchema(BaseModel):
    pharmacy_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    customer_name: Optional[str] = None


class ReviewResponseSchema(BaseModel):
    id: str
    pharmacy_id: str
    customer_id: Optional[str] = None
    customer_name: str
    rating: int
    comment: Optional[str] = ""
    created_at: Optional[str] = None
