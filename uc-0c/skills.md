skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports the null actual_spend count and affected rows, and returns the dataset for analysis.
    input: Ward budget CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated dataset with null actual_spend rows and their notes-based reasons explicitly identified.
    error_handling: If the file is missing, unreadable, or required columns are absent, report the error and stop without calculating growth.

  - name: compute_growth
    description: Calculates growth for the requested ward and category using the explicitly specified growth type and shows the formula for every result.
    input: Validated dataset, ward string, category string, and growth_type such as MoM.
    output: Per-period table containing ward, category, period, actual spend, growth type, formula, growth result, and null flags where applicable.
    error_handling: Refuse if ward or category is missing, growth_type is missing or unsupported, or a required actual_spend value is null; flag the null with its notes reason instead of computing a result.