skills:
  - name: load_dataset
    description: Read the ward_budget CSV, validate required columns exist, report null actual_spend rows before returning the data.
    input: A file path to a CSV with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: A tuple of (dataframe_or_list, null_report) where null_report lists each null actual_spend row with its period, ward, category, and notes reason.
    error_handling: If the file is missing, columns are invalid, or no data is found, raise an error with a description of the problem and do not proceed to computation.

  - name: compute_growth
    description: Take a filtered dataset for one ward and one category and a growth type, return a per-period table with growth values and the formula shown.
    input: A filtered dataset (output of load_dataset filtered by ward and category), a growth_type string ("MoM" or "YoY").
    output: A list of dicts, each with keys: period, ward, category, budgeted_amount, actual_spend, growth_value, formula. Rows with null actual_spend include the null reason instead of a computed growth_value.
    error_handling: If growth_type is not "MoM" or "YoY", return an error asking the user to specify. If the dataset has fewer than 2 periods for the requested growth type, return an error explaining the insufficient data.
