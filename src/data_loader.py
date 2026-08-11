"""Raw Olist loading, schema checks, and data-quality auditing.

This module deliberately contains no modelling code. It reads the four MVP
files without modifying them and returns plain pandas DataFrames for TV1's
aggregation pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

import pandas as pd


REQUIRED_RAW_FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

REQUIRED_COLUMNS = {
    "orders": {"order_id", "order_status", "order_purchase_timestamp"},
    "order_items": {"order_id", "product_id", "price", "freight_value"},
    "products": {
        "product_id",
        "product_category_name",
    },
    "category_translation": {
        "product_category_name",
        "product_category_name_english",
    },
}


@dataclass(frozen=True)
class RawDataSnapshot:
    """File hashes taken before the pipeline starts, used for immutability checks."""

    hashes: dict[str, str]


def raw_file_paths(raw_dir: str | Path) -> dict[str, Path]:
    """Resolve and validate the four required raw CSV paths."""

    directory = Path(raw_dir)
    missing = [name for name in REQUIRED_RAW_FILES.values() if not (directory / name).is_file()]
    if missing:
        expected = ", ".join(REQUIRED_RAW_FILES.values())
        raise FileNotFoundError(
            f"Missing required Olist raw CSV file(s): {', '.join(missing)}. "
            f"Place exactly these files in {directory}: {expected}"
        )
    return {key: directory / filename for key, filename in REQUIRED_RAW_FILES.items()}


def snapshot_raw_files(raw_dir: str | Path) -> RawDataSnapshot:
    """Hash raw input files without changing them."""

    hashes: dict[str, str] = {}
    for name, path in raw_file_paths(raw_dir).items():
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return RawDataSnapshot(hashes=hashes)


def assert_raw_files_unchanged(raw_dir: str | Path, snapshot: RawDataSnapshot) -> None:
    """Raise when a raw input differs from the initial file snapshot."""

    after = snapshot_raw_files(raw_dir)
    if after.hashes != snapshot.hashes:
        changed = sorted(
            name for name in snapshot.hashes if snapshot.hashes.get(name) != after.hashes.get(name)
        )
        raise RuntimeError(f"Raw Olist CSV files were modified during the pipeline: {changed}")


def _validate_schema(name: str, frame: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS[name].difference(frame.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {sorted(missing)}")


def load_raw_data(raw_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Load and schema-validate the four MVP Olist CSVs.

    No dtype coercion is applied here beyond pandas' normal CSV parsing; date
    parsing belongs to the aggregation step where invalid dates can be audited.
    """

    frames: dict[str, pd.DataFrame] = {}
    for name, path in raw_file_paths(raw_dir).items():
        frame = pd.read_csv(path)
        _validate_schema(name, frame)
        frames[name] = frame
    return frames


def _json_value(value: Any) -> Any:
    """Convert pandas/numpy scalar values into report-safe Python values."""

    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def audit_raw_data(raw_data: Mapping[str, pd.DataFrame]) -> dict[str, Any]:
    """Produce factual, serialisable raw-data evidence for the TV1 report."""

    report: dict[str, Any] = {"tables": {}}
    for name, frame in raw_data.items():
        report["tables"][name] = {
            "rows": int(len(frame)),
            "columns": list(frame.columns),
            "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
            "missing_values": {column: int(count) for column, count in frame.isna().sum().items()},
            "duplicate_rows": int(frame.duplicated().sum()),
        }

    orders = raw_data["orders"].copy()
    purchase_time = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
    report["order_status_distribution"] = {
        str(status): int(count)
        for status, count in orders["order_status"].value_counts(dropna=False).items()
    }
    report["purchase_timestamp"] = {
        "min": None if purchase_time.dropna().empty else purchase_time.min().isoformat(),
        "max": None if purchase_time.dropna().empty else purchase_time.max().isoformat(),
        "invalid_or_missing": int(purchase_time.isna().sum()),
    }
    return report
