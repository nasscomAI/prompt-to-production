skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag according to the UC-0A classification schema.
    input: One complaint description string from the dataset.
    output: Structured result containing category, priority, reason (one sentence citing keywords), and flag (NEEDS_REVIEW or blank).
    error_handling: If the complaint description is missing, unclear, or does not clearly match a category, return category as "Other" and set flag to NEEDS_REVIEW instead of guessing.

  - name: batch_classify
    description: Processes multiple complaint rows from a CSV file and applies classify_complaint to each row.
    input: CSV file containing complaint descriptions (one complaint per row).
    output: Output CSV file containing classification results with columns: category, priority, reason, and flag.
    error_handling: If a row is empty or invalid, mark the row with flag NEEDS_REVIEW and continue processing remaining rows.
