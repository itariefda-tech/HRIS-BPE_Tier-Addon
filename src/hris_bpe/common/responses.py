from __future__ import annotations

from typing import Any


def success_payload(
    message: str,
    data: Any = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": meta or {},
        "errors": [],
    }


def error_payload(
    message: str,
    errors: list[dict[str, Any]] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": None,
        "meta": meta or {},
        "errors": errors or [],
    }

