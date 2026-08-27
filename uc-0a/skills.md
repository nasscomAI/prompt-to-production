skills:
  - name: classify_complaint
    description: Classifies one complaint row into the approved category and priority schema.
    input: A dictionary representing one CSV row with complaint_id and description available.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If description is missing, ambiguous, or outside the taxonomy, return category Other, set flag to NEEDS_REVIEW, and explain the limitation in reason.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes a result CSV.
    input: Input CSV path and output CSV path.
    output: A CSV file containing one classification row per input complaint.
    error_handling: Continue processing after bad rows, emit a result row for failures when possible, and never stop the whole batch because one row is malformed.
