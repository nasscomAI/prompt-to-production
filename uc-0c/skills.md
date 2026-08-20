# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null counts and null rows.
    input: A CSV file path string pointing to `../data/budget/ward_budget.csv`.
    output: A validated dataset object and metadata including null row count and details of null rows.
    error_handling: If required columns are missing, the file cannot be parsed, or null handling is ambiguous, return a clear error and stop.

  - name: compute_growth
    description: Computes growth for a specific ward and category and includes formula disclosure for each row.
    input: A validated dataset, ward string, category string, and growth_type string (`MoM`).
    output: A per-period output table with actual spend, computed growth, formula used, and null flags as needed.
    error_handling: If the ward/category does not exist, growth type is missing or unsupported, or null rows prevent computation, return an explicit refusal or explanation rather than guessing.
