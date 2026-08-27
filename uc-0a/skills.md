skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority level, and provides a justification.
    input: A single citizen complaint record containing a text description and metadata (e.g., dictionary or structured object).
    output: A set of four fields (category, priority, reason, flag) based on the Classification Schema.
    error_handling: If the complaint description is ambiguous or lacks enough context to classify, sets the category to 'Other' and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies the classify_complaint skill to each row, and writes the completed records to an output CSV.
    input: Path to the input CSV file containing citizen complaint records.
    output: A newly generated output CSV file containing the original complaint data appended with the classification fields.
    error_handling: If an input row is malformed or missing a description, skips classification, outputs the row with empty classification fields, and logs a warning. If the input CSV file cannot be found, aborts execution and raises a descriptive error.
