skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and explicitly reports null values before returning the dataset.
    input:
      - file_path (string): Path to the budget dataset (e.g., ../data/budget/ward_budget.csv).
    output:
      - dataset (dataframe): The validated dataset.
      - null_report (string): Explicit report of the null count and specific rows containing null `actual_spend` values.
    error_handling:
      - "Silently handling nulls is prohibited; must report the exact rows and reasons from the `notes` column."
      - "If expected columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raise an error."

  - name: compute_growth
    description: Calculates growth (e.g., MoM) for a specific ward and category over time, outputting a per-period table alongside formulas used.
    input:
      - data (dataframe): The loaded dataset.
      - ward (string): The target ward.
      - category (string): The target category.
      - growth_type (string): The metric to calculate (e.g., MoM, YoY).
    output:
      - growth_table (dataframe): Per-period table containing actual spend, growth percentage, and the exact formula used for the calculation.
    error_handling:
      - "If `growth_type` is not specified, refuse to guess and ask the user for clarification (formula assumption failure mode)."
      - "If asked to aggregate across wards or categories, refuse execution immediately (wrong aggregation level failure mode)."
      - "For rows with null `actual_spend`, do not compute growth; instead, flag the row and report the null reason from the `notes` column."
