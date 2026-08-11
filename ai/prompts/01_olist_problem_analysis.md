# Olist Problem Analysis

## Context

Bài lab Predicting Product Sales sử dụng Brazilian E-Commerce Public Dataset by Olist.

Các file dữ liệu chính:

- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_products_dataset.csv
- product_category_name_translation.csv

## Goal

Xây dựng dataset theo product_category × month để dự đoán sales của tháng kế tiếp.

## Task

Phân tích:

1. Join plan giữa các bảng.
2. Cleaning rules.
3. Monthly aggregation.
4. Target definition.
5. Feature engineering.
6. Các nguy cơ data leakage.

## Constraints

- Không tạo feature không tồn tại trong source hoặc không có cách tính hợp lệ từ source.
- Không sử dụng dữ liệu tương lai.
- Phải nêu join keys và cardinality.
- Không sử dụng Machine Learning library cho phần thuật toán from scratch.
- Chưa viết code khi đang ở bước phân tích.

## Expected Output

AI cần trả về:

1. Join plan.
2. Cleaning rules.
3. Aggregation và target.
4. Feature list.
5. Leakage risks.
