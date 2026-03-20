skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: A single complaint description as plain text string.
    output: A structured object with fields: category (string), priority (string), reason (string), flag (string or empty).
    error_handling: If the description is unclear or ambiguous, return category as "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes multiple complaints from a CSV file and applies classification to each row.
    input: CSV file with complaint descriptions column.
    output: CSV file with added columns: category, priority, reason, flag.
    error_handling: If a row is invalid or missing description, mark it as category "Other" with flag "NEEDS_REVIEW".
