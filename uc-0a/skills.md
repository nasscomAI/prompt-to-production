skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into an allowed category, priority level, justification reason citing specific words, and an ambiguity flag.
    input: dict representing a single complaint row (must include complaint_id and description; optionally location, ward, city, reported_by, days_open, date_raised).
    output: dict containing exactly five keys (complaint_id, category, priority, reason, flag).
    error_handling: If description is null or empty, returns category 'Other', priority 'Standard', flag 'NEEDS_REVIEW', and reason noting missing description. If text is genuinely ambiguous, sets category 'Other' and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file containing citizen complaints, applies classify_complaint to each row, and writes the resulting structured classifications to a specified output CSV file.
    input: input_path (str, path to input CSV file) and output_path (str, path to output CSV destination).
    output: None (writes structured results CSV with columns complaint_id, category, priority, reason, flag).
    error_handling: Catches and logs malformed rows, null records, and I/O errors; assigns fallback classifications with flag 'NEEDS_REVIEW' and ensures batch processing completes without crashing.
