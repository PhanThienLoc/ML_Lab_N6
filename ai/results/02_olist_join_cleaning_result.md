# Kết quả 02 - Join và làm sạch Olist

- Prompt: `ai/prompts/02_olist_join_cleaning.md`; thực hiện 2026-08-11; trạng thái: PASS.

Delivered orders -> items là one-to-many: 96,478 -> 110,197, unmatched 0%. Items -> products là many-to-one: 110,197 -> 110,197, unmatched 0%. Products -> translation là many-to-one: 110,197 -> 110,197, unmatched 1.41%. `pandas.merge(validate=...)` áp đặt cardinality. Policy chỉ dùng `delivered`; category thiếu có fallback rõ ràng và timestamp lỗi bị loại trước aggregation. Không thấy join multiplication hoặc cleaning rule không có lý do.

Đã chạy `python -m pytest -q tests/test_data_pipeline.py tests/test_features.py`: **7 passed**. Không cần sửa code.
