# Prompt 11 - Reproducible EDA Visuals

You are responsible for adding and verifying only reproducible visual EDA for the completed TV1 Olist pipeline.

The project forecasts next-month purchase-time item demand at `product_category × month`. An implementation already exists.

## Task

1. Use actual pipeline data only; do not invent observations or metrics.
2. Create a script/module that regenerates EDA figures whenever the TV1 pipeline runs.
3. Generate exactly these useful figures:
   - total purchase-time order-item demand by month;
   - top 10 product categories by total demand;
   - active category-month rows with positive versus zero demand.
4. Save stable PNG artifacts under `reports/figures/`.
5. Embed the figures in `reports/data_analysis.md` and summarize observed values from the generated data.
6. State that the raw date range begins/ends mid-month when applicable, so partial boundary months are not overinterpreted.
7. Add the smallest automated test that proves the expected image artifacts are generated.
8. Run the full test suite and the pipeline from raw data.

## Constraints

- Do not alter raw CSV files.
- Do not use model predictions or the test set to make EDA plots.
- Do not add sklearn or other ML estimators.
- Do not make charts manually outside reproducible source code.

## Output language

Write all user-facing findings, result summaries, and documentation updates in Vietnamese. Keep code, commands, filenames, column names, and identifiers in English.

## Required output

- figures generated;
- data source for each figure;
- observed findings and boundary-month caveat;
- files changed;
- commands executed and real result;
- PASS / FAIL.
