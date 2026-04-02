skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, and reason.
    input: Dictionary containing complaint details, including the description string.
    output: Dictionary with four fields - category (string), priority (string), reason (string), flag (string).
    error_handling: If the description is genuinely ambiguous, the flag should be set to 'NEEDS_REVIEW' and category to 'Other'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint processing per row, and writes an output CSV.
    input: File path to the input CSV.
    output: File path or confirmation of written output CSV.
    error_handling: Log errors for row-level parsing failures while continuing the batch.
