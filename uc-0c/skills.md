skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates that all required columns are present, and reports the total null count and the exact rows (period, ward, category, reason) where actual_spend is missing before returning the data.
    input:
      type: string
      format: Absolute or relative file path to a CSV file containing columns period (YYYY-MM), ward (string), category (string), budgeted_amount (float), actual_spend (float or blank), notes (string).
    output:
      type: object
      format: "Two lists — (1) valid_rows: list of dicts with all columns and actual_spend cast to float; (2) null_rows: list of dicts for every row where actual_spend is blank, each including period, ward, category, and notes."
    error_handling: Raises an error and halts if any of the six required columns are absent from the CSV header; reports which columns are missing. If the file path does not exist, raises a file-not-found error immediately. If no rows match the requested ward and category after filtering, reports the mismatch explicitly rather than returning an empty result silently.

  - name: compute_growth
    description: Accepts a filtered list of valid rows for a single ward and category plus an explicit growth type, then returns a per-period table where every row includes the actual_spend value, the computed growth percentage, and the exact arithmetic formula used.
    input:
      type: object
      format: "Three required fields — rows: list of dicts (output of load_dataset valid_rows, pre-filtered to one ward and one category, sorted by period ascending); ward: string (exact ward name); category: string (exact category name); growth_type: string, must be exactly 'MoM' (month-over-month) or 'YoY' (year-over-year)."
    output:
      type: list
      format: "List of dicts, one per period, each containing: period (YYYY-MM), ward (string), category (string), actual_spend (float), growth (string — signed percentage such as '+33.1%' or 'N/A' for the first period or missing prior-period data), formula (string — the full arithmetic expression used, e.g. '(19.7 - 14.8) / 14.8 × 100')."
    error_handling: Refuses and raises an error if growth_type is not 'MoM' or 'YoY' — never guesses or defaults. Refuses and raises an error if rows span more than one ward or more than one category, preventing accidental cross-ward aggregation. Marks any period where the prior reference period has a null actual_spend as 'N/A — prior period null' rather than computing a value. Never produces a single aggregated number across all periods.
