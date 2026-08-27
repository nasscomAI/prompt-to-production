skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint by returning its category, priority, reason, and an optional review flag.
    input: A single string containing the description of the citizen complaint.
    output: A structured record containing category (exact string match from allowed list), priority (Urgent, Standard, Low), reason (one sentence), and flag (NEEDS_REVIEW or blank).
    error_handling: If the complaint category is genuinely ambiguous, defaults the category to 'Other' and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the classified records to an output CSV file.
    input: Path to the input CSV file containing citizen complaints.
    output: A written output CSV file containing all original rows with the appended classification columns.
    error_handling: If the input file is missing, returns a file not found error. If a row is malformed or invalid, skips the row or logs a warning and proceeds.
