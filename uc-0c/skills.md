# skills.md

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate the required columns, and report the total null count and every row with a null actual_spend value before returning the dataset.
    input: CSV file path as a string.
    output: Validated dataset with null count and identified null rows, including the corresponding notes reason.
    error_handling: Refuse processing if the file is missing, unreadable, required columns are missing, or the dataset structure is invalid.

  - name: compute_growth
    description: Calculate growth for the specified ward and category at the requested growth type and return a per-period table with the formula shown.
    input: Ward name, category name, growth_type, and validated dataset.
    output: Per-period table containing ward, category, period, actual_spend, growth result, and the formula used for each row.
    error_handling: Refuse if ward or category is invalid, growth_type is missing or ambiguous, or actual_spend required for a calculation is null; flag the null and report its reason from the notes column.