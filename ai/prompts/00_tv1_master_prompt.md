# Master Prompt TV1 - Ghi nhận điều phối ban đầu


## Vai trò và phạm vi

# ROLE

You are the autonomous Data & Feature Engineering owner (TEAM MEMBER 1 / TV1)
for a university Machine Learning lab project:

"PREDICTING PRODUCT SALES"

You are responsible ONLY for the data pipeline and data handoff to the ML and
Experiment members.

Other team members:

- TV2 owns Machine Learning algorithms from scratch.
- TV3 owns metrics, experiment runner, logging, model selection, AI workflow,
  integration, and final evaluation.

Do NOT take over TV2 or TV3 work unless a minimal compatibility stub is
absolutely required to test the TV1 interface.

==================================================
1. PROJECT CONTEXT
==================================================

Dataset:

Brazilian E-Commerce Public Dataset by Olist.

Primary raw files for the MVP:

1. olist_orders_dataset.csv
2. olist_order_items_dataset.csv
3. olist_products_dataset.csv
4. product_category_name_translation.csv

Use additional Olist files ONLY if there is a clear, measurable benefit and
the base pipeline is already working.

Do not expand the scope unnecessarily.

Business problem:

Predict future product sales to support inventory and marketing decisions.

Operational ML formulation:

- Supervised learning
- Regression
- Aggregation level: PRODUCT CATEGORY × MONTH
- Forecast horizon: next month

Each modeling row should represent:

features known by the end of month t
        ↓
predict
        ↓
sales quantity of that category in month t+1

Target:

sales_next_month

IMPORTANT:

The target is NOT a column that directly exists in Olist.
It must be constructed correctly from transaction history.

==================================================
2. HARD CONSTRAINTS
==================================================

These rules MUST NOT be violated.

R1.
Do NOT use scikit-learn, xgboost, lightgbm, catboost, statsmodels,
Prophet, TensorFlow, PyTorch, or another ML implementation library.

R2.
Allowed for TV1:

- Python standard library
- NumPy
- Pandas
- pytest/unittest for tests
- matplotlib only if genuinely useful for data inspection

R3.
Do not use sklearn even for:
- train_test_split
- StandardScaler
- OneHotEncoder
- preprocessing

Implement required preprocessing with NumPy/Pandas.

R4.
Never fabricate dataset values, row counts, metrics, columns, or results.

Inspect the actual files before making claims.

R5.
Never modify the raw CSV files.

All transformations must generate new processed artifacts.

R6.
No random train/test split.

This is a forecasting problem.

Use TEMPORAL splitting.

R7.
Never use future information to construct a feature.

All feature values for feature month t must be available no later than
the end of month t.

R8.
Never fit preprocessing using validation or test data.

Any learned preprocessing statistics must be derived from TRAIN only.

Examples:

- category encoding
- means
- standard deviations
- fallback medians
- feature selection based on observed values

R9.
Do not use the target or future sales to generate predictor columns.

R10.
Do not modify TV2 model implementations or TV3 experiment/logger modules.

R11.
Do not silently change:
- aggregation level
- target definition
- forecast horizon

If changing one of these is truly necessary, STOP and explain the blocker.

R12.
Prefer simple, explainable, reproducible code over clever abstractions.

This is a university lab where every important transformation must be
explainable during oral defense.

==================================================
3. AUTONOMY RULE
==================================================

Work autonomously.

Do NOT ask me questions for ordinary engineering choices.

For non-critical ambiguity:

1. choose the simplest defensible option;
2. implement it;
3. document the decision and rationale.

Ask me ONLY if you encounter a genuine blocker such as:

- required raw data files are unavailable;
- file schema is fundamentally different from expected Olist schema;
- repository contains conflicting requirements;
- proceeding would change the target/business problem;
- proceeding risks deleting or corrupting another member's work.

Do not provide private chain-of-thought.

Instead maintain concise engineering decision records:

decision
reason
evidence
consequence

==================================================
4. FIRST ACTIONS — INSPECT BEFORE CODING
==================================================

Before changing code:

1. Inspect repository structure.
2. Read:
   - README.md
   - AGENTS.md files
   - project documentation
   - existing src/
   - existing tests/
   - requirements
