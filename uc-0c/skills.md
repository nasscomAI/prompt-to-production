# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows (with notes) before any computation.
    input: str path to ../data/budget/ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: list of row dicts plus a null report — count and per-row detail (period, ward, category, reason from notes).
    error_handling: Missing file or missing required columns exits non-zero with a clear message; blank/whitespace numeric cells are treated as NULL (never zero).

  - name: compute_growth
    description: For one ward + category + growth_type, returns a per-period table of growth values with the exact formula shown on every row.
    input: dataset rows filtered to one ward and one category; growth_type strictly MoM (month-over-month vs previous month) or YoY (vs same month prior year); ward/category matched dash-and-case insensitively.
    output: list of dicts (period, budgeted_amount, actual_spend, growth_pct, formula, flag) written as growth_output.csv.
    error_handling: Refuses (exit 2) if growth_type is absent or unknown, if ward/category is 'all'/aggregate-style, or if no rows match — printing what was requested and which valid options exist; null current or prior periods produce a flagged empty growth cell citing the notes-column reason, never a guessed number.
