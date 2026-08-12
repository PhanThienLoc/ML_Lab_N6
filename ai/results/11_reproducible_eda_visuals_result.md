# Kết quả 11 - EDA trực quan tái lập được

- Prompt: `ai/prompts/11_reproducible_eda_visuals.md`; thực hiện ngày 2026-08-12.
- Trạng thái: **PASS**.

> Ghi chú tiến độ: Đây là evidence lịch sử trước Prompt 16. EDA/panel hiện hành dùng usable demand đến 2018-08; xem Result 16 để lấy số dòng, split và test count cuối.

Pipeline hiện sinh tự động ba PNG từ active-window category-month panel: `01_monthly_purchase_demand.png`, `02_top_categories_demand.png` và `03_zero_demand_by_month.png`. Các ảnh nằm trong `reports/figures/` và được nhúng vào `reports/data_analysis.md`; không có biểu đồ nào được tạo/chỉnh tay.

Kết quả quan sát từ data thật: demand cao nhất ở 2017-11 là 8.665 order-item; `bed_bath_table` có tổng demand cao nhất là 11.115 order-item; có 280 active category-month zero-demand (17,91%). Báo cáo cũng ghi rõ raw data bắt đầu 2016-09-04 và kết thúc 2018-10-17, nên tháng biên không phải tháng đủ để so sánh trực tiếp.

Files thay đổi chính: `src/eda.py`, `src/pipeline.py`, `tests/test_data_pipeline.py`, `reports/data_analysis.md`, `reports/figures/`. Lệnh kiểm chứng cuối: `python -m src.run_data_pipeline --raw-dir data/raw` — PASS (1.267 rows, 90 feature); `python -m pytest -q` — **15 passed in 5.93s**.
