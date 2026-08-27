# skills.md — UC-0C Ward Budget Growth Analyser

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates its columns, and reports the null
      count and exactly which rows are null — with each null's stated reason —
      before returning any data for computation.
    input: >
      path (str) — path to ward_budget.csv, UTF-8, columns period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: >
      dict:
        rows       — list of row dicts in source order
        wards      — sorted list of distinct ward names
        categories — sorted list of distinct category names
        periods    — sorted list of distinct YYYY-MM periods
        nulls      — list of {period, ward, category, reason} for every blank
                     actual_spend, reason taken verbatim from the notes column
        invalid    — list of rows whose actual_spend is present but non-numeric
      The null report is printed by this skill, not by its caller, so the report
      cannot be skipped by a caller that forgets to ask for it.
    error_handling: >
      Missing file, missing header, or any missing required column -> explicit
      message naming the missing column, exit 1. Zero data rows -> exit 1 rather
      than returning an empty dataset that would compute cleanly and mean
      nothing. A non-numeric actual_spend is recorded in `invalid` and carried
      through as uncomputable; it is never coerced to zero.

  - name: compute_growth
    description: >
      Takes a ward, a category and a growth type, and returns a per-period table
      of growth values with the substituted formula shown on every row.
    input: >
      dataset (dict) — from load_dataset
      ward (str or None) — exactly one ward, or None meaning "every ward,
        computed separately". Never a request to combine wards.
      category (str or None) — same contract as ward.
      growth_type (str) — "MoM" or "YoY". No default. Absence is refused by the
        caller before this skill is reached.
    output: >
      list of row dicts, sorted by ward then category then period, each with:
        period, ward, category, budgeted_amount, actual_spend,
        prior_period, prior_actual_spend, growth_type, growth_pct,
        formula, flag, null_reason
      growth_pct is a signed percentage to one decimal place, or empty when the
      row is not computable. formula always carries either the substituted
      arithmetic or the reason no arithmetic was possible.
    error_handling: >
      Refuses rather than guesses. --aggregate, --ward ALL or --category ALL ->
      refusal message, exit 2, no output file. Unknown ward or category name ->
      lists the valid values and exits 1. Null actual_spend -> flag
      NULL_ACTUAL_SPEND with the notes reason. Null prior period ->
      PRIOR_PERIOD_NULL. Prior period absent from the dataset -> NO_PRIOR_PERIOD.
      YoY with no prior-year row -> NO_PRIOR_YEAR_DATA. Prior actual of exactly
      0 -> ZERO_BASE_PERIOD. Non-numeric value -> INVALID_NUMBER. In every one
      of these cases the row is still emitted with an empty growth_pct, because
      a row silently missing from a budget table is worse than a row that says
      it could not be computed.
