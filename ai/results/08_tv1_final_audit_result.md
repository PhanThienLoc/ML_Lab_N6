# Kết quả 08 - Audit cuối TV1

- Prompt: `ai/prompts/08_tv1_final_audit.md`; thực hiện 2026-08-11; trạng thái: READY.

Đây là kết quả audit trước khi có refinement Prompt 09–10. Các con số 1.480 row/92 feature và completed-sales filter không còn là trạng thái hiện hành.

**Trạng thái hiện hành:** xem `09_category_active_window_fix_result.md` và `10_sales_cutoff_assumption_review_result.md`; hai prompt này sửa active-window leakage, cutoff hindsight, seasonal schema rồi chạy lại pytest/pipeline.

Lệnh: `python -m src.run_data_pipeline --raw-dir data/raw` và `python -m pytest -q`; kết quả pipeline hoàn tất, **11 passed in 0.44s**. Giới hạn: dự báo quantity theo category, không phải SKU/revenue; TV2 phụ trách model, TV3 phụ trách experiment/metric/chọn model.
