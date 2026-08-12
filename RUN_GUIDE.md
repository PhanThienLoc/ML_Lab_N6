# Hướng dẫn chạy toàn bộ project - Windows PowerShell

Tài liệu này hướng dẫn chạy **đầy đủ TV1, TV2 và TV3**: data pipeline, test, training/experiment, final test và dự đoán scenario mới.

## 1. Chuẩn bị

Cần Git và Python 3.11 hoặc 3.12. Tại thư mục gốc project, kiểm tra:

```powershell
git --version
python --version
```

> Nếu bạn nhận project dưới dạng folder/ZIP, **không dùng lại `.venv` có sẵn**. Virtual environment phụ thuộc vào đường dẫn Python của máy tạo nó.

Tạo môi trường mới và cài dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Nếu PowerShell chặn activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Chuẩn bị Olist raw data

Tải Brazilian E-Commerce Public Dataset by Olist từ:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Đặt đúng bốn CSV vào `data\raw\`:

```text
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_products_dataset.csv
product_category_name_translation.csv
```

Kiểm tra:

```powershell
Get-ChildItem data\raw\*.csv | Select-Object Name, Length
```

Raw CSV là input bất biến: không sửa và không commit chúng lên Git.

## 3. Tạo data pipeline TV1

```powershell
python -m src.run_data_pipeline --raw-dir data/raw
```

Kết quả hiện hành mong đợi:

```text
Processed rows: 1193
Train:      2017-01..2018-02 (755 rows)
Validation: 2018-03..2018-05 (219 rows)
Test:       2018-06..2018-08 (219 rows)
Model features: 90
```

Pipeline sinh processed dataset, metadata, data-quality log, EDA PNG và TV1 handoff. Nó không sửa raw data. Olist có trailing incomplete period (September 2018 chỉ có 1 order-item), nên policy tái lập được chỉ dùng demand đến 2018-08 trước khi tạo target/split.

## 4. Chạy toàn bộ test

```powershell
python -m pytest -q
```

Kết quả hiện hành:

```text
29 passed
```

Test bao phủ pipeline temporal/leakage, preprocessing train-only, scratch models, metrics, logging/validation ranking và non-negative scenario inference.

## 5. Chạy training, experiment và final test

```powershell
python main.py
```

Hoặc:

```powershell
python -m src.run_experiments
```

Runner sẽ tự:

1. tạo batch `logs\experiments.csv` mới;
2. chạy 8 experiment (baseline, Linear Regression scratch, Decision Tree scratch);
3. chọn best run chỉ bằng **validation RMSE**;
4. train lại best config trên train + validation;
5. chạy final test; và
6. lưu model bundle tại `logs\best_model.pkl`.

Không xóa `experiments.csv` bằng tay; runner tự reset file để tám `run_id` không bị trùng.

Kết quả hiện hành:

```text
Best run: LR003
Validation RMSE: 45.9968
Final test RMSE: 33.8223
```

Xem log và final result:

```powershell
python -m src.analyze_logs
Get-Content logs\final_test.json
```

## 6. Dự đoán scenario mới

`best_model.pkl` lưu model, train-only preprocessor, source feature schema, feature order và policy count không âm. Do đó inference không rebuild pipeline, không refit preprocessing và không dùng test set làm demo.

Chạy scenario mẫu:

```powershell
python -m src.predict --scenario-file examples\prediction_scenario.csv
```

CSV scenario phải có một hoặc nhiều row với đúng các cột source feature của model. Xem `examples\prediction_scenario.csv` làm mẫu. Chỉ điền thông tin đã biết đến cuối feature month; không có `sales_next_month`, không dùng giá trị tương lai.

Mọi prediction được clip về tối thiểu 0 vì sales là order-item count.

## 7. Artifact quan trọng

| Artifact | Mục đích |
| --- | --- |
| `data/processed/category_month_sales.csv` | Dataset category-month model-ready. |
| `data/processed/preprocessing_metadata.json` | Target, feature schema, split và preprocessing train-only. |
| `logs/experiments.csv` | Batch 8 experiment dùng validation để chọn model. |
| `logs/final_test.json` | Final test của selected run. |
| `logs/best_model.pkl` | Model bundle dùng cho inference. |
| `reports/data_analysis.md` | Audit, EDA và leakage checks. |
| `reports/TV1_HANDOFF.md` | Contract TV1 cho TV2/TV3. |

## 8. Lỗi thường gặp

| Lỗi | Cách xử lý |
| --- | --- |
| `.venv` không chạy hoặc trỏ máy khác | Xóa `.venv`, tạo lại bằng `python -m venv .venv`, rồi cài requirements. |
| Thiếu raw CSV | Kiểm tra đúng bốn tên file trong `data\raw\`. |
| `best_model.pkl` không hợp lệ/thiếu | Chạy lại `python main.py` để tạo model bundle mới. |
| Scenario thiếu cột | Copy header từ `examples\prediction_scenario.csv`; không thêm target/date key. |
| Test không pass | Chạy lại pipeline, đọc traceback, không sửa raw data. |

## 9. Đóng gói và Git

Trước khi commit/push, không đưa `data/raw/`, `.venv/`, `.pytest_cache/` hoặc `__pycache__/` lên repository. `.gitignore` đã bỏ qua các file này.

Nếu cần kiểm tra Git history/đóng góp thành viên, làm việc từ repository đã `git clone`; folder export/ZIP không có thư mục `.git` nên không thể hiện lịch sử branch/commit.
