# Kết quả 13 - Metrics, logging và chọn model bằng validation

- Prompt: `ai/prompts/13_experiment_logging_review.md`; thực hiện 2026-08-12.
- Trạng thái: **PASS**.

> Ghi chú tiến độ: Đây là evidence lịch sử trước Prompt 16. Quy tắc ranking/logging vẫn giữ nguyên, nhưng boundary và final metric hiện hành là test 2018-06..2018-08, 29 passed; xem Result 16.

Đã review `metrics.py` (MAE/MSE/RMSE/R² có toy test giá trị biết trước), `logger.py`, `experiment.py`, `analyze_logs.py` và runner. Phát hiện `experiments.csv` có thể append lại tám run ID cố định khi runner được chạy lặp. Đã thêm `initialise_experiment_log(..., overwrite=True)` ở đầu official batch và test bảo vệ hành vi này. Runner chỉ tính train/validation metric trong từng run; `get_best_run()` rank theo `validation_rmse`; final test chỉ chạy sau khi `LR003` đã được chọn.

Lệnh: `python main.py` — **8/8 success, 8 run ID duy nhất**; `python -m pytest -q` — **26 passed**.