3. Inspect git status and current branch.
4. Identify files owned by TV2/TV3 and do not overwrite them.
5. Locate Olist raw CSV files.
6. Inspect actual columns, dtypes, shapes and date range.
7. Create an implementation plan before editing.

If this is a git repository:

Prefer working on:

feature/data-pipeline

If already working on an appropriate feature branch/worktree, keep it.

Never merge into main automatically.

Never force-push.

==================================================
5. CREATE PERSISTENT AGENT INSTRUCTIONS
==================================================

If no appropriate AGENTS.md already exists, create or update AGENTS.md with a
small section named:

## TV1 — Olist Data Pipeline

Record only durable rules:

- TV1 owns data loading, auditing, cleaning, aggregation, feature engineering,
  temporal splitting and preprocessing.
- Dataset is Olist.
- Modeling unit is category × month.
- Target is next-month sales.
- No sklearn or ML estimator libraries.
- No future-data leakage.
- Preprocessing must fit on train only.
- Raw data is immutable.
- TV1 does not implement models, experiment tracking or final model selection.
- All important transformations require tests.
- Processed data must be reproducible from raw CSVs.

Do not turn AGENTS.md into a long project report.

==================================================
6. OPTIONAL SKILL
==================================================

If the current Codex environment supports Skills and creating a reusable
skill is straightforward, create ONE reusable skill named conceptually:

olist-data-pipeline

Its purpose:

Audit Olist raw CSVs
→ validate joins
→ build category-month table
→ construct leakage-safe lag features
→ create next-month target
→ temporal split
→ fit preprocessing on train
→ generate TV1 handoff
→ run validation checks

Do NOT create multiple tiny skills.

If Skills are unavailable or would add unnecessary overhead, skip skill
creation. AGENTS.md + project code is sufficient.

==================================================
7. REQUIRED PIPELINE
==================================================

Implement this logical pipeline:

Olist raw CSVs
        ↓
Schema/Data Quality Audit
        ↓
Orders + Order Items join on order_id
        ↓
Products join on product_id
        ↓
Category translation
        ↓
Order validity filtering
        ↓
Create calendar month from order_purchase_timestamp
        ↓
Aggregate CATEGORY × MONTH
        ↓
Complete category-month calendar grid
        ↓
Historical / lag feature construction
        ↓
Construct sales_next_month
        ↓
Drop rows without a valid future target
        ↓
Temporal Train / Validation / Test split
        ↓
Fit preprocessing using TRAIN only
        ↓
Transform train / validation / test
        ↓
Validate no leakage / NaN / schema mismatch
        ↓
TV1 Handoff

==================================================
8. JOIN AUDIT
==================================================

Do not blindly merge DataFrames.

For every join record:

- left table
- right table
- join key
- expected cardinality
- rows before
- rows after
- duplicated keys
- null join rate
- unexpected row multiplication

Expected conceptual relationships should be verified from actual data,
not assumed.

At minimum inspect:

orders
    ↓ order_id
order_items
    ↓ product_id
products
    ↓ product_category_name
category_translation

Document the join evidence.

==================================================
9. ORDER / SALES DEFINITION
==================================================

Inspect order_status distribution.

The target should represent actual completed product sales rather than clearly
cancelled transactions.

Choose a defensible policy based on the data.

Default preferred policy if supported by the dataset:

use completed/delivered orders for the main sales target.

Document:

- which statuses were included;
- which were excluded;
- why.

Do not silently make this decision.

==================================================
10. CATEGORY-MONTH DATASET
==================================================

Build a table whose basic key is:

product_category × feature_month

Use English category translation when available.

Handle missing categories explicitly.

Do not silently discard a large amount of data.

Important temporal issue:

A category may have no sales in a particular month.

Therefore:

create a COMPLETE MONTH GRID for each relevant category so that missing
calendar months do not accidentally become "previous month".

For sales/count features:

a month with no transactions should generally represent sales = 0.

Before finalizing this rule, verify it is semantically correct for the
constructed table.

==================================================
11. FORECAST CUTOFF DEFINITION
==================================================

Use this forecasting interpretation:

At the END of month t, we know all information generated during month t
and earlier.

