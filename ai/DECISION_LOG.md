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

## Decision 007 - Chính sách completed sales (đã thay thế)

**Quyết định MVP trước đây:** TV1 chỉ tổng hợp order `delivered`.
**Trạng thái:** Thay thế bởi Decision 012 sau audit cutoff. Lý do: dùng final `delivered` status để chọn purchase event của tháng trước có thể tạo hindsight leakage.

## Decision 008 - Calendar panel toàn cục trước shift (đã thay thế)

**Quyết định MVP trước đây:** Hoàn tất grid category x global observed month trước lag/target.
**Trạng thái:** Thay thế bởi Decision 011. Grid toàn cục tạo zero-demand pre-history và có thể đưa category xuất hiện ở validation/test ngược về train.

## Decision 009 - Missing transaction attribute

**Quyết định:** Zero-sales gap chỉ forward-fill từ quá khứ cùng category; gap đầu kỳ dùng train median.
**Lý do:** Future fill gây leakage; fallback train-only tái lập được.
**Tác động:** Matrix hữu hạn mà không fit trên validation/test.

## Decision 010 - Đơn vị split

**Quyết định:** Split toàn bộ `target_month` theo thời gian.
**Lý do:** Không được trộn cùng forecast period qua các split.
**Tác động:** Mọi experiment dùng boundary trong metadata.

## Decision 011 - Active window của category

**Quyết định:** Lịch của từng category bắt đầu ở tháng `order_purchase_timestamp` đầu tiên được quan sát của category đó và kết thúc ở tháng quan sát cuối toàn cục.
**Lý do:** Tháng thiếu sau khi category đã được quan sát có thể biểu diễn demand = 0; các tháng trước lần quan sát đầu tiên không có bằng chứng category đã tồn tại. Cách này không đưa category tương lai vào train dưới dạng zero row.
**Tác động:** Lag vẫn liền tháng trong active window, nhưng không còn synthetic pre-history. First observed month không được diễn giải là ngày launch thực tế.

## Decision 012 - Định nghĩa sales theo purchase-time demand

**Quyết định:** `sales_current` và `sales_next_month` đếm order-item demand tại `order_purchase_timestamp`, không lọc theo final `order_status`.
**Lý do:** Purchase event đã tồn tại tại cutoff; trạng thái delivered/canceled có thể chỉ được biết sau cutoff. Điều này loại bỏ hindsight leakage.
**Tác động:** Target là purchase-time demand (không phải delivered/fulfilled sales). Status vẫn được audit trong metadata/report nhưng không dùng để chọn record.

## Decision 013 - Seasonality dạng vòng

**Quyết định:** Dùng `month_sin` và `month_cos`; bỏ `quarter` khỏi feature schema.
**Lý do:** Month-of-year có tính chu kỳ, nên December và January cần gần nhau hơn là cách 11 đơn vị. `quarter` là hàm trực tiếp của month và không thêm tín hiệu độc lập.
**Tác động:** TV2/TV3 phải lấy feature list theo `metadata['feature_names']`, không hard-code schema cũ.

## Decision 014 - EDA trực quan tái lập được

**Quyết định:** Pipeline TV1 tự sinh ba biểu đồ EDA từ active-window panel: total demand theo tháng, top 10 category theo demand và active category có positive/zero demand.
**Lý do:** EDA phải dựa trên dữ liệu thật, tái tạo được và cho thấy rõ xu hướng, phân bố category và zero-demand month trước modeling.
**Tác động:** Ảnh PNG nằm trong `reports/figures/`, được nhúng vào `reports/data_analysis.md` và không cần tạo/chỉnh tay.

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
- 09: category active-window correction
- 10: sales cutoff/hindsight correction
- 11: reproducible EDA visuals

Bằng chứng thực thi nằm trong `ai/results/`.
