skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports all null actual_spend rows before analysis.
    input: "CSV file path for ward budget data with columns period, ward, category, budgeted_amount, actual_spend, notes."
    output: "validated dataset object plus profiling summary including null count and exact null row identifiers (period, ward, category, notes)."
    error_handling: "If required columns are missing, data types are invalid, or file cannot be read, return a blocking validation error and do not proceed to growth computation."

  - name: compute_growth
    description: Computes growth per period for the specified ward, category, and growth_type, with formula displayed per row.
    input: "validated dataset + ward string + category string + growth_type (required: MoM or YoY)."
    output: "per-period table for only the requested ward/category with computed growth values, formula text, and null flags where computation is not possible."
    error_handling: "If ward/category is missing, growth_type is not provided, or request implies cross-ward/category aggregation, refuse with explicit guidance instead of guessing or aggregating."
