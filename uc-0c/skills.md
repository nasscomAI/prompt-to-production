# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates required columns are present, identifies and reports all null actual_spend values with their row details and reasons before returning the data.
    input: file_path (string, path to ward_budget.csv).
    output: A validated dataset object containing the parsed rows, plus a null_report listing each null row with period, ward, category, and reason from the notes column. Also returns metadata with total_rows, null_count, unique_wards, and unique_categories.
    error_handling: >
      If the file does not exist or is unreadable, raise a clear error with the file path.
      If required columns (period, ward, category, budgeted_amount, actual_spend) are missing, raise an error listing missing columns.
      If data types are invalid (non-numeric in amount columns), flag those rows and continue with valid rows.
      Always report null count upfront before any computation proceeds.

  - name: compute_growth
    description: Takes a ward, category, and growth type, filters the dataset to that combination, and returns a per-period table showing actual_spend, the growth formula, and computed growth rate with null rows flagged.
    input: dataset (from load_dataset), ward (string), category (string), growth_type (string, either "MoM" or "YoY").
    output: A list of period records, each containing period, actual_spend (or NULL flag), formula (string showing the calculation), growth_rate (float percentage or "N/A — null value" or "N/A — no previous period"), and flag (string noting if null or not computable).
    error_handling: >
      If ward or category does not exist in the dataset, refuse with a clear error listing all valid ward and category values.
      If growth_type is not provided or is not "MoM"/"YoY", refuse and ask user to specify.
      If a period has null actual_spend, mark growth_rate as "N/A — null value (reason: [notes])" and also mark the NEXT period's growth as "N/A — previous period null".
      Never silently skip, impute, or zero-fill null values.
