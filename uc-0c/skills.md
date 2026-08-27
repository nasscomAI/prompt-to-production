# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates the expected columns, and reports the
      null actual_spend count and exactly which rows are null before returning.
    input: >
      input_path (str) — path to ward_budget.csv.
    output: >
      A tuple of (rows, null_report) where rows is a list of dicts (period, ward,
      category, budgeted_amount, actual_spend as float or None, notes) and
      null_report is a list of the null rows with their period, ward, category,
      and notes reason.
    error_handling: >
      If the file cannot be opened, fail fast with a clear message. If a required
      column is missing, raise a clear validation error. Blank actual_spend cells
      become None (never 0), and every null is surfaced in null_report rather than
      silently skipped.

  - name: compute_growth
    description: >
      Computes per-period growth for one ward + one category using the explicitly
      requested growth type, showing the formula in each row.
    input: >
      rows (from load_dataset), ward (str), category (str),
      growth_type (str, "MoM" or "YoY").
    output: >
      An ordered list of result rows: period, ward, category, actual_spend,
      growth_type, formula (string), growth_pct (float or "NOT COMPUTED"), flag.
    error_handling: >
      Refuses (returns an error result, computes nothing) if ward or category is
      missing/blank/'all', or if growth_type is not provided. Any period whose
      current or comparison value is null yields growth_pct = "NOT COMPUTED" with
      the null reason. YoY rows with no prior-year period are NOT COMPUTED
      (insufficient history) rather than guessed.
