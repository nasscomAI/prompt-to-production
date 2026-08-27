skills:
  - name: load_data
    description: Loads and validates the dataset from CSV.
    input: CSV file path.
    output: Parsed dataset rows.
    error_handling: If file missing or columns invalid, stop execution.

  - name: analyze_data
    description: Performs UC-X analysis and produces structured results.
    input: Dataset rows and query parameters.
    output: Table or structured analysis results.
    error_handling: If data missing, flag NEEDS_REVIEW.
