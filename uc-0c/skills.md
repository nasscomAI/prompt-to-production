# skills.md

skills:
  - name: load_dataset
    description: Loads CSV, validates required columns, and identifies null rows before processing
    input: CSV file path
    output: dataset with null row details
    error_handling: If file is missing or columns are incorrect, return error and stop execution. Report all rows where actual_spend is null.

  - name: compute_growth
    description: Computes month-over-month growth for a specific ward and category
    input: filtered dataset (ward + category)
    output: table with period, actual_spend, growth, and formula
    error_handling: If actual_spend is null, do not compute growth and mark row as NULL with explanation. If previous value is missing, set growth to N/A. If invalid ward/category is provided, return error.