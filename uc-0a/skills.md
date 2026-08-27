skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and review flag.
    input: A dictionary representing one complaint row with keys such as complaint_id and description.
    output: A dictionary with keys complaint_id, category, priority, reason, flag, location, ward.
    error_handling: If required data is missing or the description is ambiguous, return category Other, flag NEEDS_REVIEW, and a reason that cites the available description or notes the missing information.

  - name: batch_classify
    description: Read an input CSV, classify each row using classify_complaint, and write the results to a CSV.
    input: Input and output file paths.
    output: A CSV file with header complaint_id, category, priority, reason, flag, location, ward.
    error_handling: Continue processing all rows even when some rows are malformed. For malformed rows, write a fallback row with category Other, flag NEEDS_REVIEW, and a clear reason.
