"""Read-only view and aggregate access for dashboards/reports."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


ALLOWED_VIEWS = {
    "v_inventory_detail",
    "v_component_stock_summary",
    "v_low_stock_components",
    "v_request_progress",
    "v_transfer_detail",
    "v_overdue_returns",
    "v_disposal_summary",
}


def fetch_view(
    session: Session,
    view_name: str,
    *,
    lab_id: int | None = None,
    created_by: int | None = None,
    limit: int = 1000,
) -> list[Mapping[str, Any]]:
    if view_name not in ALLOWED_VIEWS:
        raise ValueError(f"Unsupported report view: {view_name}")
    safe_limit = max(1, min(int(limit), 5000))
    lab_filters = {
        "v_inventory_detail": "lab_id = :lab_id",
        "v_component_stock_summary": "lab_id = :lab_id",
        "v_low_stock_components": "lab_id = :lab_id",
        "v_request_progress": "requesting_lab_id = :lab_id",
        "v_transfer_detail": "(source_lab_id = :lab_id OR destination_lab_id = :lab_id)",
        "v_overdue_returns": "(source_lab_id = :lab_id OR destination_lab_id = :lab_id)",
        "v_disposal_summary": "lab_id = :lab_id",
    }
    predicates: list[str] = []
    if lab_id is not None:
        predicates.append(lab_filters[view_name])
    if created_by is not None:
        if view_name != "v_request_progress":
            raise ValueError("Creator scope applies only to request progress.")
        predicates.append("created_by = :created_by")
    where = " WHERE " + " AND ".join(predicates) if predicates else ""
    result = session.execute(
        text(f"SELECT * FROM {view_name}{where} LIMIT {safe_limit}"),
        {"lab_id": lab_id, "created_by": created_by},
    )
    return list(result.mappings())


def fetch_transfer_detail(
    session: Session,
    transfer_id: int,
    *,
    lab_id: int | None = None,
) -> list[Mapping[str, Any]]:
    """Return one transfer at TRANSFER_ITEM grain with optional lab scoping."""

    predicates = ["transfer_id = :transfer_id"]
    if lab_id is not None:
        predicates.append("(source_lab_id = :lab_id OR destination_lab_id = :lab_id)")
    result = session.execute(
        text(
            "SELECT * FROM v_transfer_detail WHERE "
            + " AND ".join(predicates)
            + " ORDER BY transfer_item_id"
        ),
        {"transfer_id": transfer_id, "lab_id": lab_id},
    )
    return list(result.mappings())


def dashboard_kpis(
    session: Session,
    lab_id: int | None = None,
    created_by: int | None = None,
) -> Mapping[str, Any]:
    statement = text(
        """
        SELECT
          (SELECT COUNT(*) FROM lab WHERE (:lab_id IS NULL OR lab_id = :lab_id))
            AS laboratory_count,
          (SELECT COUNT(*) FROM `user` WHERE (:lab_id IS NULL OR lab_id = :lab_id))
            AS user_count,
          (SELECT COUNT(*) FROM component) AS component_count,
          (SELECT COUNT(*) FROM inventory WHERE (:lab_id IS NULL OR lab_id = :lab_id))
            AS inventory_row_count,
          (SELECT COALESCE(SUM(quantity_available), 0) FROM inventory
             WHERE (:lab_id IS NULL OR lab_id = :lab_id))
            AS total_available_stock,
          (SELECT COALESCE(SUM(quantity_reserved), 0) FROM inventory
             WHERE (:lab_id IS NULL OR lab_id = :lab_id))
            AS total_reserved_stock,
          (SELECT COALESCE(SUM((quantity_available + quantity_reserved) * unit_cost), 0)
             FROM inventory
             WHERE (:lab_id IS NULL OR lab_id = :lab_id))
            AS inventory_valuation,
          (SELECT COUNT(*) FROM v_low_stock_components
             WHERE (:lab_id IS NULL OR lab_id = :lab_id)) AS low_stock_count,
          (SELECT COUNT(*) FROM component_request
             WHERE request_status IN ('DRAFT', 'SUBMITTED', 'PARTIALLY_APPROVED', 'APPROVED')
               AND (:lab_id IS NULL OR requesting_lab_id = :lab_id)
               AND (:created_by IS NULL OR created_by = :created_by))
            AS open_request_count,
          (SELECT COUNT(*) FROM transfer
             WHERE transfer_status IN ('DRAFT', 'APPROVED', 'DISPATCHED')
               AND (:lab_id IS NULL OR source_lab_id = :lab_id OR destination_lab_id = :lab_id))
            AS active_transfer_count,
          (SELECT COUNT(*) FROM v_overdue_returns
             WHERE (:lab_id IS NULL OR source_lab_id = :lab_id OR destination_lab_id = :lab_id))
            AS overdue_return_count,
          (SELECT COALESCE(SUM(dr.quantity_disposed), 0)
             FROM disposal_record AS dr
             JOIN inventory AS i ON i.inventory_id = dr.inventory_id
            WHERE (:lab_id IS NULL OR i.lab_id = :lab_id))
            AS disposed_quantity
        """
    )
    return session.execute(
        statement, {"lab_id": lab_id, "created_by": created_by}
    ).mappings().one()


def stock_by_lab(
    session: Session, lab_id: int | None = None
) -> list[Mapping[str, Any]]:
    return list(
        session.execute(
            text(
                """
                SELECT lab_id, lab_name,
                       SUM(quantity_available) AS quantity_available,
                       SUM(quantity_reserved) AS quantity_reserved,
                       ROUND(SUM(inventory_value), 2) AS inventory_value
                FROM v_inventory_detail
                WHERE (:lab_id IS NULL OR lab_id = :lab_id)
                GROUP BY lab_id, lab_name
                ORDER BY lab_name
                """
            ),
            {"lab_id": lab_id},
        ).mappings()
    )


def request_status_distribution(
    session: Session,
    lab_id: int | None = None,
    created_by: int | None = None,
) -> list[Mapping[str, Any]]:
    return list(
        session.execute(
            text(
                """
                SELECT request_status, COUNT(*) AS request_count
                FROM component_request
                WHERE (:lab_id IS NULL OR requesting_lab_id = :lab_id)
                  AND (:created_by IS NULL OR created_by = :created_by)
                GROUP BY request_status
                ORDER BY request_status
                """
            ),
            {"lab_id": lab_id, "created_by": created_by},
        ).mappings()
    )
