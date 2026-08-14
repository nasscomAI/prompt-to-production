# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag fields adhering strictly to RICE enforcement rules.
    input: Dictionary representing a single complaint row containing complaint_id and description text.
    output: Dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If description is missing, empty, or category is genuinely ambiguous, set category to 'Other' and set flag to 'NEEDS_REVIEW' without crashing.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies classify_complaint row-by-row, and writes the resulting classifications to an output CSV file.
    input: File paths `input_path` (str) for input test CSV and `output_path` (str) for target results CSV.
    output: Results CSV file populated with complaint_id, category, priority, reason, and flag columns.
    error_handling: Flags missing values or malformed rows as NEEDS_REVIEW, logging errors and ensuring batch execution completes even if individual rows fail.
