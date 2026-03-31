skills:
  - name: load_dataset
    description: Reads CSV, validates columns, and reports null count and which rows have nulls before returning data.
    input: File path to the budget CSV (string).
    output: List of dictionaries representing the dataset rows.
    error_handling: Flags missing columns and explicitly handles/reports null values in the actual_spend column.
    
  - name: compute_growth
    description: Takes ward, category, and growth_type, and returns a per-period table with formula shown.
    input: Filtered dataset rows, target ward, target category, and growth_type.
    output: List of dictionaries containing period, ward, category, actual_spend, growth, formula, and flag.
    error_handling: Bypasses calculations for null rows and propagates the note into the flag field, and refuses aggregation if missing ward or category.
