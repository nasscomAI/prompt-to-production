# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and reports the null actual_spend count with the exact rows (period, ward, category, notes reason) before any analysis runs.
    input: filesystem path to a UTF-8 CSV with columns period (YYYY-MM), ward, category, budgeted_amount, actual_spend (may be blank), notes.
    output: list of row dicts plus a null_report list of the rows where actual_spend is blank, each with the quoted notes reason; prints "Loaded N rows, M null actual_spend rows" to stdout.
    error_handling: missing file or missing required columns exits with a clear error naming the missing column; blank actual_spend values are kept as None and reported, never coerced to zero; malformed numeric fields are reported with the row identity and skipped from computation, not silently dropped.

  - name: compute_growth
    description: Computes MoM or YoY growth for one ward + one category series and emits a per-period table with the formula shown in every row.
    input: the loaded dataset, ward (exact string), category (exact string), growth_type ("MoM" or "YoY"), and an output CSV path.
    output: growth_output.csv with columns period, ward, category, actual_spend, growth_pct, formula, flag — one row per period of the series, plus the 5 dataset-wide null rows appended with flag NULL_SPEND_NOT_COMPUTED and their notes reason so nulls are visible rather than skipped.
    error_handling: ward/category of "all", "ALL", "*" or empty is refused with an explanation; unknown ward or category values are refused with the list of valid values; growth_type other than MoM/YoY is refused; a period whose previous value is null yields growth "N/A — previous period actual_spend is NULL" instead of a number.
