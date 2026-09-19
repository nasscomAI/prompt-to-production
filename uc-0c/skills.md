# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports every null actual_spend row with its reason before returning.
    input: >
      path (string) to a CSV with columns period (YYYY-MM), ward, category,
      budgeted_amount, actual_spend (float or blank), notes.
    output: >
      list of row dicts with an added numeric 'actual' field (float or None). Prints the
      row count, the null count, and one line per null row: period · ward · category → notes.
    error_handling: >
      Missing file or missing required column → refuses with exit code 2 and no output.
      Blank actual_spend is kept as None and reported — never converted to 0.

  - name: compute_growth
    description: Computes MoM or YoY growth for exactly one ward and one category, returning a per-period table with the formula shown.
    input: >
      rows (from load_dataset), ward (exact string), category (exact string),
      growth_type ("MoM" or "YoY" — required).
    output: >
      list of dicts, one per period: ward, category, period, actual_spend, compared_with,
      previous_actual_spend, growth_type, growth_pct (e.g. "+33.1%"), formula, status, note.
    error_handling: >
      Null current value → NULL_FLAGGED with the notes reason. Null previous value →
      PRIOR_NULL_FLAGGED. Previous period absent → NO_PRIOR_PERIOD. Previous value 0 →
      DIVIDE_BY_ZERO. Unknown ward/category, missing growth_type, or an aggregate request
      ('all', 'total', ...) → refused by the CLI before this skill runs.
