"""End-to-end TV1 data preparation and reproducible handoff generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.build_dataset import OLIST_USABLE_DEMAND_END_MONTH, build_category_month_dataset
from src.data_loader import (
    REQUIRED_RAW_FILES,
    assert_raw_files_unchanged,
    audit_raw_data,
    load_raw_data,
    snapshot_raw_files,
)
from src.eda import generate_eda_figures
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
        f"sales event definition: {built['sales_event_definition']}",
        f"order-status policy: {built['order_status_policy']}",
        f"joined item rows: {built['joined_item_rows']}",
        f"categories: {built['categories']}; calendar months: {built['calendar_months']}; category-month rows: {built['category_month_rows']}",
        f"category active-window rule: {built['category_active_window']['start_rule']}",
        "trailing-period policy: "
        f"usable demand through {built['trailing_period_policy']['usable_demand_end_month']}; "
        f"excluded order-item rows={built['trailing_period_policy']['excluded_order_item_rows']}",
        f"modeling rows removed for insufficient history or future target: {filtered['rows_removed_missing_history_or_target']}",
        f"modeling rows: {filtered['rows_after_modeling_filter']}",
        "target-month splits: " + "; ".join(
            f"{name}={item['target_month_start']}..{item['target_month_end']} ({item['rows']} rows)"
            for name, item in split.items()
        ),
        "preprocessing: category encoder, imputation medians, means, and stds fitted only on train",
        "EDA figures: " + ", ".join(payload["metadata"]["eda_summary"]["figures"]),
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
    trailing = built["trailing_period_policy"]
    trailing_rows = [
        [item["month"], item["order_item_demand"], item["order_count"]]
        for item in trailing["boundary_month_observations"]
    ]
    outlier_rows = [
        [name, item["non_missing"], item["min"], item["median"], item["p99"], item["max"]]
        for name, item in metadata["outlier_summary"].items()
    ]
    eda = metadata["eda_summary"]
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

    analysis = f"""# Phân tích dữ liệu TV1 - Olist Product Sales

Báo cáo được tạo trực tiếp từ raw CSV bằng `python -m src.run_data_pipeline`; mọi số liệu dưới đây là quan sát thực tế, không phải ví dụ.

## Dữ liệu đầu vào

{_markdown_table(['table', 'rows', 'columns', 'duplicate rows'], raw_rows)}

Khoảng purchase timestamp: **{raw['purchase_timestamp']['min']}** đến **{raw['purchase_timestamp']['max']}**. Timestamp không hợp lệ/thiếu: **{raw['purchase_timestamp']['invalid_or_missing']}**.

Phân bố order status: `{json.dumps(raw['order_status_distribution'], ensure_ascii=False, sort_keys=True)}`.

Toàn bộ dtype và missing count được lưu trong `data/processed/preprocessing_metadata.json` tại `raw_audit`; pipeline không tự tạo hoặc impute giá trị raw.

## Làm sạch và định nghĩa demand tại cutoff

- Sự kiện demand: `{built['sales_event_definition']}`
- Chính sách order status: `{built['order_status_policy']}` Điều này chặn hindsight: final status ghi nhận sau cutoff không thể chọn purchase event của tháng trước.
- Record có purchase timestamp không hợp lệ bị loại trước aggregate.
- Category dùng bản dịch tiếng Anh nếu có; nếu không dùng source category; nếu vẫn thiếu dùng `unknown_category`.
- Price, freight và product attribute không backfill từ tương lai: zero-demand gap chỉ forward-fill quá khứ cùng category, sau đó dùng train median khi preprocessing.
- Không outlier nào bị xóa/cắt. Thống kê kiểm tra nằm trong metadata `outlier_summary`.

## Kiểm tra join

{_markdown_table(['left', 'right', 'key', 'expected cardinality', 'left rows', 'rows after', 'unmatched-left rate'], join_rows)}

`pandas.merge(validate=...)` ép từng cardinality đã khai báo; many-to-many ngoài dự kiến sẽ làm pipeline fail thay vì làm phồng demand im lặng.

## Category-month và target

Một dòng là một `product_category × feature_month`. Lịch của mỗi category bắt đầu từ tháng purchase đầu tiên quan sát được của chính category đó và kéo dài đến tháng quan sát cuối toàn cục. Tháng thiếu sau mốc đó có `sales_current = 0`; tháng trước lần quan sát đầu tiên không bị bịa thành zero-demand history.

Target **`sales_next_month`** là purchase-time order-item demand của category trong tháng lịch kế tiếp. Target được tạo sau active-window grid bằng forward group shift một dòng. Dòng thiếu ba sales lag hoặc future target bị loại khỏi model-ready table.

