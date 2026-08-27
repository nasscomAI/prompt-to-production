# skills.md — UC-0C

skills:
  - name: load_dataset
    description: Reads ward_budget.csv with the expected columns and returns all rows plus the subset where actual_spend is null.
    input: "Path to CSV; expected columns period, ward, category, budgeted_amount, actual_spend, notes."
    output: "Tuple of (all_rows as dicts, null_rows as dicts)."
    error_handling: "Raise if required columns are missing; treat empty actual_spend field as null for reporting."

  - name: compute_growth
    description: Filters to one ward and category, sorts by period, and builds MoM or YoY rows with prior period values and formula text.
    input: "Full row list, ward string, category string, growth_type MoM or YoY."
    output: "List of growth dicts with period, prior period, spend values, growth_pct or blank, formula, and notes."
    error_handling: "If prior month or prior-year month is missing or either spend is null, leave growth_pct empty and set notes explaining why."
