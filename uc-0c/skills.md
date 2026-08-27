# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates expected columns, reports null count and which rows are null before returning the data.
    input: file_path (str) — path to ward_budget.csv.
    output: dict with keys — 'data' (list of row dicts), 'null_rows' (list of dicts with period, ward, category, notes for each null actual_spend row), 'null_count' (int).
    error_handling: If file is missing, raise FileNotFoundError. If any of the required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent, raise ValueError naming the missing columns. Always report nulls before returning — never silently proceed past them.

  - name: compute_growth
    description: Takes a specific ward, category, and growth type, filters the dataset, and returns a per-period table with actual_spend, computed growth value, and the formula string used.
    input: data (list of row dicts from load_dataset), ward (str), category (str), growth_type (str — must be 'MoM' or 'YoY').
    output: list of dicts per period, each containing — period, actual_spend, growth_value, formula (e.g. 'MoM = (19.7 - 14.8) / 14.8 = +33.1%'), and flag ('NOT_COMPUTED' if actual_spend is null for that row or the previous row needed for the formula).
    error_handling: If growth_type is not 'MoM' or 'YoY', raise ValueError with message 'Growth type not specified. Please re-run with --growth-type MoM or --growth-type YoY.' If ward or category not found in data, raise ValueError naming the unrecognised value. Never impute or skip null rows — mark them NOT_COMPUTED with the null reason from notes.
