# Kết quả 16 - Ranh giới trailing incomplete period

- Prompt: `ai/prompts/16_trailing_incomplete_period_boundary.md`; thực hiện 2026-08-12.
- Trạng thái: **PASS / READY**.

Audit raw data xác nhận order-item demand theo tháng cuối: 2018-06 = 7.078, 2018-07 = 7.092, 2018-08 = 7.248, 2018-09 = 1. Order count: 2018-08 = 6.512, 2018-09 = 16, 2018-10 = 4. September là right-censored trailing period, không thể làm target month sales bình thường.

Đã đặt policy tái lập được `OLIST_USABLE_DEMAND_END_MONTH = 2018-08`: period sau cutoff bị loại trong `build_category_month_dataset()` trước aggregate, monthly calendar, lag và target. Không sửa hoặc loại metric thủ công. `run_experiments.py` cũng đọc đúng `temporal_split.target_month_start/end`, nên `experiments.csv`, `analyze_logs.py` và `final_test.json` ghi đúng boundary mới.

Kết quả tái tạo: 1.193 model-ready row, 90 feature; train 2017-01..2018-02 (755), validation 2018-03..2018-05 (219), test 2018-06..2018-08 (219). Batch có 8 run ID duy nhất; `LR003` được chọn bằng validation RMSE 45.9968. Theo `logs/final_test.json` (source of truth), final test: MAE 18.6818, MSE 1143.9507, RMSE 33.8223, R² 0.9608.

Lệnh đã chạy: `python -m pytest -q` (29 passed), `python -m src.run_data_pipeline --raw-dir data/raw`, `python main.py`, `python -m src.analyze_logs`, `python -m src.predict --scenario-file examples/prediction_scenario.csv` — PASS.
