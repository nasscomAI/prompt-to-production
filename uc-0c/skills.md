skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected columns, and reports null count along with which rows contain null values.
    input: File path to the CSV (string, e.g., "../data/budget/ward_budget.csv").
    output: Structured dataset and a validation report highlighting any null 'actual_spend' rows and their corresponding 'notes'.
    error_handling: Terminate and report an error if the file is missing or required columns (period, ward, category, budgeted_amount, actual_spend, notes) are not present.

  - name: compute_growth
    description: Calculates per-period spending growth for a specific single ward and category, returning a table with the formula used.
    input: ward (string), category (string), growth_type (string), and structured dataset.
    output: Per-period table containing actual spend, computed growth, the exact formula used, and flags/notes for any null rows.
    error_handling: Refuse to guess if growth_type is missing; refuse to execute if aggregating across wards or categories is attempted; skip calculation and return a flag for rows where actual_spend is null.
