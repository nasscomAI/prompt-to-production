# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV file, validates expected columns, detects
      and reports all null actual_spend rows with their reasons before
      returning the data for computation.
    input: >
      A file path (str) to the ward budget CSV (e.g., ward_budget.csv).
    output: >
      A structured dataset with columns: period, ward, category,
      budgeted_amount, actual_spend, notes. Additionally returns:
        - total_row_count (int): Number of rows in the dataset.
        - null_rows (list): List of rows where actual_spend is null/blank,
          each with period, ward, category, and reason from notes column.
        - null_count (int): Total number of null actual_spend rows.
    error_handling: >
      If the file does not exist or cannot be read: print error and exit.
      If expected columns are missing: print which columns are missing and exit.
      If no null rows are found: report "No null values detected" and proceed.

  - name: compute_growth
    description: >
      Computes growth rates (MoM or YoY) for a specific ward and category
      combination, returning a per-period table with formula shown for
      every computed value.
    input: >
      Four parameters:
        - ward (str): The ward to filter on (e.g., "Ward 1 – Kasba").
        - category (str): The budget category to filter on (e.g., "Roads & Pothole Repair").
        - growth_type (str): Either "MoM" (month-over-month) or "YoY" (year-over-year).
        - data: The structured dataset from load_dataset.
    output: >
      A CSV table with columns:
        - period (str): The time period (YYYY-MM).
        - actual_spend (float or "NULL"): The spend value, or "NULL" if missing.
        - growth_rate (str): The computed percentage to 1 decimal place,
          or "N/A — null value" or "N/A — previous period null" or
          "N/A — first period" as appropriate.
        - formula (str): The formula used (e.g., "(19.7 - 14.8) / 14.8 × 100 = 33.1%")
          or explanation for why growth was not computed.
        - flag (str): "NULL_VALUE" with reason if actual_spend is null, else blank.
    error_handling: >
      If ward or category is not found in the data: return error with
      list of valid wards/categories. If growth_type is not "MoM" or "YoY":
      refuse and list valid options. Never compute growth for null periods
      or periods immediately following a null baseline.
