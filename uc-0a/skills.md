skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint record into category, priority, reason, and flag according to enforcement rules.
    input: Dictionary representing a single complaint row with fields including complaint_id, description, location, ward.
    output: Dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If fields are missing or category is ambiguous, defaults category to Other, priority based on severity keywords, reason explaining missing/ambiguous details, and sets flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a CSV of citizen complaints, applies classify_complaint to each row, and writes the classified records to an output CSV.
    input: File path to input CSV (input_path) and file path for output CSV (output_path).
    output: Writes output CSV containing columns complaint_id, category, priority, reason, flag.
    error_handling: Handles empty files, missing columns, or bad rows gracefully without crashing, logging errors and setting flag to NEEDS_REVIEW for corrupted rows.
