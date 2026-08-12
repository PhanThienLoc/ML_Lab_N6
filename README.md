# Dự đoán doanh số sản phẩm - Olist

## 1. Giới thiệu bài toán

Project thực hiện bài toán **dự đoán doanh số sản phẩm tháng kế tiếp** bằng bộ dữ liệu Brazilian E-Commerce Public Dataset by Olist.

Mức dữ liệu được sử dụng cho mô hình là:

```text
product_category × month
```

Với mỗi danh mục sản phẩm tại tháng `t`, mô hình sử dụng những thông tin đã biết đến cuối tháng `t` để dự đoán số lượng order-item được đặt trong tháng `t + 1`.

Biến mục tiêu:

```text
sales_next_month
```

Đây là biến số nên bài toán thuộc nhóm **Supervised Regression**.

Mục tiêu của project là xây dựng một pipeline hoàn chỉnh gồm:

```text
Raw Data
   ↓
Data Preparation
   ↓
Feature Engineering
   ↓
Temporal Split
   ↓
Preprocessing
   ↓
Model Training
   ↓
Model Selection
   ↓
Model Evaluation
   ↓
Prediction Demo
```

---

## 2. Bộ dữ liệu

Dataset sử dụng:

**Brazilian E-Commerce Public Dataset by Olist**

Nguồn:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Project sử dụng 4 file dữ liệu chính:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`
- `product_category_name_translation.csv`

Các file này được đặt trong:

```text
data/raw/
```

Luồng join dữ liệu:

```text
olist_orders_dataset.csv
        |
        | order_id
        v
olist_order_items_dataset.csv
        |
        | product_id
        v
olist_products_dataset.csv
        |
        | product_category_name
        v
product_category_name_translation.csv
```

Project sử dụng `order_purchase_timestamp` để xác định nhu cầu mua hàng theo thời điểm đặt hàng.

Các sản phẩm không xác định được category được biểu diễn bằng:

```text
unknown_category
```

Các bảng Olist khác như:

- customers
- payments
- reviews
- sellers
- geolocation

không bắt buộc trong phiên bản hiện tại của pipeline.

---

## 3. Định nghĩa dữ liệu dự đoán

Một dòng dữ liệu model-ready tương ứng với:

```text
product_category × month
```

Ví dụ:

```text
Category A tại tháng t
        ↓
sales_current
sales_lag_1
sales_lag_2
sales_lag_3
rolling features
price features
freight features
seasonal features
        ↓
sales_next_month tại tháng t + 1
```

Target chính thức:

```text
sales_next_month
```

Target là số lượng order-item của danh mục sản phẩm trong tháng kế tiếp.

Feature tại tháng `t` chỉ sử dụng thông tin có sẵn tại tháng `t` hoặc trước đó.

Không sử dụng thông tin tương lai để tạo feature.

---

## 4. Phân công thành viên

### Thành viên 1 - Data & Feature Engineering

Phụ trách:

- Nạp dữ liệu Olist.
- Audit dữ liệu.
- Kiểm tra missing values và duplicate.
- Join các bảng dữ liệu.
- Làm sạch dữ liệu.
- Tổng hợp theo `product_category × month`.
- Tạo target `sales_next_month`.
- Tạo lag và rolling features.
- Tạo seasonal features.
- Temporal split.
- Preprocessing chỉ fit trên train.
- Sinh EDA.
- Sinh processed dataset và metadata.

### Thành viên 2 - Machine Learning Algorithms

Phụ trách:

- Mean Baseline.
- Linear Regression from Scratch.
- Decision Tree Regression from Scratch.
- Giao diện `fit()` và `predict()`.
- Kiểm thử các thuật toán trên dữ liệu nhỏ.

Các thuật toán ML chính được tự cài đặt và không sử dụng estimator dựng sẵn từ scikit-learn.

### Thành viên 3 - Experiment, Evaluation & Integration

Phụ trách:

- Regression metrics.
- Experiment runner.
- Experiment logger.
- Hyperparameter experiments.
- Phân tích experiment log.
- Chọn best run.
- Final test evaluation.
- Tích hợp pipeline hoàn chỉnh.
- Lưu best model.
- Prediction demo.

---

## 5. Cấu trúc project

```text
ML_Lab_N6-feature-data-pipeline/
│
├── main.py
├── README.md
├── requirements.txt
├── AGENTS.md
├── LICENSE
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── build_dataset.py
│   ├── eda.py
│   ├── features.py
│   ├── preprocessing.py
│   ├── pipeline.py
│   ├── run_data_pipeline.py
│   │
│   ├── metrics.py
│   ├── logger.py
│   ├── experiment.py
│   ├── analyze_logs.py
│   ├── run_experiments.py
│   ├── predict.py
│   │
│   └── models/
│       ├── __init__.py
│       ├── baseline.py
│       ├── linear_regression.py
│       └── decision_tree.py
│
├── tests/
│   ├── test_data_pipeline.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_preprocessing.py
│
├── logs/
│   ├── data_quality.log
│   ├── experiments.csv
│   ├── final_test.json
│   └── best_model.pkl
│
├── reports/
│   ├── data_analysis.md
│   └── figures/
│
└── ai/
    ├── AI_RULES.md
    ├── WORKFLOW.md
    ├── DECISION_LOG.md
    ├── prompts/
    └── results/
