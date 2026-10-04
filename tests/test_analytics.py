"""Analytics/CSV behavior that does not require MySQL."""

import pandas as pd

from services.analytics_service import to_csv


def test_csv_export_handles_empty_report() -> None:
    assert to_csv([]) == b"\n"


def test_csv_export_preserves_columns_and_rows() -> None:
    data = to_csv([{"lab": "VLSI", "available": 12}]).decode("utf-8")
    assert data.splitlines() == ["lab,available", "VLSI,12"]


def test_csv_export_neutralizes_formula_like_text_but_not_numeric_values() -> None:
    frame = pd.DataFrame(
        [{"component": "=HYPERLINK(\"bad\")", "note": "  +SUM(A1:A2)", "delta": -2}]
    )
    data = to_csv(frame).decode("utf-8")
    assert "'=HYPERLINK" in data
    assert "'  +SUM" in data
    assert ",-2" in data
