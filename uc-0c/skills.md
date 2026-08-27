# skills.md — UC-0C Budget Growth Analyst

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the expected columns, and reports how many actual_spend values are null and exactly which rows before returning.
    input: >
      input_path (path to ward_budget.csv). Expected columns:
      period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A list of parsed rows (dicts) with actual_spend as float or None, plus a
      printed validation report: total row count, null count, and the
      period/ward/category + notes reason of every null row.
    error_handling: >
      If the file is missing/unreadable, fail loudly (raise) — do not analyse a
      partial dataset. If a required column is absent, raise with the missing
      column name. Blank actual_spend becomes None (never 0) so it can be flagged
      downstream rather than silently treated as zero spend.

  - name: compute_growth
    description: Computes period-over-period growth for ONE ward and ONE category, returning a per-period table with the formula shown and every null flagged.
    input: >
      rows (from load_dataset), ward (single value), category (single value),
      growth_type (MoM or YoY). ward/category identify exactly one series.
    output: >
      A per-period table (list of dicts) with: period, ward, category,
      growth_type, actual_spend, prev_period, prev_actual_spend, growth_pct,
      formula, flag. growth_pct is rounded to one decimal; formula shows the exact
      arithmetic. Rows with a null current or prior value carry a flag and no
      computed number.
    error_handling: >
      Refuse (raise/return refusal) if growth_type is not MoM or YoY — never pick
      one silently. Refuse if ward or category resolves to more than one series or
      to an aggregate request. If the ward/category is not found, refuse and list
      available values. Null current spend -> flag NULL_CURRENT with the notes
      reason; null prior spend -> flag NULL_PREVIOUS (not computable); first
      period -> flag NO_PRIOR_PERIOD; YoY with no prior-year row -> flag
      NO_PRIOR_YEAR_DATA. Never impute or interpolate a missing value.
