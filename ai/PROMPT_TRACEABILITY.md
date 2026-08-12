# Prompt Traceability

`ai/results/` chứa bản tóm tắt kết quả thực thi và kiểm chứng của từng prompt; đây không phải nguyên văn phản hồi thô của AI.

## Trạng thái hiện hành (2026-08-12)

Prompt 01–08 là evidence của vòng MVP/review ban đầu. Prompt 09–11 là các refinement hiện hành; sau Prompt 11, pipeline tạo 1.267 model-ready row, 90 model feature, ba EDA PNG tái lập được và `python -m pytest -q` đạt 15 passed. Các số test/feature ở result lịch sử được giữ nguyên để trung thực với lần chạy đó, không phải contract hiện tại cho TV2/TV3.

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

Nguồn chuẩn hiện tại cho contract dữ liệu là `reports/TV1_HANDOFF.md` và `data/processed/preprocessing_metadata.json`; chi tiết evidence mới nhất là `ai/results/11_reproducible_eda_visuals_result.md`.
