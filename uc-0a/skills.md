skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row to deduce its category, priority, reason, and flag.
    input: A single citizen complaint row description (String or Dictionary).
    output: A structured object containing category, priority, reason, and flag.
    error_handling: If the input is ambiguous or unclear, classify as closely as possible, and explicitly set the flag field to NEEDS_REVIEW to prevent false confidence.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies the classify_complaint skill to each row, and writes the full results to an output CSV file.
    input: File path to the input CSV containing complaint rows (String).
    output: File path to the generated output CSV populated with classification results (String).
    error_handling: If a specific row is malformed or processing fails, log the error for that row and continue processing subsequent rows to ensure the batch completes.
