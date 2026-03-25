# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports null count and the specific rows with null actual_spend values.
    input: CSV file path (string).
    output: List of dictionaries (dataset rows) and a report of identified null rows.
    error_handling: Raise an error if required columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Calculates growth (e.g., MoM) for actual spend for a specific ward and category, returning a per-period table with formulas.
    input: Dataset (list of dicts), ward (string), category (string), growth_type (string).
    output: List of dictionaries specifying period, ward, category, actual spend, growth, and formula.
    error_handling: Refuse and ask if growth_type is not provided; flag null rows as non-computable with reasons from the 'notes' column.
