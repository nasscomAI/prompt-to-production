# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, and justification according to the defined schema.
    input: Text string containing the complaint description.
    output: Dictionary containing 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string/null).
    error_handling: If the description is genuinely ambiguous, the category is set to 'Other' and the 'flag' is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a CSV file of complaints by applying classify_complaint to each row and writing the results to a new CSV file.
    input: Path to an input CSV file.
    output: Path to the generated output CSV file containing the classification results.
    error_handling: Validates file existence and handles malformed CSV rows by logging errors while continuing the batch process.