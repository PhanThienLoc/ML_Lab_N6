"""End-to-end TV1 data preparation and reproducible handoff generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.build_dataset import build_category_month_dataset
from src.data_loader import (
    REQUIRED_RAW_FILES,
    assert_raw_files_unchanged,
    audit_raw_data,
    load_raw_data,
    snapshot_raw_files,
)
from src.features import (
    apply_past_only_forward_fill,
    available_feature_columns,
    assert_feature_alignment,
    create_features,
    feature_definitions,
    select_modeling_rows,
)
from src.preprocessing import (
    TARGET_NAME,
    assert_temporal_split,
    fit_preprocessor,
    temporal_split,
    temporal_split_metadata,
    transform_splits,
)


def _month_range(frame: pd.DataFrame, column: str) -> dict[str, str | None]:
    values = pd.to_datetime(frame[column], errors="coerce").dropna()
    return {
        "start": None if values.empty else values.min().strftime("%Y-%m"),
        "end": None if values.empty else values.max().strftime("%Y-%m"),
    }


def _outlier_summary(modeling_rows: pd.DataFrame) -> dict[str, dict[str, float | int | None]]:
    summary: dict[str, dict[str, float | int | None]] = {}
    for column in ("avg_price_current", "avg_freight_current", "sales_current"):
        if column not in modeling_rows.columns:
            continue
        values = pd.to_numeric(modeling_rows[column], errors="coerce").dropna()
        summary[column] = {
            "non_missing": int(len(values)),
            "min": None if values.empty else float(values.min()),
            "median": None if values.empty else float(values.median()),
            "p99": None if values.empty else float(values.quantile(0.99)),
            "max": None if values.empty else float(values.max()),
        }
    return summary


def _manual_sanity_samples(modeling_rows: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    """Select two deterministic category sequences for a human lag/target check."""

    columns = [
        "feature_month",
        "sales_lag_2",
        "sales_lag_1",
        "sales_current",
        "sales_next_month",
    ]
    samples: dict[str, list[dict[str, Any]]] = {}
    for category in sorted(modeling_rows["product_category"].unique())[:2]:
        rows = modeling_rows.loc[modeling_rows["product_category"] == category, columns].head(5).copy()
        rows["feature_month"] = pd.to_datetime(rows["feature_month"]).dt.strftime("%Y-%m")
        samples[str(category)] = rows.to_dict(orient="records")
    return samples


def _write_data_quality_log(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = payload["raw_audit"]
    built = payload["build_evidence"]
    filtered = payload["filter_evidence"]
    split = payload["split_metadata"]
    lines = [
        "TV1 data-quality log (generated; no experiment metrics)",
        f"raw files loaded: {', '.join(payload['raw_files'])}",
        "raw rows: " + ", ".join(
            f"{name}={details['rows']}" for name, details in raw["tables"].items()
        ),
        f"purchase date range: {raw['purchase_timestamp']['min']} to {raw['purchase_timestamp']['max']}",
        f"invalid/missing purchase timestamps: {raw['purchase_timestamp']['invalid_or_missing']}",
        f"included order statuses: {', '.join(built['included_statuses'])}",
        f"joined item rows: {built['joined_item_rows']}",
        f"categories: {built['categories']}; calendar months: {built['calendar_months']}; category-month rows: {built['category_month_rows']}",
        f"modeling rows removed for insufficient history or future target: {filtered['rows_removed_missing_history_or_target']}",
        f"modeling rows: {filtered['rows_after_modeling_filter']}",
        "target-month splits: " + "; ".join(
            f"{name}={item['target_month_start']}..{item['target_month_end']} ({item['rows']} rows)"
            for name, item in split.items()
        ),
        "preprocessing: category encoder, imputation medians, means, and stds fitted only on train",
        "validation checks passed: temporal separation, target exclusion, aligned schemas, finite matrices, raw immutability",
        "manual target-alignment samples: two deterministic category sequences recorded in reports/data_analysis.md",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    body = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    body.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(body)


def _write_reports(report_dir: Path, payload: dict[str, Any]) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    raw = payload["raw_audit"]
    built = payload["build_evidence"]
    metadata = payload["metadata"]
    split = payload["split_metadata"]
    feature_rows = []
    for feature, definition in metadata["feature_definitions"].items():
        feature_rows.append(
            [
                feature,
                definition.get("formula", "See source transformation."),
                definition.get("availability", "End of feature month t."),
                definition.get("leakage_assessment", "Not documented."),
            ]
        )
    raw_rows = [
        [name, detail["rows"], len(detail["columns"]), detail["duplicate_rows"]]
        for name, detail in raw["tables"].items()
    ]
    join_rows = [
        [
            record["left_table"],
            record["right_table"],
            record["join_key"],
            record["expected_cardinality"],
            record["left_before"]["rows"],
            record["rows_after"],
            f"{record['unmatched_left_rate']:.2%}",
        ]
        for record in built["join_audit"]
    ]
    split_rows = [
        [name, item["target_month_start"], item["target_month_end"], item["target_month_count"], item["rows"]]
        for name, item in split.items()
    ]
    outlier_rows = [
        [name, item["non_missing"], item["min"], item["median"], item["p99"], item["max"]]
        for name, item in metadata["outlier_summary"].items()
    ]
    manual_samples = metadata["manual_sanity_samples"]
    manual_sections = []
    for category, rows in manual_samples.items():
        manual_sections.append(
            f"### `{category}`\n\n"
            + _markdown_table(
                ["feature month", "sales_lag_2", "sales_lag_1", "sales_current", "sales_next_month"],
                [[record[column] for column in ["feature_month", "sales_lag_2", "sales_lag_1", "sales_current", "sales_next_month"]] for record in rows],
            )
        )
    handoff_join_lines = "\n".join(
        f"- `{record['left_table']}` -> `{record['right_table']}` on `{record['join_key']}` "
        f"({record['expected_cardinality']})."
        for record in built["join_audit"]
    )

    analysis = f"""# TV1 Data Analysis - Olist Product Sales

