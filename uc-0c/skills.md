skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates column structure, and reports any null values before processing.
    input: File path to the CSV dataset (e.g., `ward_budget.csv`).
    output: Parsed dataset, including a summary of total null count and specific rows containing nulls with their reasons from the notes column.
    error_handling: Return an error if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing or if the file cannot be read.

  - name: compute_growth
    description: Computes growth metrics for a specific ward and category over time, showing the exact formula used for each period.
    input: Validated dataset, `ward` (string), `category` (string), and `growth_type` (string).
    output: A per-ward, per-category table containing the calculated growth and the formula used alongside each result.
    error_handling: Refuse and ask if `growth_type` is not specified. Refuse if asked to aggregate across wards or categories. Do not compute on null rows; flag them instead.
