# skills.md — UC-0C Budget Growth

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate its columns, and report null actuals before returning anything for computation.
    input: `path` (string, path to a CSV with columns period, ward, category, budgeted_amount, actual_spend, notes).
    output: A dict with `rows` (list of dicts, one per CSV row, ordered as read) and `null_report` (count plus the list of `{period, ward, category, reason}` for every row whose actual_spend is blank, reason copied from notes). Prints the null report to stdout.
    error_handling: Raises FileNotFoundError with a clear message for a missing path; raises ValueError listing any missing required columns. Never imputes or drops null rows — they are reported and returned as-is.

  - name: compute_growth
    description: Compute per-period growth for one ward and one category with the formula shown on every row and nulls flagged, never aggregated.
    input: `rows` (loaded dataset rows), `ward` (exact single ward string), `category` (exact single category string), `growth_type` (exactly `MoM` or `YoY`).
    output: An ordered per-period table (list of dicts with period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, flag, notes). MoM growth is `(curr-prev)/prev*100` on actual_spend within the slice, one decimal with sign; first period, null actuals, and null baselines yield blank growth with an explicit flag and reason-formula; YoY rows are all flagged NO_BASELINE since no prior-year data exists.
    error_handling: Refuses (raises ValueError, no rows returned) when ward/category is missing, multi-scope (`all`, `*`, comma lists), or not found in the dataset, and when growth_type is missing or not MoM/YoY — it never guesses a scope or formula.
