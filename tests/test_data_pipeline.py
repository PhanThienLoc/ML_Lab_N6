from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.build_dataset import build_category_month_dataset
from src.data_loader import load_raw_data
from src.features import create_features
from src.pipeline import prepare_data
from src.preprocessing import assert_temporal_split


def test_monthly_grid_inserts_missing_calendar_month(synthetic_raw_dir: Path) -> None:
    panel, evidence = build_category_month_dataset(load_raw_data(synthetic_raw_dir))
    category_a = panel.loc[panel["product_category"] == "category_a"].set_index("feature_month")
    assert pd.Timestamp("2018-02-01") in category_a.index
    assert category_a.loc[pd.Timestamp("2018-02-01"), "sales_current"] == 0
    assert evidence["categories"] == 2


def test_grid_does_not_invent_pre_history_for_later_category(synthetic_raw_dir: Path) -> None:
    panel, _ = build_category_month_dataset(load_raw_data(synthetic_raw_dir))
    category_b_months = set(
        panel.loc[panel["product_category"] == "category_b", "feature_month"]
    )
    assert pd.Timestamp("2018-03-01") in category_b_months
    assert pd.Timestamp("2018-01-01") not in category_b_months
    assert pd.Timestamp("2018-02-01") not in category_b_months


def test_later_category_lags_start_at_its_first_observed_month(synthetic_raw_dir: Path) -> None:
    panel, _ = build_category_month_dataset(load_raw_data(synthetic_raw_dir))
    features = create_features(panel)
    category_b = features.loc[features["product_category"] == "category_b"].set_index("feature_month")
    april = category_b.loc[pd.Timestamp("2018-04-01")]
    assert april["sales_lag_1"] == category_b.loc[pd.Timestamp("2018-03-01"), "sales_current"]
    assert pd.isna(april["sales_lag_2"])


def test_purchase_time_demand_does_not_filter_later_order_status(synthetic_raw_dir: Path) -> None:
    panel, evidence = build_category_month_dataset(load_raw_data(synthetic_raw_dir))
    category_a = panel.loc[panel["product_category"] == "category_a"].set_index("feature_month")
    # Five regular May items plus the later-cancelled order-item are known as
    # purchase-time demand in May.
    assert category_a.loc[pd.Timestamp("2018-05-01"), "sales_current"] == 6
    assert evidence["status_counts_in_valid_purchase_orders"]["canceled"] == 1


def test_trailing_incomplete_period_is_excluded_before_feature_construction(
    synthetic_raw_dir: Path,
) -> None:
    panel, evidence = build_category_month_dataset(
        load_raw_data(synthetic_raw_dir),
        usable_demand_end_month="2018-08-01",
    )

    assert panel["feature_month"].max() == pd.Timestamp("2018-08-01")
    policy = evidence["trailing_period_policy"]
    assert policy["usable_demand_end_month"] == "2018-08"
    assert policy["excluded_order_item_rows"] > 0
    assert "2018-09" in policy["excluded_months"]


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


def test_prepared_target_months_never_extend_beyond_usable_demand_boundary(
    synthetic_raw_dir: Path, tmp_path: Path
) -> None:
    prepared = _prepared(synthetic_raw_dir, tmp_path)
    target_months = pd.to_datetime(prepared["processed_dataset"]["target_month"])
    assert target_months.max() == pd.Timestamp("2018-08-01")
    assert prepared["metadata"]["trailing_period_policy"]["usable_demand_end_month"] == "2018-08"


def test_pipeline_never_overwrites_raw_csvs(synthetic_raw_dir: Path, tmp_path: Path) -> None:
    before = {path.name: path.read_bytes() for path in synthetic_raw_dir.glob("*.csv")}
    _prepared(synthetic_raw_dir, tmp_path)
    assert {path.name: path.read_bytes() for path in synthetic_raw_dir.glob("*.csv")} == before


def test_prepare_data_writes_reproducible_handoff_artifacts(synthetic_raw_dir: Path, tmp_path: Path) -> None:
    prepared = _prepared(synthetic_raw_dir, tmp_path)
    assert (tmp_path / "processed" / "category_month_sales.csv").is_file()
    assert (tmp_path / "processed" / "preprocessing_metadata.json").is_file()
    assert (tmp_path / "reports" / "TV1_HANDOFF.md").is_file()
    assert (tmp_path / "logs" / "data_quality.log").is_file()
    assert prepared["metadata"]["eda_summary"]["figures"] == [
        "01_monthly_purchase_demand.png",
        "02_top_categories_demand.png",
        "03_zero_demand_by_month.png",
    ]
    for filename in prepared["metadata"]["eda_summary"]["figures"]:
        figure = tmp_path / "reports" / "figures" / filename
        assert figure.is_file()
        assert figure.stat().st_size > 0
