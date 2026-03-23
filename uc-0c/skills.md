# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the schema, and specifically identifies rows where 'actual_spend' is missing, logging the associated notes.
    input: Path to ward_budget.csv.
    output: A cleaned dataframe or dictionary and a list of identified null rows with reasons.
    error_handling: Critical failure if file is missing or schema columns are renamed.

  - name: compute_growth
    description: Calculates growth (MoM or YoY) for a filtered subset (Single Ward + Single Category) and attaches the formula used to each result.
    input: ward name, category name, growth_type (MoM/YoY).
    output: A per-period table with columns for Spend, Growth Percentage, and Formula.
    error_handling: Refuses if inputs would result in cross-category or cross-ward aggregation.
