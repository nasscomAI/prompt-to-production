skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row by determining its category, priority, reason, and flag.
    input: One complaint row containing the raw citizen complaint information.
    output: Object containing category, priority (Urgent/Standard/Low), reason citation, and flag string.
    error_handling: Sets flag to 'NEEDS_REVIEW' when the category is genuinely ambiguous to prevent false confidence.

  - name: batch_classify
    description: Reads an input CSV file, applies the classify_complaint skill per row, and writes the classified results to an output CSV.
    input: Path to the input CSV file.
    output: Processed data written to the specified output CSV file path.
    error_handling: Skips or logs malformed rows and continues processing the rest of the batch.
