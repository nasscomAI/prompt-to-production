skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports null count and which rows have missing values before returning the dataset.
    input: File path to a CSV (e.g., ward_budget.csv)
    output: A validated, structured dataset accompanied by a pre-computation report of any null values (with reasons from the notes column).
    error_handling: Return a clear error if the file is missing or unreadable. Flag every null row before returning the data for computation.

  - name: compute_growth
    description: Computes financial growth metrics per-period for a specific ward and category based on the requested growth type.
    input: Ward string, Category string, and growth_type (e.g., MoM or YoY).
    output: A per-period table of growth metrics specifically for the requested ward and category, with the calculation formula explicitly shown alongside every result.
    error_handling: Refuse to aggregate across multiple wards or categories. If the growth_type is omitted, refuse to proceed and explicitly ask the user for it (never guess).
