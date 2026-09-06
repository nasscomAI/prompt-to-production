# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the expected columns, detects and reports every null actual_spend row (with its notes reason) BEFORE any computation, and returns the rows in period order ready for growth calculation.
    input: input_path (str) — path to ward_budget.csv (period, ward, category, budgeted_amount, actual_spend, notes columns).
    output: A dict with 'rows' (list of parsed rows as dicts, parsed with utf-8-sig so en-dash ward names match exactly), 'null_rows' (list of dicts for rows with blank actual_spend, each including the 'notes' reason), and 'wards'/'categories' (unique valid values for refusal messages).
    error_handling: Raises FileNotFoundError if the file is absent, and a ValueError listing the expected columns if any required column is missing — it never proceeds with partially validated data.

  - name: compute_growth
    description: Computes the requested growth type (MoM — the only supported type; any other value is refused) for exactly one ward + one category, producing a per-period table where every row shows the period, budgeted and actual values, the comparison period, the growth percentage, and the exact formula string; null actual_spend rows are flagged 'NULL — not computed' with the notes reason.
    input: rows (list of dicts from load_dataset filtered to the requested ward and category), ward (str — MANDATORY, exactly one ward), category (str — MANDATORY, exactly one category), growth_type (str — MANDATORY, must equal 'MoM'; the caller must supply it, never inferred), all three are required inputs with no defaults.
    output: List of output-row dicts (period, ward, category, budgeted_amount, actual_spend, growth_type, growth_pct, previous_period, formula, flag). growth_pct is 'NULL' with flag 'not computed' for null-source or missing-previous rows.
    error_handling: Never guesses growth_type (caller must validate); for a null previous period or null current period it outputs growth_pct 'NULL' with a human-readable flag instead of fabricating a number; division-safe (guards divide-by-zero when previous value is 0).