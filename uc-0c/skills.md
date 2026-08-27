skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: CSV file path
    output: Validated dataset, count of nulls, list of rows with null actual_spend and their notes.
    error_handling: Fail if column structure is missing required fields (period, ward, category, budgeted_amount, actual_spend, notes).

  - name: compute_growth
    description: Computes growth per period using the specified growth type.
    input: Dataset, ward string, category string, growth_type string
    output: Per-period table with growth values and the formula shown alongside each result.
    error_handling: Fail if inputs are invalid or missing. Refuse if growth_type is missing.
