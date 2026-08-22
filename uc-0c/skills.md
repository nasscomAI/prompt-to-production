# skills.md — UC-0C Skills Definition

skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates required columns, detects null values in actual_spend, and logs null locations before filtering.
    input: `input_path` (string path to ward_budget.csv).
    output: List of row dictionaries with parsed numerical types and null flags.
    error_handling: Raises FileNotFoundError if CSV path is invalid; reports count and details of all missing actual_spend entries.

  - name: compute_growth
    description: Filters data by ward and category, sorts chronologically by period, and calculates Month-over-Month (MoM) growth while flagging null values and displaying exact formulas.
    input: Dataset list, target `ward`, target `category`, `growth_type`.
    output: Table containing period, ward, category, actual_spend, mom_growth_pct, formula, notes.
    error_handling: Refuses un-scoped multi-ward queries; flags null actual_spend rows as non-computable.

