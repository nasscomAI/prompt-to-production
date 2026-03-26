skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag.
    input: One complaint row containing complaint_id and description text.
    output: Dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or ambiguous, set category to Other and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and applies classify_complaint to each row.
    input: CSV file path containing complaint rows.
    output: Output CSV file with classification results.
    error_handling: If a row fails classification, write the row with category Other and flag NEEDS_REVIEW instead of crashing.