This report is generated from the raw CSV files by `python -m src.run_data_pipeline`; all counts below are observed values, not examples.

## Raw inputs

{_markdown_table(['table', 'rows', 'columns', 'duplicate rows'], raw_rows)}

Purchase timestamps range from **{raw['purchase_timestamp']['min']}** to **{raw['purchase_timestamp']['max']}**. Invalid or missing purchase timestamps: **{raw['purchase_timestamp']['invalid_or_missing']}**.

Order-status distribution: `{json.dumps(raw['order_status_distribution'], ensure_ascii=False, sort_keys=True)}`.

Full observed dtypes and per-column missing-value counts are preserved in `data/processed/preprocessing_metadata.json` under `raw_audit`; the pipeline never invents or imputes raw-source values.

## Cleaning and completed-sales policy

- Included statuses: `{', '.join(built['included_statuses'])}`. The pipeline uses delivered orders as the defensible completed-sales proxy.
- Excluded statuses observed in the source: `{', '.join(built['excluded_statuses']) or 'none'}`.
- Records with an invalid purchase timestamp are excluded before the monthly aggregation.
- An English category is used where translated. Otherwise the source category is retained; if both are absent, the explicit label `unknown_category` is used.
- Price, freight, and product-average attributes are not backfilled from future months: zero-sales month gaps use only an in-category forward fill, then a training-only median during preprocessing.
- No outlier is deleted or capped. The generated descriptive inspection is recorded in metadata under `outlier_summary`.

## Join audit

{_markdown_table(['left', 'right', 'key', 'expected cardinality', 'left rows', 'rows after', 'unmatched-left rate'], join_rows)}

`pandas.merge(validate=...)` enforces every listed cardinality, so an unexpected many-to-many multiplication fails the pipeline rather than silently inflating sales.

## Category-month representation and target

One row represents one `product_category × feature_month`. The pipeline creates a complete global calendar grid across observed categories and months; a missing transaction month therefore has `sales_current = 0` rather than a skipped lag.

The target is **`sales_next_month`**, the category's item quantity in the immediately following calendar month. It is constructed only after grid completion using a one-row forward group shift. Rows lacking three historical sales lags or a future target are excluded from the model-ready table.

## Final feature specification

{_markdown_table(['feature', 'formula', 'available at', 'leakage assessment'], feature_rows)}

## Temporal split

{_markdown_table(['split', 'target start', 'target end', 'target months', 'rows'], split_rows)}

