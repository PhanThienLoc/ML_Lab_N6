"""Current-record dataset construction for Customer Shopping Trends."""
from __future__ import annotations
from typing import Any
import pandas as pd
from .data_loader import TARGET_SOURCE
TARGET_NAME = "product_sales_amount_usd"
FREQUENCY_MAP = {"Weekly":52,"Fortnightly":26,"Bi-Weekly":26,"Monthly":12,"Every 3 Months":4,"Quarterly":4,"Annually":1}
def build_modeling_dataset(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str,Any]]:
    frame=raw.copy()
    frame[TARGET_NAME]=pd.to_numeric(frame[TARGET_SOURCE],errors="coerce")
    frame=frame.dropna(subset=[TARGET_NAME]); frame=frame[frame[TARGET_NAME]>=0].reset_index(drop=True)
    return frame, {"rows_before":int(len(raw)),"rows_after":int(len(frame)),"target_source":TARGET_SOURCE,"target_name":TARGET_NAME,"aggregation":"current_purchase_record"}