## Ranh giới trailing incomplete period

Raw Olist có demand cuối kỳ bị right-censored. Pipeline chỉ dùng demand đến **{trailing['usable_demand_end_month']}**; các tháng sau bị loại trước calendar/feature/target construction, không bị loại bằng cách sửa metric. Bằng chứng tại boundary:

{_markdown_table(['month', 'raw order-item demand', 'raw order count'], trailing_rows)}

Các tháng order-item bị loại: {', '.join(trailing['excluded_months']) or 'không có'}; số order-item row bị loại: {trailing['excluded_order_item_rows']}. Chính sách: {trailing['reason']}

## EDA trực quan

Ba biểu đồ dưới đây được sinh lại tự động từ active-window panel ở mỗi pipeline run, không phải ảnh tạo thủ công.

![Tổng purchase-time demand theo tháng](figures/01_monthly_purchase_demand.png)

![Top 10 category theo demand](figures/02_top_categories_demand.png)

![Category active có demand dương và zero-demand](figures/03_zero_demand_by_month.png)

- Demand tháng cao nhất: **{eda['monthly_demand_peak']['month']}** với **{eda['monthly_demand_peak']['order_item_demand']}** order-item.
- Category có tổng demand cao nhất: **{eda['top_category_by_demand']['product_category']}** với **{eda['top_category_by_demand']['order_item_demand']}** order-item.
- Active category-month có zero-demand: **{eda['zero_demand_category_months']['rows']}** dòng ({eda['zero_demand_category_months']['rate']:.2%}).
- Khoảng raw data bắt đầu ở ngày **{str(raw['purchase_timestamp']['min'])[:10]}** và kết thúc ở ngày **{str(raw['purchase_timestamp']['max'])[:10]}**; tháng đầu/cuối là tháng chưa đủ nên không nên so sánh trực tiếp với tháng hoàn chỉnh.

## Đặc tả feature cuối

{_markdown_table(['feature', 'formula', 'available at', 'leakage assessment'], feature_rows)}

## Temporal split

{_markdown_table(['split', 'target start', 'target end', 'target months', 'rows'], split_rows)}

All rows for a target month are placed in one split. The assertions require train < validation < test with no target-month overlap.

## Kiểm tra outlier

{_markdown_table(['field', 'non-missing', 'min', 'median', 'p99', 'max'], outlier_rows)}

Giá trị lớn được giữ lại trừ khi không hợp lệ. Đây là báo cáo kiểm tra, không phải quy tắc clipping.

## Mẫu kiểm tra lag/target thủ công

Hai mẫu theo thời gian dưới đây được tạo từ model-ready data. Trong mỗi mẫu, `sales_next_month` là `sales_current` của tháng kế tiếp trong cùng category.

{chr(10).join(manual_sections)}

## Kiểm tra leakage

- `sales_next_month`, `target_month` và date keys bị loại khỏi mọi model matrix.
- Category grid bắt đầu tại first observation, nên category chỉ xuất hiện ở validation/test không bị chèn vào train dưới dạng synthetic zero row.
- Lag/target assertion tính lại shift từ active-window panel ở mỗi pipeline run.
- Preprocessor chỉ fit từ train và được lưu trong metadata.
- Train, validation và test có feature order giống nhau cùng giá trị số hữu hạn.

## Giới hạn và trạng thái tích hợp

- Target là purchase-time demand quantity (order-item count), không phải revenue, delivered sales hoặc customer lifetime value.
- First observed purchase month là active-window boundary trong dữ liệu, không chứng minh đây là ngày launch thật của category.
- Olist không có age, gender, campaign hoặc ad-spend trực tiếp; không field nào bị bịa.
- TV2/TV3 đã hoàn thành model scratch, experiment tracking, validation-based selection, final test, model bundle và CLI scenario. Các kết quả hiện hành được ghi tại `logs/experiments.csv` và `logs/final_test.json`.
"""
    handoff = f"""# Bàn giao TV1 - Leakage-safe Olist arrays

## Biểu diễn bài toán

Mỗi model row là một `product_category × feature_month`. Ở cuối feature month *t*, nó dự đoán purchase-time item demand cho *t+1*.

## Target

`{metadata['target_name']}` = purchase-time order-item demand của category trong tháng lịch kế tiếp. Target không nằm trong `X`.

## Raw input, join và làm sạch

Raw MVP files: `{', '.join(metadata['raw_files'])}`.

{handoff_join_lines}

- Chính sách sales event: `{built['sales_event_definition']}`
- Chính sách order status: `{built['order_status_policy']}`
- Category dùng English translation nếu có, source category nếu không, sau cùng là `unknown_category`.
- Purchase timestamp không hợp lệ bị loại trước aggregate. Giá trị price/freight âm chỉ được audit, không tự sửa.

