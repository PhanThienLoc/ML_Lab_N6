# Kết quả 09 - Sửa active window của category

- Prompt: `ai/prompts/09_category_active_window_fix.md`; thực hiện ngày 2026-08-12.
- Trạng thái: **PASS**.

`_monthly_grid()` không còn tạo global Cartesian grid. Mỗi `product_category` chỉ có lịch từ `feature_month` đầu tiên có purchase event đến tháng quan sát cuối toàn cục. Tháng thiếu sau mốc bắt đầu được điền `sales_current = 0`; tháng trước lần quan sát đầu tiên không tồn tại.

Đã thêm test phân biệt hai tình huống: `category_a` có February zero-demand sau khi đã xuất hiện; `category_b` xuất hiện lần đầu ở March và không có January/February synthetic row. Test cũng xác nhận April của `category_b` có `lag_1 = March` và `lag_2` trống, không dùng February zero giả. Nhờ đó category xuất hiện muộn không lọt vào vocabulary của train qua grid giả.

Files thay đổi chính: `src/build_dataset.py`, `src/features.py`, `tests/test_data_pipeline.py`. Lệnh kiểm chứng cuối: `python -m pytest -q` — **15 passed**; pipeline được chạy lại sau cùng tại Prompt 10.
