# skills.md

skills:
  - name: load_dataset
    description: Reads the municipal budget CSV, validates columns (period, ward, category, budgeted_amount, actual_spend, notes), and reports the count and location of null actual_spend rows.
    input: CSV file path
    output: Validated dataframe or structured data object
    error_handling: Refuse if columns are missing or if the file cannot be read.

  - name: compute_growth
    description: Calculates growth (MoM or YoY) for a specific ward and category, returning a per-period table that includes the calculation formula for each row.
    input: Ward name, Category name, Growth type (MoM/YoY), optional Output filename
    output: Table/CSV containing period, actual spend, growth percentage, and formula
    error_handling: Refuse and flag rows where actual_spend is null; refuse if growth_type is not provided.
