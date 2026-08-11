# Machine Learning Workflow

## 1. Problem Definition

Bài toán của nhóm là dự đoán doanh số sản phẩm trong tháng kế tiếp.

Đây là bài toán Supervised Learning dạng Regression vì target là một biến số.

## 2. Data Source

Nhóm sử dụng Brazilian E-Commerce Public Dataset by Olist.

Các file dữ liệu chính:

- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_products_dataset.csv
- product_category_name_translation.csv

## 3. Data Preparation

Các bảng dữ liệu được join dựa trên các khóa phù hợp:

- order_id
- product_id
- product_category_name

Sau đó nhóm thực hiện cleaning, kiểm tra missing values, duplicates và xác định policy đối với order status.

## 4. Data Aggregation

Dữ liệu được aggregate theo:

product_category × month

Target được xây dựng để dự đoán sales của tháng kế tiếp:

sales_next_month

## 5. Feature Engineering

Các feature được xây dựng từ dữ liệu quá khứ, bao gồm:

- sales_lag_1
- sales_lag_2
- sales_lag_3
- rolling_sales_mean_3
- avg_price
- avg_freight
- month
- quarter

Không sử dụng dữ liệu tương lai để tạo feature.

## 6. Train / Validation / Test

Dữ liệu được chia theo thứ tự thời gian:

- Training set
- Validation set
- Test set

Validation được sử dụng để lựa chọn model và hyperparameters.

Test set chỉ được sử dụng để đánh giá cuối cùng sau khi đã chọn model.

## 7. Machine Learning Models

Nhóm sử dụng:

1. Mean Baseline
2. Linear Regression from Scratch
3. Decision Tree Regression from Scratch

Các thuật toán Machine Learning được tự cài đặt theo yêu cầu của bài lab.

## 8. Model Evaluation

Các metrics được sử dụng:

- MAE
- MSE
- RMSE
- R²

Các metrics được tính trên validation set để so sánh các experiment.

## 9. Experiment Tracking

Mỗi experiment quan trọng được ghi vào:

logs/experiments.csv

Thông tin được lưu gồm model, parameters, dataset configuration, feature version và validation metrics.

## 10. Model Selection

Best run được lựa chọn dựa trên validation performance.

Test set không được sử dụng để lựa chọn model hoặc hyperparameters.

## 11. Final Evaluation

Sau khi chọn được best model và configuration, nhóm mới đánh giá model trên test set.

Kết quả final test được lưu lại để phục vụ báo cáo và bảo vệ.

## 12. Prediction Demo

Best model được sử dụng để thực hiện dự đoán sales của tháng kế tiếp.

