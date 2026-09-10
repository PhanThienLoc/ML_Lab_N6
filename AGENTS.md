## Project contract — Customer Shopping Trends

- Dataset: Customer Shopping Trends Dataset, source file data/raw/shopping_trends.csv.
- One modeling row is one purchase record.
- Target: product_sales_amount_usd = Purchase Amount (USD), supervised regression.
- Split: random 70/15/15, seed 42.
- No sklearn. Keep MeanBaseline, LinearRegressionScratch and DecisionTreeRegressorScratch.
- Fit all preprocessing and popularity mappings on training data only.
- Customer ID and target are excluded from X.
- Raw input is immutable and not committed.

