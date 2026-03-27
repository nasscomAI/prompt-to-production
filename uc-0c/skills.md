# skills.md

skills:
  - name: load_dataset
    description: Reads a CSV budget file, validates its columns, and reports null actual_spend rows before returning the data.
    input: >
      File path to a CSV file containing columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      A validated DataFrame along with a null report containing:
        - total_rows: count of all rows in the dataset
        - null_count: count of rows where actual_spend is blank/null
        - null_rows: list of dicts, each with period, ward, category, and reason (from notes column)
      The DataFrame is returned unmodified — nulls are NOT filled or dropped.
    error_handling: >
      If the file does not exist, return: "ERROR: File not found at [path]."
      If any of the 6 required columns are missing, return:
      "ERROR: Missing required columns: [list]. Expected: period, ward, category, budgeted_amount, actual_spend, notes."

  - name: compute_growth
    description: Takes a ward, category, and growth type, then returns a per-period growth table with the formula shown for each row.
    input: >
      - ward: the specific ward name (must match a value in the ward column)
      - category: the specific category name (must match a value in the category column)
      - growth_type: "MoM" (month-over-month) or "YoY" (year-over-year)
      - df: the DataFrame returned by load_dataset
    output: >
      A list of dicts, one per period, each containing:
        - period (e.g. "2024-07")
        - actual_spend (float or null)
        - prev_spend (float or null — the comparison period's value)
        - formula (string showing the substituted calculation, e.g. "(19.7 - 14.8) / 14.8 × 100")
        - growth_pct (float, e.g. 33.1)
        - flag (one of: "" for normal rows, "[NULL — reason]" for null rows, "[N/A — no prior period]" for the first row)
    error_handling: >
      If the specified ward is not found in the data, return:
      "ERROR: Ward '[ward]' not found. Available wards: [list]."
      If the specified category is not found, return:
      "ERROR: Category '[category]' not found. Available categories: [list]."
      If a row has null actual_spend, flag it with the reason from the notes column
      and skip it as a growth computation basis. The next valid row computes growth
      against the last non-null predecessor.
