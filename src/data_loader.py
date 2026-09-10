"""Loading and auditing the Kaggle Customer Shopping Trends CSV."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any
import pandas as pd

RAW_FILENAME = "shopping_trends.csv"
REQUIRED_COLUMNS = ["Customer ID", "Age", "Gender", "Item Purchased", "Category", "Purchase Amount (USD)", "Location", "Size", "Color", "Season", "Review Rating", "Subscription Status", "Payment Method", "Shipping Type", "Discount Applied", "Promo Code Used", "Previous Purchases", "Preferred Payment Method", "Frequency of Purchases"]
TARGET_SOURCE = "Purchase Amount (USD)"

@dataclass(frozen=True)
class RawDataSnapshot:
    hashes: dict[str, str]

def raw_file_path(raw_dir: str | Path) -> Path:
    path = Path(raw_dir) / RAW_FILENAME
    if not path.is_file(): raise FileNotFoundError(f"Missing {RAW_FILENAME} in {Path(raw_dir)}")
    return path

def snapshot_raw_files(raw_dir: str | Path) -> RawDataSnapshot:
    path = raw_file_path(raw_dir); return RawDataSnapshot({RAW_FILENAME: sha256(path.read_bytes()).hexdigest()})

def assert_raw_files_unchanged(raw_dir: str | Path, snapshot: RawDataSnapshot) -> None:
    if snapshot_raw_files(raw_dir).hashes != snapshot.hashes: raise RuntimeError("Raw CSV was modified during the pipeline")

def load_raw_data(raw_dir: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(raw_file_path(raw_dir)); missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing: raise ValueError(f"CSV missing required columns: {missing}")
    if len(frame.columns) != len(REQUIRED_COLUMNS): raise ValueError(f"Expected exactly {len(REQUIRED_COLUMNS)} source columns")
    return frame[REQUIRED_COLUMNS].copy()

def audit_raw_data(frame: pd.DataFrame) -> dict[str, Any]:
    return {"rows": int(len(frame)), "columns": list(frame.columns), "dtypes": {c: str(t) for c,t in frame.dtypes.items()}, "missing_values": {c:int(v) for c,v in frame.isna().sum().items()}, "duplicate_rows": int(frame.duplicated().sum()), "target": {"min":float(frame[TARGET_SOURCE].min()), "max":float(frame[TARGET_SOURCE].max()), "mean":float(frame[TARGET_SOURCE].mean())}, "categorical_cardinality": {c:int(frame[c].nunique(dropna=False)) for c in frame.select_dtypes(exclude="number").columns}}
