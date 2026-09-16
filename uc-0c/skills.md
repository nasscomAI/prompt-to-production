skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports all null actual_spend rows before returning records.
    input: "UTF-8 CSV path containing period, ward, category, budgeted_amount, actual_spend, and notes columns."
    output: "Tuple-like data containing all validated records and a list of null actual_spend audit records."
    error_handling: "Raises clear errors for missing files, missing columns, empty data, malformed amounts, null required fields, or ambiguous rows."
  - name: compute_growth
    description: Computes explicit MoM growth for one ward and one category without aggregation and with formulas shown.
    input: "Dataset records, exact ward string, exact category string, and growth_type MoM."
    output: "Rows using the required growth_output.csv schema, including 12 CALCULATION rows plus NULL_AUDIT rows."
    error_handling: "Refuses missing growth type, unsupported growth types, all-ward requests, wildcards, multiple wards/categories, null calculation inputs, and zero previous actual_spend."
