# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates that all required columns exist, and reports the null actual_spend count and which specific rows are null before returning the data.
    input: File path (string) to a CSV with columns — period, ward, category, budgeted_amount, actual_spend, notes.
    output: A validated DataFrame plus a printed report listing the total number of null actual_spend rows and each null row's period, ward, category, and reason from the notes column.
    error_handling: >
      If the file does not exist, raise FileNotFoundError with the path.
      If any required column is missing, raise ValueError listing the missing columns.
      If there are zero data rows after reading, raise ValueError indicating empty dataset.

  - name: compute_growth
    description: Takes a specific ward, category, and growth type (MoM or YoY), filters the dataset, and returns a per-period table with actual_spend, the formula used, and the computed growth percentage.
    input: DataFrame, ward (string), category (string), growth_type (string — "MoM" or "YoY").
    output: A per-period table with columns — period, ward, category, actual_spend, previous_period_spend, formula, growth_pct, null_flag, null_reason. Null rows are flagged and growth is not computed for them.
    error_handling: >
      If the specified ward or category does not exist in the data, raise ValueError listing valid options.
      If growth_type is not "MoM" or "YoY", raise ValueError stating valid choices.
      If all rows for the ward+category combination have null actual_spend, raise ValueError indicating no computable data.
