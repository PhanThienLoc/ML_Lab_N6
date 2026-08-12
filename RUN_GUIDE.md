# Hướng dẫn chạy TV1 từ đầu - Windows PowerShell

Tài liệu này dành cho người mới. Nó hướng dẫn chạy phần **TV1 - Data & Feature Engineering** từ repository trống đến khi có processed dataset, report và test pass.

> Phạm vi hiện tại là TV1. TV2 sẽ cài model từ đầu; TV3 sẽ tích hợp experiment, metric và merge vào `main`.

## 1. Chuẩn bị

Cần cài:

- Git;
- Python 3.11 hoặc 3.12;
- tài khoản Kaggle để tải Olist dataset.

Mở PowerShell và kiểm tra:

```powershell
git --version
python --version
```

> Lưu ý: lệnh đúng là `git clone`, có khoảng trắng; không phải `gitclone`.

## 2. Clone repository và vào nhánh TV1

```powershell
cd D:\ML-lab
git clone https://github.com/PhanThienLoc/ML_Lab_N6.git
cd ML_Lab_N6
git fetch origin
git switch feature/data-pipeline
```

Kiểm tra nhánh:

```powershell
git status --short --branch
```

Kết quả mong đợi có dạng:

```text
## feature/data-pipeline...origin/feature/data-pipeline
```

Không push hoặc merge trực tiếp vào `main`. TV3 phụ trách tích hợp các nhánh vào `main`.

## 3. Tạo môi trường Python riêng

Tại thư mục repository (`ML_Lab_N6`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Nếu PowerShell chặn script kích hoạt, chỉ áp dụng quyền cho **cửa sổ PowerShell hiện tại**, sau đó kích hoạt lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Khi thành công, dòng lệnh thường bắt đầu bằng `(.venv)`.

## 4. Tải và đặt raw data Olist

Mở trang Kaggle:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Tải dataset, giải nén, rồi tạo thư mục raw data:

```powershell
New-Item -ItemType Directory -Force data\raw
```

Copy **đúng bốn file** sau vào `data\raw\`:

```text
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_products_dataset.csv
product_category_name_translation.csv
```

Kiểm tra trước khi chạy pipeline:

```powershell
Get-ChildItem data\raw\*.csv | Select-Object Name, Length
```

Raw CSV bị Git bỏ qua có chủ ý: không sửa chúng và không `git add` các file data lớn này.

## 5. Chạy pipeline TV1

```powershell
python -m src.run_data_pipeline --raw-dir data/raw
```

Pipeline sẽ:

1. audit 4 CSV raw;
2. join orders, order items, products và category translation;
3. tạo purchase-time item demand theo `order_purchase_timestamp`;
4. tạo category active window, lag/rolling feature và target `sales_next_month`;
5. chia train/validation/test theo `target_month`;
6. fit preprocessing chỉ trên train;
7. tạo processed data, metadata, log, report và EDA visual.

Với bản Olist được dùng trong project, output mong đợi gần như:

```text
TV1 pipeline completed.
Processed rows: 1267
Target-month splits:
  train: 2017-01..2018-02 (755 rows)
  validation: 2018-03..2018-05 (219 rows)
  test: 2018-06..2018-09 (293 rows)
Model features: 90
```

Số dòng/feature có thể khác nếu raw file khác phiên bản; lỗi pipeline hoặc cảnh báo phải được kiểm tra trước khi bàn giao.

## 6. Chạy automated tests

```powershell
python -m pytest -q
```

Kết quả hiện hành mong đợi:

```text
15 passed
```

Test kiểm tra active window của category, zero-demand month, lag/target alignment, rolling feature, target exclusion, temporal split, train-only preprocessing, unknown category, finite matrix và raw-data immutability.

## 7. Kiểm tra artifact đã sinh

```powershell
Get-ChildItem data\processed
Get-ChildItem reports\figures
Get-Content logs\data_quality.log
Get-Content reports\TV1_HANDOFF.md
```

Các file quan trọng:

| File | Ý nghĩa |
| --- | --- |
| `data/processed/category_month_sales.csv` | Dòng model-ready ở mức `product_category × month`. |
| `data/processed/preprocessing_metadata.json` | Target, feature list, split, encoder/scaler train-only và metadata. |
| `logs/data_quality.log` | Audit, join và split tóm tắt. |
| `reports/data_analysis.md` | Phân tích dữ liệu, feature và leakage checks. |
| `reports/figures/*.png` | Ba biểu đồ EDA tái lập được: demand theo tháng, top category và zero-demand. |
| `reports/TV1_HANDOFF.md` | Contract bàn giao cho TV2/TV3. |

## 8. Cách dùng dữ liệu trong code TV2/TV3

```python
from src.pipeline import prepare_data

prepared = prepare_data("data/raw")
X_train, y_train = prepared["X_train"], prepared["y_train"]
X_val, y_val = prepared["X_val"], prepared["y_val"]
X_test, y_test = prepared["X_test"], prepared["y_test"]
metadata = prepared["metadata"]
```

Luôn dùng `metadata["feature_names"]`; không hard-code schema cũ. Target `sales_next_month` là **số order-item được đặt ở tháng kế tiếp theo purchase timestamp**, không phải delivered sales/revenue.

## 9. Lỗi thường gặp

| Lỗi | Cách xử lý |
| --- | --- |
| `gitclone is not recognized` | Dùng `git clone <URL>` với khoảng trắng. |
| `python is not recognized` | Cài Python, mở PowerShell mới hoặc thử `py --version`. |
| `Activate.ps1 cannot be loaded` | Chạy `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, rồi activate lại. |
| `FileNotFoundError`/thiếu raw CSV | Kiểm tra 4 tên file và vị trí `data\raw\`. |
| `ModuleNotFoundError` | Kích hoạt `.venv`, rồi chạy lại `python -m pip install -r requirements.txt`. |
| Test không pass | Không sửa raw CSV; chạy lại pipeline, đọc traceback và kiểm tra `reports/data_analysis.md`. |

## 10. Quy trình làm việc Git cho TV1

Sau khi thay đổi code/docs và đã chạy pipeline + test thành công:

```powershell
git status --short
git add src tests ai reports data/processed logs requirements.txt README.md RUN_GUIDE.md AGENTS.md
git commit -m "feat(tv1): add leakage-safe pipeline and reproducible EDA"
git push origin feature/data-pipeline
```

Không commit `data/raw/*.csv`, `.pytest_cache/` hoặc `__pycache__/`. Sau khi push, thông báo TV3 nhánh và commit mới để họ review/tích hợp vào `main`.
