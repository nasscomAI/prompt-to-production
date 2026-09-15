skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports the null count and which rows are null before returning the data.
    input: file_path (str, path to ward_budget.csv).
    output: A tuple of (rows, null_rows) where rows is a list of dicts (period, ward, category, budgeted_amount, actual_spend, notes) and null_rows is the subset with actual_spend blank, each annotated with its notes reason.
    error_handling: If a required column is missing from the CSV header, raises a clear error naming the missing column. Null actual_spend values are never dropped or coerced to 0 — they are kept and reported.

  - name: compute_growth
    description: Takes ward, category, and growth_type, and returns a per-period table of actual_spend and growth for that single ward/category pair, with the formula shown.
    input: rows (from load_dataset), ward (str), category (str), growth_type (str, "MoM" or "YoY").
    output: A list of dicts with keys period, actual_spend, growth_pct, formula, flag — one row per period for the given ward+category, in period order.
    error_handling: If ward or category matches no rows, or growth_type is missing/invalid, refuses and returns an explanatory message instead of guessing a default. If a period's actual_spend or its comparison period's actual_spend is null, growth_pct is left blank and flag is set to NULL_SPEND with the notes reason instead of being computed.
