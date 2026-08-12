# Kết quả 02 - Join và làm sạch Olist

- Prompt: `ai/prompts/02_olist_join_cleaning.md`; thực hiện 2026-08-11; trạng thái: PASS.

Kết quả lịch sử của lượt review ban đầu: delivered orders -> items là one-to-many: 96,478 -> 110,197, unmatched 0%. Items -> products là many-to-one: 110,197 -> 110,197, unmatched 0%. Products -> translation là many-to-one: 110,197 -> 110,197, unmatched 1.41%. `pandas.merge(validate=...)` áp đặt cardinality.

**Cập nhật trạng thái:** chính sách chỉ dùng `delivered` đã được thay thế bởi Prompt 10 để tránh hindsight leakage. Kết quả hiện hành nằm ở `10_sales_cutoff_assumption_review_result.md`.

Đã chạy `python -m pytest -q tests/test_data_pipeline.py tests/test_features.py`: **7 passed**. Không cần sửa code.
