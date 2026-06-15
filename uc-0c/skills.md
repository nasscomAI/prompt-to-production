# skills.md

skills:
  - name: load_ward_budget
    description: Loads ward_budget.csv and returns rows filtered to exactly one ward and one category, sorted ascending by period.
    input: ward (string, exact match), category (string, exact match), data_path (file path string; default ../data/budget/ward_budget.csv).
    output: List of dicts with keys period, ward, category, budgeted_amount, actual_spend, notes.
    error_handling: Raises ValueError if ward or category is not found; refuses any request that omits ward or category, or targets multiple wards/categories at once.

  - name: flag_null_spend
    description: Separates rows with missing actual_spend from computable rows and attaches the null reason from the notes column.
    input: List of row dicts as returned by load_ward_budget.
    output: Tuple (computable_rows, null_rows); each null_row includes a null_reason field copied from notes.
    error_handling: Returns an empty null_rows list when no nulls are present; never silently drops or skips null rows.

  - name: compute_mom_growth
    description: Computes month-over-month percentage change in actual_spend for each period in a single ward+category series.
    input: List of computable row dicts (actual_spend present), sorted ascending by period.
    output: Same rows enriched with growth_pct (float, rounded to 4 dp), formula (human-readable expression showing values used), and growth_type="MoM".
    error_handling: Sets growth_pct to None and formula to "N/A — no prior period" for the earliest row; never infers a value when the prior period is absent.

  - name: compute_yoy_growth
    description: Computes year-over-year percentage change in actual_spend by comparing each period to the same calendar month one year earlier.
    input: List of computable row dicts (actual_spend present), sorted ascending by period.
    output: Same rows enriched with growth_pct (float, rounded to 4 dp), formula (human-readable expression showing values used), and growth_type="YoY".
    error_handling: Sets growth_pct to None and formula to "N/A — no prior year period" when the matching prior-year row is absent; never assumes or interpolates a missing value.

  - name: generate_growth_output
    description: Merges computed growth rows and flagged null rows into a single CSV with explicit formula and null columns.
    input: growth_rows (list of dicts with growth fields), null_rows (list of null-flagged dicts), output_path (writable file path string).
    output: CSV file at output_path with columns period, ward, category, budgeted_amount, actual_spend, growth_pct, growth_type, formula, null_flag, null_reason; null rows appear with null_flag=True and growth_pct empty.
    error_handling: Raises IOError if output_path is not writable; aborts and reports if both growth_rows and null_rows are empty.
