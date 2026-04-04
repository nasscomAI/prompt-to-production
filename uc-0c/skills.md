# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports null count and which rows have null actual_spend before returning the data.
    input: A file path to a CSV with columns — period, ward, category, budgeted_amount, actual_spend, notes.
    output: A validated dataset object plus a null report listing each null actual_spend row with its period, ward, category, and reason from the notes column. Reports total row count and null count upfront.
    error_handling: If required columns are missing, refuses and lists the missing columns. If file does not exist or is empty, returns an error and halts. Never silently proceeds with malformed data.

  - name: compute_growth
    description: Takes a ward + category + growth-type and returns a per-period growth table with the formula shown alongside each result.
    input: A dictionary with keys — ward (string), category (string), growth_type (MoM or YoY), and the validated dataset from load_dataset.
    output: A CSV table with columns — period, actual_spend, growth_rate, formula_used, null_flag. Each row shows the computed growth percentage and the exact formula (e.g. "(19.7 - 14.8) / 14.8 * 100 = 33.1%"). Null rows are included with null_flag set and growth_rate marked as "N/A — actual_spend missing". Rows immediately after a null are marked "N/A — previous value missing".
    error_handling: If growth_type is not provided, refuses and asks user to specify MoM or YoY. If the requested ward or category does not exist in the dataset, refuses and lists available values. If all rows for the combination are null, returns the null report only with no growth computation. Never silently aggregates across wards or categories.
