skills:
  - name: classify_complaint
    description: Classifies a single complaint record into exact category, priority, justification reason citing source words, and review flag.
    input: Dictionary representing a single complaint row (keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open).
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If description is missing, empty, or ambiguous, sets category to Other, priority to Standard, reason to descriptive explanation, and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies classify_complaint to each row, and writes structured results to an output CSV.
    input: Filepath string for input CSV (test_[city].csv) and filepath string for output CSV (results_[city].csv).
    output: Output CSV file containing classified rows with columns [complaint_id, category, priority, reason, flag].
    error_handling: Validates file existence and handles malformed rows or encoding issues without crashing, assigning NEEDS_REVIEW to corrupted entries.
