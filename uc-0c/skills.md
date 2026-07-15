# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports null rows before returning.
    input: path to ward_budget.csv.
    output: >
      (rows, null_rows) — rows is a list of dicts with the 6 expected columns;
      null_rows is the subset whose actual_spend is blank. Prints each null row with
      its period, ward, category, and the notes reason.
    error_handling: >
      If any expected column (period, ward, category, budgeted_amount, actual_spend,
      notes) is missing, raise RefusalError rather than computing on a malformed file.

  - name: compute_growth
    description: Computes per-period MoM/YoY growth for one exact ward + category.
    input: rows, ward (exact), category (exact), growth_type (MoM or YoY).
    output: >
      A list of per-period row dicts: period, ward, category, budgeted_amount,
      actual_spend, growth_type, growth_pct, formula, flag. Each computed row carries
      the full formula string.
    error_handling: >
      REFUSE (RefusalError) when ward/category is an aggregate token, when growth_type
      is not MoM/YoY, or when no rows match the exact ward+category. Null current or
      null prior period → flagged 'not computed' with the notes reason; zero prior →
      'growth undefined'. Never guesses a value or a formula.