```

---

## 6. Data Preparation

Pipeline dữ liệu thực hiện các bước:

1. Kiểm tra các file CSV đầu vào.
2. Kiểm tra schema và kiểu dữ liệu.
3. Kiểm tra missing values.
4. Kiểm tra duplicate.
5. Join các bảng Olist.
6. Chuẩn hóa tên category.
7. Tổng hợp sales theo category và tháng.
8. Tạo đầy đủ calendar trong active window của từng category.
9. Các tháng không có giao dịch trong active window được biểu diễn bằng sales = 0.
10. Loại trailing incomplete period sau 2018-08 trước khi tạo target.
11. Tạo target `sales_next_month`.
12. Temporal split.
13. Fit preprocessing trên training set.
14. Transform validation và test bằng preprocessing đã học từ train.
15. Sinh processed dataset, metadata, log và EDA.

Raw CSV được xem là dữ liệu bất biến và không bị chỉnh sửa bởi pipeline.

### Ghi chú về outlier

Project hiện không áp dụng quy tắc loại bỏ outlier toàn cục.

Các giá trị lớn của sales, price hoặc freight có thể là dữ liệu giao dịch thực tế, vì vậy không tự động loại bỏ chỉ vì chúng có giá trị cao.

Việc phân tích hoặc xử lý outlier chi tiết hơn được xem là một hướng cải tiến trong tương lai.

---

## 7. Feature Engineering

Các feature chính gồm:

```text
sales_current
sales_lag_1
sales_lag_2
sales_lag_3
rolling_sales_mean_3
month_sin
month_cos
year
order count
product count
average price
average freight
product attributes
product category encoding
```

### Historical Sales Features

Các feature như:

```text
sales_lag_1
sales_lag_2
sales_lag_3
rolling_sales_mean_3
```

được tạo từ lịch sử sales.

Không sử dụng `sales_next_month` để tạo feature.

### Seasonal Features

Seasonality được biểu diễn bằng:

```text
month_sin
month_cos
```

Cách biểu diễn dạng chu kỳ giúp tháng 12 và tháng 1 được xem là gần nhau về mặt mùa vụ.

### Category Encoding

Product category được chuyển sang dạng số bằng encoding.

Các mapping và preprocessing statistics chỉ được fit bằng training data.

---

## 8. Kết quả Data Pipeline

Pipeline hiện tại tạo ra:

```text
Processed rows: 1193
Model features: 90
```

Temporal split:

```text
Train:
2017-01..2018-02
755 rows

