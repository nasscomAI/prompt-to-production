skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: File path to the CSV dataset
    output: Parsed list of dictionaries representing the dataset rows
    error_handling: Identifying and flagging deliberately null actual_spend values using the notes column.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Filtered dataset, target ward, target category, and specified growth_type
    output: A table (CSV format) showing period, ward, category, actual_spend, growth, and formula
    error_handling: Refuses to compute if growth_type is missing; refuses to aggregate across multiple wards/categories; flags null rows in the output instead of calculating.
