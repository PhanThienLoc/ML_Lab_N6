# Kết quả 12 - Review model regression tự cài đặt

- Prompt: `ai/prompts/12_scratch_models_review.md`; thực hiện 2026-08-12.
- Trạng thái: **PASS**.

> Ghi chú tiến độ: Đây là evidence lịch sử trước Prompt 16. Model review vẫn hợp lệ, nhưng số test và data boundary hiện hành là 29 passed với usable demand kết thúc ở 2018-08; xem Result 16 cho contract hiện tại.

Đã review `MeanBaseline`, `LinearRegressionScratch` và `DecisionTreeRegressorScratch`. Source chỉ dùng NumPy, không import ML estimator; Linear Regression có gradient descent/loss history, Tree dùng weighted MSE và stopping rules `max_depth`, `min_samples_split`, `min_impurity_decrease`.

Toy line, loss trend, tree split, output shape và constant target được kiểm chứng. Không cần thay đổi thuật toán. Lệnh: `python -m pytest -q` — **26 passed**.
