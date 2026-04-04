skills:
  - name: classify_complaint
    description: Classify a single citizen complaint into a category, priority, and provide a reason.
    input: A single citizen complaint row/description (Text/String).
    output: Category, priority, reason, and an optional flag (JSON/Structured string).
    error_handling: If the complaint category is genuinely ambiguous, set the flag field to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Read an input CSV of citizen complaints, apply the classify_complaint skill row by row, and write the classified results to an output CSV.
    input: Path to input CSV file.
    output: Path to output CSV file with completed classification columns.
    error_handling: If the input file is missing or unreadable, throw an error. If a row is malformed, skip or flag it.
