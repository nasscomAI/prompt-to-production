skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its required columns, and reports all null actual_spend rows before returning the records.
    input: "CSV file path (string) for ward_budget.csv."
    output: "Validated list of row records with period, ward, category, budgeted_amount, actual_spend, and notes, plus the null-row count and null-row details."
    error_handling: "Report an explicit error and stop when the file is missing, unreadable, malformed, or missing any required column; preserve blank actual_spend values as nulls, count every null, and report each affected period, ward, category, and notes reason before returning."

  - name: compute_growth
    description: Computes the requested growth metric for one ward and one category as a per-period table with the formula shown.
    input: "Validated dataset records, one ward string, one category string, and an explicit growth_type string; the supported growth type is MoM."
    output: "Per-period CSV-ready rows for only the selected ward-category series, including actual_spend, growth_type, formula, growth_percent, status, and null_reason."
    error_handling: "Reject missing or invalid growth_type values, refuse cross-ward or cross-category aggregation, and flag null current or required previous actual_spend values with their notes reason instead of computing or treating them as zero."
