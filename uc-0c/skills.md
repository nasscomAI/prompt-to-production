skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, reports null count and which rows before returning.
    input: >
      file_path (string) — path to ward_budget.csv. Expected columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      List of row dicts sorted by period, plus null_report dict with count, list of (period, ward, category, notes) for null actual_spend rows.
      Returns (rows, null_report). Rows preserve all original string values; actual_spend is float or None if blank.
      Prints null report to stdout/stderr before returning.
    error_handling: >
      If file not found → FileNotFoundError. If header missing required columns → ValueError listing missing columns.
      Reports null count explicitly; if 5 deliberate nulls not found, warns but does not crash. Never imputes or fills nulls.
      Malformed rows are skipped with warning to stderr, not crash.

  - name: compute_growth
    description: Takes ward, category, growth_type and returns per-period table with formula shown and nulls flagged.
    input: >
      rows (list from load_dataset), ward (string, exactly one of 5 wards), category (string, exactly one of 5 categories),
      growth_type (string, must be "MoM" or "YoY" — no default).
    output: >
      List of output row dicts with keys: period, ward, category, budgeted_amount, actual_spend, growth_percent, formula, flag_notes.
      growth_percent is formatted as "+33.1%" or "-34.8%" or "" if NULL flagged. formula is e.g., "(19.7 - 14.8) / 14.8 * 100 = 33.1% (MoM)"
      or "NULL — flagged: <notes reason> — not computed". Sorted by period. Flag_notes contains original notes for null rows.
    error_handling: >
      If ward/category not in allowed lists or growth_type not in ["MoM", "YoY"] → raise ValueError and refuse with message:
      "Refusing to aggregate — ward/category must be single value; growth-type MoM or YoY must be specified explicitly".
      If filtered rows empty → raise ValueError "No rows for given ward/category". If previous period null, current growth is flagged NULL
      and formula explains missing prior value. Never guesses growth type; if growth_type is None/blank → refuse immediately.
