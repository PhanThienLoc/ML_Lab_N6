# Prompt Traceability

`ai/results/` chứa bản tóm tắt kết quả thực thi và kiểm chứng của từng prompt; đây không phải nguyên văn phản hồi thô của AI.

## Trạng thái hiện hành (2026-08-12)

Prompt 01–08 là evidence của vòng MVP/review ban đầu. Prompt 09–11 là refinement TV1; Prompt 12–16 kiểm chứng/refine TV2–TV3 và full integration. Trạng thái hiện hành: pipeline tạo 1.193 model-ready row, 90 model feature; usable demand kết thúc ở 2018-08; official batch có 8 run duy nhất; `LR003` được chọn bằng validation RMSE; `python -m pytest -q` đạt 29 passed. Các số test/feature ở result lịch sử được giữ nguyên để trung thực với lần chạy đó, không phải contract hiện tại.

| Prompt | Công việc | Code liên quan | Evidence | Test |
| ------ | --------- | -------------- | -------- | ---- |
| 00 | Orchestrate MVP | TV1 pipeline | master prompt | pipeline run |
| 01 | Audit Olist | `data_loader.py` | result 01 | PASS |
| 02 | Join/clean | `build_dataset.py` | result 02 | 7 pass |
| 03 | Category-month | `build_dataset.py` | result 03 | 7 pass |
| 04 | Lag + target | `features.py` | result 04 | PASS |
| 05 | Split/preprocess | `preprocessing.py` | result 05 | 11 pass |
| 06 | Tests | `tests/*` | result 06 | 11 pass |
| 07 | Report/handoff | `pipeline.py`, reports | result 07 | pipeline pass |
| 08 | Final audit | toàn TV1 | result 08 | 11 pass |
| 09 | Category active window | `build_dataset.py`, tests | result 09 | 15 pass |
| 10 | Sales cutoff policy | `build_dataset.py`, `features.py`, reports | result 10 | 15 pass + pipeline PASS |
| 11 | Reproducible EDA visuals | `eda.py`, `pipeline.py`, reports | result 11 | 15 pass + pipeline PASS |
| 12 | Scratch-model review | `models/*`, model tests | result 12 | 26 pass |
| 13 | Metrics, logging/validation audit | `metrics.py`, `logger.py`, `experiment.py`, `analyze_logs.py`, `run_experiments.py` | result 13 | 26 pass + 8 unique runs |
| 14 | Inference/count policy | `predict.py`, model bundle, tests | result 14 | 26 pass + CLI PASS |
| 15 | Full project final audit | all TV1–TV3 modules | result 15 | 26 pass + end-to-end PASS |
| 16 | Trailing incomplete period | `build_dataset.py`, `pipeline.py`, `run_experiments.py`, `metrics.py`, `analyze_logs.py` | result 16 | 29 pass + 2018-06..2018-08 test |

Nguồn chuẩn hiện tại cho contract dữ liệu là `reports/TV1_HANDOFF.md`, `data/processed/preprocessing_metadata.json`, `logs/experiments.csv` và `logs/final_test.json`; evidence mới nhất là `ai/results/16_trailing_incomplete_period_result.md`.