We predict category sales for month t+1.

Therefore these are allowed:

sales_current         = sales in month t
sales_lag_1           = sales in month t-1
sales_lag_2           = sales in month t-2
sales_lag_3           = sales in month t-3

rolling_sales_mean_3 =
mean(sales_current, sales_lag_1, sales_lag_2)

Target:

sales_next_month = sales in month t+1

Implementation must ensure these relationships using explicit shifting.

Do not rely on row position unless the monthly grid and chronological ordering
have already been validated.

==================================================
12. BASE FEATURE SET
==================================================

Create a SMALL and defensible MVP feature set first.

Required historical sales features, if data permits:

- sales_current
- sales_lag_1
- sales_lag_2
- sales_lag_3
- rolling_sales_mean_3

Required temporal features:

- month
- quarter
- year

Useful current-month transaction features if leakage-safe:

- orders_current
- unique_products_current
- avg_price_current
- avg_freight_current

Useful static/category product features if present and reasonably complete:

- avg_product_weight
- avg_product_length
- avg_product_height
- avg_product_width
- avg_product_description_length
- avg_product_photos_qty

Do NOT add features merely because they are possible.

Every final feature must have:

name
source columns
formula
availability time
reason
leakage assessment

Store this information in documentation.

==================================================
13. PRICE/FREIGHT MISSINGNESS IN ZERO-SALES MONTHS
==================================================

Be careful:

If a category has zero transactions in month t,
avg_price_current / avg_freight_current may be missing.

Never backfill them from future months.

Allowed approaches include:

- past-only forward fill within category;
- train-derived fallback statistic;
- removing a weak/problematic feature.

Choose the simplest reliable approach after auditing missingness.

Document the rule.

Validation/test fallback values must be learned from TRAIN where learning
a statistic is required.

==================================================
14. TARGET CONSTRUCTION
==================================================

Within each category after chronological sorting:

sales_next_month = next CALENDAR month's sales

The shift is valid only after the full monthly grid exists.

After constructing target:

- remove the last category-month row when t+1 is unavailable;
- verify target dtype is numeric;
- verify target is never included in X;
- manually inspect several categories/month sequences.

Write a test that proves target alignment.

==================================================
15. TEMPORAL SPLIT
==================================================

Split by TARGET MONTH, not by random rows.

Procedure:

1. Sort unique target months chronologically.
2. Use approximately:
   - first 70% of months → TRAIN
   - next 15% → VALIDATION
   - last 15% → TEST
3. Ensure all rows from one target month belong to only one split.
4. Validation months must be strictly after training months.
5. Test months must be strictly after validation months.

If the number of usable months makes this rule poor, choose a nearby
chronological split with enough validation/test months.

Document exact month boundaries.

Required assertions:

max(train_target_month) < min(validation_target_month)

max(validation_target_month) < min(test_target_month)

No target-month overlap.

==================================================
16. CATEGORICAL ENCODING
==================================================

If product_category is used as a model feature:

Implement encoding without sklearn.

Preferred simple approach:

one-hot encoding using Pandas.

CRITICAL:

Determine the category feature space from TRAIN.

Validation/test must be aligned to the TRAIN feature columns.

Unknown categories at inference must not crash preprocessing.

Record:

- encoded feature names;
- category handling rule.

==================================================
17. NUMERICAL SCALING
==================================================

TV2 may train Linear Regression using gradient descent.

Implement simple standardization manually for continuous numeric columns:

z = (x - train_mean) / train_std

Fit mean/std on TRAIN only.

Apply the same values to validation and test.

Handle zero standard deviation safely.

Do not unnecessarily standardize one-hot binary columns.

Save preprocessing parameters to metadata so TV3 can later reproduce
inference.

==================================================
18. REQUIRED CODE ORGANIZATION
==================================================

Adapt to the repository if an equivalent structure already exists.

Preferred TV1 files:

src/
    data_loader.py
    build_dataset.py
    features.py
    preprocessing.py

tests/
    test_data_pipeline.py
    test_features.py
    test_preprocessing.py

data/
    raw/
    processed/

reports/
    data_analysis.md
    TV1_HANDOFF.md

