skills:
  - name: classify_complaint
    description: Classifies a complaint into category and priority.
    input: One complaint row from CSV.
    output: complaint_id, category, priority, reason, flag.
    error_handling: Unknown complaints become category Other with flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads complaint CSV and classifies every complaint.
    input: CSV file path.
    output: CSV containing classifications.
    error_handling: Skip malformed rows but continue processing remaining records.
