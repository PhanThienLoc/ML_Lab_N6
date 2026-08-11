# Prompt 02 - Join and Cleaning

Review and refine only the existing Olist join/cleaning stage. Verify orders -> order_items on `order_id`, items -> products on `product_id`, and products -> category translation on `product_category_name`. For every join inspect left/right rows, key uniqueness/cardinality, output rows, duplicate rows, unmatched joins, and unexpected row multiplication.

Inspect order-status handling, missing categories, duplicates, invalid price/freight/timestamps, and whether the completed-sales policy is defensible from actual Olist data. Do not redesign later features, construct models, use sklearn, fabricate data, modify raw files, or silently drop material data. If a proven issue exists, explain it, fix only the relevant code, rerun checks, and update report/log only when findings change.

Report join plan, cardinality evidence, cleaning rules, problems, changes, tests/checks, and PASS/FAIL.

## Output language

Write all user-facing findings, reports, result summaries, and documentation updates in Vietnamese. Keep code, commands, filenames, column names, and identifiers in English.
