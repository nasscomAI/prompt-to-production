skills:
  - name: load_budget_data
    description: Load the ward budget CSV dataset and return structured records for analysis.
    input: File path to ward_budget.csv
    output: List of dictionaries where each dictionary represents one row with column names as keys.
    error_handling: If the file is missing, unreadable, or malformed, return an error message and stop processing.

  - name: analyze_budget_metrics
    description: Perform budget calculations such as totals, comparisons, or category analysis from the dataset.
    input: Structured dataset (list of row dictionaries) returned by load_budget_data.
    output: Numeric results or summaries derived strictly from the dataset with clear labels.
    error_handling: If required columns are missing or values are invalid, return a descriptive error instead of estimating values.