Validation:
2018-03..2018-05
219 rows

Test:
2018-06..2018-08
219 rows
```

Tổng cộng:

```text
755 + 219 + 219 = 1193 rows
```

---

## 9. Temporal Split

Project sử dụng **temporal split** thay vì random split.

Thứ tự thời gian:

```text
Train
2017-01 → 2018-02
        ↓
Validation
2018-03 → 2018-05
        ↓
Test
2018-06 → 2018-08
```

Lý do:

Bài toán dự đoán sales tháng kế tiếp có yếu tố thời gian.

Nếu random split, dữ liệu tương lai có thể xuất hiện trong training set và gây data leakage.

### Trailing incomplete period

Raw Olist bị right-censored ở cuối kỳ: demand order-item là 7.078 (2018-06), 7.092 (2018-07), 7.248 (2018-08), nhưng chỉ **1** ở 2018-09. Pipeline vì vậy chốt usable demand đến **2018-08** và loại các period sau cutoff *trước* aggregate/calendar/target construction. Đây là data-boundary policy tái lập được, không phải bỏ thủ công metric xấu.

Quy trình chính xác:

```text
Train
   ↓
Fit model
   ↓
Validation
   ↓
Tune hyperparameters
   ↓
Choose best configuration
   ↓
Train + Validation
   ↓
Final Test
```

Test set không được dùng để chọn model hoặc hyperparameter.

---

## 10. Preprocessing

Preprocessing chỉ được fit trên training set.

Pipeline xử lý:

- Missing values.
- Unknown categories.
- Categorical encoding.
- Numeric scaling.
- Feature schema alignment.
- Finite value checking.

Validation và test chỉ sử dụng transformation đã được fit từ training data.

Điều này giúp hạn chế data leakage.

---

## 11. Các mô hình Machine Learning

Project sử dụng ba loại model.

### 11.1 Mean Baseline

Mean Baseline dự đoán giá trị trung bình của target trên training set.

Mục đích:

- Tạo baseline.
- Kiểm tra các model phức tạp hơn có thực sự cải thiện kết quả hay không.

---

### 11.2 Linear Regression From Scratch

Linear Regression được tự cài đặt bằng NumPy.

Công thức tổng quát:

```text
y_pred = Xw + b
```

Loss sử dụng trong quá trình optimization:

```text
MSE = mean((y - y_pred)^2)
```

Phương pháp tối ưu:

```text
Gradient Descent
```

Hyperparameter chính:

- `learning_rate`
- `epochs`
- `tol`

---

### 11.3 Decision Tree Regression From Scratch

Decision Tree Regression cũng được tự cài đặt.

Model tìm các split giúp giảm sai số dự đoán.

Hyperparameter chính:

- `max_depth`
- `min_samples_split`
- `min_impurity_decrease`

---

## 12. Ràng buộc thư viện

Project không sử dụng các estimator ML dựng sẵn từ:

- scikit-learn
- XGBoost
- LightGBM
- CatBoost
- statsmodels
- Prophet
- TensorFlow
- PyTorch

NumPy được sử dụng để tính toán vector và ma trận.

Pandas được sử dụng để xử lý dữ liệu.

Matplotlib được sử dụng để sinh biểu đồ EDA.

---

## 13. Evaluation Metrics

Project sử dụng bốn metric.

### Mean Absolute Error - MAE

```text
MAE = mean(|y - y_pred|)
```

MAE cho biết sai số tuyệt đối trung bình.

### Mean Squared Error - MSE

```text
MSE = mean((y - y_pred)^2)
```

MSE phạt mạnh hơn đối với các dự đoán sai lệch lớn.

### Root Mean Squared Error - RMSE

```text
RMSE = sqrt(MSE)
```

RMSE có cùng đơn vị với target.

### R-squared - R²

```text
R² = 1 - SS_res / SS_tot
```

R² được sử dụng như metric bổ sung.

Các metric chính theo yêu cầu bài Lab là:

```text
MAE
MSE
RMSE
```

Vì `sales_next_month` là order-item count không âm, validation, final test và CLI inference đều áp dụng cùng policy:

```text
predicted_sales = max(0, raw_model_prediction)
```

Policy này ngăn Linear Regression trả về doanh số âm. Model bundle lưu policy cùng model, preprocessor train-only và thứ tự feature.

---

## 14. Experiment Tracking

Kết quả các experiment được lưu tại:

```text
logs/experiments.csv
```

Mỗi experiment lưu các thông tin như:

- run ID
- timestamp
- dataset
- aggregation
- target
- feature version
- split method
- train period
- validation period
- model
- hyperparameters
- training metrics
- validation metrics
- status
- notes

Test metrics không được sử dụng để xếp hạng các model trong quá trình tuning.

Mỗi lần chạy `python main.py` hoặc `python -m src.run_experiments` tự tạo một batch log mới. Điều này giữ tám `run_id` chính thức là duy nhất, không append lặp kết quả cũ.

---

## 15. Các experiment đã chạy

Project chạy 8 experiment chính thức:

```text
BASE001
LR001
LR002
LR003
LR004
TREE001
TREE002
TREE003
```

Kết quả:

| Run | Model | Validation MAE | Validation RMSE | Validation R² |
|---|---|---:|---:|---:|
| BASE001 | MeanBaseline | 120.6339 | 187.5014 | -0.0162 |
| LR001 | LinearRegressionScratch | 24.4940 | 46.8873 | 0.9365 |
| LR002 | LinearRegressionScratch | 23.9140 | 46.4505 | 0.9376 |
| LR003 | LinearRegressionScratch | **22.6835** | **46.0037** | **0.9388** |
| LR004 | LinearRegressionScratch | 22.7687 | 46.1780 | 0.9384 |
| TREE001 | DecisionTreeRegressorScratch | 38.1281 | 73.4563 | 0.8440 |
| TREE002 | DecisionTreeRegressorScratch | 35.5093 | 77.9657 | 0.8243 |
| TREE003 | DecisionTreeRegressorScratch | 32.4327 | 72.1061 | 0.8497 |

Tất cả experiment:

```text
8 / 8 success
```

---

## 16. Chọn Best Model

Tiêu chí chính để chọn model là:

```text
Validation RMSE
```

RMSE càng thấp càng tốt.

Kết quả:

```text
Best Run: LR003
Best Model: LinearRegressionScratch

