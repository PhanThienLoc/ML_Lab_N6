# Olist Join and Cleaning

## Context

The project uses Olist datasets containing information about orders, order items, products, and product category translations.

## Task

Design a data joining and cleaning plan before constructing the `product_category × month` dataset.

## Required Analysis

1. Identify the join key for each dataset.
2. Identify the cardinality of each join.
3. Check for duplicate keys.
4. Check for missing values.
5. Define the policy for order status.
6. Check for invalid values.
7. Identify potential data leakage risks.

## Constraints

- Do not use future information.
- Do not fabricate data that does not exist in the source datasets.
- Explain the reason for every important cleaning rule.
- Do not use the test set during feature construction.
- Preserve data consistency after joining.

## Expected Output

The analysis should provide:

- Join plan.
- Join keys.
- Join cardinality.
- Cleaning rules.
- Missing-value handling rules.
- Duplicate checks.
- Invalid-value checks.
- Data leakage risks.
