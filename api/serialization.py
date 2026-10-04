"""Convert approved SEMS domain values into predictable JSON-safe data."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any


def serialize(value: Any) -> Any:
    """Serialize mappings, ORM rows and domain records without leaking internals."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): serialize(item) for key, item in value.items()}
    if is_dataclass(value):
        return serialize(asdict(value))
    mapping = getattr(value, "_mapping", None)
    if mapping is not None:
        return serialize(dict(mapping))
    table = getattr(value, "__table__", None)
    if table is not None:
        return {
            column.name: serialize(getattr(value, column.name))
            for column in table.columns
        }
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return [serialize(item) for item in value]
    raise TypeError(f"Unsupported API response type: {value.__class__.__name__}")


def success(data: Any = None, *, message: str | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {"data": serialize(data)}
    if message:
        response["message"] = message
    return response

