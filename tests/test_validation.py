"""Unit tests for reusable, user-facing input validation."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from services.exceptions import ValidationError
from services.validation import (
    actual_date,
    date_value,
    email_address,
    nonnegative_decimal,
    nonnegative_int,
    optional_text,
    phone_number,
    positive_int,
    required_text,
)


pytestmark = pytest.mark.unit


def test_text_validation_trims_and_normalizes_blank_optional_values() -> None:
    assert required_text("  VLSI  ", "Name", max_length=20) == "VLSI"
    assert optional_text("   ", "Shelf", max_length=20) is None


@pytest.mark.parametrize("value", [None, "", "   "])
def test_required_text_rejects_blank_values(value: object) -> None:
    with pytest.raises(ValidationError, match="is required"):
        required_text(value, "Name", max_length=20)


@pytest.mark.parametrize("value", [0, -1, True, 1.5, "1"])
def test_positive_integer_rejects_nonpositive_or_ambiguous_values(value: object) -> None:
    with pytest.raises(ValidationError, match="positive whole number"):
        positive_int(value, "Quantity")


@pytest.mark.parametrize("value", [-1, True, 2.5, "2"])
def test_nonnegative_integer_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValidationError, match="non-negative whole number"):
        nonnegative_int(value, "Quantity")


def test_decimal_validation_enforces_scale_and_finite_range() -> None:
    assert nonnegative_decimal("12.50", "Cost") == Decimal("12.50")
    for value in ["-0.01", "1.001", "NaN", "10000000000.00"]:
        with pytest.raises(ValidationError):
            nonnegative_decimal(value, "Cost")


def test_email_and_phone_validation() -> None:
    assert email_address("  USER@Example.in ") == "user@example.in"
    assert phone_number("+91-90000-00001") == "+91-90000-00001"
    with pytest.raises(ValidationError):
        email_address("not-an-email")
    with pytest.raises(ValidationError):
        phone_number("+91+90000")


def test_date_validation_rejects_datetime_and_future_actual_date() -> None:
    assert date_value(date.today(), "Date") == date.today()
    with pytest.raises(ValidationError):
        date_value(datetime.now(), "Date")
    with pytest.raises(ValidationError, match="future"):
        actual_date(date.today() + timedelta(days=1), "Date")
