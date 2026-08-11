"""Leakage-safe forecasting features for the category-month Olist panel."""

from __future__ import annotations

from typing import Any

import pandas as pd


LAG_COLUMNS = ["sales_lag_1", "sales_lag_2", "sales_lag_3"]
CURRENT_TRANSACTION_COLUMNS = [
    "avg_price_current",
    "avg_freight_current",
    "avg_product_weight",
    "avg_product_length",
    "avg_product_height",
    "avg_product_width",
    "avg_product_description_length",
    "avg_product_photos_qty",
]


FEATURE_DOCUMENTATION: dict[str, dict[str, str]] = {
    "product_category": {
        "source_columns": "product_category_name_translation.csv.product_category_name_english (fallback: source category; then unknown_category)",
        "formula": "Category label, one-hot encoded from train categories only.",
        "availability": "Known before the forecast cutoff.",
        "reason": "Captures persistent demand differences by category.",
        "leakage_assessment": "No target or future sales used; unknown validation/test categories are all-zero encoded.",
    },
    "sales_current": {
        "source_columns": "order_items.product_id joined to delivered orders.order_purchase_timestamp",
        "formula": "Count of order-item rows for category in feature month t.",
        "availability": "End of month t.",
        "reason": "Most recent observed sales signal.",
        "leakage_assessment": "Uses month t only, never t+1.",
    },
    "sales_lag_1": {
        "source_columns": "sales_current",
        "formula": "Category sales in t-1 after completing the monthly grid.",
        "availability": "End of month t.",
        "reason": "Short-term demand persistence.",
        "leakage_assessment": "Explicit backward shift only.",
    },
    "sales_lag_2": {
        "source_columns": "sales_current",
        "formula": "Category sales in t-2 after completing the monthly grid.",
        "availability": "End of month t.",
        "reason": "Medium-term history.",
        "leakage_assessment": "Explicit backward shift only.",
    },
    "sales_lag_3": {
        "source_columns": "sales_current",
        "formula": "Category sales in t-3 after completing the monthly grid.",
        "availability": "End of month t.",
        "reason": "Longer recent history.",
        "leakage_assessment": "Explicit backward shift only.",
    },
    "rolling_sales_mean_3": {
        "source_columns": "sales_current, sales_lag_1, sales_lag_2",
        "formula": "mean(sales_current(t), sales(t-1), sales(t-2))",
        "availability": "End of month t.",
        "reason": "Smooths a noisy recent sales history.",
        "leakage_assessment": "Does not include sales(t+1) or any later value.",
    },
    "month": {
        "source_columns": "orders.order_purchase_timestamp",
        "formula": "Calendar month number of feature month t.",
        "availability": "End of month t.",
        "reason": "Simple seasonality signal.",
        "leakage_assessment": "Derived from the feature-month calendar only.",
    },
    "quarter": {
        "source_columns": "orders.order_purchase_timestamp",
        "formula": "Calendar quarter of feature month t.",
        "availability": "End of month t.",
        "reason": "Coarse seasonality signal.",
        "leakage_assessment": "Derived from the feature-month calendar only.",
    },
    "year": {
        "source_columns": "orders.order_purchase_timestamp",
        "formula": "Calendar year of feature month t.",
        "availability": "End of month t.",
        "reason": "Captures observed time trend.",
        "leakage_assessment": "Derived from the feature-month calendar only.",
    },
}


def _validate_monthly_panel(panel: pd.DataFrame) -> None:
    required = {"product_category", "feature_month", "sales_current"}
    missing = required.difference(panel.columns)
    if missing:
        raise ValueError(f"Monthly panel is missing required columns: {sorted(missing)}")
    if panel.duplicated(["product_category", "feature_month"]).any():
        raise ValueError("Category-month panel has duplicate keys; lags would be ambiguous.")


