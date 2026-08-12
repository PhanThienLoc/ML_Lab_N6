# Workflow ML hoàn chỉnh

Tài liệu này mô tả **quy trình kỹ thuật và trạng thái triển khai** của project. Hướng dẫn từng lệnh cho người mới nằm tại [RUN_GUIDE.md](../RUN_GUIDE.md); các quyết định chi tiết nằm tại [DECISION_LOG.md](DECISION_LOG.md).

## 1. Bài toán đã chốt

Project dự đoán **purchase-time item demand** ở mức `product_category × month` bằng Brazilian E-Commerce Public Dataset by Olist.

- Một model row đại diện cho một category ở feature month *t*.
- `sales_current` là số order-item được đặt tại `order_purchase_timestamp` trong tháng *t*.
- `sales_next_month` là số order-item được đặt trong tháng *t + 1*.
- `sales_next_month` là biến mục tiêu dạng số/count, nên đây là bài toán **supervised regression**.

`order_status` được audit nhưng không lọc demand. Final status như `delivered` hoặc `canceled` có thể chỉ xuất hiện sau cutoff, nên dùng nó để chọn purchase event của tháng trước sẽ gây hindsight leakage.

## 2. Dữ liệu và mức tổng hợp

TV1 dùng bốn raw CSV:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`
- `product_category_name_translation.csv`

Join theo chuỗi:

```text
orders --order_id--> order_items --product_id--> products
       --product_category_name--> category_translation
```

Mọi join dùng kiểm tra cardinality. Raw CSV là bất biến, không được sửa hoặc commit.

## 3. Luồng TV1 đã triển khai

```text
Raw Olist CSV
  → audit schema/missing/duplicate/status/date range
  → chọn order có order_purchase_timestamp hợp lệ
  → validated joins
  → purchase-time order-item demand theo category × month
  → loại trailing incomplete period sau 2018-08
  → category active-window calendar
  → EDA trực quan tái lập được
  → lag / rolling / transaction / seasonal features
  → sales_next_month
  → temporal train / validation / test split
  → train-only encoding, imputation, scaling
  → processed dataset + metadata + log + handoff
```

### Active-window calendar

Lịch của mỗi category bắt đầu ở tháng purchase đầu tiên được quan sát của category đó và kéo dài đến tháng quan sát cuối toàn cục.

- Tháng thiếu **sau** lần xuất hiện đầu tiên: `sales_current = 0`.
- Tháng **trước** lần xuất hiện đầu tiên: không tạo row.

Quy tắc này giữ lag theo tháng lịch liền kề nhưng không tạo zero-demand pre-history hay làm category chỉ xuất hiện ở validation/test lọt vào train.

### Feature và chống leakage

Feature chính gồm `sales_current`, `sales_lag_1/2/3`, `rolling_sales_mean_3`, `month_sin`, `month_cos`, `year`, số order/product hiện tại, price/freight và product attributes theo mix order-item của tháng.

- Lag dùng `shift(1..3)` theo từng category.
- Target dùng `shift(-1)` đúng một tháng lịch kế tiếp.
- Rolling mean chỉ dùng *t*, *t-1*, *t-2*.
- Product/transaction attributes ở zero-demand month chỉ forward-fill từ quá khứ cùng category; leading missing value được xử lý bằng median fit trên train.
- `quarter` đã bỏ khỏi model schema; `month_sin`/`month_cos` biểu diễn tính chu kỳ December–January.
- `sales_next_month`, date keys và target month không bao giờ nằm trong `X`.

## 4. Temporal split và preprocessing

Split dựa trên `target_month`, không random row. Kết quả pipeline hiện tại:

| Split | Target month | Rows |
| --- | --- | ---: |
| Train | 2017-01 .. 2018-02 | 755 |
| Validation | 2018-03 .. 2018-05 | 219 |
| Test | 2018-06 .. 2018-08 | 219 |

One-hot category vocabulary, median, mean và standard deviation chỉ fit trên train. Validation/test chỉ transform bằng state đã lưu; category chưa thấy trong train thành all-zero vector.

## 5. Artifact và contract bàn giao

Lần chạy hiện tại tạo 1.193 model-ready row và 90 model feature. Demand usable kết thúc ở 2018-08: raw order-item demand September chỉ là 1, nên period right-censored này bị loại trước khi tạo target.

| Artifact | Mục đích |
| --- | --- |
| `data/processed/category_month_sales.csv` | Model-ready category-month data. |
| `data/processed/preprocessing_metadata.json` | Target, feature order, preprocessing state và split metadata. |
| `logs/data_quality.log` | Audit/join/split summary. |
| `reports/data_analysis.md` | Data analysis và leakage checks. |
| `reports/figures/*.png` | EDA visual tái lập được. |
| `reports/TV1_HANDOFF.md` | Contract sử dụng cho TV2/TV3. |

TV2/TV3 gọi `prepare_data("data/raw")` hoặc đọc metadata. Không được hard-code feature schema cũ; luôn dùng `metadata["feature_names"]`.

## 6. Trách nhiệm và tiến độ

| Thành viên | Phần việc | Trạng thái hiện tại |
| --- | --- | --- |
| TV1 | Data, feature, temporal split, preprocessing, handoff | Hoàn thành và đã kiểm chứng. |
| TV2 | Baseline, Linear Regression, Decision Tree from scratch | Hoàn thành; toy tests và scratch interface đã kiểm chứng. |
| TV3 | Metrics, experiment log, model selection, integration | Hoàn thành; 8-run validation batch, final test, model bundle và CLI scenario đã kiểm chứng. |

TV1 không triển khai model, chọn hyperparameter hoặc dùng test set để chọn model; TV2/TV3 dùng contract TV1 mà không thay đổi target/split.

### Tích hợp TV2/TV3 đã triển khai

```text
train + validation metrics (count prediction clipped at 0)
  → rank only by validation RMSE
  → choose LR003
  → retrain on train + validation
  → final test once
  → save model + train-only preprocessor bundle
  → predict a new CSV scenario without rebuilding the pipeline
```

Batch hiện hành có 8 run duy nhất, tất cả success. `LR003` được chọn với validation RMSE 46.0037; final test RMSE là 33.8225 trên June–August hoàn chỉnh. `logs/experiments.csv` tự reset ở đầu mỗi official run để `run_id` không bị lặp.

## 7. Kiểm chứng và AI traceability

Kiểm chứng mới nhất:

```text
python -m src.run_data_pipeline --raw-dir data/raw  → PASS
python -m pytest -q                               → 29 passed
python main.py                                    → 8 success + final test PASS
python -m src.predict --scenario-file examples/prediction_scenario.csv → PASS
```

Các prompt được lưu tại `ai/prompts/`. `00` là master prompt lịch sử; `01–16` là các scoped prompt đã được chạy để review, test và refine code TV1–TV3. `ai/results/` là **bản tóm tắt evidence**, không phải raw AI transcript. Xem mapping đầy đủ tại [PROMPT_TRACEABILITY.md](PROMPT_TRACEABILITY.md).

## 8. Cách chạy

Để clone repo, tạo môi trường, tải data, chạy pipeline/model/test/inference và xử lý lỗi, làm theo [RUN_GUIDE.md](../RUN_GUIDE.md). Sau mọi thay đổi phải chạy pipeline, pytest, experiment batch và CLI scenario trước khi nộp.
