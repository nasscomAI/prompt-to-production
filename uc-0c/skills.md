# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Read the ward_budget CSV, validate that all required columns are present, count and identify all rows where actual_spend is null, and return the cleaned dataset with a null-row report before any computation begins.
    input: A file path string pointing to the ward_budget.csv file.
    output: A tuple of (DataFrame of all rows, list of null rows each containing period, ward, category, and notes reason).
    error_handling: If the file is not found, required columns are missing, or the file is empty, raise an error immediately with a descriptive message and stop execution — do not attempt to proceed with incomplete data.

  - name: compute_growth
    description: For a given ward, category, and growth type (MoM or YoY), compute the per-period spend growth and return a table where every row includes the period, actual_spend, growth percentage, and the formula used to calculate it.
    input: A DataFrame (from load_dataset), a ward name string, a category name string, and a growth_type string (must be exactly "MoM" or "YoY").
    output: A CSV-writable table with columns — period, actual_spend, growth_pct, formula, null_flag, null_reason — where null rows are flagged and skipped from growth computation.
    error_handling: If growth_type is not provided or is not one of "MoM" or "YoY", REFUSE and prompt the user to specify the type. If the ward or category does not exist in the dataset, raise an error listing valid values. Never interpolate or skip null rows silently — always include them in the output with null_flag=TRUE and the reason from the notes column.
