

skills:
  - name: load_dataset
    description: "Reads the ward budget CSV, validates required columns, and reports null counts and affected rows before returning data."
    input: "string"
    format: "File path to CSV (e.g., ../data/budget/ward_budget.csv)"
    output: "object"
    format: "Validated dataset with metadata including null count and list of rows with null actual_spend and their notes"
    error_handling:
    -"If file path is invalid or file not found, return error and stop execution"
    -"If required columns are missing, return error specifying missing columns"
    -"If dataset format is incorrect or corrupted, return validation error"
    -"If null values exist in actual_spend, do not fail but explicitly report count and affected rows with notes"
    -"Do not attempt to fill or infer missing values"

  - name: compute_growth
    description: "Computes per-period growth for a specified ward and category using the specified growth type and returns results with formulas."
    input: "object"
    format: "Dataset object, ward (string), category (string), growth_type (string: MoM/YoY)"
    output: "table"
    format: "Per-period table filtered by ward and category including actual_spend, growth value, and formula used for each row"
    error_handling: 
    -"If growth_type is missing or ambiguous, refuse and request clarification"
    -"If ward or category is not found in dataset, return error"
    -"If input attempts aggregation across multiple wards or categories, refuse execution"
    -"If actual_spend is null for any row, flag the row, include reason from notes, and do not compute growth"
    -"If previous period data is missing for growth calculation, return null for growth without guessing"
    -"Do not return a single aggregated value; enforce per-period output only"
    -"Do not assume or change formula type; use only specified growth_type"