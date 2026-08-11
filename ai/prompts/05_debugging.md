# Machine Learning Debugging

## Context

The team is debugging components of the Machine Learning pipeline for the Product Sales Prediction project.

## Task

Analyze possible causes of errors and propose small tests to identify the actual cause.

## Required Checks

### Linear Regression

Check:

- Feature scaling.
- Learning rate.
- Input and output shapes.
- Gradient calculation.
- Loss calculation.
- Weight updates.
- NaN or Inf values.
- Convergence behavior.

### Data Pipeline

Check:

- Join keys.
- Join cardinality.
- Duplicate rows.
- Missing values.
- Invalid values.
- Temporal leakage.
- Train / Validation / Test split.

## Constraints

- Do not replace the from-scratch implementation with a pre-built Machine Learning estimator.
- Identify the possible cause before modifying the code.
- Each hypothesis should have a small test to verify it.
- Avoid making multiple unrelated changes at the same time.

## Expected Output

Provide:

1. Possible causes.
2. Priority order for investigation.
3. A small test for each hypothesis.
4. Expected result of each test.
5. Method for confirming that the problem has been fixed.
