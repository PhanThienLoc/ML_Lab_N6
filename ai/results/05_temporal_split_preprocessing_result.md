# Kết quả 05 - Temporal split và preprocessing

- Prompt: `ai/prompts/05_temporal_split_preprocessing.md`; thực hiện 2026-08-11; trạng thái: PASS.

> Ghi chú tiến độ: Đây là evidence lịch sử của lượt thực thi 2026-08-11. Contract hiện hành được chốt tại Result 16: 1.193 model-ready row, 90 feature, test 2018-06..2018-08 và 29 test passed.

Train: 2017-01..2018-02 (1,036 dòng); validation: 2018-03..2018-05 (222); test: 2018-06..2018-08 (222). Matrix có 92 cột: 18 numerical và 74 category level học từ train. Median/mean/std train-only được lưu metadata; unknown category thành one-hot all-zero; mọi split dùng cùng thứ tự cột.

Đã review `src/preprocessing.py`/metadata và chạy `python -m pytest -q`: **11 passed**. Không cần sửa code.
