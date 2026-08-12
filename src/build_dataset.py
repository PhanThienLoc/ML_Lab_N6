"""Join Olist tables and construct the product-category monthly panel."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd


PRODUCT_ATTRIBUTE_COLUMNS = {
    "product_weight_g": "avg_product_weight",
    "product_length_cm": "avg_product_length",
    "product_height_cm": "avg_product_height",
    "product_width_cm": "avg_product_width",
    "product_description_lenght": "avg_product_description_length",
    "product_photos_qty": "avg_product_photos_qty",
}


def _key_evidence(frame: pd.DataFrame, key: str) -> dict[str, int | float]:
    null_count = int(frame[key].isna().sum())
    duplicate_key_rows = int(frame.duplicated(subset=[key], keep=False).sum())
    return {
        "rows": int(len(frame)),
        "null_keys": null_count,
        "null_key_rate": float(null_count / len(frame)) if len(frame) else 0.0,
        "duplicate_key_rows": duplicate_key_rows,
    }


def _join_record(
    left_name: str,
    right_name: str,
    key: str,
    expected_cardinality: str,
    left: pd.DataFrame,
    right: pd.DataFrame,
    merged: pd.DataFrame,
) -> dict[str, Any]:
    matching_left_rows = int(left[key].isin(right[key]).sum())
    unmatched_left_rows = int(len(left) - matching_left_rows)
    return {
        "left_table": left_name,
        "right_table": right_name,
        "join_key": key,
        "expected_cardinality": expected_cardinality,
        "left_before": _key_evidence(left, key),
        "right_before": _key_evidence(right, key),
        "rows_after": int(len(merged)),
        "unmatched_left_rows": unmatched_left_rows,
        "unmatched_left_rate": float(unmatched_left_rows / len(left)) if len(left) else 0.0,
        "row_multiplier_vs_matched_left": (
            float(len(merged) / matching_left_rows) if matching_left_rows else None
        ),
        # pandas validates the stated relationship below. This field records
        # that the merge did not create an unapproved many-to-many explosion.
        "unexpected_row_multiplication": False,
    }


def _assert_unique(frame: pd.DataFrame, key: str, table_name: str) -> None:
    duplicates = int(frame.duplicated(subset=[key]).sum())
    nulls = int(frame[key].isna().sum())
    if duplicates or nulls:
        raise ValueError(
            f"{table_name}.{key} must be a non-null unique key before its join; "
            f"duplicates={duplicates}, nulls={nulls}."
        )


def _monthly_grid(aggregated: pd.DataFrame) -> pd.DataFrame:
    """Complete each category's calendar from its first observation onward.

    A missing month *after* a category has first been observed represents zero
    demand.  Months before that first observation are deliberately absent: a
    global category-by-month Cartesian grid would invent an unobserved category
    history and could expose a future category to the training split.
    """

    if aggregated.empty:
        raise ValueError("No category-month rows remain after purchase-timestamp and join filtering.")
    global_end_month = aggregated["feature_month"].max()
    panels: list[pd.DataFrame] = []
    for category, category_rows in aggregated.groupby("product_category", sort=True):
        active_months = pd.date_range(
            start=category_rows["feature_month"].min(),
            end=global_end_month,
            freq="MS",
        )
        category_panel = category_rows.set_index("feature_month").reindex(active_months)
        category_panel.index.name = "feature_month"
        category_panel["product_category"] = category
        panels.append(category_panel.reset_index())

    panel = pd.concat(panels, ignore_index=True).sort_values(
        ["product_category", "feature_month"]
    ).reset_index(drop=True)

    zero_fill_columns = ["sales_current", "orders_current", "unique_products_current"]
    for column in zero_fill_columns:
        panel[column] = panel[column].fillna(0)
    return panel


def build_category_month_dataset(
    raw_data: Mapping[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return a complete category-by-month sales panel plus join evidence.

    `sales_current` is purchase-time quantity of order-item records in a month. For the
    supplied Olist order-items schema, one row represents an individual item;
    the aggregation intentionally does not sum revenue because the prediction
    target is sales quantity.
    """

    orders = raw_data["orders"].copy()
    order_items = raw_data["order_items"].copy()
    products = raw_data["products"].copy()
    translation = raw_data["category_translation"].copy()

    _assert_unique(orders, "order_id", "orders")
    _assert_unique(products, "product_id", "products")
    _assert_unique(translation, "product_category_name", "category_translation")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    valid_orders = orders.loc[
        orders["order_purchase_timestamp"].notna(),
        ["order_id", "order_status", "order_purchase_timestamp"],
    ].copy()
    if valid_orders.empty:
        raise ValueError("No orders with a valid purchase timestamp remain.")

    join_audit: list[dict[str, Any]] = []
    orders_items = valid_orders.merge(
        order_items,
        on="order_id",
        how="inner",
        validate="one_to_many",
    )
    join_audit.append(
        _join_record(
            "orders (valid purchase timestamp)",
            "order_items",
            "order_id",
            "one_to_many",
            valid_orders,
            order_items,
            orders_items,
        )
    )

    orders_items_products = orders_items.merge(
        products,
        on="product_id",
        how="left",
        validate="many_to_one",
    )
    join_audit.append(
        _join_record(
            "orders + order_items", "products", "product_id", "many_to_one", orders_items, products, orders_items_products
        )
    )
    final = orders_items_products.merge(
        translation,
        on="product_category_name",
        how="left",
        validate="many_to_one",
    )
    join_audit.append(
        _join_record(
            "orders + items + products",
            "category_translation",
            "product_category_name",
            "many_to_one",
            orders_items_products,
            translation,
            final,
        )
    )

    final["product_category"] = (
        final["product_category_name_english"]
        .fillna(final["product_category_name"])
        .fillna("unknown_category")
        .astype(str)
    )
    final["feature_month"] = final["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    final["price"] = pd.to_numeric(final["price"], errors="coerce")
    final["freight_value"] = pd.to_numeric(final["freight_value"], errors="coerce")

    aggregation: dict[str, tuple[str, str]] = {
        "sales_current": ("product_id", "size"),
        "orders_current": ("order_id", "nunique"),
        "unique_products_current": ("product_id", "nunique"),
        "avg_price_current": ("price", "mean"),
        "avg_freight_current": ("freight_value", "mean"),
    }
    present_static_columns = {
        source: target for source, target in PRODUCT_ATTRIBUTE_COLUMNS.items() if source in final.columns
    }
    for source, target in present_static_columns.items():
        final[source] = pd.to_numeric(final[source], errors="coerce")
        aggregation[target] = (source, "mean")

    grouped = (
        final.groupby(["product_category", "feature_month"], as_index=False)
        .agg(**aggregation)
        .sort_values(["product_category", "feature_month"])
        .reset_index(drop=True)
    )
    panel = _monthly_grid(grouped)
    panel["sales_current"] = panel["sales_current"].astype("int64")
    panel["orders_current"] = panel["orders_current"].astype("int64")
    panel["unique_products_current"] = panel["unique_products_current"].astype("int64")

    evidence: dict[str, Any] = {
        "sales_event_definition": (
            "Count order-item demand at order_purchase_timestamp; include every order status "
            "with a valid purchase timestamp."
        ),
        "order_status_policy": "Audit only; final order status is not used to select demand events.",
        "status_counts_in_valid_purchase_orders": {
            str(status): int(count)
            for status, count in valid_orders["order_status"].fillna("missing").value_counts().sort_index().items()
        },
        "valid_orders": int(len(valid_orders)),
        "joined_item_rows": int(len(final)),
        "join_audit": join_audit,
        "categories": int(panel["product_category"].nunique()),
        "calendar_months": int(panel["feature_month"].nunique()),
        "category_month_rows": int(len(panel)),
        "category_active_window": {
            "start_rule": "Each category starts at its first observed purchase month.",
            "end_month": pd.Timestamp(panel["feature_month"].max()).strftime("%Y-%m"),
        },
        "missing_product_category_after_translation": int(
            final["product_category_name_english"].isna().sum()
        ),
        "product_attribute_features_present": list(present_static_columns.values()),
        "invalid_values": {
            "negative_price": int((final["price"] < 0).sum()),
            "negative_freight": int((final["freight_value"] < 0).sum()),
            "negative_sales_rows": int((panel["sales_current"] < 0).sum()),
        },
    }
    return panel, evidence
