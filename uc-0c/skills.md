# skills.md — UC-0C: Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates all required columns are present,
      and reports the total null count and the exact rows with null actual_spend
      (with their notes reason) before returning any data to downstream skills.
    input: >
      file_path : string — absolute or relative path to ward_budget.csv
    output: >
      On success: a validated DataFrame with all 6 columns intact, plus a
      null_report list — each entry containing:
        { period, ward, category, reason }
      The null_report is always printed to stdout before the DataFrame is returned,
      even if null_count is 0.
      On failure: raises ValueError with a message describing the missing column
      or unreadable file — does not return partial data.
    error_handling: >
      - Missing required column → raise ValueError("Missing column: <name>. Cannot proceed.")
      - File not found → raise FileNotFoundError with the attempted path
      - Null actual_spend rows → report ALL of them in null_report; do not drop,
        zero-fill, or forward-fill any null value

  - name: compute_growth
    description: >
      Computes month-over-month (MoM) or year-over-year (YoY) growth for a single
      specified ward and category, returning a per-period table with the formula
      shown alongside every computed value.
    input: >
      data          : DataFrame — output of load_dataset (pre-validated)
      ward          : string — exact ward name, e.g. "Ward 1 – Kasba"
      category      : string — exact category name, e.g. "Roads & Pothole Repair"
      growth_type   : string — must be exactly "MoM" or "YoY"; no default
    output: >
      A DataFrame with columns:
        period | actual_spend | growth_pct | formula_used | flag
      Where:
        - growth_pct  : float, rounded to 1 decimal place, e.g. +33.1 or −34.8
        - formula_used: string showing the arithmetic applied, e.g.
            MoM → "(19.7 - 14.8) / 14.8 × 100"
            YoY → "(19.7 - 17.2) / 17.2 × 100"
        - flag        : "NULL_FLAGGED" if actual_spend is null (growth_pct left blank);
                        "BASE_NULL" if the prior period used for denominator is null
                        (growth_pct left blank); empty string otherwise
    error_handling: >
      - growth_type not "MoM" or "YoY" → raise ValueError("growth_type must be
        'MoM' or 'YoY'. Received: <value>. I will not pick one silently.")
      - ward not found in data → raise ValueError("Ward '<value>' not found.
        Available wards: <list>")
      - category not found in data → raise ValueError("Category '<value>' not found.
        Available categories: <list>")
      - Null actual_spend in output row → set flag = "NULL_FLAGGED", leave
        growth_pct blank. Do NOT interpolate, forward-fill, or use budgeted_amount
        as a substitute.
      - Null prior-period value (denominator) → set flag = "BASE_NULL", leave
        growth_pct blank. Do NOT skip the row silently.