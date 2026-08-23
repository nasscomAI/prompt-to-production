skills:
  - name: load_dataset
    description: Load and validate the ward budget CSV and report all null actual_spend rows before calculation.
    input: CSV file path.
    output: Validated records, column status, and null-row report.
    error_handling: Stop with a clear error when required columns are missing; never silently discard malformed rows.

  - name: compute_growth
    description: Compute MoM or YoY actual-spend growth for one ward and one category with a formula shown for each result.
    input: Validated dataset, one ward, one category, and explicit growth type.
    output: Per-period table containing actual spend, previous comparison value, formula, growth, and null status.
    error_handling: Refuse missing growth type, all-ward aggregation, or calculations that cross null values.