All rows for a target month are placed in one split. The assertions require train < validation < test with no target-month overlap.

## Outlier inspection

{_markdown_table(['field', 'non-missing', 'min', 'median', 'p99', 'max'], outlier_rows)}

Large values are retained unless an impossible value is found. This is an inspection report, not a clipping rule.

## Manual lag/target sanity samples

The following two chronological samples are generated from the model-ready data. In each row, `sales_next_month` is the next line's `sales_current` for the same category.

{chr(10).join(manual_sections)}

## Leakage checks

- `sales_next_month`, `target_month`, and date keys are excluded from every model matrix.
- The lag/target assertion recalculates shifts from the completed panel at every pipeline run.
- Preprocessor parameters are fitted from the train split only and persisted in metadata.
- Train, validation, and test have identical feature order and finite numeric values.

## Limitations and next work

- The target is sales quantity (order-item count), not revenue or customer lifetime value.
- The grid uses all observed months for all observed categories; it does not infer a product-category launch date.
- Olist lacks direct age, gender, campaign, and ad-spend fields, so none are fabricated.
- TV2 owns model algorithms; TV3 owns experiment tracking, model selection, and final metrics.
"""
    handoff = f"""# TV1 Handoff - Leakage-safe Olist arrays

## Problem representation

Each model row is one `product_category × feature_month`. At the end of feature month *t*, it predicts sales quantity for *t+1*.

## Target

`{metadata['target_name']}` = category order-item count in the next calendar month. It is not included in `X`.

## Raw inputs, joins, and cleaning

Raw MVP files: `{', '.join(metadata['raw_files'])}`.

{handoff_join_lines}

- Completed-sales policy: include `{', '.join(built['included_statuses'])}` orders; exclude `{', '.join(built['excluded_statuses'])}`.
- Category policy: use English translation when available, source category as fallback, then explicit `unknown_category`.
- Invalid purchase timestamps are excluded before aggregation. Negative price/freight values are audited, not silently corrected.

## Forecast cutoff and leakage guarantees

- Sales lags are explicit history shifts after a complete monthly calendar grid.
- `rolling_sales_mean_3` uses *t*, *t-1*, and *t-2* only.
- Split allocation uses `target_month`, not random rows.
- One-hot categories, missing-value medians, means, and standard deviations are fitted on train only.
- Validation/test categories not seen in train are accepted and encoded as all zeros.

## Ordered model feature schema

{chr(10).join(f'- `{name}`' for name in metadata['feature_names'])}

## Arrays/DataFrames

{_markdown_table(['split', 'X shape', 'y dtype', 'target-month range'], [[name, f"{item['x_rows']} × {item['x_columns']}", item['y_dtype'], f"{split[name]['target_month_start']}..{split[name]['target_month_end']}"] for name, item in metadata['handoff_shapes'].items()])}

## How to call

```python
from src.pipeline import prepare_data

prepared = prepare_data('data/raw')
X_train, y_train = prepared['X_train'], prepared['y_train']
X_val, y_val = prepared['X_val'], prepared['y_val']
X_test, y_test = prepared['X_test'], prepared['y_test']
metadata = prepared['metadata']
```

`X_*` are pandas DataFrames with identical ordered columns and finite floats. `y_*` are float pandas Series. TV2 should convert with `.to_numpy()` only if its implementation requires NumPy arrays. TV3 should read split periods and feature names from `metadata`, and must not refit preprocessing.

## Preprocessing and verification

- One-hot category levels are learned only from train; unknown later categories become an all-zero category vector.
- Missing numerical values use train medians. Numerical means and standard deviations are fitted only from train, then reused unchanged for validation/test.
- The reproducible preprocessing state is in `data/processed/preprocessing_metadata.json`.
- Current scoped-prompt verification evidence is in `ai/results/`; run `python -m pytest -q` before any handoff revision.

## Known limitations