Validation MAE: 22.6835
Validation RMSE: 46.0037
Validation R²: 0.9388
```

LR003 đồng thời có Validation MAE và RMSE thấp nhất trong batch hiện hành:

```text
LR003 MAE = 22.6835
LR004 MAE = 22.7687
```

LR003 có Validation RMSE thấp hơn LR004:

```text
LR003 RMSE = 46.0037
LR004 RMSE = 46.1780
```

Do tiêu chí chọn model chính thức là Validation RMSE nên LR003 được chọn.

Test set không được sử dụng để đưa ra quyết định này.

---

## 17. Final Model Training

Sau khi LR003 được chọn bằng validation set:

```text
Train + Validation
        ↓
Final LinearRegressionScratch
```

Model cuối được train lại bằng dữ liệu:

```text
Train + Validation
```

Sau đó model mới được đánh giá trên test set.

---

## 18. Final Test Evaluation

Test set chỉ được đánh giá sau khi best configuration đã được chọn.

Kết quả:

```text
Selected Run: LR003
Model: LinearRegressionScratch

Test MAE: 18.6781
Test MSE: 1143.9581
Test RMSE: 33.8225
Test R²: 0.9608
```

Kết quả được lưu tại:

```text
logs/final_test.json
```

Model cuối được lưu tại:

```text
logs/best_model.pkl
```

Final test RMSE thấp hơn validation RMSE trên ba tháng June–August hoàn chỉnh. Điều này không thay thế validation-based selection và không chứng minh mô hình sẽ ổn định ở mọi future period; test window chỉ có ba tháng, nên kết quả cần được diễn giải cùng giới hạn time window này.

---

## 19. Automated Tests

Chạy test bằng:

```powershell
python -m pytest -q
```

Kết quả đã xác minh:

```text
29 passed
```

Các test bao gồm:

- Missing calendar month.
- Category active window.
- Calendar-aligned lag.
- Target alignment.
- Target không xuất hiện trong model matrix.
- Temporal split.
- Raw CSV immutability.
- Reproducible artifacts.
- Rolling mean không sử dụng future sales.
- Cyclical month features.
- Linear Regression toy line.
- Gradient Descent loss trend.
- Decision Tree simple split.
- Prediction shape.
- Constant target.
- Train-only preprocessing.
- Unknown category.
- Aligned feature schema.
- Finite model matrix.
- Regression metrics trên giá trị đã biết và constant-target guard.
- Fresh experiment batch và validation-only ranking.
- Scenario inference dùng saved preprocessor và output count không âm.
- Trailing incomplete period bị loại trước khi calendar/target được tạo.
- Experiment period đọc boundary thật từ metadata temporal split.

Kết quả hiện tại:

```text
29 / 29 tests passed
```

---

## 20. Prediction / Deployment Demo

Model tốt nhất được lưu tại:

```text
logs/best_model.pkl
```

Prediction demo được triển khai bằng command line.

Chạy:

```powershell
python -m src.predict --scenario-file examples\prediction_scenario.csv
```

Kết quả đã xác minh:

```text
============================================================
PRODUCT SALES PREDICTION DEMO
============================================================
Model: LinearRegressionScratch
Scenarios: 1
Policy: sales predictions are clipped to a minimum of 0.
Scenario 1: predicted next-month sales = 53.0523
============================================================
```

`best_model.pkl` là model bundle gồm model, train-only preprocessor, feature order và policy prediction. CLI không chạy lại pipeline, không đọc raw data và không fit preprocessing.

File CSV phải chứa các source feature được ghi trong metadata. File [examples/prediction_scenario.csv](examples/prediction_scenario.csv) là schema mẫu; mỗi value phải chỉ dùng thông tin có ở cuối feature month, không bao gồm target hoặc dữ liệu tương lai.

Có thể dự đoán nhiều scenario bằng cách thêm nhiều dòng hợp lệ vào CSV:

```powershell
python -m src.predict --scenario-file path\to\scenarios.csv
```

Đây là **CLI prediction demo**, không phải production web deployment.

---

## 21. Cách chạy toàn bộ project

Chạy tất cả các lệnh tại thư mục gốc của project.

### Bước 0 - Cài dependencies

```powershell
python -m pip install -r requirements.txt
```

---

### Bước 1 + 2 - Data Preparation và Feature Engineering

```powershell
python -m src.run_data_pipeline --raw-dir data/raw
```

Kết quả mong đợi:

```text
TV1 pipeline completed.
Processed rows: 1193
Target-month splits:
  train: 2017-01..2018-02 (755 rows)
  validation: 2018-03..2018-05 (219 rows)
  test: 2018-06..2018-08 (219 rows)