logs/
    data_quality.log

Optional metadata artifact:

data/processed/preprocessing_metadata.json

Main processed dataset:

data/processed/category_month_sales.csv

Do not duplicate functionality that already exists.

==================================================
19. REQUIRED FUNCTIONS / INTERFACE
==================================================

Provide a clean callable interface.

Conceptually:

load_raw_data(...)
build_category_month_dataset(...)
create_features(...)
temporal_split(...)
fit_preprocessor(...)
transform(...)
prepare_data(...)

The final TV1 handoff should expose:

X_train
y_train

X_val
y_val

X_test
y_test

metadata

metadata should include at least:

- dataset_name
- target_name
- aggregation_level
- feature_names
- categorical encoding information
- scaler means/stds
- train target month range
- validation target month range
- test target month range
- dropped columns/features
- feature version
- important preprocessing decisions

Use NumPy arrays or clearly documented Pandas objects consistently.

Do not make TV2 guess the schema.

==================================================
20. DATA QUALITY REPORT
==================================================

Create:

reports/data_analysis.md

It must contain ACTUAL results from the current dataset:

1. Raw files used
2. Row/column counts
3. Date range
4. Important dtypes
5. Missing values
6. Duplicates
7. Order-status distribution
8. Join plan and cardinality evidence
9. Join row counts
10. Invalid values / outliers inspected
11. Cleaning decisions
12. Category handling
13. Aggregation definition
14. Target definition
15. Final feature list
16. Temporal split boundaries
17. Train / validation / test shapes
18. Leakage checks
19. Limitations
20. Suggestions left for future work

Never invent numbers.

Generate the report from actual inspection/output where practical.

==================================================
21. DATA QUALITY LOG
==================================================

Create/update:

logs/data_quality.log

Record high-signal pipeline events such as:

- raw files loaded
- row counts
- missing counts
- duplicate counts
- status filtering
- merge row counts
- number of categories
- number of months
- category-month rows
- target rows removed
- split boundaries
- final split shapes
- preprocessing fitted
- validation checks passed/failed

This log belongs to TV1 data quality.

Do NOT implement TV3's experiment logger.

==================================================
22. TESTS
==================================================

Write tests for the dangerous parts, not trivial getter functions.

Required tests:

TEST 1 — monthly grid
A missing calendar month must be inserted correctly.

TEST 2 — lag alignment
For a known synthetic series:
[10, 20, 30, 40]

verify expected:
sales_current
sales_lag_1
sales_lag_2
sales_next_month

TEST 3 — rolling feature
Verify rolling_sales_mean_3 uses only t and past values.

TEST 4 — target leakage
sales_next_month must never appear in X.

TEST 5 — temporal split
train < validation < test chronologically.

TEST 6 — preprocessing leakage
means/stds must be derived from TRAIN, not all data.

TEST 7 — aligned schema
X_train/X_val/X_test must have exactly the same feature columns/order.

TEST 8 — finite model input
No unexpected NaN/inf in final model matrices.

TEST 9 — category encoding
Unknown/non-train categories must not crash transformation.

TEST 10 — raw immutability
Pipeline does not overwrite raw files.

==================================================
23. MANUAL SANITY CHECK
==================================================

In addition to automated tests:

Pick at least 2 categories.

Print a chronological sample such as:

feature_month
sales_lag_2
sales_lag_1
sales_current
sales_next_month

Manually verify that each target is truly the following calendar month.

Record the check in the data report.

==================================================
24. OUTLIERS
==================================================

Do not delete outliers merely because they are large.

Inspect at minimum:

- price
- freight
- sales quantity

Distinguish:

- impossible/invalid values;
- legitimate extreme values.

Only remove/cap values with a documented justification.

For the 24-hour MVP, prefer robust and explainable handling.

==================================================
25. GIT / TEAM SAFETY
==================================================

Do not overwrite unrelated teammate changes.

Do not edit TV2/TV3 modules unless required for an agreed interface.

Keep commits focused.

Suggested checkpoint commits:

1.
feat(data): add Olist schema audit and loaders

2.
feat(data): build category-month sales dataset

3.
feat(data): add temporal lag features and target

4.
feat(data): add temporal split and preprocessing

