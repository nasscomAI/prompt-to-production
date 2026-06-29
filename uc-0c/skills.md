skills:
  - name: load_dataset
    description: Ingests the ward budget CSV file and performs safety checks on null tracking.
    input: File path string pointing to ward_budget.csv.
    output: Cleaned data rows filtered strictly by the selected target parameters.
    error_handling: System raises an explicit FileNotFoundError if path mapping is unreadable.

  - name: compute_growth
    description: Iterates sequentially across consecutive periods to evaluate chronological Month-over-Month percentage changes.
    input: Filtered dataset structure alongside target growth metrics format instructions.
    output: A per-period table structure displaying the raw numbers alongside explicit formula logs.
    error_handling: Flags matching rows containing null actual_spend rows by printing the notes text column value verbatim instead of a calculated number.
