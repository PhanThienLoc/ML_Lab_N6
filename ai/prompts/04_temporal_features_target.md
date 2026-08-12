# Prompt 04 - Temporal Features and Target

Review only the temporal feature and target stage. At the end of month t, use information in t and earlier to predict category sales in t+1. Verify chronological sorting, contiguous months before shifting, `sales_lag_1/2/3`, leakage-safe `rolling_sales_mean_3`, exact next-calendar-month `sales_next_month`, target exclusion from X, and final rows without valid targets.

Inspect at least two actual categories and run the synthetic series 10, 20, 30, 40: at current=30, lag_1=20, lag_2=10, target=40. If a leakage/alignment defect exists, explain, fix, and rerun tests. Do not redesign unrelated code. Report formulas, manual verification, leakage findings, changes, test results, and PASS/FAIL.

## Output language

Write all user-facing findings, reports, result summaries, and documentation updates in Vietnamese. Keep code, commands, filenames, column names, and identifiers in English.
