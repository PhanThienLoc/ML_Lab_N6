from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture()
def synthetic_raw_dir(tmp_path: Path) -> Path:
    """Write a small, deterministic Olist-shaped dataset for TV1 tests."""

    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    months = pd.date_range("2018-01-01", periods=10, freq="MS")
    orders = []
    items = []
    for index, month in enumerate(months):
        order_id = f"order_a_{index}"
        orders.append(
            {
                "order_id": order_id,
                "order_status": "delivered",
                "order_purchase_timestamp": (month + pd.Timedelta(days=2)).isoformat(),
            }
        )
        # Category A intentionally has no sale in February. In other months,
        # the item count changes so the target/lag assertions are meaningful.
        if index != 1:
            for unit in range(index + 1):
                items.append(
                    {
                        "order_id": order_id,
                        "order_item_id": unit + 1,
                        "product_id": "p_a",
                        "price": 10 + index,
                        "freight_value": 2 + index / 10,
                    }
                )
        if index >= 2:
            items.append(
                {
                    "order_id": order_id,
                    "order_item_id": 99,
                    "product_id": "p_b",
                    "price": 20 + index,
                    "freight_value": 3 + index / 10,
                }
            )
    # A non-delivered order verifies the completed-sales filter.
    orders.append(
        {
            "order_id": "cancelled_order",
            "order_status": "canceled",
            "order_purchase_timestamp": "2018-05-10T00:00:00",
        }
    )
    items.append(
        {
            "order_id": "cancelled_order",
            "order_item_id": 1,
            "product_id": "p_a",
            "price": 999,
            "freight_value": 99,
        }
    )
    products = pd.DataFrame(
        [
            {
                "product_id": "p_a",
                "product_category_name": "cat_a",
                "product_weight_g": 100,
                "product_length_cm": 10,
                "product_height_cm": 5,
                "product_width_cm": 8,
                "product_description_lenght": 50,
                "product_photos_qty": 2,
            },
            {
                "product_id": "p_b",
                "product_category_name": "cat_b",
                "product_weight_g": 200,
                "product_length_cm": 20,
                "product_height_cm": 6,
                "product_width_cm": 9,
                "product_description_lenght": 60,
                "product_photos_qty": 3,
            },
        ]
    )
    translation = pd.DataFrame(
        [
            {"product_category_name": "cat_a", "product_category_name_english": "category_a"},
            {"product_category_name": "cat_b", "product_category_name_english": "category_b"},
        ]
    )
    pd.DataFrame(orders).to_csv(raw_dir / "olist_orders_dataset.csv", index=False)
    pd.DataFrame(items).to_csv(raw_dir / "olist_order_items_dataset.csv", index=False)
    products.to_csv(raw_dir / "olist_products_dataset.csv", index=False)
    translation.to_csv(raw_dir / "product_category_name_translation.csv", index=False)
    return raw_dir
