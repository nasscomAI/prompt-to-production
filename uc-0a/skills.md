skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to assign a standardized category, priority level, and justification.
    input: A single dictionary or row containing a 'description' string.
    output: A dictionary containing {'category': string, 'priority': string, 'reason': string, 'flag': string}.
    error_handling: If the description is empty or null, return category: 'Other', priority: 'Low', and flag: 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of a municipal CSV file, ensuring structural integrity of the output.
    input: File paths for --input (CSV) and --output (CSV).
    output: A CSV file at the specified destination with columns: description, category, priority, reason, flag.
    error_handling: Validates that the input file exists; if a specific row fails classification, it logs the error and continues to the next row to ensure partial completion.
