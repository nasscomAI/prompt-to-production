skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns are present, reports the count and details of every null actual_spend row before returning the data.
    input: File path string pointing to ward_budget.csv.
    output: List of row dicts with validated columns, plus a printed null report listing each null row's period, ward, category, and notes reason.
    error_handling: If the file cannot be read, exit with a clear error message. If required columns are missing, exit listing which columns are absent. Never return data without first printing the null report.

  - name: compute_growth
    description: Takes a ward, category, and growth_type and returns a per-period table with actual_spend, growth value, and the formula used for each row.
    input: List of row dicts (output of load_dataset), ward string, category string, growth_type string (MoM or YoY).
    output: CSV with columns period, ward, category, actual_spend, growth_pct, formula, null_flag — one row per period.
    error_handling: If ward or category is not found in the data, exit with an error listing available values. If a period's actual_spend is null, write NULL_FLAGGED in growth_pct and formula columns — never skip the row or compute with a null value.
