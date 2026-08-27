# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns, and strictly maps the deliberate null actual_spend rows.
    input: The file path to the budget dataset (e.g., ../data/budget/ward_budget.csv).
    output: A structured dataset ready for computation, accompanied by a validation report detailing the exact null count and the explicit rows containing nulls.
    error_handling: If the file is missing or malformed, raise a fatal error immediately instead of attempting to parse partial data.

  - name: compute_growth
    description: Calculates the specified growth type for a designated ward and category over given periods, explicitly surfacing the literal formula used.
    input: Validated dataset rows filtered strictly by ward and category, along with the specified 'growth_type' string.
    output: A per-period data table containing the period, actual spend, computed growth metric, and a dedicated column showing the verbatim formula used.
    error_handling: If a requested period contains a null actual_spend, the skill must flag the cell, inject the reason from the 'notes' column, and explicitly refrain from computing growth (do not substitute with zero).
