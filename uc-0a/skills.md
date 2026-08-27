skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category and severity-based priority, and provides a justification.
    input: A single complaint row (text description).
    output: Structured object containing exactly: category, priority, reason, and flag.
    error_handling: If the complaint description is genuinely ambiguous, do not guess; instead set the flag field to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the classified results to an output CSV.
    input: Path to an input CSV file containing citizen complaints.
    output: Writes an output CSV file with the added classification columns (category, priority, reason, flag) for each row.
    error_handling: If an individual row fails to parse or process, log the error and continue processing the remaining rows.
