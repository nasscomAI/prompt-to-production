# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports null count and which rows have null actual_spend before returning the data.
    input: >
      A file path (string) pointing to the ward_budget.csv file.
      Example: "../data/budget/ward_budget.csv"
    output: >
      A list of row dicts with columns: period, ward, category, budgeted_amount, actual_spend, notes.
      Before returning, prints a null report listing:
        - Total row count
        - Number of null actual_spend rows
        - For each null row: period, ward, category, and reason from the notes column
    error_handling: >
      If the file does not exist or cannot be read, raise a clear error and exit.
      If required columns (period, ward, category, budgeted_amount, actual_spend) are missing,
      report the missing columns and exit. Null actual_spend rows are reported but NOT removed —
      they are passed through with a flag for downstream handling.

  - name: compute_growth
    description: Takes a ward, category, and growth type, filters the dataset, and returns a per-period table with growth percentages and formulas shown.
    input: >
      Four arguments:
        - data (list): The full dataset from load_dataset
        - ward (string): Exact ward name, e.g. "Ward 1 – Kasba"
        - category (string): Exact category name, e.g. "Roads & Pothole Repair"
        - growth_type (string): "MoM" (month-over-month). Must be explicitly provided.
    output: >
      A list of row dicts, one per period, each containing:
        - period (string): e.g. "2024-01"
        - actual_spend (float or "NULL"): the spend value or "NULL" if missing
        - previous_spend (float or "N/A"): the prior period's spend
        - growth_pct (float or "NULL" or "N/A"): the computed growth %
        - formula (string): the exact calculation, e.g. "(19.7 - 14.8) / 14.8 * 100 = 33.1%"
        - flag (string): "NULL_VALUE" if spend is null, "FIRST_PERIOD" if first month, "" otherwise
        - null_reason (string): the notes column value if actual_spend is null, "" otherwise
    error_handling: >
      If the ward or category does not exist in the dataset, report available values and exit.
      If growth_type is not provided or not recognized, refuse and list supported types.
      Null actual_spend rows produce flag="NULL_VALUE" with no growth computed.
      The month following a null row also cannot compute growth (no valid previous_spend)
      and must be flagged appropriately.
