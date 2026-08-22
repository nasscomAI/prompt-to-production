skills:
  - name: calculate_growth
    description: Calculates month-over-month growth strictly within a single ward and category, refusing cross-ward aggregations.
    input: dataset, ward, category, growth_type
    output: period, ward, category, actual_spend, previous_period, previous_spend, growth, formula, status
    error_handling: Refuses to calculate if previous period is missing or 0. Flags deliberate NULL values without coercion to zero.

  - name: validate_budget_data
    description: Validates dataset structure and identifies missing or NULL data before any arithmetic is performed.
    input: CSV dataset
    output: Validated records for the exact ward and category requested.
    error_handling: Halts and raises an explicit refusal if the dataset query lacks a specific ward or category boundary.
