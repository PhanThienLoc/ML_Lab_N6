# Quy trình Machine Learning

## 1. Định nghĩa bài toán

Project dự đoán doanh số sản phẩm tháng kế tiếp. `sales_next_month` là biến mục tiêu dạng số (numerical/count), vì vậy trong bài lab nhóm mô hình hóa bằng supervised regression.

## 2. Nguồn dữ liệu

Dùng Brazilian E-Commerce Public Dataset by Olist với bốn file: orders, order items, products và category translation.

## 3. Chuẩn bị dữ liệu

Join theo `order_id`, `product_id`, `product_category_name`; kiểm tra missing, duplicate, giá trị không hợp lệ, status và cardinality.

## 4. Tổng hợp và feature

Tổng hợp ở mức `product_category x month`; target là `sales_next_month`. Feature lịch sử chỉ dùng thông tin tại hoặc trước cutoff: sales lag, rolling mean, price/freight, calendar feature.

## 5. Split, model và đánh giá

Split theo thời gian: train -> validation -> test. TV2 cài Mean Baseline, Linear Regression và Decision Tree từ đầu. TV3 tính MAE/MSE/RMSE/R², log thí nghiệm, chọn model bằng validation và chỉ đánh giá test sau cùng.

## 6. Luồng tổng quát

Raw Olist -> join/làm sạch -> category-month -> feature -> temporal split -> baseline/model -> validation metric -> experiment log -> chọn best run -> final test -> demo dự đoán.
