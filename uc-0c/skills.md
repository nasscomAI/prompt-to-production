# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates column structure, and reports null counts and which specific rows contain nulls before returning the data.
    input: >
      File path to the budget CSV (e.g., ../data/budget/ward_budget.csv).
      Expected columns: period (YYYY-MM), ward (string), category (string),
      budgeted_amount (float), actual_spend (float or blank), notes (string).
    output: >
      A structured dataset containing:
        - All rows parsed with correct types.
        - A null report listing every row where actual_spend is blank/null,
          including: period, ward, category, and the reason from the notes column.
        - A summary count: total rows, valid rows, null rows.
      The null report must be presented to the user BEFORE any computation proceeds.
    error_handling: >
      If the CSV cannot be read or required columns are missing, return an
      error and halt — do not attempt computation on malformed data. If
      unexpected nulls are found in columns other than actual_spend (e.g.,
      period, ward, category), flag them as data quality issues and halt.

  - name: compute_growth
    description: Takes a specific ward, category, and growth type (MoM or YoY), and returns a per-period growth table with the formula shown for every row.
    input: >
      - ward: Exact ward name string (e.g., "Ward 1 – Kasba").
      - category: Exact category name string (e.g., "Roads & Pothole Repair").
      - growth_type: One of "MoM" (month-over-month) or "YoY" (year-over-year).
      - dataset: The validated dataset as returned by load_dataset.
    output: >
      A CSV table with columns:
        - period: The month (YYYY-MM).
        - actual_spend: The actual spend value, or "NULL" if missing.
        - previous_period_spend: The comparison period value.
        - formula: The exact formula used (e.g., "(19.7 - 14.8) / 14.8 × 100").
        - growth_rate: The computed percentage, or "N/A — null in current or prior period".
        - flag: "NULL_PERIOD" if current period is null, "NULL_PRIOR" if prior period is null, blank otherwise.
    error_handling: >
      If growth_type is not provided, refuse and return an error asking the
      user to specify MoM or YoY — never default silently. If the specified
      ward or category does not exist in the dataset, return an error listing
      the valid ward and category values. If a period's actual_spend or its
      comparison period's actual_spend is null, set growth_rate to "N/A" and
      flag accordingly — never compute growth using null values.
