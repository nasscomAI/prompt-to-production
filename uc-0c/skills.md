# skills.md — UC-0C Number That Looks Right
# Workshop: RICE prompt → generated draft → manual CRAFT refinement | Verified on Ward 1 Kasba Roads MoM

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, reports null count and which rows before returning typed rows.
    input: Path to ward_budget.csv (CSV with columns period, ward, category, budgeted_amount, actual_spend, notes).
    output: List of dict rows with added `_actual: float|None` and `_budgeted: float`, plus stderr summary `300 rows, 5 null`.
    error_handling: Missing columns → ValueError with expected vs found; file not found → FileNotFoundError; nulls → log to stderr with period|ward|category|notes, never impute or skip.

  - name: compute_growth
    description: Filters to single ward+category, sorts by period, computes MoM (or YoY) growth with formula shown per row.
    input: Filtered rows for single ward+category (sorted), ward: str, category: str, growth_type: "MoM"|"YoY".
    output: List of dicts {period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, notes} — 12 rows for 12 months.
    error_handling: growth_type missing/unsupported → REFUSAL exit 2; ward/category missing → REFUSAL aggregation not allowed + list available; actual null → growth "" + formula "NULL: flagged — <notes>"; previous null/0 → "N/A: previous period ... is NULL"; first period → "N/A: first period, no previous".

  - name: verification
    description: Checks growth table against reference values before writing.
    input: Generated growth rows.
    output: Pass if 2024-07 +33.1% and 2024-10 -34.8% for Ward 1 Kasba Roads, null flagged for 2024-03/07 etc., formula present every row.
    error_handling: If reference mismatch or formula missing → raise ValueError with details.

notes: >
  CRAFT loop: naive "Calculate growth" → single aggregated number, no null mention, guessed MoM → fixed via per-ward enforcement + null flag before compute + formula column + refusal exits. Verified 300→12, 2024-07 +33.1% monsoon spike, 2024-10 -34.8% post-monsoon.
