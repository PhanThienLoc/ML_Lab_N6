# Prompt 10 - Purchase-Time Sales Cutoff Correction

You are reviewing and refining only the sales-event cutoff definition in the existing TV1 Olist pipeline.

The forecasting cutoff is the end of feature month t. The target remains `sales_next_month`, a numerical order-item quantity in t+1.

## Risk to resolve

Selecting only records whose final `order_status` is `delivered` can use an outcome learned after the purchase-month cutoff. For example, an order purchased in January may be delivered or cancelled only in February.

## Task

Implement the strict cutoff policy:

1. Define `sales_current` as the count of order-item demand at `order_purchase_timestamp` in month t.
2. Include every order with a valid purchase timestamp regardless of later final `order_status`.
3. Retain order-status distribution as audit evidence, but do not use final status to select the demand rows.
4. Update metadata, report, handoff, README, and decision log so they call the target purchase-time demand, not delivered sales.
5. Add a test that a later-cancelled order is retained as a purchase-time demand event.
6. Run all TV1 tests and rerun the pipeline from raw data.

## Constraints

- Do not modify raw CSV files.
- Do not change the aggregation level, target name, or forecast horizon.
- Do not use sklearn.
- Do not modify TV2 or TV3 code.

## Output language

Write all user-facing findings, result summaries, and documentation updates in Vietnamese. Keep code, commands, filenames, column names, and identifiers in English.

## Required output

- sales-event definition;
- explanation of the hindsight issue resolved;
- tests added or changed;
- commands executed and real result;
- files changed;
- PASS / FAIL.
