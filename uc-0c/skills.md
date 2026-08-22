# skills.md — UC-0C Budget Growth Analyst

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports null rows before any computation.
    input: Path to a UTF-8 CSV with columns period (YYYY-MM), ward (str), category (str), budgeted_amount (float), actual_spend (float or blank), notes (str).
    output: List of row dicts with typed amounts, plus a report {total_rows, null_rows: [{period, ward, category, notes}]} describing every blank actual_spend.
    error_handling: Unreadable file or missing/renamed columns aborts with an explicit error naming the problem; malformed amount values are reported and excluded rather than coerced or invented.

  - name: compute_growth
    description: Computes per-period growth for one ward × one category series with the formula shown on every row.
    input: Dataset rows from load_dataset plus exact ward (str), category (str), and growth_type ("MoM"; YoY refused unless prior-year data exists).
    output: Per-period table [{period, budgeted_amount, actual_spend, growth_pct, formula, flag}] sorted by period, where formula is the explicit calculation string and null periods carry flag "NULL — not computed (<notes reason>)" or "N/A — prior period actual_spend is NULL".
    error_handling: Unknown ward/category returns a refusal listing valid values instead of an empty file; growth_type missing, invalid, or unsupported is refused with an ask — never silently substituted.
