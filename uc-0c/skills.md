# skills.md

skills:
  - name: load_dataset
    description: Reads a CSV file, validates columns, and reports any null values in the actual_spend column.
    input: File path (str) pointing to a CSV file (e.g. ward_budget.csv).
    output: A structured dataset (e.g. pandas DataFrame or list of dicts) containing the parsed rows, along with a metadata object reporting the null count and row indices.
    error_handling: If required columns (`period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `notes`) are missing, raise a ValueError identifying the missing columns. Never silently drop rows with null values or impute data.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a specific ward and category, returning a per-period table with explicit formulas.
    input: The structured dataset from load_dataset, target ward (str), target category (str), and growth_type (str, must be 'MoM' or 'YoY').
    output: A per-period table (e.g. CSV or list of dicts) with the computed growth percentage. Each row must explicitly include the formula used to calculate the value. Null 'actual_spend' periods must include a flag and the reason from the 'notes' column instead of a computation.
    error_handling: Refuse and raise ValueError if the growth_type is invalid or not specified. Refuse and raise ValueError if asked to aggregate across all wards or categories. If a null value prevents computation of a period or the subsequent period's growth, flag both rows and do not compute an incorrect value.
