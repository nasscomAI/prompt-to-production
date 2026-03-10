skills:
  - name: load_dataset
    description: Load the ward budget dataset from CSV and validate its structure before any computation.
    input: CSV file path containing ward_budget data with columns period, ward, category, budgeted_amount, actual_spend, and notes.
    output: Validated dataset with a report of null values including which rows contain null actual_spend and their notes.
    error_handling: If required columns are missing or the file cannot be read, return DATASET_ERROR and stop processing.

  - name: compute_growth
    description: Compute month-over-month (MoM) or year-over-year (YoY) growth for a specific ward and category.
    input: Validated dataset, ward name, category name, and growth_type parameter.
    output: Per-period table showing period, actual_spend, computed growth value, and the formula used for calculation.
    error_handling: If actual_spend is null for any period, flag the row and do not compute growth. If growth_type is missing or invalid, refuse computation and request clarification.