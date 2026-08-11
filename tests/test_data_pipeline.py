from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.build_dataset import build_category_month_dataset
from src.data_loader import load_raw_data
from src.pipeline import prepare_data
from src.preprocessing import assert_temporal_split


def test_monthly_grid_inserts_missing_calendar_month(synthetic_raw_dir: Path) -> None:
    panel, evidence = build_category_month_dataset(load_raw_data(synthetic_raw_dir))
    category_a = panel.loc[panel["product_category"] == "category_a"].set_index("feature_month")
    assert pd.Timestamp("2018-02-01") in category_a.index
    assert category_a.loc[pd.Timestamp("2018-02-01"), "sales_current"] == 0
    assert evidence["categories"] == 2


def _prepared(synthetic_raw_dir: Path, tmp_path: Path) -> dict:
    return prepare_data(
        raw_dir=synthetic_raw_dir,
        processed_dir=tmp_path / "processed",
        report_dir=tmp_path / "reports",
        log_path=tmp_path / "logs" / "data_quality.log",
    )


def test_target_never_appears_in_model_matrix(synthetic_raw_dir: Path, tmp_path: Path) -> None:
    prepared = _prepared(synthetic_raw_dir, tmp_path)
    assert "sales_next_month" not in prepared["X_train"].columns
    assert prepared["metadata"]["target_name"] == "sales_next_month"


def test_temporal_split_is_strict_in_prepared_handoff(synthetic_raw_dir: Path, tmp_path: Path) -> None:
    prepared = _prepared(synthetic_raw_dir, tmp_path)
    assert_temporal_split(prepared["split_frames"])


def test_pipeline_never_overwrites_raw_csvs(synthetic_raw_dir: Path, tmp_path: Path) -> None:
    before = {path.name: path.read_bytes() for path in synthetic_raw_dir.glob("*.csv")}
    _prepared(synthetic_raw_dir, tmp_path)
    assert {path.name: path.read_bytes() for path in synthetic_raw_dir.glob("*.csv")} == before


def test_prepare_data_writes_reproducible_handoff_artifacts(synthetic_raw_dir: Path, tmp_path: Path) -> None:
    _prepared(synthetic_raw_dir, tmp_path)
    assert (tmp_path / "processed" / "category_month_sales.csv").is_file()
    assert (tmp_path / "processed" / "preprocessing_metadata.json").is_file()
    assert (tmp_path / "reports" / "TV1_HANDOFF.md").is_file()
    assert (tmp_path / "logs" / "data_quality.log").is_file()
