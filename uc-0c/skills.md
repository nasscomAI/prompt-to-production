# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that all required columns are
      present, counts and identifies null actual_spend rows, and returns
      the full dataset plus a null report before any computation begins.
    input: >
      A string: file_path — the path to ward_budget.csv.
    output: >
      A dict with two keys:
        rows        (list of dicts, one per CSV row, all columns preserved),
        null_report (list of dicts for rows where actual_spend is blank/null,
                     each with keys: period, ward, category, notes).
      The null_report is always present (empty list if no nulls found).
      Caller must inspect null_report before calling compute_growth.
    error_handling: >
      If the file does not exist, raise FileNotFoundError. If any of the
      required columns (period, ward, category, budgeted_amount, actual_spend,
      notes) are missing, raise ValueError listing the missing column names.
      Never silently drop null rows — they must appear in null_report.

  - name: compute_growth
    description: >
      Filters the dataset to a single ward and category, then computes
      per-period growth (MoM or YoY) with the formula shown for every row.
    input: >
      Four parameters:
        rows        (list of dicts from load_dataset),
        ward        (string, must exactly match a ward value in the data),
        category    (string, must exactly match a category value in the data),
        growth_type (string, must be exactly "MoM" or "YoY" — no default).
    output: >
      A list of dicts, one per period in the filtered data, each with keys:
        period       (string, YYYY-MM),
        actual_spend (float or "NULL"),
        prior_value  (float or "NULL" if no prior period exists),
        formula      (string, e.g. "(19.7 - 14.8) / 14.8 × 100"),
        growth_pct   (float rounded to 1 decimal, or "NULL_GROWTH" with reason).
      Null rows are included with actual_spend "NULL", formula "N/A — null row",
      growth_pct "NULL_GROWTH: <notes text>".
    error_handling: >
      If growth_type is not "MoM" or "YoY", raise ValueError:
        "growth_type must be 'MoM' or 'YoY'. Received: <value>."
      If ward or category does not exactly match any row in the data, raise
      ValueError: "Ward '<value>' / Category '<value>' not found in dataset."
      Never guess or fuzzy-match — exact string match only.
      If no prior period exists for the first row, set prior_value to "NULL"
      and growth_pct to "NULL_GROWTH: no prior period available".
