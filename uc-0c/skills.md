# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, reports the count and identity of null actual_spend rows before returning the filtered dataset for the requested ward and category.
    input: >
      Three values:
        input_path — path to ward_budget.csv (string)
        ward       — exact ward name to filter on, e.g. "Ward 1 – Kasba" (string)
        category   — exact category name to filter on, e.g. "Roads & Pothole Repair" (string)
      Example: load_dataset("../data/budget/ward_budget.csv", "Ward 1 – Kasba", "Roads & Pothole Repair")
    output: >
      A tuple of two values: (rows, null_report)
        rows        — list of dicts, each with columns: period, ward, category,
                      budgeted_amount, actual_spend (float or None), notes.
                      Filtered to the specified ward and category only.
        null_report — list of dicts for rows where actual_spend is null:
                      [{"period": "2024-11", "ward": "...", "category": "...", "reason": "<notes value>"}]
      Prints null_report to stdout before returning — nulls are never silent.
    error_handling: >
      If the file does not exist, abort with FileNotFoundError — do not return partial data.
      If required columns (period, ward, category, actual_spend, notes) are missing, abort
      with a clear column-listing error message.
      If no rows match the requested ward+category combination, abort with a clear message
      listing valid ward and category values found in the file.
      Never impute, interpolate, or fill null actual_spend values.

  - name: compute_growth
    description: Takes the filtered row list from load_dataset and computes per-period growth rates for the specified growth type (MoM or YoY), showing the formula alongside every result and skipping null rows.
    input: >
      Three values:
        rows        — list of dicts as returned by load_dataset (must be single ward + category)
        growth_type — exactly "MoM" (month-on-month) or "YoY" (year-on-year) (string)
        null_periods — set of period strings where actual_spend is null, to skip
      Example: compute_growth(rows, "MoM", {"2024-11"})
    output: >
      A list of dicts, one per computable period, each containing:
        period      — e.g. "2024-07"
        ward        — ward name
        category    — category name
        actual_spend — float value used in computation
        growth_pct  — float, e.g. 33.1 (or None if not computable)
        formula     — human-readable formula string showing the calculation,
                      e.g. "MoM: (19.7 − 14.8) / 14.8 × 100 = +33.1%"
        flag        — "NULL_SKIPPED" if this or prior period was null, otherwise blank
      First computable period has growth_pct: None and formula: "No prior period — base period."
    error_handling: >
      If growth_type is not exactly "MoM" or "YoY" (case-sensitive), raise ValueError
      and refuse to compute — never guess or default to either type.
      If fewer than 2 non-null rows exist for the ward+category, return an empty list
      with a message: "Insufficient non-null data to compute growth."
      Never aggregate across wards or categories — if rows contains data from more than
      one ward or category, raise ValueError before any computation begins.
