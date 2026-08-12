# Kết quả 03 - Tổng hợp category-month

- Prompt: `ai/prompts/03_category_month_aggregation.md`; thực hiện 2026-08-11; trạng thái: PASS.

Kết quả lịch sử của lượt review ban đầu: aggregation delivered-order tạo 1,776 dòng category-month cho 74 category trước modeling filter. Pipeline reindex category theo calendar, vì vậy tháng không có transaction nhận sales/order/product count bằng 0 trước shift.

**Cập nhật trạng thái:** global calendar grid đã được thay thế bởi active-window grid ở Prompt 09. Tháng thiếu sau lần xuất hiện đầu tiên vẫn là 0; pre-history của category xuất hiện muộn không còn bị tạo giả. Kết quả hiện hành nằm ở `09_category_active_window_fix_result.md`.

Đã review `build_category_month_dataset()`, manual sample và chạy `python -m pytest -q tests/test_data_pipeline.py tests/test_features.py`: **7 passed**. Không cần sửa code.
