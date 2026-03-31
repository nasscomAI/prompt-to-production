# skills.md

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint to determine its category, priority, and justification.
    input: A single citizen complaint description (string).
    output: A row containing category, priority, reason, and flag.
    error_handling: Return "Other" for category and set flag to "NEEDS_REVIEW" if input is ambiguous or invalid.

  - name: batch_classify
    description: Read an input CSV file of complaints, apply classify_complaint to each row, and write the results to an output CSV.
    input: Path to the input CSV file.
    output: Path to the written output CSV file containing the classifications.
    error_handling: Log errors for missing input files or row processing failures, and proceed with the remaining rows.