Model features: 90
```

---

### Kiểm tra toàn bộ code

```powershell
python -m pytest -q
```

Kết quả hiện tại:

```text
29 passed
```

---

> Không cần xóa `logs\experiments.csv` thủ công. Runner tự tạo batch log mới để tám `run_id` chính thức không bị trùng.

---

### Bước 3 + 4 + 5 - Model Selection, Training và Evaluation

```powershell
python -m src.run_experiments
```

Hoặc:

```powershell
python main.py
```

Flow:

```text
Load Data
   ↓
Mean Baseline
   ↓
Linear Regression Experiments
   ↓
Decision Tree Experiments
   ↓
Validation Evaluation
   ↓
Select Best Run
   ↓
Train Final Model
   ↓
Final Test Evaluation
   ↓
Save Best Model
```

---

### Xem Best Model

```powershell
python -m src.analyze_logs
```

Best model hiện tại:

```text
Best Run: LR003
Best Model: LinearRegressionScratch
Validation RMSE: 46.0037
```

---

### Xem Final Test

```powershell
Get-Content logs\final_test.json
```

---

### Bước 6 - Prediction Demo

```powershell
python -m src.predict --scenario-file examples\prediction_scenario.csv
```

---

## 22. Lệnh chạy toàn bộ bài từ đầu đến cuối

```powershell
python -m src.run_data_pipeline --raw-dir data/raw