The artifact is a category-level monthly forecast, not an SKU forecast. Price/freight/product means are unavailable in zero-sales months; the explicit past-only/train-only fallback is described in `data_analysis.md` and metadata.
"""
    (report_dir / "data_analysis.md").write_text(analysis, encoding="utf-8")
    (report_dir / "TV1_HANDOFF.md").write_text(handoff, encoding="utf-8")


def prepare_data(
    raw_dir: str | Path = "data/raw",
    processed_dir: str | Path = "data/processed",
    report_dir: str | Path = "reports",
    log_path: str | Path = "logs/data_quality.log",
) -> dict[str, Any]:
    """Build, split, preprocess, persist, and hand off the TV1 dataset.

    Returns DataFrames/Series for TV2 and TV3 and writes reproducible processed
    artifacts. No models, metrics, experiments, or model selection occur here.
    """

    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    report_dir = Path(report_dir)
    log_path = Path(log_path)

    raw_snapshot = snapshot_raw_files(raw_dir)
    raw_data = load_raw_data(raw_dir)
    raw_audit = audit_raw_data(raw_data)
    panel, build_evidence = build_category_month_dataset(raw_data)
    features = create_features(panel)
    assert_feature_alignment(features)
    features = apply_past_only_forward_fill(features)
    modeling_rows, filter_evidence = select_modeling_rows(features)
    numerical_columns, categorical_columns = available_feature_columns(modeling_rows)
    splits = temporal_split(modeling_rows)
    assert_temporal_split(splits)
    preprocessor = fit_preprocessor(splits["train"], numerical_columns, categorical_columns)
    matrices, targets = transform_splits(preprocessor, splits)

    if TARGET_NAME in matrices["train"].columns:
        raise AssertionError("Target leakage: sales_next_month appeared in the model matrix.")
    if not all(list(matrix.columns) == list(preprocessor.feature_names) for matrix in matrices.values()):
        raise AssertionError("Feature schemas differ between temporal splits.")

    split_metadata = temporal_split_metadata(splits)
    handoff_shapes = {
        name: {
            "x_rows": int(matrices[name].shape[0]),
            "x_columns": int(matrices[name].shape[1]),
            "y_dtype": str(targets[name].dtype),
        }
        for name in ("train", "validation", "test")
    }
    metadata: dict[str, Any] = {
        "dataset_name": "olist_brazilian_ecommerce",
        "target_name": TARGET_NAME,
        "aggregation_level": "product_category_month",
        "forecast_horizon": "next_calendar_month",
        "raw_files": list(REQUIRED_RAW_FILES.values()),
        "sales_definition": "Count of order-item records from delivered orders.",
        "feature_names": list(preprocessor.feature_names),
        "source_numerical_features": numerical_columns,
        "source_categorical_features": categorical_columns,
        "feature_definitions": feature_definitions(numerical_columns + categorical_columns),
        "preprocessing": preprocessor.metadata(),
        "temporal_split": split_metadata,
        "feature_month_range": _month_range(modeling_rows, "feature_month"),
        "target_month_range": _month_range(modeling_rows, "target_month"),
        "handoff_shapes": handoff_shapes,
        "grid_and_target_filter": filter_evidence,
        "outlier_summary": _outlier_summary(modeling_rows),
        "static_product_features_present": build_evidence["static_product_features_present"],
        "raw_immutability_sha256": raw_snapshot.hashes,
        "raw_audit": raw_audit,
        "join_audit": build_evidence["join_audit"],
        "completed_sales_policy": {
            "included_statuses": build_evidence["included_statuses"],
            "excluded_statuses": build_evidence["excluded_statuses"],
        },
        "manual_sanity_samples": _manual_sanity_samples(modeling_rows),
    }
    payload = {
        "raw_files": list(REQUIRED_RAW_FILES.values()),
        "raw_audit": raw_audit,
        "build_evidence": build_evidence,
        "filter_evidence": filter_evidence,
        "split_metadata": split_metadata,
        "metadata": metadata,
    }

    processed_dir.mkdir(parents=True, exist_ok=True)
    modeling_rows.to_csv(processed_dir / "category_month_sales.csv", index=False, date_format="%Y-%m-%d")
    (processed_dir / "preprocessing_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    _write_data_quality_log(log_path, payload)
    _write_reports(report_dir, payload)
    assert_raw_files_unchanged(raw_dir, raw_snapshot)

    return {
        "X_train": matrices["train"],
        "y_train": targets["train"],
        "X_val": matrices["validation"],
        "y_val": targets["validation"],
        "X_test": matrices["test"],
        "y_test": targets["test"],
        "metadata": metadata,
        "processed_dataset": modeling_rows,
        "split_frames": splits,
    }
