# skills.md — UC-0C Ward Budget MoM Growth Analyzer

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports the null count and which rows are null before returning.
    input: path to ward_budget.csv (UTF-8 or cp1252; ward names contain en-dashes).
    output: list of records {period, ward, category, budgeted_amount, actual_spend (float or None), notes}; prints "Null check BEFORE computing" with each null period + notes reason.
    error_handling: unreadable file or missing required columns → ERROR line + exit code 1; undecodable bytes → falls back from utf-8 to cp1252 before failing; empty CSV → ERROR line + exit code 1.

  - name: compute_growth
    description: Takes ward + category + growth_type and returns the per-period growth table with the formula shown on every computed row.
    input: scoped record list for one ward+category, growth_type ("MoM" or "YoY").
    output: rows {period, ward, category, budgeted_amount, actual_spend, growth_pct, growth_formula, flag, notes} where growth_formula is e.g. "(19.7 - 14.8) / 14.8 * 100 = +33.11%"; flags BASELINE_NO_PRIOR, NULL_ACTUAL_SPEND, PRIOR_IS_NULL, INSUFFICIENT_HISTORY mark non-computed rows.
    error_handling: refuses (exit 2, no output file) when growth_type is missing/unsupported or when scope words like "all wards"/"all categories" are passed; unknown ward/category → lists valid values and exits 1; null current or prior periods are flagged with reasons, never imputed.