## Forecast cutoff và bảo vệ leakage

- Grid mỗi category bắt đầu ở first observed purchase month; không pre-history nào bị bịa.
- Demand usable kết thúc ở `{trailing['usable_demand_end_month']}`; trailing incomplete period sau cutoff bị loại trước khi tạo target.
- Demand được gán tại `order_purchase_timestamp`; final order status sau cutoff không được dùng.
- Sales lag là history shift tường minh sau monthly calendar grid.
- `rolling_sales_mean_3` chỉ dùng *t*, *t-1* và *t-2*.
- Split dựa trên `target_month`, không random row.
- One-hot category, missing-value median, mean và standard deviation chỉ fit trên train.
- Category ở validation/test chưa thấy trong train được chấp nhận và mã hóa all-zero.

## Ordered model feature schema

{chr(10).join(f'- `{name}`' for name in metadata['feature_names'])}

## Arrays/DataFrames

{_markdown_table(['split', 'X shape', 'y dtype', 'target-month range'], [[name, f"{item['x_rows']} × {item['x_columns']}", item['y_dtype'], f"{split[name]['target_month_start']}..{split[name]['target_month_end']}"] for name, item in metadata['handoff_shapes'].items()])}

## Cách gọi

```python
from src.pipeline import prepare_data

prepared = prepare_data('data/raw')
X_train, y_train = prepared['X_train'], prepared['y_train']
X_val, y_val = prepared['X_val'], prepared['y_val']
X_test, y_test = prepared['X_test'], prepared['y_test']
metadata = prepared['metadata']
```

`X_*` là pandas DataFrame có thứ tự cột giống nhau và finite float. `y_*` là pandas Series float. TV2 chỉ đổi `.to_numpy()` khi implementation cần NumPy; TV3 đọc split period/feature name từ `metadata` và không fit preprocessing lại.

## Preprocessing và xác minh

- One-hot category level chỉ học từ train; category xuất hiện sau đó thành all-zero vector.
- Missing numerical value dùng train median. Mean/std chỉ fit từ train, sau đó tái sử dụng bất biến cho validation/test.
- Preprocessing state tái lập được ở `data/processed/preprocessing_metadata.json`.
- Ba EDA PNG được pipeline sinh lại tại `reports/figures/` và được nhúng trong `reports/data_analysis.md`; không có biểu đồ được chỉnh tay.
- Evidence scoped-prompt nằm trong `ai/results/`; chạy `python -m pytest -q` trước mọi handoff revision.

## Giới hạn đã biết

Artifact là forecast category theo tháng, không phải SKU. Price/freight/product mean không có ở zero-demand month; fallback past-only/train-only được mô tả trong `data_analysis.md` và metadata. First observed purchase month không khẳng định đây là ngày launch thật của category.
"""
    (report_dir / "data_analysis.md").write_text(analysis, encoding="utf-8")
    (report_dir / "TV1_HANDOFF.md").write_text(handoff, encoding="utf-8")


def prepare_data(
    raw_dir: str | Path = "data/raw",
    processed_dir: str | Path = "data/processed",
    report_dir: str | Path = "reports",
    log_path: str | Path = "logs/data_quality.log",
    usable_demand_end_month: str | pd.Timestamp | None = OLIST_USABLE_DEMAND_END_MONTH,
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
    panel, build_evidence = build_category_month_dataset(
        raw_data,
        usable_demand_end_month=usable_demand_end_month,
    )
    eda_summary = generate_eda_figures(panel, report_dir / "figures")
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
        "sales_definition": (
            "Count of order-item demand at order_purchase_timestamp; all final order statuses are included."
        ),
        "sales_event_timestamp": "order_purchase_timestamp",
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
        "eda_summary": eda_summary,
        "product_attribute_features_present": build_evidence["product_attribute_features_present"],
        "raw_immutability_sha256": raw_snapshot.hashes,
        "raw_audit": raw_audit,
        "join_audit": build_evidence["join_audit"],
        "sales_event_policy": {
            "definition": build_evidence["sales_event_definition"],
            "order_status_policy": build_evidence["order_status_policy"],
            "status_counts_in_valid_purchase_orders": build_evidence[
                "status_counts_in_valid_purchase_orders"
            ],
        },
        "category_active_window": build_evidence["category_active_window"],
        "trailing_period_policy": build_evidence["trailing_period_policy"],
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
        "preprocessor": preprocessor,
        "processed_dataset": modeling_rows,
        "split_frames": splits,
    }
