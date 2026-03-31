# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, and reports null count and which rows contain nulls before returning the dataset.
    input: Path to the budget CSV file (string).
    output: Validated dataset structure containing rows and an explicit report of null counts.
    error_handling: Raise an error if required columns are missing or the file cannot be read.

  - name: compute_growth
    description: Takes ward, category, and growth_type to compute and return a per-period table with the explicit formula shown.
    input: Validated dataset, target ward, target category, and growth_type (e.g., MoM).
    output: A table/list of dictionaries containing period, actual spend, computed growth, and formula used.
    error_handling: Refuse to compute and ask for clarification if growth_type is missing. If actual_spend is null for a period, flag it and do not compute growth.
