# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates that all required columns are present, reports the total null count and the exact rows with null actual_spend (including their notes) before returning the data.
    input: >
      A single file path (string) pointing to ward_budget.csv.
      Expected columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A dict with two keys:
        rows      — list of dicts, one per CSV row, all columns preserved as strings/floats
        null_rows — list of dicts for rows where actual_spend is blank or non-numeric,
                    each containing: period, ward, category, notes (the null reason)
      On load, prints a null report to stdout:
        "Null actual_spend rows found: <count>"
        One line per null row: "<period> | <ward> | <category> | reason: <notes>"
      This report is printed before any computation can proceed.
    error_handling: >
      If the file path does not exist, raise FileNotFoundError with the path.
      If any required column is missing, raise ValueError listing the columns found.
      If actual_spend cannot be parsed as a number and notes is also blank,
      include the row in null_rows with notes: "(no reason given in source data)".
      Never silently skip a null row or substitute a default value (e.g. 0 or mean).

  - name: compute_growth
    description: Takes a single ward, a single category, and a growth type (MoM or YoY), filters the dataset to that ward+category combination, flags null rows, then returns a per-period growth table with the exact formula shown for every computed row.
    input: >
      Four values:
        rows        — the rows list returned by load_dataset
        ward        — exact ward name string (must match a value in the data)
        category    — exact category name string (must match a value in the data)
        growth_type — string, must be exactly "MoM" or "YoY"; no other values accepted
    output: >
      A list of dicts, one per period in the filtered ward+category subset, in
      chronological order. Each dict contains:
        period        — the period string (YYYY-MM)
        actual_spend  — numeric value or "NULL"
        growth        — numeric percentage rounded to 1 decimal place, or "N/A"
                        (for first period, or when current or previous row is null)
        formula       — exact formula string used, e.g.:
                        "MoM = (19.7 - 14.8) / 14.8 × 100 = +33.1%"  for computed rows
                        "N/A — null actual_spend (reason: <notes>)"     for null rows
                        "N/A — first period, no prior value"            for first row
    error_handling: >
      If growth_type is not "MoM" or "YoY" (including if it is blank or None),
      raise ValueError: "Growth type not specified. Please provide --growth-type MoM
      or --growth-type YoY. Never guess or default silently."
      If ward or category does not match any row in the dataset, raise ValueError
      listing the distinct wards and categories actually present in the data.
      If the filtered subset has fewer than 2 rows, return the single row with
      growth: "N/A — insufficient data for growth calculation".
      Never aggregate across wards or categories — if ward or category is "*" or
      "all", raise ValueError: "Cross-ward or cross-category aggregation is not
      permitted. Please specify a single ward and category."
