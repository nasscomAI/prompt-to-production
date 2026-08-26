# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and review flag.
    input: Dictionary containing complaint_id (str) and description (str).
    output: Dictionary containing complaint_id (str), category (str), priority (str), reason (str), and flag (str).
    error_handling: If description is missing/null or category is genuinely ambiguous, set category to 'Other', priority to 'Low' or 'Standard', flag to 'NEEDS_REVIEW', and document missing info in reason.

  - name: batch_classify
    description: Reads input CSV of citizen complaints, applies classify_complaint per row, and writes structured results CSV.
    input: Input CSV file path (input_path) and destination CSV file path (output_path).
    output: CSV file created at output_path with columns complaint_id, category, priority, reason, flag.
    error_handling: Flags null/corrupt rows, skips bad formatting gracefully without crashing the pipeline, and guarantees output file generation.
