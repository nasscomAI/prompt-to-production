skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: CSV file path (string)
    output: Dataset object with validated columns and reports.
    error_handling: Refuse if mandatory columns (ward, category, actual_spend) are absent or file is missing.

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown.
    input: Ward name, Category name, Growth type, Dataset.
    output: Table/List of growth results with period, actual_spend, growth, and formula.
    error_handling: Refuse and flag rows where actual_spend is null; refuse if growth type is unspecified.
