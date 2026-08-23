"""
Audit log model for enterprise traceability.
"""
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    actor_type: str = Field(..., description="customer, pharmacist, admin, system")
    actor_id: Optional[str] = None
    action: str
    detail: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
