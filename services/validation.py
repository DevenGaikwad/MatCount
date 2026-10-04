"""Small, reusable input validators aligned with frozen column domains."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from services.exceptions import ValidationError


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9()\-\s]{5,18}$")


def required_text(value: Any, label: str, *, max_length: int) -> str:
    cleaned = str(value).strip() if value is not None else ""
    if not cleaned:
        raise ValidationError(f"{label} is required.")
    if len(cleaned) > max_length:
        raise ValidationError(f"{label} must not exceed {max_length} characters.")
    return cleaned


def optional_text(value: Any, label: str, *, max_length: int) -> str | None:
    if value is None or not str(value).strip():
        return None
    return required_text(value, label, max_length=max_length)


def positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ValidationError(f"{label} must be a positive whole number.")
    try:
        converted = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{label} must be a positive whole number.") from None
    if converted <= 0 or converted != value:
        raise ValidationError(f"{label} must be a positive whole number.")
    return converted


def nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ValidationError(f"{label} must be a non-negative whole number.")
    try:
        converted = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{label} must be a non-negative whole number.") from None
    if converted < 0 or converted != value:
        raise ValidationError(f"{label} must be a non-negative whole number.")
    return converted


def nonnegative_decimal(
    value: Any,
    label: str,
    *,
    maximum: Decimal = Decimal("9999999999.99"),
) -> Decimal:
    try:
        converted = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f"{label} must be a valid non-negative amount.") from None
    if not converted.is_finite() or converted < 0 or converted > maximum:
        raise ValidationError(
            f"{label} must be between 0 and {maximum} for the database column."
        )
    if converted.as_tuple().exponent < -2:
        raise ValidationError(f"{label} must have at most two decimal places.")
    return converted


def email_address(value: Any) -> str:
    email = required_text(value, "Email", max_length=190).lower()
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValidationError("Enter a valid email address, for example user@domain.in.")
    return email


def phone_number(value: Any, label: str = "Contact number") -> str:
    number = required_text(value, label, max_length=20)
    if not PHONE_PATTERN.fullmatch(number):
        raise ValidationError(
            f"{label} may contain digits, spaces, +, -, and parentheses only."
        )
    return number


def date_value(value: Any, label: str) -> date:
    if isinstance(value, datetime) or not isinstance(value, date):
        raise ValidationError(f"{label} must be a valid date.")
    return value


def actual_date(value: Any, label: str) -> date:
    value = date_value(value, label)
    if value > date.today():
        raise ValidationError(f"{label} cannot be in the future.")
    return value
