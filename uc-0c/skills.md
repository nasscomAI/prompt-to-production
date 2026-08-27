skills:
  - name: load_dataset
    description: Reads the ward budget CSV dataset, validates required columns, and reports null rows.
    input: Path to the CSV budget dataset.
    output: Structured dataset with column validation and null row report.
    error_handling: If required columns are missing or data cannot be parsed, return NEEDS_REVIEW.

  - name: compute_growth
    description: Calculates growth metrics for a specific ward and category using the specified growth type.
    input: Structured dataset, ward name, category name, and growth type (MoM or YoY).
    output: Per-period table showing actual spend, computed growth value, and formula used.
    error_handling: If null values are present for the requested rows, flag them instead of computing growth.
