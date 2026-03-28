skills:
  - name: load_dataset
    description: Reads the provided CSV file, validates expected columns, and strictly reports the count and locations of any null actual_spend rows.
    input: The file path to the CSV file (e.g., `../data/budget/ward_budget.csv`).
    output: The validated dataset representation, accompanied by a detailed report of the total null count and specific rows mapping to null values.
    error_handling: Raises a validation error if required columns are missing, and ensures the null row report is prominently returned to the calling context before computation.

  - name: compute_growth
    description: Calculates the requested period-over-period financial growth strictly for a specified ward and category, returning the results with explict formulas.
    input: Validated dataset rows filtered by specific `ward` and `category`, along with the strictly defined `growth_type`.
    output: A per-period data table reflecting the computation that includes the actual metric, relative variance, and the literal mathematical formula used for that specific row.
    error_handling: Immediately rejects the request if `growth_type` is omitted/unrecognized, or if the calculation demands an operation over unresolvable null actuals.
