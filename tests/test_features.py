from __future__ import annotations

import math

import pandas as pd

from src.features import create_features


def _featured_series() -> pd.DataFrame:
    panel = pd.DataFrame(
        {
            "product_category": ["category_a"] * 5,
            "feature_month": pd.date_range("2020-01-01", periods=5, freq="MS"),
            "sales_current": [10, 20, 30, 40, 500],
        }
    )
    return create_features(panel)


def test_lags_and_target_use_calendar_aligned_history_only() -> None:
    featured = _featured_series()
    april = featured.loc[featured["feature_month"] == pd.Timestamp("2020-04-01")].iloc[0]
    assert april["sales_lag_1"] == 30
    assert april["sales_lag_2"] == 20
    assert april["sales_lag_3"] == 10
    assert april["rolling_sales_mean_3"] == 30
    assert april["sales_next_month"] == 500
    january = featured.iloc[0]
    assert math.isnan(january["sales_lag_1"])
    assert january["sales_next_month"] == 20


def test_rolling_mean_does_not_include_next_month_sales() -> None:
    featured = _featured_series()
    april = featured.loc[featured["feature_month"] == pd.Timestamp("2020-04-01")].iloc[0]
    assert april["rolling_sales_mean_3"] == (40 + 30 + 20) / 3
    assert april["rolling_sales_mean_3"] != (40 + 30 + 500) / 3
