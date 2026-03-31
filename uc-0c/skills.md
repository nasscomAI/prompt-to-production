# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and identifies rows with null values before returning the dataframe.
    input: File path string (e.g., `../data/budget/ward_budget.csv`).
    output: Tuple containing (DataFrame, List of null row summaries).
    error_handling: Refuse and report if the file is missing or required columns are absent.

  - name: compute_growth
    description: Calculates growth for a specific ward and category based on the requested growth type (e.g., MoM).
    input: Dictionary containing `ward`, `category`, and `growth_type`.
    output: DataFrame with `period`, `actual_spend`, `growth_result`, and `formula`.
    error_handling: Refuse if `growth_type` is missing or if input ward/category combination yields no data.
