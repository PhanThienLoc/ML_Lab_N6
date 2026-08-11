# Kết quả 07 - Báo cáo và handoff

- Prompt: `ai/prompts/07_data_report_handoff.md`; thực hiện 2026-08-11; trạng thái: PASS.

Phát hiện handoff cũ có feature/shape/target/split nhưng chưa gom rõ raw file, join key, completed-sales policy và preprocessing rule. Đã sửa template tái lập được trong `src/pipeline.py`, không sửa tay report; sau đó chạy lại pipeline.

Lệnh: `python -m src.run_data_pipeline --raw-dir data/raw` -> 1,480 model-ready row, 92 feature, report/handoff/log được sinh lại.
