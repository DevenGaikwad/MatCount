"""Role-sensitive response projection for financial and availability data.

Navigation is a usability aid; this module is the server-side information-
visibility boundary used before values are serialized or exported.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from config.constants import Role
from services.rbac import Actor


FINANCIAL_FIELDS = frozenset(
    {
        "unit_cost",
        "available_value",
        "inventory_value",
        "inventory_valuation",
        "disposed_value",
        "total_on_hand_inventory_value",
    }
)

STUDENT_AVAILABILITY_FIELDS = frozenset(
    {
        "inventory_id",
        "lab_id",
        "lab_name",
        "department_name",
        "component_id",
        "component_name",
        "part_number",
        "category_id",
        "category_name",
        "quantity_available",
        "inventory_status",
        "last_updated",
    }
)


def has_financial_visibility(actor: Actor) -> bool:
    """Return the documented SEMS financial-data policy decision.

    Administrators have global valuation visibility. Laboratory assistants may
    view cost only in their own-laboratory operational scope. Faculty and
    students never receive financial values.
    """

    return actor.role in {
        Role.LAB_ASSISTANT.value,
        Role.ADMINISTRATOR.value,
    }


def _mapping(value: Mapping[str, Any] | object) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    sqlalchemy_mapping = getattr(value, "_mapping", None)
    if sqlalchemy_mapping is not None:
        return dict(sqlalchemy_mapping)
    table = getattr(value, "__table__", None)
    if table is not None:
        return {
            column.name: getattr(value, column.name)
            for column in table.columns
        }
    raise TypeError(f"Unsupported policy row: {value.__class__.__name__}")


def redact_financial_row(
    actor: Actor, value: Mapping[str, Any] | object
) -> dict[str, Any]:
    row = _mapping(value)
    if has_financial_visibility(actor):
        return row
    return {key: item for key, item in row.items() if key not in FINANCIAL_FIELDS}


def redact_financial_rows(
    actor: Actor, values: Iterable[Mapping[str, Any] | object]
) -> list[dict[str, Any]]:
    return [redact_financial_row(actor, value) for value in values]


def project_availability_rows(
    actor: Actor, values: Iterable[Mapping[str, Any] | object]
) -> list[dict[str, Any]]:
    """Apply role-sensitive detail minimization to inventory availability."""

    rows = redact_financial_rows(actor, values)
    if actor.role != Role.STUDENT.value:
        return rows
    return [
        {key: item for key, item in row.items() if key in STUDENT_AVAILABILITY_FIELDS}
        for row in rows
    ]

