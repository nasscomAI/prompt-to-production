# skills.md — UC-0C Skills Definitions

skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: Filepath string pointing to ../data/budget/ward_budget.csv.
    output: Validated dataset rows including metadata on which indices contain null actual_spend references.
    error_handling: Halts if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Filtered dataset for a specific ward/category pair and a growth_type string.
    output: A per-period table highlighting the growth result and the explicit mathematical formula used for every row.
    error_handling: Refuses to compute if growth_type is omitted or if the input row is flagged as NULL.
