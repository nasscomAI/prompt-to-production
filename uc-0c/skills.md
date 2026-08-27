skills:
  - name: load_dataset
    description: Read the ward_budget.csv, validate columns, and report null counts with row details before returning the dataset.
    input: Path to a CSV file with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: A pandas DataFrame (or equivalent) with validated columns and a separate report listing any null actual_spend rows with their notes.
    error_handling: If required columns are missing, raise a clear error listing which columns are expected vs found. If the file is empty, raise an error.

  - name: compute_growth
    description: Take a filtered dataset (specific ward + category) and a growth type, return a per-period growth table with formula shown for each row.
    input: Filtered DataFrame (one ward, one category), growth_type string ("MoM" or "YoY").
    output: A DataFrame with columns: period, actual_spend, previous_spend, growth_value, growth_formula, null_flag.
    error_handling: If growth_type is not "MoM" or "YoY", raise a clear error. If a row has null actual_spend, set growth_value to NULL and null_flag to the reason from notes. Do not skip null rows silently.
