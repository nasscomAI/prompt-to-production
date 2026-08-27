# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward budget CSV file, validates schema, reports null count and row details.
    input: file_path (str)
    output: dataset (list of dicts) + null row report
    error_handling: Identifies missing actual_spend rows and preserves notes for null explanation.

  - name: compute_growth
    description: Calculates per-period MoM or YoY growth for a specific ward and category.
    input: dataset, ward (str), category (str), growth_type (str)
    output: table of per-period spend, growth percentage, formula used, and null flags
    error_handling: Refuses all-ward aggregation or missing growth_type parameters.
