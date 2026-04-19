skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports the total null count and specific rows with missing values before returning the dataset.
    input: File path to the budget dataset CSV string.
    output: Validated dataset structure and a log/report explicitly calling out rows with a null 'actual_spend'.
    error_handling: System halts and throws an error if the CSV is missing required columns ('period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes') or if the file cannot be loaded.

  - name: compute_growth
    description: Calculates specific growth metrics for a provided ward and category without unauthorized aggregations, and returns a table detailing the formula applied.
    input: Dataset object, ward (string), category (string), and growth_type (string, e.g., 'MoM').
    output: A per-period table showing the period, raw spend values, explicit formula used, and the result (or a flagged null row with reason).
    error_handling: Halts and refuses to guess if `growth_type` is missing or invalid. Halts and refuses if requested to aggregate across multiple wards or categories.
