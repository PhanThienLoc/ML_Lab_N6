You are the autonomous migration owner for the ML_Lab_N6 project.

AUTHORITATIVE PLAN

Read this file completely before changing anything:

D:\ML-lab\customer-shopping-trends-migration-plan.md

Use the requirements, task order, interfaces, tests, artifacts and
acceptance checklist from that plan.

The older file below is superseded and must not be used as the active
migration specification:

D:\ML-lab\customer-behavior-sales-migration-plan-v2.md

Use superpowers:executing-plans to execute the new migration plan
task by task. Apply test-driven development within each phase.

PROJECT

Repository:

D:\ML-lab\ML_Lab_N6

CURRENT STATE

The current repository implements an Olist category-month,
next-month forecasting pipeline.

The migration must replace the active modeling contract with the
Customer Shopping Trends contract while preserving honest historical
evidence about the earlier Olist implementation.

Do not pretend the Olist implementation never existed.

==================================================
0. PREFLIGHT AND SAFETY
==================================================

Before modifying files:

1. Read completely:
   - customer-shopping-trends-migration-plan.md
   - ML_Lab_N6/AGENTS.md
   - ML_Lab_N6/README.md
   - ML_Lab_N6/ai/AI_RULES.md
   - ML_Lab_N6/ai/DECISION_LOG.md
   - ML_Lab_N6/ai/WORKFLOW.md
   - ML_Lab_N6/ai/PROMPT_TRACEABILITY.md

2. Inspect:
   - git status;
   - current branch;
   - recent commits;
   - existing source modules;
   - tests;
   - generated artifacts;
   - raw-data directory.

3. Verify the real Customer Shopping Trends CSV exists as one of:

   data/raw/shopping_trends.csv
   data/raw/shopping_trends_updated.csv

4. Verify its actual schema before implementation.

5. If the CSV is missing, stop without modifying the project and return:

   STATUS: BLOCKED

   Missing:
   Customer Shopping Trends CSV

   Expected location:
   data/raw/shopping_trends.csv

6. Verify whether lab2.ipynb and the lecturer PDF are available.

7. If lab2.ipynb is unavailable:
   - continue only when the five-step structure is fully specified by
     the migration plan;
   - do not claim the notebook is visually identical to lab2.ipynb;
   - report the missing reference as a limitation.

8. The Git worktree may contain uncommitted work.

   Do not:
   - reset;
   - discard;
   - overwrite unrelated changes;
   - delete unverified paths;
   - commit;
   - push;
   - merge;
   - modify main.

   If migration would overwrite uncommitted user work, stop and report
   the overlapping files.

9. Raw CSV files are immutable and ignored by Git.

==================================================
1. MODELING CONTRACT
==================================================

Replace the active Olist contract with:

Dataset:
Customer Shopping Trends Dataset

Kaggle:
https://www.kaggle.com/datasets/iamsouravbanerjee/customer-shopping-trends-dataset

Unit of observation:
One current customer purchase record

Problem:
Supervised regression

Target source:
Purchase Amount (USD)

Target name:
product_sales_amount_usd

Meaning:
Monetary sales value in USD of the current purchase record

Constants:

TARGET_SOURCE = "Purchase Amount (USD)"
TARGET_NAME = "product_sales_amount_usd"
ID_COLUMNS = {"Customer ID"}
LEAKAGE_COLUMNS = {
    "Purchase Amount (USD)",
    "product_sales_amount_usd",
}
RANDOM_STATE = 42

Important exclusions:

- Customer ID must not enter X.
- Purchase Amount (USD) must not enter X.
- product_sales_amount_usd must not enter X.
- Raw Review Rating must not enter X if it is used to build
  train-fitted product popularity mappings, as required by the plan.

The active project must never claim that it predicts:

- quantity;
- units sold;
- next-month sales;
- category-month sales;
- future demand.

The dataset does not contain quantity or transaction timestamps.

==================================================
2. DATA LOADING AND AUDIT
==================================================

Replace the four-table Olist loader with a single-file Customer Shopping
Trends loader.

Require and validate the exact 19-column source schema from the plan.

The loader must report from the actual local CSV:

- filename;
- row count;
- column count;
- column names;
- dtypes;
- missing count per column;
- duplicate rows;
- duplicate Customer ID count;
- target min, mean, median, standard deviation, p95, p99 and max;
- Age range;
- Review Rating range;
- Previous Purchases range;
- categorical cardinalities.

Domain validation:

- Age > 0
- Purchase Amount (USD) > 0
- 1 <= Review Rating <= 5
- Previous Purchases >= 0

Remove only domain-invalid records and record the exact count by reason.

Do not automatically delete valid IQR outliers.

Do not fabricate missing values to demonstrate imputation.

==================================================
3. EDA
==================================================

Rewrite src/eda.py and the generated data-analysis report for the
Customer Shopping Trends dataset.

Generate the ten EDA artifacts required by the plan:

