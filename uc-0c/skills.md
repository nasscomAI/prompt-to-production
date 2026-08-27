# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null count and which rows have null actual_spend before returning the data.
    input: >
      A file path (string) pointing to ward_budget.csv.
    output: >
      A dictionary containing:
        - data (list of dicts): All rows from the CSV with original types preserved.
        - columns (list of str): Column names found in the CSV.
        - total_rows (int): Total number of data rows.
        - null_report (list of dicts): Each null actual_spend row with its period,
          ward, category, and reason from the notes column.
        - null_count (int): Number of rows with null actual_spend.
        - wards (list of str): Distinct ward values found.
        - categories (list of str): Distinct category values found.
    error_handling: >
      If the file does not exist or is not a valid CSV, raise an error with a
      descriptive message. If required columns (period, ward, category,
      budgeted_amount, actual_spend) are missing, raise an error listing the
      missing columns. Always report null rows upfront — never silently skip them.

  - name: compute_growth
    description: Filters data to a specific ward + category, computes per-period growth (MoM or YoY) with formula shown, and flags null periods.
    input: >
      Four parameters:
        - data (list of dicts): The loaded dataset from load_dataset.
        - ward (string): The specific ward to filter to.
        - category (string): The specific category to filter to.
        - growth_type (string): "MoM" (month-over-month) or "YoY" (year-over-year).
    output: >
      A list of dicts (one per period), each containing:
        - period (string): The YYYY-MM period.
        - actual_spend (float or "NULL"): The actual spend value, or "NULL" if missing.
        - previous_spend (float or "NULL" or "N/A"): The prior period's spend.
        - growth_pct (float or "NULL" or "N/A"): The computed growth percentage.
        - formula (string): The formula with actual numbers substituted,
          e.g. "((19.7 - 14.8) / 14.8) × 100 = +33.1%", or "NULL — data missing"
          for null periods.
        - null_reason (string): The reason from the notes column if actual_spend
          is null; blank otherwise.
    error_handling: >
      If growth_type is not specified or not one of MoM/YoY, refuse and return
      an error message asking the caller to specify. If ward or category is not
      found in the data, return an error listing valid values. If a null
      actual_spend is encountered, mark that row AND the following row's growth
      as "NULL — cannot compute" (since the following row's previous_spend is
      unknown). Never impute or interpolate missing values.