def create_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Create history-only features and the following-calendar-month target.

    The panel must already contain a complete monthly grid. Group shifts are
    therefore calendar-aligned rather than merely aligned to prior observed
    transactions.
    """

    _validate_monthly_panel(panel)
    features = panel.copy()
    features["feature_month"] = pd.to_datetime(features["feature_month"])
    features = features.sort_values(["product_category", "feature_month"]).reset_index(drop=True)
    grouped_sales = features.groupby("product_category", sort=False)["sales_current"]
    features["sales_lag_1"] = grouped_sales.shift(1)
    features["sales_lag_2"] = grouped_sales.shift(2)
    features["sales_lag_3"] = grouped_sales.shift(3)
    features["rolling_sales_mean_3"] = features[
        ["sales_current", "sales_lag_1", "sales_lag_2"]
    ].mean(axis=1, skipna=False)
    features["sales_next_month"] = grouped_sales.shift(-1)
    features["target_month"] = features["feature_month"] + pd.offsets.MonthBegin(1)
    features["month"] = features["feature_month"].dt.month.astype("int64")
    features["quarter"] = features["feature_month"].dt.quarter.astype("int64")
    features["year"] = features["feature_month"].dt.year.astype("int64")
    return features


def assert_feature_alignment(features: pd.DataFrame) -> None:
    """Prove that lags and target are attached to adjacent calendar months."""

    required = {
        "product_category",
        "feature_month",
        "sales_current",
        *LAG_COLUMNS,
        "rolling_sales_mean_3",
        "sales_next_month",
        "target_month",
    }
    missing = required.difference(features.columns)
    if missing:
        raise ValueError(f"Cannot validate alignment; missing columns: {sorted(missing)}")
    for category, group in features.groupby("product_category", sort=False):
        ordered = group.sort_values("feature_month").reset_index(drop=True)
        months = pd.to_datetime(ordered["feature_month"])
        if not months.diff().dropna().eq(pd.Timedelta(days=0)).all():
            # Month offsets have variable day lengths, so validate the period
            # sequence rather than a fixed day count.
            periods = months.dt.to_period("M")
            expected_periods = pd.period_range(periods.min(), periods.max(), freq="M")
            if not periods.equals(pd.Series(expected_periods)):
                raise AssertionError(f"{category!r} does not have a complete monthly grid.")
        expected_lag_1 = ordered["sales_current"].shift(1)
        expected_lag_2 = ordered["sales_current"].shift(2)
        expected_lag_3 = ordered["sales_current"].shift(3)
        expected_target = ordered["sales_current"].shift(-1)
        expected_rolling = pd.concat(
            [ordered["sales_current"], expected_lag_1, expected_lag_2], axis=1
        ).mean(axis=1, skipna=False)
        for name, actual, expected in (
            ("sales_lag_1", ordered["sales_lag_1"], expected_lag_1),
            ("sales_lag_2", ordered["sales_lag_2"], expected_lag_2),
            ("sales_lag_3", ordered["sales_lag_3"], expected_lag_3),
            ("sales_next_month", ordered["sales_next_month"], expected_target),
            ("rolling_sales_mean_3", ordered["rolling_sales_mean_3"], expected_rolling),
        ):
            try:
                pd.testing.assert_series_equal(actual, expected, check_dtype=False, check_names=False)
            except AssertionError as error:
                raise AssertionError(f"{category!r} has misaligned {name}.") from error
        expected_target_month = months + pd.offsets.MonthBegin(1)
        try:
            pd.testing.assert_series_equal(
                pd.to_datetime(ordered["target_month"]), expected_target_month, check_names=False
            )
        except AssertionError as error:
            raise AssertionError(f"{category!r} has misaligned target_month.") from error


def apply_past_only_forward_fill(features: pd.DataFrame) -> pd.DataFrame:
    """Fill transaction attributes from each category's past only.

    Months with zero sales have no price/freight/product averages. Forward
    filling within a chronologically sorted category uses only values already
    known by the feature-month cutoff. Leading gaps deliberately remain NaN and
    are later replaced by a statistic fitted on the training split only.
    """

    result = features.copy().sort_values(["product_category", "feature_month"])
    candidates = [column for column in CURRENT_TRANSACTION_COLUMNS if column in result.columns]
    if candidates:
        result[candidates] = result.groupby("product_category", sort=False)[candidates].ffill()
    return result.reset_index(drop=True)


def select_modeling_rows(features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Discard rows whose target or required three-month sales history is unavailable."""

    required_history = LAG_COLUMNS + ["rolling_sales_mean_3"]
    missing = set(required_history + ["sales_next_month", "target_month"]).difference(features.columns)
    if missing:
        raise ValueError(f"Feature table is missing expected modeling columns: {sorted(missing)}")
    before = len(features)
    valid = features.dropna(subset=required_history + ["sales_next_month"]).copy()
    valid["sales_next_month"] = valid["sales_next_month"].astype(float)
    valid = valid.sort_values(["target_month", "product_category", "feature_month"]).reset_index(drop=True)
    return valid, {
        "rows_before_modeling_filter": int(before),
        "rows_removed_missing_history_or_target": int(before - len(valid)),
        "rows_after_modeling_filter": int(len(valid)),
    }


