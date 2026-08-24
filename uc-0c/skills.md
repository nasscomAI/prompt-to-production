skills:
  - name: load_dataset
    description: >
      Reads the budget CSV, validates that every required column is present, and reports
      the null count and exactly which rows are null — before any caller is allowed to
      compute anything from it.
    input: >
      path (str) — path to ward_budget.csv with columns period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      dict with keys: rows (list of parsed row dicts where actual_spend is a float or
      None), wards (sorted list), categories (sorted list), periods (sorted list),
      nulls (list of {period, ward, category, budgeted_amount, note}), null_count (int).
      The null report is printed to stdout on every run, not only when asked.
    error_handling: >
      Missing file exits with the path. A missing required column exits naming the
      column and listing what was found. A non-numeric actual_spend is treated as null
      with its raw text preserved in the note, never coerced to 0. A non-numeric
      budgeted_amount exits, since it indicates a corrupt file rather than an
      un-submitted figure. Zero data rows exits rather than returning an empty set.

  - name: compute_growth
    description: >
      Computes a per-period growth table for exactly one ward and one category under an
      explicitly named growth type, showing the formula with operands substituted in
      every row.
    input: >
      dataset (dict from load_dataset), ward (str, exact), category (str, exact),
      growth_type (str, "MoM" or "YoY"). None of these has a default.
    output: >
      list of row dicts: ward, category, period, budgeted_amount, actual_spend,
      previous_period, previous_actual, growth_pct, formula, status, note.
      status is one of OK, NULL_ACTUAL, NULL_BASE, NO_BASE, INSUFFICIENT_HISTORY.
      growth_pct is empty for every status other than OK.
    error_handling: >
      Refuses an unknown ward or category by listing the available values instead of
      returning an empty table. Refuses a missing or unrecognised growth_type instead of
      defaulting. A null actual yields NULL_ACTUAL with the source note; a null
      comparison base yields NULL_BASE; a base of exactly zero yields NO_BASE rather
      than a division-by-zero or an infinite percentage. Never skips a period, so the
      output period count always equals the source period count for that series.
