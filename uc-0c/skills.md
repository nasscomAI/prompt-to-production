# skills.md

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates its columns, and reports every null actual_spend row before returning any data.
    input: Path to ward_budget.csv.
    output: >
      A list of row dicts (period, ward, category, budgeted_amount,
      actual_spend, notes) plus a null_report list of {period, ward,
      category, reason} for every row where actual_spend is blank.
    error_handling: >
      If a required column is missing, raise a clear error naming the
      missing column rather than silently proceeding. Null actual_spend
      values are not an error — they must be reported, not skipped or
      defaulted to zero.

  - name: compute_growth
    description: Computes MoM or YoY growth in actual_spend for one explicit ward and category, showing the formula for every period.
    input: The row list from load_dataset, plus explicit ward, category, and growth_type (MoM or YoY).
    output: >
      A per-period table (period, actual_spend, growth_pct, formula, note)
      scoped to exactly the given ward and category, in period order.
    error_handling: >
      If ward, category, or growth_type is missing, refuse and ask rather
      than guessing or aggregating. If a period's actual_spend or its
      comparison period is null, output growth_pct as "not computed" with
      the null reason in note, instead of skipping the row or the period.
