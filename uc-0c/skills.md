skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the expected schema, and confirms the deliberate null rows are present.
    input: A path to ward_budget.csv.
    output: A list of dataset rows as dictionaries after schema and null-count validation.
    error_handling: Raises an error when required columns are missing or when the null actual_spend count does not match the expected dataset contract.

  - name: compute_growth
    description: Filters the dataset to one ward and one category, then computes per-period MoM or YoY growth with formulas and null-aware status flags.
    input: Dataset rows plus an exact ward, exact category, and growth type.
    output: A per-period table containing actual spend, growth type, growth percent, formula, status, and notes.
    error_handling: Refuses invalid growth types, empty filtered results, and any request that implies guessing or unsupported aggregation.
