skills:

  - name: load_dataset
    description: Loads budget data, validates columns, identifies null values and reports affected rows.
    input: ward_budget.csv file path.
    output: Validated dataset and null-value report.
    error_handling: Stops processing if required columns are missing.

  - name: compute_growth
    description: Calculates per-period growth for a specific ward and category.
    input: Dataset, ward, category, growth type.
    output: Growth table with formula shown for every row.
    error_handling: Skips growth calculation for rows with missing values and reports the reason.
