skills:
  - name: classify_complaint
    description: Processes a single complaint description to determine its category, priority, and justification.
    input: String (complaint description).
    output: Object containing category, priority, reason, and flag.
    error_handling: Return category 'Other', priority 'Low', and flag 'NEEDS_REVIEW' if input is empty or incomprehensible.

  - name: batch_classify
    description: Reads an input CSV, processes each row using classify_complaint, and writes the results to an output CSV.
    input: CSV file path.
    output: CSV file path.
    error_handling: Log errors for individual row failures and ensure the output file is still generated for successful rows.
