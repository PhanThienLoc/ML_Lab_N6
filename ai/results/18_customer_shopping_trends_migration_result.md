# Kết quả Prompt 18 — Customer Shopping Trends migration

Trạng thái: PASS (worktree migration/customer-shopping-trends).

- CSV thật: 3.900 dòng, 19 cột; target Purchase Amount (USD) → product_sales_amount_usd.
- Split random 70/15/15 seed 42: 2.730 / 585 / 585.
- Tạo 10 hình EDA, metadata, processed features và inference scenario.
- Huấn luyện 8 cấu hình scratch; chọn TREE003 theo validation RMSE.
- Kiểm thử: chạy pytest và pipeline thành công.