01_sales_amount_distribution.png
02_sales_amount_boxplot.png
03_age_distribution.png
04_review_rating_distribution.png
05_previous_purchases_distribution.png
06_sales_by_category.png
07_sales_by_season.png
08_sales_by_discount.png
09_sales_by_promo_code.png
10_sales_by_frequency.png

Requirements:

- Generate every image from code and actual data.
- Do not edit PNGs manually.
- Remove/archive stale Olist EDA figures after verifying their paths.
- Use readable Vietnamese titles, axes, units and legends.
- Use mean and median where group averages could hide differences.
- Compute IQR evidence for numerical columns.
- Generate numerical correlation analysis using:
  - Age;
  - Review Rating;
  - Previous Purchases;
  - product_sales_amount_usd.
- State that correlation is exploratory, not causal.
- Do not claim promotion, season or demographics increase sales unless
  the actual evidence supports that wording.
- Write the Step 2 conclusion from computed results.

==================================================
4. FEATURE ENGINEERING
==================================================

Remove all Olist temporal features:

- sales_current;
- sales_next_month;
- lag features;
- rolling sales;
- target_month;
- category-month calendar;
- purchase timestamp features;
- temporal forecasting assumptions.

Create row-local features exactly as defined by the plan:

annual_purchase_frequency
log_previous_purchases
customer_activity_score
is_subscriber
has_discount
used_promo_code
discount_promo_interaction

Use the exact FREQUENCY_TO_YEARLY mapping from the plan.

customer_activity_score is a proxy. Never call it true CLV.

After splitting, fit these mappings on Train only:

item_purchase_frequency_train
category_purchase_frequency_train
item_mean_review_rating_train
category_mean_review_rating_train

Validation/Test fallback:

- unseen purchase frequency = 0;
- unseen mean rating = global Train mean Review Rating.

Tests must prove Validation/Test rows do not influence these mappings.

==================================================
5. SPLIT AND PREPROCESSING
==================================================

Replace temporal splitting with deterministic random splitting:

Train: 70%
Validation: 15%
Test: 15%
Seed: 42

Use:

np.random.default_rng(42)

Required properties:

- deterministic;
- mutually disjoint;
- complete coverage of retained rows;
- no duplicated row indices across splits.

Fit using Train only:

- numerical medians;
- categorical missing tokens;
- one-hot vocabulary;
- feature means;
- feature standard deviations;
- item/category popularity mappings.

Transform Validation and Test using saved Train state only.

All final matrices must:

- have identical feature columns;
- preserve identical column order;
- contain finite numerical values;
- exclude IDs, target source, target alias and leakage columns.

Do not describe the split as temporal.

==================================================
6. MODEL TRAINING AND SELECTION
==================================================

Reuse and verify:

- MeanBaseline
- LinearRegressionScratch
- DecisionTreeRegressorScratch
- metrics.py
- logger.py
- experiment.py
- analyze_logs.py

Run the official configurations from the migration plan:

BASE001
LR001
LR002
LR003
LR004
TREE001
TREE002
TREE003

Use Validation RMSE only to select the best run.

Do not inspect Test metrics during model selection.

After selection:

1. Combine Train and Validation.
2. Retrain the selected configuration.
3. Evaluate Test once.
4. Save model, preprocessor, popularity mappings, feature order and
   non-negative prediction policy in one bundle.

Experiment metadata:

{
    "dataset": "customer_shopping_trends",
    "aggregation": "current_purchase_record",
    "target": "product_sales_amount_usd",
    "split_method": "random_70_15_15",
    "random_state": 42
}

The dataset has approximately 3,900 rows. Remove the old 20,000/50,000
sampling policy.

==================================================
7. FINAL EVALUATION
==================================================

logs/final_test.json is the source of truth.

Report:

- MAE in USD;
- MSE in USD²;
- RMSE in USD;
- R².

Compare the selected model against Mean Baseline.

Compute:

rmse_improvement_pct = (
    baseline_test_rmse - selected_test_rmse
) / baseline_test_rmse * 100

Create:

reports/model_comparison.md
reports/figures/model_validation_rmse.png
reports/figures/actual_vs_predicted_sales_amount.png
reports/figures/residual_distribution.png
reports/figures/residual_vs_predicted.png

Residual definition:

residual = y_true - y_pred

Do not claim residuals are random, unbiased or normally distributed
unless the actual evidence supports it.

A weak R² or failure to beat Mean Baseline must be reported honestly.

==================================================
8. NOTEBOOK
==================================================

Rewrite project_pipeline_presentation.ipynb in Vietnamese.

It must contain exactly these five main top-level sections, in order:

# Step 1 : Thu thập dữ liệu
# Step 2 : Thống kê và trực quan hóa dữ liệu
# Step 3 : Tiền xử lí dữ liệu
# Step 4 : Train model
# Step 5 : Đánh giá

Step 3 must visibly contain:

