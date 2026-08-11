# Prompt 03 - Category-Month Aggregation

Review only the TV1 `product_category x calendar month` aggregation. Verify purchase timestamps, category consistency, sales-quantity definition, zero-sales months, complete calendar grid, and prevention of double-counted order items. Inspect at least two real categories. For Jan=10, Feb=20, Mar=0, Apr=30, April lag_1 must later represent March=0, not February=20.

Do not create lag features yet, change the horizon, work on models, use sklearn, or fill missing months from the future. Fix only a demonstrated aggregation defect. Report aggregation definition, category-month rows, month range, zero-sales handling, manual checks, changes, tests, and PASS/FAIL.

## Output language

Write all user-facing findings, reports, result summaries, and documentation updates in Vietnamese. Keep code, commands, filenames, column names, and identifiers in English.
