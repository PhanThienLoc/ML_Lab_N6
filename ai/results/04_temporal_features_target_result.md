# Kết quả 04 - Temporal feature và target

- Prompt: `ai/prompts/04_temporal_features_target.md`; thực hiện 2026-08-11; trạng thái: PASS.

> Ghi chú tiến độ: Đây là evidence lịch sử của lượt thực thi 2026-08-11. Contract hiện hành được chốt tại Result 11: 1.267 model-ready row, 90 feature và 15 test passed.

Feature được sort theo thời gian trong category sau complete grid. `sales_lag_1/2/3` là backward group shift; `sales_next_month` là forward group shift; `rolling_sales_mean_3` chỉ dùng current, lag1, lag2. Target/date key bị loại khỏi model matrix. Test synthetic xác nhận series `10,20,30,40`: ở current 30 có lag1=20, lag2=10, target=40. Đã kiểm tra manual sample của hai category thật.

Đã review `create_features()`/`assert_feature_alignment()` và chạy test liên quan: **7 passed**. Không cần sửa code.
