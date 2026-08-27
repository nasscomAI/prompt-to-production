# skills.md — UC-0C Budget Growth Analyst

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates its columns, and reports the null actual_spend rows with their notes before anything is computed.
    input: input_path (string, path to ward_budget.csv)
    output: dict with rows (list of dicts with period, ward, category, budgeted_amount, actual_spend, notes), null_rows (list of {period, ward, category, notes} for every row where actual_spend is blank)
    error_handling: Fails loudly with a clear message if the file is missing, empty, or missing the expected columns (period, ward, category, budgeted_amount, actual_spend, notes). Null rows are never silently dropped — they are surfaced in null_rows and reported before compute.

  - name: compute_growth
    description: Computes growth of actual spend for one ward + category scope over a requested growth type and returns a per-period table with the formula shown on every row.
    input: dataset (dict from load_dataset), ward (string), category (string), growth_type (string — MoM or YoY, required, never guessed)
    output: list of result rows — {period, ward, category, actual_spend, growth_pct, formula, notes} — one per period in order; growth_pct is rounded to 1 decimal with an explicit sign
    error_handling: Refuses (returns no results or errors) if growth_type is missing or not MoM/YoY, if the ward or category does not exist, or if any cross-ward/cross-category scope is requested. For a null actual_spend on current or base period, the row is emitted with growth_pct blank and flag/notes containing the null reason from notes — never computed, zero-filled, or skipped.