def available_feature_columns(features: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Return ordered numerical and categorical model inputs, excluding target/date keys."""

    numerical_preference = [
        "sales_current",
        "sales_lag_1",
        "sales_lag_2",
        "sales_lag_3",
        "rolling_sales_mean_3",
        "month",
        "quarter",
        "year",
        "orders_current",
        "unique_products_current",
        *CURRENT_TRANSACTION_COLUMNS,
    ]
    numerical = [column for column in numerical_preference if column in features.columns]
    categorical = ["product_category"] if "product_category" in features.columns else []
    if not numerical or not categorical:
        raise ValueError("Feature table must contain numerical features and product_category.")
    return numerical, categorical


def feature_definitions(feature_names: list[str]) -> dict[str, dict[str, str]]:
    """Return documentation for final features, including dynamic attributes."""

    definitions = dict(FEATURE_DOCUMENTATION)
    definitions.update(
        {
            "orders_current": {
                "source_columns": "orders.order_id joined to order_items",
                "formula": "Number of distinct delivered order_id values for the category in month t.",
                "availability": "End of month t.",
                "reason": "Separates order frequency from quantity of items.",
                "leakage_assessment": "Uses delivered orders in month t only.",
            },
            "unique_products_current": {
                "source_columns": "order_items.product_id",
                "formula": "Number of distinct product_id values for the category in month t.",
                "availability": "End of month t.",
                "reason": "Describes current assortment breadth.",
                "leakage_assessment": "Uses month t only.",
            },
            "avg_price_current": {
                "source_columns": "order_items.price",
                "formula": "Mean item price for category sales in month t.",
                "availability": "End of month t; zero-sales gaps use past-only forward fill then train median.",
                "reason": "Captures the current observed price mix.",
                "leakage_assessment": "Neither aggregation nor fill looks into future months.",
            },
            "avg_freight_current": {
                "source_columns": "order_items.freight_value",
                "formula": "Mean freight value for category sales in month t.",
                "availability": "End of month t; zero-sales gaps use past-only forward fill then train median.",
                "reason": "Captures current shipping-cost mix.",
                "leakage_assessment": "Neither aggregation nor fill looks into future months.",
            },
        }
    )
    static_sources = {
        "avg_product_weight": "product_weight_g",
        "avg_product_length": "product_length_cm",
        "avg_product_height": "product_height_cm",
        "avg_product_width": "product_width_cm",
        "avg_product_description_length": "product_description_lenght",
        "avg_product_photos_qty": "product_photos_qty",
    }
    for feature in CURRENT_TRANSACTION_COLUMNS[2:]:
        source = static_sources[feature]
        definitions[feature] = {
            "source_columns": f"olist_products_dataset.csv.{source} joined through sold product_id",
            "formula": f"Mean {source} of products sold in the category in month t.",
            "availability": "End of month t; zero-sales gaps use past-only forward fill then train median.",
            "reason": "Describes the observed physical/content mix of the category basket.",
            "leakage_assessment": "Neither aggregation nor fill looks into future months.",
        }
    return {name: definitions.get(name, {}) for name in feature_names}