python -m pytest -q

python -m src.run_experiments

python -m src.analyze_logs

Get-Content logs\final_test.json

python -m src.predict --scenario-file examples\prediction_scenario.csv
```

---

## 23. Đối chiếu với yêu cầu bài Lab

### Bước 1 - Data Preparation

Đã thực hiện:

- Nạp dữ liệu.
- Audit dữ liệu.
- Xử lý missing values.
- Xử lý categorical variables.
- Tổng hợp dữ liệu.
- Temporal split.
- Preprocessing.

### Bước 2 - Feature Engineering

Đã thực hiện:

- Current sales.
- Lag features.
- Rolling features.
- Seasonal features.
- Price features.
- Freight features.
- Product features.
- Category encoding.

### Bước 3 - Model Selection

Đã thực hiện:

- Mean Baseline.
- Linear Regression.
- Decision Tree Regression.
- Nhiều hyperparameter configuration.
- Validation-based model selection.

### Bước 4 - Model Training

Các model được train trên training set.

Best configuration sau đó được train lại bằng:

```text
Train + Validation
```

### Bước 5 - Model Evaluation

Đã sử dụng:

```text
MAE
MSE
RMSE
R²
```

Final test chỉ được chạy sau khi best model đã được chọn.

### Bước 6 - Model Deployment

Project cung cấp CLI prediction demo:

```powershell
python -m src.predict --scenario-file examples\prediction_scenario.csv
```

Demo nhận CSV scenario mới, transform bằng preprocessor đã lưu trong model bundle và trả về sales không âm. Nó không refit preprocessing hoặc dùng test set làm input demo.

---

## 24. Artifact được sinh tự động

Các artifact chính:

```text
data/processed/category_month_sales.csv
data/processed/preprocessing_metadata.json
```

Logs:

```text
logs/data_quality.log
logs/experiments.csv
logs/final_test.json
logs/best_model.pkl
```

Reports:

```text
reports/data_analysis.md
reports/figures/
```

---

## 25. AI Workflow

AI được sử dụng như một công cụ hỗ trợ trong quá trình phát triển project.

Các công việc AI hỗ trợ:

- Phân tích yêu cầu.
- Phân tích dataset.
- Thiết kế pipeline.
- Thiết kế thuật toán.
- Giải thích công thức.
- Tạo pseudocode.
- Hỗ trợ debug.
- Thiết kế experiment.
- Review code.
- Hỗ trợ viết tài liệu.

Các nguyên tắc chính:

1. Không sử dụng ML estimator dựng sẵn cho thuật toán chính.
2. Không thay đổi target tùy ý.
3. Không preprocessing toàn bộ dataset trước khi split.
4. Không dùng test set để tune hyperparameter.
5. Experiment quan trọng phải được log.
6. Code do AI hỗ trợ phải được review và test.
7. Không tạo các feature không tồn tại trong Olist.
8. Không sử dụng thông tin tương lai để tạo feature.

Các tài liệu AI nằm trong:

```text
ai/AI_RULES.md
ai/WORKFLOW.md
ai/DECISION_LOG.md
ai/prompts/
ai/results/
```

---

## 26. Data Leakage Prevention

Project áp dụng các biện pháp hạn chế leakage:

- Temporal split thay vì random split.
- Lag chỉ sử dụng dữ liệu quá khứ.
- Rolling feature không sử dụng target tương lai.
- Target không xuất hiện trong model matrix.
- Preprocessing chỉ fit trên train.
- Validation dùng để chọn hyperparameter.
- Test không được dùng để chọn model.
- Final test chỉ thực hiện sau khi đã chốt best configuration.

---

## 27. Hạn chế của project

Project hiện tại có một số hạn chế:

1. Dự đoán ở mức product category thay vì từng product ID.

2. Chỉ sử dụng 4 bảng Olist chính trong pipeline MVP.

3. Dataset Olist không có các trường như customer age, gender hoặc advertising spend nên project không tự tạo các feature này.

4. Project chưa áp dụng một quy tắc loại bỏ outlier toàn cục.

5. Final test hiện có RMSE thấp hơn validation (33.8225 so với 46.0037), nhưng test chỉ gồm ba tháng hoàn chỉnh (2018-06..2018-08). Kết quả này không đủ để khẳng định mô hình ổn định ở mọi future period hoặc thị trường khác.

6. Scenario inference yêu cầu người dùng cung cấp đầy đủ feature-month fields hợp lệ; project chưa tự thu thập các field này từ một hệ thống vận hành thời gian thực.

7. Deployment hiện tại là CLI demo, chưa phải REST API hoặc web application.

8. Dataset Olist là dữ liệu lịch sử của thị trường Brazil nên khả năng tổng quát sang thị trường hoặc thời gian khác còn hạn chế.

---

## 28. Hướng phát triển

Có thể tiếp tục cải tiến project bằng:

- Thêm nhiều temporal validation window.
- Mở rộng hyperparameter search.
- Phân tích outlier chi tiết hơn.
- Feature selection.
- Bổ sung các historical demand features.
- Sử dụng thêm Olist reviews.
- Sử dụng thêm Olist payments.
- Regularized Linear Regression from scratch.
- Random Forest from scratch.
- Xây dựng inference scenario thực tế hơn.
- Xây dựng REST API.
- Xây dựng giao diện web demo.

Test set phải tiếp tục được giữ độc lập với quá trình model selection.

---

## 29. Kết quả cuối cùng

### Data Pipeline

```text
Processed rows: 1193
Model features: 90
```

### Temporal Split

```text
Train:      755
Validation: 219
Test:       219
```

### Automated Tests

```text
29 passed
```

### Experiments

```text
8 experiments
8 success
0 failed
```

### Best Model

```text
Run: LR003
Model: LinearRegressionScratch

