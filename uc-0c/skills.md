# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: CSV file path (e.g., ../data/budget/ward_budget.csv)
    output: Validated dataset structure with a report on null values and row details.
    error_handling: Refuses to process if columns are missing or if null values are not properly flagged and logged with notes.

  - name: compute_growth
    description: Takes ward, category, and growth_type to calculate per-period growth showing the formula used.
    input: Validated dataset, ward name, category name, and growth_type (MoM/YoY).
    output: Per-period table showing actual spend, calculated growth, and formula used alongside the result.
    error_handling: Refuses calculation if growth_type is not specified, or if an aggregation across wards/categories is requested implicitly. Flags null rows without computing.
