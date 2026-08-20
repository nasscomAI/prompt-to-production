skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: File path of the dataset (String).
    output: Parsed list of dictionaries with flagged nulls.
    error_handling: Return error if file doesn't exist or is malformed.

  - name: compute_growth
    description: Takes ward, category, growth_type, returns per-period table with formula shown.
    input: JSON with 'ward', 'category', 'growth_type', and 'data'.
    output: JSON list containing period, actual_spend, growth, and formula.
    error_handling: Refuse and return an error if growth_type is missing or if input requests multi-ward aggregation.
