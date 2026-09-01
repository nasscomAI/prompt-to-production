# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports the null count and which rows before returning data.
    input: Path to ward_budget.csv.
    output: A list of row dicts (period, ward, category, budgeted_amount, actual_spend, notes), plus a printed/logged report of how many rows have null actual_spend and which period/ward/category they belong to.
    error_handling: If a required column is missing, raise a clear error. If actual_spend is null, keep the row (do not drop it) so it can be flagged later.

  - name: compute_growth
    description: Takes ward, category, and growth_type, and returns a per-period table of growth values with the formula shown for each row.
    input: ward (string), category (string), growth_type (MoM or YoY).
    output: A list of rows, one per period, each with period, actual_spend, growth_value, formula_used, and a flag (NULL if actual_spend or the prior comparison period is null).
    error_handling: If growth_type is not provided, refuse and raise an error asking the caller to specify MoM or YoY — never default silently. If a period's actual_spend is null, or the period needed for comparison is null, output NULL for growth_value with a flag explaining why, instead of computing a number.