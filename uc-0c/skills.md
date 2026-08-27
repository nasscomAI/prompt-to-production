# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Read the budget CSV, validate required columns, and report how many actual_spend values are null and which rows before returning.
    input: path — path to ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: A dict {rows, nulls, columns} where rows is every row as a dict and nulls is the subset with blank actual_spend. Prints the null count and each null row with its reason from the notes column.
    error_handling: Raises ValueError listing any missing required column. Blank actual_spend is detected and reported, never coerced to zero.

  - name: compute_growth
    description: Compute MoM or YoY growth in actual spend for exactly one ward and one category, with the formula shown per row and nulls flagged.
    input: dataset (from load_dataset), ward (one ward string), category (one category string), growth_type ("MoM" or "YoY").
    output: A dict {refused, reason, table}. table rows include period, prev_period, actual_spend, prev_spend, formula, growth_pct, and flag.
    error_handling: Refuses (refused=True, with reason) if ward/category is an aggregate token, if growth_type is not MoM/YoY, or if no matching rows exist. Flags NULL_CURRENT, NULL_PRIOR, NO_PRIOR_PERIOD, and PRIOR_ZERO rows instead of computing a misleading number.
