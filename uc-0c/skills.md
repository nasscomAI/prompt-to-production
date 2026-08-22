skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns are present, and reports which rows have a null actual_spend before any computation happens.
    input: path (str) to ward_budget.csv.
    output: (rows, null_rows) — rows: list of dicts for every row; null_rows: list of dicts for rows where actual_spend is blank, each carrying its notes reason.
    error_handling: Missing required column → raises with a clear message naming the missing column; this is a schema failure, not a data failure, so it must not be silently patched.

  - name: compute_growth
    description: Computes per-period growth for exactly one ward + one category, refusing to guess when the growth type is unspecified or the data can't support it.
    input: rows (from load_dataset), ward (str), category (str), growth_type ("MoM" or "YoY").
    output: list of per-period dicts, each with period, actual_spend, growth_pct (or None), formula, flag, reason.
    error_handling: ward/category not present in data → refuse with the available values listed. growth_type missing/invalid → refuse. YoY requested on a single-year dataset → refuse, state why. Null actual_spend (current or comparison period) → row is flagged NULL_ACTUAL_SPEND with the notes reason, growth_pct left unset, never computed.