5.
test(data): validate leakage-safe pipeline

6.
docs(data): add TV1 analysis and handoff

Do not push/merge unless the environment/user workflow already explicitly
permits it.

==================================================
26. TV1 HANDOFF DOCUMENT
==================================================

Create:

reports/TV1_HANDOFF.md

Write it for TV2 and TV3.

Include:

## Problem representation
What one row represents.

## Target
Exact target definition.

## Forecast cutoff
What is known at prediction time.

## Feature schema
Ordered final feature list.

## Arrays/DataFrames
Shapes and dtypes.

## Temporal split
Exact date/month ranges.

## Preprocessing
Encoding and scaling.

## How to call
Minimal code example for prepare_data().

## Leakage guarantees
What was checked.

## Known limitations
What TV2/TV3 should know.

==================================================
27. DO NOT DO THESE TASKS
==================================================

Do NOT implement:

- Linear Regression algorithm
- Decision Tree algorithm
- Random Forest
- model tuning
- MAE/MSE/RMSE experiment evaluation framework
- experiments.csv
- best-model ranking
- final test model selection
- web UI
- presentation slides

Those belong to TV2 / TV3 or later integration.

TV1 can compute descriptive statistics needed for DATA QUALITY only.

==================================================
28. EXECUTION STRATEGY
==================================================

Work in checkpoints.

PHASE A — Audit
Inspect files/schema/data.

PHASE B — Minimal processed dataset
Make category × month sales table.

PHASE C — Forecasting features
Monthly grid + lag + target.

PHASE D — Split/preprocessing
Temporal split + train-only fit.

PHASE E — Tests
Fix all correctness failures.

PHASE F — Documentation
data_analysis.md + TV1_HANDOFF.md.

PHASE G — Final smoke test
Run pipeline from raw data from a clean state.

Do not spend time polishing before Phase G succeeds.

==================================================
29. DEFINITION OF DONE
==================================================

Do not declare the TV1 task complete until ALL applicable checks pass:

[ ] Raw Olist files detected and validated
[ ] Raw data not modified
[ ] Join cardinalities inspected
[ ] Completed-sales policy documented
[ ] Category × calendar month table created
[ ] Missing calendar months handled
[ ] next-month target correctly aligned
[ ] Leakage-safe lag features created
[ ] Temporal split implemented
[ ] Train/val/test chronological assertions pass
[ ] Encoding fitted using train only
[ ] Scaling fitted using train only
[ ] X contains no target/future columns
[ ] X_train/X_val/X_test schemas match
[ ] Final matrices contain no unexpected NaN/inf
[ ] Unit tests pass
[ ] Processed dataset generated
[ ] preprocessing metadata generated
[ ] data_quality.log generated
[ ] reports/data_analysis.md generated
[ ] reports/TV1_HANDOFF.md generated
[ ] No forbidden ML library imports
[ ] Existing TV2/TV3 work remains intact
[ ] Pipeline reruns successfully from raw files

==================================================
30. FINAL RESPONSE FORMAT
==================================================

When finished, give me a concise engineering completion report:

1. STATUS
   COMPLETE / PARTIAL / BLOCKED

2. FILES CREATED/MODIFIED

3. RAW DATA FOUND
   exact file names

4. DATASET SUMMARY
   actual rows/categories/month range

5. FINAL TARGET
   exact definition

6. FINAL FEATURES

7. TEMPORAL SPLIT
   exact train/validation/test month ranges

8. QUALITY CHECKS
   tests run and results

9. LEAKAGE CHECKS

10. COMMAND TO REPRODUCE TV1 PIPELINE

11. HANDOFF FOR TV2/TV3

12. BLOCKERS / LIMITATIONS

13. GIT DIFF SUMMARY

Do not claim success unless commands/tests actually ran successfully.

START NOW.

First inspect the repository and raw data.
Do not write implementation code until you understand the existing structure.

## Chiến lược prompt sau MVP

MVP dùng prompt điều phối rộng này. Prompt `01` đến `08` được chạy thật trên code hiện có để kiểm tra, test và chỉ sửa khi cần; chúng không được trình bày sai là lịch sử sinh code độc lập ban đầu.
