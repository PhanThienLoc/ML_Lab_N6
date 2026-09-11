# Báo cáo phân tích dữ liệu và mô hình

## 1. Tóm tắt dự án

Đây là dự án supervised regression dự đoán **Purchase Amount (USD)** từ bộ Customer Shopping Trends. Mỗi dòng là một giao dịch/khách hàng; mục tiêu `product_sales_amount_usd` là biến số numerical liên tục, không phải phân loại và không phải dự báo chuỗi thời gian.

Pipeline hiện tại gồm: audit dữ liệu → xây dựng target/đặc trưng → chia ngẫu nhiên có seed → preprocessing train-only → huấn luyện thuật toán scratch → chọn mô hình bằng validation → đánh giá final test → inference.

## 2. Phát biểu bài toán

- **Đầu vào:** tuổi, lịch sử mua hàng, thông tin sản phẩm, mùa, phương thức thanh toán, vận chuyển, khuyến mại, đăng ký thành viên và tần suất mua.
- **Đầu ra:** số tiền mua dự đoán bằng USD (`product_sales_amount_usd`).
- **Đơn vị quan sát:** một bản ghi mua hàng hiện tại (`aggregation=current_purchase_record`).
- **Mục tiêu:** giảm MAE/RMSE trên dữ liệu chưa thấy; R² được báo cáo để phản ánh mức giải thích phương sai.
- **Không áp dụng:** timestamp, lag, target tháng kế tiếp hoặc Olist joins; đây là các khái niệm của pipeline Olist cũ.

## 3. Nguồn dữ liệu và phạm vi

Nguồn là Customer Shopping Trends Dataset từ Kaggle. File runtime là `data/raw/shopping_trends.csv` (raw data bị bỏ qua bởi `.gitignore`).

Audit thực tế ghi nhận 3.900 dòng và 19 cột. Pipeline không sửa file raw; artifact tái lập được sinh vào `data/processed/` và `logs/`.

## 4. Cấu trúc dữ liệu

Cột số ban đầu gồm `Customer ID`, `Age`, `Purchase Amount (USD)`, `Review Rating`, `Previous Purchases`. Cột phân loại gồm giới tính, mặt hàng, nhóm hàng, địa điểm, kích thước, màu, mùa, subscription, thanh toán, vận chuyển, discount/promo và frequency.

Target được đổi tên thành `product_sales_amount_usd`; miền thực tế 20–100 USD, trung bình 59.7644 USD. `Customer ID` chỉ là định danh và không đưa vào feature. `Review Rating` được giữ trong audit/EDA nhưng loại khỏi feature để tránh dùng tín hiệu hậu mua.

## 5. Kiểm tra chất lượng dữ liệu

Kết quả audit trong `preprocessing_metadata.json`:

| Kiểm tra | Kết quả |
|---|---:|
| Số dòng | 3.900 |
| Số cột | 19 |
| Dòng trùng lặp | 0 |
| Tổng giá trị thiếu | 0 |
| Target nhỏ nhất/lớn nhất | 20 / 100 |
| Target trung bình | 59.7644 |

Không phát hiện missing, bản ghi trùng, kiểu dữ liệu bất thường hoặc target ngoài miền. Metadata cũng ghi cardinality của toàn bộ cột phân loại.

## 6. Phân tích khám phá dữ liệu (EDA)

EDA được sinh bằng `src/visualize_eda.py` và gồm đúng 10 hình:

1. [`01_sales_amount_distribution.png`](figures/01_sales_amount_distribution.png) – phân phối target.
2. [`02_sales_amount_boxplot.png`](figures/02_sales_amount_boxplot.png) – ngoại lệ và độ phân tán target.
3. [`03_age_distribution.png`](figures/03_age_distribution.png) – phân phối tuổi.
4. [`04_review_rating_distribution.png`](figures/04_review_rating_distribution.png) – phân phối đánh giá.
5. [`05_previous_purchases_distribution.png`](figures/05_previous_purchases_distribution.png) – lịch sử mua.
6. [`06_sales_by_category.png`](figures/06_sales_by_category.png) – target theo nhóm hàng.
7. [`07_sales_by_season.png`](figures/07_sales_by_season.png) – target theo mùa.
8. [`08_sales_by_discount.png`](figures/08_sales_by_discount.png) – so sánh discount.
9. [`09_sales_by_promo_code.png`](figures/09_sales_by_promo_code.png) – so sánh promo.
10. [`10_sales_by_frequency.png`](figures/10_sales_by_frequency.png) – target theo tần suất mua.

