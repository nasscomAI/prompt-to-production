skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: File path to the input CSV
    output: Validated tabular data, including a report of the total null count and specific rows containing nulls
    error_handling: Reports an error and halts execution if columns are invalid or file is unreadable

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Validated tabular data, ward (string), category (string), growth_type (string)
    output: Per-period table containing actual spend, computed growth, and the formula used in every row
    error_handling: Refuses calculation and halts if growth_type is not provided, or if asked to aggregate across all wards/categories without explicit instruction.
