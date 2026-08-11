# Prompt 08 - Final TV1 Audit

Perform the final correctness and reproducibility audit only. Do not add features, optimize, or redesign. Verify raw CSV -> load -> clean/join -> category-month aggregation -> complete grid -> temporal features -> `sales_next_month` -> temporal split -> train-only preprocessing -> TV1 handoff.

Check joins, multiplication, sales count, skipped months, lag/target alignment, future/target leakage, random split, preprocessing leakage, schema consistency, NaN/inf, and raw-data modification. Run the complete test suite and pipeline from raw data; inspect two real category timelines. Return READY/PARTIAL/BLOCKED with tests, command, artifacts, target, feature count, split, limitations, and changed files.

## Output language

Write all user-facing findings, reports, result summaries, and documentation updates in Vietnamese. Keep code, commands, filenames, column names, and identifiers in English.
