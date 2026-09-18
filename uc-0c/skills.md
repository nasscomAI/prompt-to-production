# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows.
    input: input_path string to ward_budget.csv.
    output: List of validated records plus a null-row audit list with period/ward/category/reason.
    error_handling: Fails fast with explicit validation error if required columns are missing or file is unreadable.

  - name: compute_growth
    description: Computes period-wise growth for one ward and one category using explicit MoM or YoY formula.
    input: records list, ward string, category string, growth_type string (MoM or YoY).
    output: Table rows with period, actual_spend, prior value, formula, growth_percent, status, and notes.
    error_handling: Refuses aggregate/missing growth-type requests and flags null/non-computable rows without crashing.
