# Workflow ML hiện tại

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
| Test | 2018-06 .. 2018-09 | 293 |

One-hot category vocabulary, median, mean và standard deviation chỉ fit trên train. Validation/test chỉ transform bằng state đã lưu; category chưa thấy trong train thành all-zero vector.

## 5. Artifact và contract bàn giao

Lần chạy hiện tại tạo 1.267 model-ready row và 90 model feature.

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
| TV2 | Baseline, Linear Regression, Decision Tree from scratch | Nhận `X_train/y_train`, validation/test từ TV1. |
| TV3 | Metrics, experiment log, model selection, integration | Dùng metadata TV1, tích hợp và merge vào `main`. |

TV1 không triển khai model, chọn hyperparameter hoặc dùng test set để chọn model.

## 7. Kiểm chứng và AI traceability

Kiểm chứng mới nhất:

```text
python -m src.run_data_pipeline --raw-dir data/raw  → PASS
python -m pytest -q                               → 15 passed
```

Các prompt được lưu tại `ai/prompts/`. `00` là master prompt lịch sử; `01–11` là các scoped prompt đã được chạy để review, test và refine code. `ai/results/` là **bản tóm tắt evidence**, không phải raw AI transcript. Xem mapping đầy đủ tại [PROMPT_TRACEABILITY.md](PROMPT_TRACEABILITY.md).

## 8. Cách chạy

Để clone repo, tạo môi trường, tải data, chạy pipeline/test và xử lý lỗi, làm theo [RUN_GUIDE.md](../RUN_GUIDE.md). Sau mỗi thay đổi TV1 phải chạy pipeline và `pytest` trước khi bàn giao nhánh cho TV3.
