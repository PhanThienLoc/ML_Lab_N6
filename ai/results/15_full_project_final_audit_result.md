# Kết quả 15 - Final audit toàn project

- Prompt: `ai/prompts/15_full_project_final_audit.md`; thực hiện 2026-08-12.
- Trạng thái lịch sử: **READY, đã được thay thế bởi Result 16**.

> Ghi chú tiến độ: Audit này diễn ra trước khi phát hiện September 2018 là trailing incomplete period. Các con số 1.267 row, test đến 2018-09, 26 test và metric cũ không còn là trạng thái hiện hành.

Đã chạy end-to-end từ raw Olist qua TV1 pipeline, TV2 scratch models, TV3 validation-only selection, final test, saved model bundle và CLI scenario. Không có import ML estimator cấm; raw CSV không bị sửa; log có 8 record success với 8 `run_id` duy nhất; bundle dùng saved train-only preprocessor và 293/293 test prediction sau policy đều không âm.

Lệnh đã chạy:

```text
python -m src.run_data_pipeline --raw-dir data/raw
python -m pytest -q
python main.py
python -m src.analyze_logs
python -m src.predict --scenario-file examples/prediction_scenario.csv
```

Kết quả: 1.267 model-ready row, 90 feature, **26 passed**. Best run `LR003` (validation RMSE 46.0037); final test MAE 38.0376, MSE 11682.8771, RMSE 108.0874, R² 0.5051. Giới hạn còn lại: scenario CSV phải được người dùng cung cấp từ thông tin hợp lệ ở feature month; demo chưa phải API/web production.
