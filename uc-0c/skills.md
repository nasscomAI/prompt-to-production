skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports the null actual_spend rows with their notes before any computation.
    input: input_path (path to ../data/budget/ward_budget.csv).
    output: A list of row dicts; prints a warning listing every row with a null actual_spend (period, ward, category, null reason from notes) to stdout.
    error_handling: Missing file, empty file, or missing required columns (period, ward, category, budgeted_amount, actual_spend, notes) prints an error to stderr and exits with status 1.

  - name: compute_growth
    description: Takes ward + category + growth_type and returns a per-period growth table with the formula shown in every row.
    input: rows (list of row dicts from load_dataset), ward (exact string), category (exact string), growth_type ("MoM" or "YoY").
    output: A list of output dicts with keys period, ward, category, budgeted_amount, actual_spend, previous_actual_spend, growth_type, growth_pct, formula, status — one row per period, sorted by period, per-ward per-category only.
    error_handling: Null actual_spend (current or previous) or zero previous spend produces an empty growth_pct with a status explaining why — never a guessed number. A missing period produces no row for it rather than a fabricated one.