"""
Consistent REST API response envelopes.
"""
from typing import Any, Optional, Dict
from flask import jsonify, Response


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None
) -> Response:
    payload: Dict[str, Any] = {
        "success": True,
        "status_code": status_code,
        "message": message,
    }
    if data is not None:
        payload["data"] = data
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status_code


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    details: Optional[Any] = None
) -> Response:
    payload: Dict[str, Any] = {
        "success": False,
        "status_code": status_code,
        "error": message,
    }
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code
