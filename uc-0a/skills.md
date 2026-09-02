# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: One complaint description string.
    output: JSON object with category, priority, reason, flag fields.
    error_handling: If description is ambiguous or empty, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint to each row, and writes output CSV.
    input: CSV file path with columns including description.
    output: CSV file path with columns: category, priority, reason, flag.
    error_handling: If input file missing or malformed, return error message. If rows fail validation, log and continue with remaining rows.
