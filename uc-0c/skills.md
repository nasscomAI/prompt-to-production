# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports
      the null actual_spend rows before any computation.
    input: Path string to ward_budget.csv with required columns period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: Tuple (rows, null_report) where rows are validated dicts (amounts
      parsed to float, blanks kept as None) and null_report lists each row
      with a null actual_spend including its line number and notes reason.
    error_handling: Missing/unreadable file exits cleanly with ERROR on
      stderr (exit 1). Missing required columns exit with the exact missing
      column names. Non-numeric amount cells are skipped with a WARNING that
      names the row, never silently coerced to zero.

  - name: compute_growth
    description: Takes one ward + one category + an explicit growth type and
      returns a per-period table with the formula shown on every computed row.
    input: Validated dataset rows plus ward (exact name), category (exact
      name), and growth_type ("MoM" or "YoY" — must be explicit).
    output: List of per-period dicts {period, ward, category,
      budgeted_amount, actual_spend, growth_type, growth_pct, formula,
      status, notes} sorted by period; growth_pct formatted like "+33.1%".
    error_handling: Null current period → status NULL_FLAGGED with the notes
      reason and NO computed growth; null prior period → PREV_NULL_FLAGGED;
      first period → FIRST_PERIOD_NO_PRIOR; YoY on the single-year 2024
      dataset → INSUFFICIENT_HISTORY instead of a fabricated number. An
      unknown ward/category refuses with the list of valid options (exit 2).
