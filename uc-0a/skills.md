# skills.md

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag.
    input: A single complaint description string.
    output: Object with fields: category (string), priority (Urgent/Standard/Low), reason (one sentence citing keywords), flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or the category is ambiguous, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to each row, and write the results to an output CSV.
    input: Path to a CSV file with a complaint description column (category and priority_flag columns already stripped).
    output: CSV file at the specified output path with columns: category, priority, reason, flag.
    error_handling: If the input CSV is missing required columns or is empty, abort with an error. If any individual row cannot be classified, set its category to Other and flag to NEEDS_REVIEW but continue processing remaining rows.
