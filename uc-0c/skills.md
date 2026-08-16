# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and identifies null values.
    input: File path to ward_budget.csv.
    output: A structured table along with a count of null rows and their reasons.
    error_handling: If the file is missing or malformed, return an error and halt.

  - name: compute_growth
    description: Computes the growth metrics for a specified ward, category, and growth type.
    input: Ward name, category, and growth_type (MoM or YoY).
    output: A per-period table showing actual spend, computed growth, and the formula used.
    error_handling: If an aggregate query across wards/categories is requested, or if the growth type is missing, explicitly refuse to process.
