skills:
  - name: load_budget_data
    description: Load the ward budget CSV file and convert it into structured records for analysis.
    input: File path to ward_budget.csv (string)
    output: List of dictionaries representing rows in the dataset.
    error_handling: If the file does not exist or cannot be parsed, raise a clear error and stop execution.

  - name: analyze_budget_metrics
    description: Perform budget calculations such as totals or category summaries using the structured dataset.
    input: List of row dictionaries from load_budget_data.
    output: Dictionary containing calculated metrics such as totals per ward or category.
    error_handling: If required columns are missing or values are invalid, return an error message rather than estimating values.