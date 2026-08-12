# Prompt 05 - Temporal Split and Preprocessing

Review only temporal split and preprocessing. Verify train target months are strictly before validation, validation strictly before test, and no target month overlaps. Inspect category encoding, numerical scaling, missing-value fallback, and feature alignment. All learned preprocessing state must come only from train; validation/test reuse it. Unknown categories must not fail and target must not be a feature.

Do not use sklearn, test data for preprocessing decisions, or modify models. Report exact split ranges, preprocessing state, leakage/schema checks, fixes, tests, and PASS/FAIL.

## Output language

Write all user-facing findings, reports, result summaries, and documentation updates in Vietnamese. Keep code, commands, filenames, column names, and identifiers in English.
