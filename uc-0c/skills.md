# skills.md
skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports the total null count and each null actual_spend row with its reason.
    input: CSV file path.
    output: Validated dataset and list of null actual_spend rows with their notes reasons.
    error_handling: Fail if the file is missing, unreadable, or required columns are absent. Never replace null actual_spend values with zero.
  - name: compute_growth
    description: Computes growth for exactly one ward and one category using an explicitly specified growth type.
    input: Dataset, ward, category, growth_type.
    output: Per-period growth table with actual spend, growth result, formula, status, and null reason where applicable.
    error_handling: Refuse missing or unsupported growth_type, invalid ward/category, or aggregation requests. Flag null rows instead of calculating them.
