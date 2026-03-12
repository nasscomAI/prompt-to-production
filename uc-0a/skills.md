# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row by category, priority, reason, and flag using deterministic keyword matching.
    input: A dictionary representing a complaint row with fields like complaint_id, description, etc.
    output: A dictionary with category (one of the allowed strings), priority (Urgent/Standard), reason (one sentence citing clue words), and flag (NEEDS_REVIEW or blank).
    error_handling: If description is missing or empty, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Process a CSV file of complaints, classify each row, and write results to a new CSV.
    input: Input CSV file path and output CSV file path.
    output: Output CSV file with original columns plus category, priority, reason, flag.
    error_handling: Skip rows that cannot be parsed, log errors, but produce output for valid rows.
