# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its schema, and reports how many actual_spend values are null and exactly which (period, ward, category) rows they are — before any computation runs.
    input: "path to a CSV file (string). Expected columns: period, ward, category, budgeted_amount, actual_spend, notes."
    output: "A list of parsed row records (period, ward, category, budgeted_amount, actual_spend as float-or-None, notes) plus a null report: total null count and the identifying fields + notes reason for each null row."
    error_handling: "If the file is missing, unreadable, or any required column is absent, raise a clear error naming the problem and abort — never proceed with a partial or assumed schema. Blank actual_spend is parsed as None (not 0.0)."

  - name: compute_growth
    description: Computes period-over-period growth (MoM or YoY) of actual_spend for a single ward + category slice, returning a per-period table with the formula shown for each row.
    input: "parsed rows (from load_dataset), a ward (string), a category (string), and a growth_type ('MoM' or 'YoY')."
    output: "An ordered per-period table. Each row: period, actual_spend, prior-period value used, growth_pct, and the exact formula string. Rows where the current or comparison value is null are marked 'NULL — <notes reason>' with growth left blank."
    error_handling: "Refuse if growth_type is missing/invalid, if the ward or category is not found in the data, or if the request implies aggregation across wards/categories. Null current or comparison values yield a flagged, uncomputed row rather than an error or a zero."