Target có trung vị 60, độ lệch chuẩn 23.6854, Q1 = 39 và Q3 = 81. Trung bình theo category: Accessories 59.8387, Clothing 60.0253, Footwear 60.2554, Outerwear 57.1728 USD. Theo mùa, Fall cao nhất (61.5569) và Summer thấp nhất (58.4052). Discount chênh lệch nhỏ (No 60.1305; Yes 59.2791).

## 7. Kết luận từ EDA

Target phân tán trong miền 20–100 USD nhưng không có missing/outlier cần loại bỏ theo audit. Các nhóm danh mục và mùa có khác biệt trung bình nhưng không lớn. Tương quan của các số ban đầu với target đều gần 0 (Age −0.0104; Review Rating 0.0308; Previous Purchases 0.0081), nên cần đánh giá bằng holdout thay vì suy diễn từ EDA.

## 8. Xây dựng đặc trưng

`src/features.py` tạo 13 cột số: `Age`, `Previous Purchases`, `annual_purchase_frequency`, `log_previous_purchases`, `customer_activity_score`, `is_subscriber`, `has_discount`, `used_promo_code`, `discount_promo_interaction`, `item_purchase_frequency_train`, `category_purchase_frequency_train`, `item_mean_review_rating_train`, `category_mean_review_rating_train`.

Các cột phân loại được one-hot encode theo levels học từ train. Feature cuối cùng có 158 cột theo `data/processed/preprocessing_metadata.json`. Các thống kê popularity/rating hậu tố `_train` chỉ fit trên train.

## 9. Chia dữ liệu và preprocessing

Pipeline dùng `random_70_15_15`, `random_state=42`: train 2.730 dòng, validation 585 dòng, test 585 dòng. Đây là random holdout cho dữ liệu không có thời gian; không được mô tả là temporal split.

Preprocessing chỉ fit trên train: học fallback số, category levels và feature schema. Validation/test chỉ transform bằng trạng thái đã lưu; category chưa biết được xử lý an toàn và schema được căn chỉnh.

## 10. Biện pháp chống data leakage

- Target bị loại khỏi ma trận `X` trước khi fit.
- `Customer ID` và `Review Rating` không dùng làm feature model.
- Thống kê tần suất/trung bình item/category chỉ fit trên train.
- Test không tham gia chọn hyperparameter hoặc fit preprocessing.
- Seed 42 cố định split; metadata ghi `fit_scope=train_only`.

## 11. Các thuật toán scratch

Dự án giữ các cài đặt không dùng sklearn trong `src/models/`:

- `baseline.py`: dự đoán bằng trung bình target train.
- `linear_regression.py`: hồi quy tuyến tính tối ưu gradient descent.
- `decision_tree.py`: cây hồi quy tự cài đặt, chọn split theo giảm SSE với `max_depth` và `min_samples_split`.

## 12. Thiết kế thực nghiệm

`main.py`/`src/run_experiments.py` chạy 8 cấu hình: baseline, 4 learning rate cho linear regression và 3 cấu hình cây. Tiêu chí chọn là validation RMSE thấp nhất; final test chỉ chạy sau khi khóa cấu hình.

## 13. So sánh validation

