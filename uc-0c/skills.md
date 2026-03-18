# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and identifies all rows with null actual_spend values.
    input: File path to the budget .csv.
    output: A structured dataset (dataframe/list of dicts) with verified columns.
    error_handling: Report the exact count and reason for null rows found during loading.

  - name: compute_growth
    description: Takes specific ward, category, and growth_type (MoM/YoY) and returns a per-period table with formulas.
    input: ward (string), category (string), growth_type (MoM/YoY).
    output: A list of result rows containing period, actual_spend, growth_value, and formula.
    error_handling: Refuse computation if aggregations are too broad or growth_type is missing.
