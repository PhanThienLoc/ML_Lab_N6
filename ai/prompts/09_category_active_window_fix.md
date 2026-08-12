# Prompt 09 - Category Active-Window Correction

You are reviewing and refining only the category-month calendar construction in the existing TV1 Olist pipeline.

The pipeline forecasts next-month category demand. An implementation already exists.

## Problem to verify

Do not create a global Cartesian grid of every category by every observed month. That can invent zero-demand history before a category was first observed and can expose a category that appears only in validation/test to training data.

## Task

1. Inspect the category-month grid implementation.
2. Make each category's calendar start at its own first observed purchase month and end at the global last observed month.
3. Preserve zero-demand months only after that category has been observed.
4. Verify that lags remain aligned to consecutive calendar months within the category active window.
5. Add focused automated tests covering both cases:
   - an already active category with a missing middle month must receive `sales_current = 0`;
   - a category first observed in March must not receive invented January or February rows.
6. Run the relevant tests and the complete TV1 test suite.

## Constraints

- Do not modify raw CSV files.
- Do not change the next-month target horizon.
- Do not use future values to fill a missing month.
- Do not redesign TV2 or TV3.

## Output language

Write all user-facing findings, result summaries, and documentation updates in Vietnamese. Keep code, commands, filenames, column names, and identifiers in English.

## Required output

- active-window rule;
- evidence that pre-history is not invented;
- tests added or changed;
- commands executed and real result;
- files changed;
- PASS / FAIL.
