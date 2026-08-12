"""Reproducible visual EDA for the TV1 Olist category-month panel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd

# The pipeline runs in terminals and CI as well as locally; no GUI backend is
# required to create the report figures.
matplotlib.use("Agg")

import matplotlib.pyplot as plt


FIGURE_FILENAMES = (
    "01_monthly_purchase_demand.png",
    "02_top_categories_demand.png",
    "03_zero_demand_by_month.png",
)


def _validate_panel(panel: pd.DataFrame) -> None:
    required = {"product_category", "feature_month", "sales_current"}
    missing = required.difference(panel.columns)
    if missing:
        raise ValueError(f"EDA panel is missing required columns: {sorted(missing)}")
    if panel.empty:
        raise ValueError("Cannot create EDA figures from an empty category-month panel.")


def _save_figure(figure: plt.Figure, path: Path) -> None:
    figure.tight_layout()
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def generate_eda_figures(panel: pd.DataFrame, figures_dir: Path) -> dict[str, Any]:
    """Create three deterministic EDA PNGs and return their observed summary.

    The input is the active-window category-month panel before modeling-row
    filtering. This keeps EDA faithful to the purchase-time demand definition
    and makes zero-demand months visible.
    """

    _validate_panel(panel)
    figures_dir.mkdir(parents=True, exist_ok=True)
    data = panel.copy()
    data["feature_month"] = pd.to_datetime(data["feature_month"])
    data["sales_current"] = pd.to_numeric(data["sales_current"], errors="raise")

    monthly = data.groupby("feature_month", as_index=False)["sales_current"].sum()
    figure, axis = plt.subplots(figsize=(10.5, 4.8))
    axis.plot(monthly["feature_month"], monthly["sales_current"], color="#1f77b4", marker="o")
    axis.set_title("Total purchase-time item demand by month")
    axis.set_xlabel("Purchase month")
    axis.set_ylabel("Order-item demand")
    axis.grid(axis="y", alpha=0.25)
    figure.autofmt_xdate(rotation=45)
    _save_figure(figure, figures_dir / FIGURE_FILENAMES[0])

    top_categories = (
        data.groupby("product_category", as_index=False)["sales_current"]
        .sum()
        .sort_values(["sales_current", "product_category"], ascending=[False, True])
        .head(10)
        .sort_values("sales_current")
    )
    figure, axis = plt.subplots(figsize=(10.5, 5.6))
    axis.barh(top_categories["product_category"], top_categories["sales_current"], color="#2ca02c")
    axis.set_title("Top 10 product categories by purchase-time demand")
    axis.set_xlabel("Order-item demand across the observed period")
    axis.set_ylabel("Product category")
    axis.grid(axis="x", alpha=0.25)
    _save_figure(figure, figures_dir / FIGURE_FILENAMES[1])

    activity = (
        data.assign(is_zero_demand=data["sales_current"].eq(0))
        .groupby("feature_month", as_index=False)
        .agg(
            active_categories=("product_category", "size"),
            zero_demand_categories=("is_zero_demand", "sum"),
        )
    )
    activity["positive_demand_categories"] = (
        activity["active_categories"] - activity["zero_demand_categories"]
    )
    figure, axis = plt.subplots(figsize=(10.5, 4.8))
    axis.bar(
        activity["feature_month"],
        activity["positive_demand_categories"],
        width=22,
        label="Positive demand",
        color="#1f77b4",
    )
    axis.bar(
        activity["feature_month"],
        activity["zero_demand_categories"],
        bottom=activity["positive_demand_categories"],
        width=22,
        label="Zero demand",
        color="#ff7f0e",
    )
    axis.set_title("Active categories by month: positive versus zero demand")
    axis.set_xlabel("Purchase month")
    axis.set_ylabel("Active product categories")
    axis.legend()
    axis.grid(axis="y", alpha=0.25)
    figure.autofmt_xdate(rotation=45)
    _save_figure(figure, figures_dir / FIGURE_FILENAMES[2])

    peak_month = monthly.loc[monthly["sales_current"].idxmax()]
    top_category = top_categories.iloc[-1]
    zero_rows = int(data["sales_current"].eq(0).sum())
    return {
        "figures": list(FIGURE_FILENAMES),
        "monthly_demand_peak": {
            "month": pd.Timestamp(peak_month["feature_month"]).strftime("%Y-%m"),
            "order_item_demand": int(peak_month["sales_current"]),
        },
        "top_category_by_demand": {
            "product_category": str(top_category["product_category"]),
            "order_item_demand": int(top_category["sales_current"]),
        },
        "zero_demand_category_months": {
            "rows": zero_rows,
            "rate": float(zero_rows / len(data)),
        },
    }
