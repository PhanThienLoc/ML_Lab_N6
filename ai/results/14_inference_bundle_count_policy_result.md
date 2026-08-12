# Kết quả 14 - Model bundle và count prediction không âm

- Prompt: `ai/prompts/14_inference_bundle_count_policy.md`; thực hiện 2026-08-12.
- Trạng thái: **PASS**.

> Ghi chú tiến độ: Đây là evidence lịch sử trước Prompt 16. Bundle đã được tái tạo trên boundary test 2018-06..2018-08; metric hiện hành nằm ở Result 16.

Phát hiện Linear Regression có 109/293 raw test prediction âm (min -22.1773) dù target là order-item count. Đã áp dụng `max(0, raw_prediction)` nhất quán cho validation, final test và CLI. `logs/best_model.pkl` nay là bundle chứa model, preprocessor train-only, feature order, schema source và policy; `src.predict` chỉ nhận `--scenario-file` nên không rebuild pipeline/refit preprocessing hoặc dùng test set làm demo.

Lệnh: `python main.py`, `python -m src.analyze_logs`, `python -m src.predict --scenario-file examples/prediction_scenario.csv` — PASS. Final test: MAE 38.0376, MSE 11682.8771, RMSE 108.0874, R² 0.5051. `python -m pytest -q` — **26 passed**.
