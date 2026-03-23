skills:
  - name: classify_complaint
    description: Classifies a single civic complaint description into category, priority, reason, and review flag.
    input: One complaint row as dictionary containing complaint_id and description text.
    output: Dictionary with complaint_id, category, priority, reason, and flag fields.
    error_handling: If description is missing or unclear, assigns category as Other and sets flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Processes multiple complaint rows from input CSV and writes classification results to output CSV.
    input: CSV file path containing complaint records.
    output: CSV file with classified complaint results.
    error_handling: Skips invalid rows and continues processing without crashing.