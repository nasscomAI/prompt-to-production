# UC-0C skills

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate the schema, and report the number of null `actual_spend` rows.
    input: |
      Path to `../data/budget/ward_budget.csv`.
    output: |
      A structured dataset object containing rows, valid column names, and null row metadata.
    error_handling: |
      - If required columns are missing, raise a clear validation error.
      - If rows have invalid period or numeric formats, report the bad rows and stop.

  - name: compute_growth
    description: Compute period-level growth for a specific ward and category using the requested growth type.
    input: |
      A structured dataset from `load_dataset`, plus required parameters: `ward`, `category`, and `growth_type` (`MoM` or `YoY`).
    output: |
      A per-period output table with columns for period, ward, category, actual_spend, growth result, formula, and null reason when applicable.
    error_handling: |
      - If `growth_type` is missing, refuse and prompt for `MoM` or `YoY` explicitly.
      - If the requested ward/category combination is not found, raise a clear error.
      - For null `actual_spend` rows, flag them and include the `notes` reason instead of computing growth.

notes: |
  - The output must remain per-ward and per-category only; cross-ward aggregation is forbidden.
  - The implementation should surface the formula used for each row and preserve null handling from the dataset.
  - The five intentionally null rows must be reported and not used in growth calculations.
