skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and strictly reports the count of null values along with identifying the specific null rows.
    input: File path pointing to the dataset (`--input`).
    output: A validated dataset object (or dictionary array), accompanied by a printed report detailing any missing `actual_spend` values and their corresponding `notes`.
    error_handling: If the file is missing or columns are incorrect, fail explicitly. If nulls exist, log them clearly before proceeding.

  - name: compute_growth
    description: Calculates exact growth metrics for a single requested ward and category across time periods, displaying the formula alongside the results.
    input: The validated dataset, specific `ward`, specific `category`, and the `growth_type` (e.g., MoM).
    output: A per-period table (CSV file) detailing Actual Spend, Computed Growth, and the exact formula applied.
    error_handling: If `growth_type` is missing or aggregation across wards/categories is attempted, refuse the computation and demand clarification. For periods containing nulls, flag them explicitly instead of computing growth.
