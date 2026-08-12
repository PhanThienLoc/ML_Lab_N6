# Prompt 14 - Inference Bundle and Non-Negative Count Policy

Review only deployment/inference for the completed product-sales project.

Target `sales_next_month` is a non-negative order-item count. Verify that saved inference uses the exact train-only preprocessing state and feature order from training, accepts a new feature-month scenario without rebuilding the data pipeline, and never returns a negative sales prediction. Apply the same post-processing policy to validation, final test, and CLI inference.

Do not redesign models or change the target. Add the smallest relevant tests, run the full suite and an end-to-end CLI demo, then report in Vietnamese: policy, files changed, evidence, commands, and PASS/FAIL.
