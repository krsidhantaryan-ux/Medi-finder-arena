"""
Custom structured exception classes for MediFinder.
"""
from typing import Any, Optional, Dict


class AppError(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        rv = {"success": False, "error": self.message, "status_code": self.status_code}
        if self.details:
            rv["details"] = self.details
        return rv


class ValidationError(AppError):
    def __init__(self, message: str = "Invalid input payload", details: Optional[Any] = None):
        super().__init__(message, status_code=422, details=details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)


class InternalServerError(AppError):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)
