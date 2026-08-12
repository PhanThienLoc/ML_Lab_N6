# Kết quả 10 - Sửa cutoff purchase-time demand

- Prompt: `ai/prompts/10_sales_cutoff_assumption_review.md`; thực hiện ngày 2026-08-12.
- Trạng thái: **PASS**.

> Ghi chú tiến độ: Đây là evidence lịch sử trước Prompt 16. Boundary hiện hành loại trailing incomplete period sau 2018-08; xem Result 16 để lấy split và metric cuối.

`sales_current` và `sales_next_month` hiện đếm order-item demand theo `order_purchase_timestamp`, giữ toàn bộ order có timestamp hợp lệ bất kể final `order_status`. `order_status` chỉ được audit trong report/metadata. Vì vậy feature của tháng *t* không dùng kết quả delivered/canceled chỉ xuất hiện sau cutoff.

Đã thêm test chứng minh order bị canceled sau đó vẫn là purchase-time demand event. Đồng thời cập nhật metadata, README, decision log, handoff, report và feature schema: thêm `month_sin`/`month_cos`, bỏ `quarter`, đổi nhãn product attributes theo bản chất purchase-weighted monthly attributes.

Lệnh: `python -m pytest -q` — **15 passed**; `python -m src.run_data_pipeline --raw-dir data/raw` — **PASS**.

Artifact mới: 1.267 model-ready row, 90 model feature; train 755 (2017-01..2018-02), validation 219 (2018-03..2018-05), test 293 (2018-06..2018-09). Target vẫn là `sales_next_month`, nhưng nghĩa chính xác là next-month purchase-time item demand.