## Fill các giá trị Missing
## Feature engineering
## Tiền xử lí dữ liệu

Rules:

- Do not insert deployment, Git, logging or test-engineering sections
  between the five main steps.
- Put optional engineering notes in an appendix after Step 5.
- Read values from generated metadata and logs.
- Do not hard-code experiment or final-test metrics.
- Run all notebook cells top to bottom.
- Save outputs.
- Verify zero notebook error outputs.
- Do not claim an exact lab2 visual match if lab2.ipynb is unavailable.

==================================================
9. INFERENCE
==================================================

Update:

src/predict.py
examples/prediction_scenario.csv

Scenario input must not request:

- Purchase Amount (USD);
- product_sales_amount_usd;
- engineered Train-only popularity outputs.

The saved inference bundle must derive engineered features and reuse:

- popularity mappings;
- imputation state;
- encoding vocabulary;
- numerical scaling;
- feature order.

Output:

Predicted Purchase Amount = $xx.xx

Apply:

prediction = np.maximum(raw_prediction, 0.0)

Inference must never fit or rebuild preprocessing.

Do not create app.py unless explicitly requested.

==================================================
10. DOCUMENTATION AND HISTORY
==================================================

Update all current-facing documentation:

- AGENTS.md
- README.md
- RUN_GUIDE.md
- ai/AI_RULES.md
- ai/DECISION_LOG.md
- ai/WORKFLOW.md
- ai/PROMPT_TRACEABILITY.md
- reports/TV1_HANDOFF.md
- reports/data_analysis.md
- reports/model_comparison.md
- EDA documentation
- preprocessing documentation
- pipeline code map

Add:

ai/prompts/18_customer_shopping_trends_migration.md
ai/results/18_customer_shopping_trends_migration_result.md

Prompt 18 remains in English.
Result 18 must be written in Vietnamese.

Preserve historical accuracy:

- Mark Olist prompts/results as archived or superseded.
- Mark the older Customer Behavior migration plan as superseded.
- Do not call result summaries raw AI transcripts.
- Do not rewrite historical metrics as if they came from the new data.
- Do not delete raw Olist CSV files without explicit user authorization.

Remove/archive old generated current artifacts only after verifying exact
paths.

Every current-facing document must describe:

Dataset:
Customer Shopping Trends Dataset

Target:
product_sales_amount_usd = Purchase Amount (USD)

Split:
random 70/15/15, seed 42

Limitations:
no timestamp, no quantity, no unit-demand target, synthetic dataset.

==================================================
11. TDD EXECUTION ORDER
==================================================

For each plan task:

1. Add the smallest failing test.
2. Run the focused test and confirm it fails for the expected reason.
3. Implement the minimum relevant change.
4. Run the focused test again.
5. Run the full test suite.
6. Review the task against the plan.
7. Continue only when the task passes.

Do not modify unrelated modules.

Do not claim a test was run unless its command completed.

==================================================
12. FINAL COMMANDS
==================================================

Run:

python -m src.run_data_pipeline --raw-dir data/raw
python -m pytest -q
python main.py
python -m src.analyze_logs
python -m src.predict --scenario-file examples/prediction_scenario.csv

Search for stale current-facing terminology using rg:

Olist
sales_next_month
sales_current
category_month
order_item
lag_1
rolling_sales
transaction_date
product_sales_units
retail_sales_customer_behavior

Historical/archive files may retain old terms only when clearly marked
historical.

==================================================
13. ACCEPTANCE GATE
==================================================

Return READY only when:

- The actual shopping CSV was used.
- The exact 19-column source schema was validated.
- One row represents one current purchase record.
- Target is product_sales_amount_usd.
- Purchase Amount (USD), Customer ID and leakage columns are absent
  from X.
- No quantity, timestamp or future-sales claim remains active.
- Random split is reproducible with seed 42.
- All learned transformations are fitted on Train only.
- Product-popularity mappings are fitted on Train only.
- Validation RMSE alone selects the best model.
- Test is evaluated only after model selection.
- Final metrics come from logs/final_test.json.
- The notebook contains exactly Step 1 through Step 5.
- All notebook cells run without errors.
- All required EDA and evaluation figures exist.
- Current documentation matches the generated artifacts.
- The full test suite passes.

==================================================
FINAL RESPONSE FORMAT — VIETNAMESE
==================================================

STATUS: READY / PARTIAL / BLOCKED

Preflight:
...

Dataset:
...

Observed schema and quality:
...

Modeling contract:
...

Rows retained/removed:
...

Feature count:
...

Split:
...

EDA artifacts:
...

Best validation run:
...

Final-test metrics:
...

Baseline comparison:
...

Tests:
...

Notebook verification:
...

Historical artifacts:
...

Files changed:
...

Known limitations:
...

Do not return PASS or READY unless the associated commands actually ran.
Do not fabricate dataset facts, feature counts, metrics or test results.