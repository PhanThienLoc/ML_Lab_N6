# AI Usage Rules

## 1. Purpose

This document defines the rules for using Artificial Intelligence (AI) tools during the development of the Machine Learning project.

AI is used as a supporting tool for learning, design, implementation, debugging, documentation, and code review.

## 2. Allowed Uses of AI

AI may be used to:

- Explain Machine Learning concepts and formulas.
- Help analyze the dataset and identify possible data issues.
- Suggest data preprocessing and feature engineering approaches.
- Help design software modules and interfaces.
- Provide pseudocode and implementation suggestions.
- Assist with debugging and error analysis.
- Suggest unit tests and edge cases.
- Review code for readability and correctness.
- Help improve project documentation.

## 3. Restricted Uses of AI

AI must not:

- Replace the team's understanding of the implemented algorithms.
- Generate or fabricate experimental results.
- Create fake dataset records or fake evaluation results.
- Use future information to construct features.
- Use the test set to select models or hyperparameters.
- Replace the required from-scratch implementations with pre-built Machine Learning estimators.
- Make final project decisions without review and verification by the team.

## 4. From-Scratch Implementation Rules

The required Machine Learning algorithms must be implemented from scratch.

The following pre-built estimators must not be used for the main implementation:

- sklearn LinearRegression
- sklearn DecisionTreeRegressor

NumPy may be used for numerical calculations and array operations.

## 5. Data Leakage Prevention

The team must prevent data leakage throughout the project.

In particular:

- Features must only use information available at prediction time.
- Future observations must not be used to construct historical features.
- The test set must not be used for model or hyperparameter selection.
- Validation data must be used for model comparison and selection.
- The test set must only be used for final evaluation.

## 6. Verification

AI-generated suggestions must be reviewed and tested by the team before being included in the project.

The team is responsible for understanding and explaining all submitted code, formulas, design decisions, and experimental results.

## 7. Documentation

Important AI-assisted decisions should be documented in:

- `WORKFLOW.md`
- `DECISION_LOG.md`
- The appropriate files under `prompts/`

The team does not need to store every AI conversation. Only prompts and decisions that have a meaningful impact on the project should be documented.