Validation MAE: 22.6835
Validation RMSE: 46.0037
Validation R²: 0.9388
```

### Final Test

```text
Test MAE: 18.6781
Test MSE: 1143.9581
Test RMSE: 33.8225
Test R²: 0.9608
```

### Prediction Demo

```text
Scenario file: examples/prediction_scenario.csv
Predicted next-month sales: 53.0523
```

---

## 30. Trạng thái project

```text
Data Preparation                 DONE
Feature Engineering              DONE
Temporal Split                   DONE
Preprocessing                    DONE
EDA                              DONE

Mean Baseline                    DONE
Linear Regression Scratch        DONE
Decision Tree Regression Scratch DONE

Regression Metrics               DONE
Experiment Logger                DONE
Experiment Runner                DONE
Hyperparameter Experiments       DONE

Best Model Selection             DONE
Final Model Training             DONE
Final Test Evaluation            DONE
Model Serialization              DONE

Prediction Demo                  DONE

Automated Tests                  29 PASSED
Official Experiments             8 / 8 SUCCESS
```

Best model hiện tại:

```text
LR003 - LinearRegressionScratch
```

Final test:

```text
MAE  = 18.6781
MSE  = 1143.9581
RMSE = 33.8225
R²   = 0.9608
```

Project hiện đã hoàn thành pipeline từ dữ liệu thô đến model prediction demo theo phạm vi triển khai hiện tại.
