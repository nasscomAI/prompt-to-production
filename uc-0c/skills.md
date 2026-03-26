skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and explicitly reports null counts and locations over `actual_spend`.
    input: 
      - file_path (string): The path to the budget CSV.
    output: 
      - rows (list of dicts): The parsed CSV rows.
      - null_report (string): Explicit report of which rows have null `actual_spend` and their `notes`.
    error_handling: "Fail cleanly if schema does not match."

  - name: compute_growth
    description: Computes growth per-period, per-ward, per-category and returns the results with formulas.
    input:
      - data (list of dicts): The loaded dataset.
      - ward (string): The target ward.
      - category (string): The target category.
      - growth_type (string): The explicit growth type (e.g., MoM).
    output: 
      - results (list of dicts): Table containing period, ward, category, actual_spend, growth_percentage, and formula_used.
    error_handling: "Refuse if target ward/category is missing or 'all' is requested without explicit permission. Flag nulls inside the results."
