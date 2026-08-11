# Kết quả 08 - Audit cuối TV1

- Prompt: `ai/prompts/08_tv1_final_audit.md`; thực hiện 2026-08-11; trạng thái: READY.

Luồng raw CSV -> audit -> completed-sales filter -> validated joins -> category-month calendar -> temporal feature/target -> chronological split -> train-only preprocessing -> handoff đã hoàn tất. Có 1,480 model-ready row và 92 feature. Target là `sales_next_month`; split là 2017-01..2018-02 / 2018-03..2018-05 / 2018-06..2018-08. Đã kiểm tra hai category timeline trong `reports/data_analysis.md`.

Lệnh: `python -m src.run_data_pipeline --raw-dir data/raw` và `python -m pytest -q`; kết quả pipeline hoàn tất, **11 passed in 0.44s**. Giới hạn: dự báo quantity theo category, không phải SKU/revenue; TV2 phụ trách model, TV3 phụ trách experiment/metric/chọn model.
