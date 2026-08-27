skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into its corresponding category, priority, reason, and review flag.
    input: A single string or dictionary containing the citizen's complaint description.
    output: A dictionary or object containing exactly four fields - category (string), priority (string), reason (string), and flag (string).
    error_handling: If input is invalid, malformed, or ambiguous, assigns category 'Other', priority 'Standard', reason 'Invalid or ambiguous input format', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path to the input CSV containing rows of citizen complaints.
    output: File path to the newly written output CSV containing classified complaints.
    error_handling: If the input file is missing or unreadable, logs an error and halts. If individual rows fail, handles them via classify_complaint error rules and continues to the next row.
