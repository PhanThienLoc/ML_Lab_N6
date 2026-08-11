# Prompt Traceability

`ai/results/` chứa bản tóm tắt kết quả thực thi và kiểm chứng của từng prompt; đây không phải nguyên văn phản hồi thô của AI.

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