| Run | Mô hình | MAE | RMSE | R² |
|---|---|---:|---:|---:|
| BASE001 | MeanBaseline | 20.0819 | 23.2253 | -0.0112 |
| LR001 | LinearRegressionScratch | 20.0606 | 23.2099 | -0.0098 |
| LR002 | LinearRegressionScratch | 20.0021 | 23.1762 | -0.0069 |
| LR003 | LinearRegressionScratch | 19.9790 | 23.2172 | -0.0105 |
| LR004 | LinearRegressionScratch | 19.9935 | 23.2880 | -0.0167 |
| TREE001 | DecisionTreeRegressorScratch | 20.0830 | 23.3061 | -0.0182 |
| TREE002 | DecisionTreeRegressorScratch | 20.0457 | 23.2356 | -0.0121 |
| TREE003 | DecisionTreeRegressorScratch | **19.9256** | **23.1282** | -0.0027 |

## 14. Lựa chọn mô hình

TREE003 được chọn vì validation RMSE thấp nhất, với `max_depth=4`, `min_samples_split=10`. Việc chọn chỉ dùng validation, không nhìn vào test. R² xấp xỉ 0 cho thấy mô hình hiện gần baseline về khả năng giải thích phương sai; đây là kết quả cần báo cáo trung thực.

## 15. Đánh giá final test

Kết quả chính thức trong [`logs/final_test.json`](../logs/final_test.json):

| Chỉ số | Giá trị |
|---|---:|
| MAE | 20.7680 USD |
| MSE | 565.1858 |
| RMSE | 23.7736 USD |
| R² | −0.0180 |

Mô hình cuối là `DecisionTreeRegressorScratch` TREE003. Hậu xử lý clipping về 0 tôn trọng miền không âm của Purchase Amount; metric không bị chỉnh thủ công.

## 16. Phân tích residual

Residual final test có trung bình 1.3359, trung vị 2.1905, độ lệch chuẩn 23.7361, min −46.9268 và max 43.5500 USD. Dự đoán nằm khoảng 34.5–73.9268 USD, hẹp hơn miền target; cây nông chưa mô hình hóa tốt các giao dịch biên.

## 17. Quy trình inference

`src/predict.py` nhận scenario CSV, áp dụng metadata/bundle đã lưu và in Purchase Amount dự đoán bằng USD. Ví dụ nằm tại `examples/prediction_scenario.csv`. Unknown category không làm crash; output không âm nhờ prediction policy.

## 18. Khả năng tái lập

```powershell
pip install -r requirements.txt
python -m src.run_data_pipeline
python main.py
python -m src.analyze_logs
python -m src.visualize_results
python -m src.predict --scenario-file examples/prediction_scenario.csv
python -m pytest -q
```

Artifact chính: `data/processed/preprocessing_metadata.json`, `logs/experiments.csv`, `logs/final_test.json`, `logs/best_model.pkl`, `reports/figures/`.

## 19. Hạn chế

Dataset có 3.900 bản ghi và tín hiệu target yếu. Random split không đo khả năng dự báo theo thời gian; dữ liệu không có timestamp nên temporal split không phù hợp. Một số biến khảo sát có thể được ghi nhận sau hành vi mua; phạm vi nhân quả không được khẳng định. Cần thêm dữ liệu/feature nghiệp vụ hoặc mô hình mạnh hơn nếu muốn cải thiện R².

## 20. Kết luận

Pipeline chạy end-to-end, audit không phát hiện lỗi, preprocessing train-only và artifact JSON hợp lệ. Tám thí nghiệm scratch đã được ghi log; TREE003 tốt nhất theo validation RMSE và đạt final test RMSE 23.7736 USD. R² âm nhẹ phản ánh chất lượng dự báo còn hạn chế, nhưng báo cáo và kết quả hiện nhất quán, trung thực và tái lập được.

### Evidence và trạng thái kiểm chứng

- `python -m pytest -q`: 16 passed.
- `logs/final_test.json`: JSON hợp lệ và là source of truth cho final metrics.
- `data/processed/preprocessing_metadata.json`: JSON hợp lệ.
- `lab2.ipynb`: 14/14 code cells đã thực thi, 0 error output.
- Hình EDA: đúng 10 file; thêm 1 hình so sánh validation RMSE.
