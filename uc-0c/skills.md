skills:
  - name: load_dataset
    description: Reads the CSV, validates required columns and reports null rows.
    input: CSV file path.
    output: Validated dataset and list of null rows.
    error_handling: Stop execution if required columns are missing.

  - name: compute_growth
    description: Computes growth for one ward and one category.
    input: Dataset, ward, category, growth_type.
    output: Per-period growth table with formula.
    error_handling: Skip null rows and report the reason from notes.