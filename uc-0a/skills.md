skills:
  - name: classify_complaint
    description: Analyzes one complaint row to determine its category, priority, reason, and flag.
    input: Dictionary or string representing one complaint row.
    output: Dictionary with exactly the keys category, priority, reason, and flag.
    error_handling: If classification is genuinely ambiguous or row is malformed, category defaults to 'Other' and flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint per row, and writes the results to an output CSV.
    input: Strings representing the input_path and output_path for the CSV files.
    output: A newly written CSV file at the output_path containing the classification results.
    error_handling: Handles nulls gracefully, skips or flags bad rows without crashing the entire batch process.
