# Nhật ký quyết định

## Decision 001 - Loại bài toán

**Quyết định:** Supervised Learning Regression.
**Lý do:** `sales_next_month` là biến mục tiêu dạng số (numerical/count), nên bài lab được mô hình hóa bằng supervised regression.
**Tác động:** Dùng regression model và regression metric.

## Decision 002 - Mức tổng hợp

**Quyết định:** `product_category x month`.
**Lý do:** Phù hợp dự đoán doanh số category tháng kế tiếp.
**Tác động:** Đây là đơn vị của processed dataset.

## Decision 003 - Chia dữ liệu theo thời gian

**Quyết định:** Train, validation, test theo thứ tự thời gian.
**Lý do:** Forecasting không được dùng tương lai.
**Tác động:** Validation chọn model; test chỉ đánh giá cuối.

## Decision 004 - Model

**Quyết định:** Mean Baseline, Linear Regression Scratch, Decision Tree Scratch.
**Lý do:** Đúng yêu cầu môn học.
**Tác động:** TV2 cài đặt; TV3 đánh giá cùng split.

## Decision 005 - Metric

**Quyết định:** MAE, MSE, RMSE và R².
**Lý do:** Phù hợp regression.
**Tác động:** TV3 ghi metric vào experiment log.

## Decision 006 - Cách dùng test set

**Quyết định:** Không dùng test để chọn model/hyperparameter.
**Lý do:** Tránh evaluation bias.
**Tác động:** Chốt best run bằng validation trước final test.

## Decision 007 - Chính sách completed sales

**Quyết định:** TV1 chỉ tổng hợp order `delivered`.
**Lý do:** Đây là proxy rõ ràng cho sales đã hoàn tất; cancelled/unavailable không được làm tăng target.
**Bằng chứng:** Pipeline ghi status distribution và status include/exclude vào report/log.
**Tác động:** Đổi policy phải chạy lại pipeline và experiment.

## Decision 008 - Calendar panel trước shift

**Quyết định:** Hoàn tất grid category x global observed month trước lag/target.
**Lý do:** Tháng không có transaction nghĩa là sales=0; không được để shift nhảy qua tháng.
**Tác động:** Lag/target chỉ đúng tháng lịch liền kề.

## Decision 009 - Missing transaction attribute

**Quyết định:** Zero-sales gap chỉ forward-fill từ quá khứ cùng category; gap đầu kỳ dùng train median.
**Lý do:** Future fill gây leakage; fallback train-only tái lập được.
**Tác động:** Matrix hữu hạn mà không fit trên validation/test.

## Decision 010 - Đơn vị split

**Quyết định:** Split toàn bộ `target_month` theo thời gian.
**Lý do:** Không được trộn cùng forecast period qua các split.
**Tác động:** Mọi experiment dùng boundary trong metadata.

## Chiến lược prompt TV1

MVP TV1 ban đầu dùng một master prompt, được giữ tại `ai/prompts/00_tv1_master_prompt.md`. Sau khi xác nhận yêu cầu cần AI prompt cho từng giai đoạn, code hiện có được tách thành prompt scope nhỏ và **chạy thật** để inspect, verify, test và chỉ refine khi cần; đây không phải lịch sử prompt giả.

- 01: audit raw data
- 02: join và cleaning
- 03: category-month aggregation
- 04: temporal feature/target
- 05: temporal split/preprocessing
- 06: test
- 07: report/handoff
- 08: final audit

Bằng chứng thực thi nằm trong `ai/results/`.
