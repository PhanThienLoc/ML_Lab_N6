# Dự đoán doanh số sản phẩm - Olist

Project dự đoán **purchase-time item demand** tháng kế tiếp ở mức **product category x month** bằng Brazilian E-Commerce Public Dataset by Olist. Một dòng model chỉ dùng thông tin biết được đến cuối tháng *t* để dự đoán số order-item được đặt của category ở tháng *t + 1* (`sales_next_month`). Đây là biến mục tiêu dạng số, nên bài toán là supervised regression.

## Phân công

- TV1: audit/nạp Olist, tạo panel category-month, feature an toàn leakage, temporal split và preprocessing train-only.
- TV2: baseline, Linear Regression và Decision Tree tự cài đặt.
- TV3: metrics, experiment runner/logging, chọn model, đánh giá cuối và tích hợp.

## Dữ liệu và phạm vi

Đặt nguyên vẹn bốn raw file Olist sau vào `data/raw/`:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`
- `product_category_name_translation.csv`

Raw CSV được Git bỏ qua có chủ ý. Pipeline đếm order-item tại `order_purchase_timestamp` là demand; mọi order status có timestamp hợp lệ đều được giữ để không dùng trạng thái hoàn tất xảy ra sau cutoff. Pipeline join orders -> items -> products -> category translation tiếng Anh, và dùng rõ ràng `unknown_category` khi không xác định được category.

## Nguồn dữ liệu

Dataset: Brazilian E-Commerce Public Dataset by Olist

Kaggle:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Pipeline TV1

Pipeline tạo lịch category-month theo **active window** trước khi shift theo nhóm: mỗi category bắt đầu từ tháng mua đầu tiên được quan sát, các tháng thiếu sau đó được biểu diễn bằng `0`. Pipeline không tự tạo lịch sử zero-demand cho category chỉ xuất hiện ở tương lai.

Feature gồm `sales_current`, ba sales lag, trung bình sales ba tháng gần nhất, seasonality dạng vòng (`month_sin`, `month_cos`), năm, số order/product hiện tại, trung bình price/freight và thuộc tính sản phẩm. `quarter` không dùng vì trùng thông tin với tháng. Ở tháng zero-demand, trung bình transaction/product chỉ forward-fill từ quá khứ trong cùng category; khoảng trống còn lại dùng median từ train. One-hot category, median, mean và standard deviation đều chỉ fit trên train.

Pipeline cũng sinh EDA trực quan tái lập được tại `reports/figures/`: demand theo tháng, top category và tỷ lệ zero-demand trong active category-month. Các biểu đồ được nhúng trong `reports/data_analysis.md`.

## Trạng thái TV1 đã xác minh (2026-08-12)

- Pipeline hoàn tất với **1.267 model-ready row** và **90 model feature**.
- Split theo `target_month`: train 2017-01..2018-02 (755 dòng), validation 2018-03..2018-05 (219), test 2018-06..2018-09 (293).
- Kiểm thử hiện hành: **15 passed**.
- EDA được sinh tự động từ pipeline; không có biểu đồ hoặc số liệu được tạo/chỉnh tay.

Chạy toàn bộ handoff TV1 tại thư mục gốc repository:

```bash
python -m pip install -r requirements.txt
python -m src.run_data_pipeline --raw-dir data/raw
python -m pytest -q
```

Hướng dẫn đầy đủ cho người mới, từ clone repository đến kiểm tra artifact và xử lý lỗi, nằm tại [RUN_GUIDE.md](RUN_GUIDE.md).

Artifact tái lập được:

- `data/processed/category_month_sales.csv`
- `data/processed/preprocessing_metadata.json`
- `logs/data_quality.log`
- `reports/data_analysis.md`
- `reports/TV1_HANDOFF.md`
- `reports/figures/*.png`

`prepare_data()` trả về `X_train`, `y_train`, `X_val`, `y_val`, `X_test`, `y_test` và metadata cho TV2/TV3. Split theo thời gian nghiêm ngặt dựa trên **target month** (xấp xỉ 70% / 15% / 15%); không random split.

Prompt và bằng chứng kiểm chứng theo từng giai đoạn nằm trong `ai/prompts/`, `ai/results/` và `ai/PROMPT_TRACEABILITY.md`. `ai/results/` là **bản tóm tắt kết quả thực thi và kiểm chứng** của từng prompt, không phải nguyên văn phản hồi thô của AI.

## Ràng buộc

- Không dùng sklearn, xgboost, lightgbm, catboost, statsmodels, Prophet, TensorFlow hoặc PyTorch.
- Không sửa raw CSV hoặc dùng thông tin tương lai trong feature/preprocessing.
- Không dùng kết quả test để chọn model.
- Không tạo các field Olist không có như age, gender hoặc advertising spend.
