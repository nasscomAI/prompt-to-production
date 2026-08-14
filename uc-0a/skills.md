# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a standardized category, priority, reason justification, and review flag based on RICE enforcement rules.
    input: Dictionary representing one complaint row containing keys complaint_id (str) and description (str).
    output: Dictionary containing keys complaint_id (str), category (str), priority (str: Urgent|Standard|Low), reason (str: single sentence citing description words), and flag (str: NEEDS_REVIEW or blank).
    error_handling: If description is missing, empty, or genuinely ambiguous, sets category to 'Other', reason to 'Insufficient details in description', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, invokes classify_complaint for each row, and writes the formatted classifications to an output CSV.
    input: Input CSV path (input_path) and destination CSV path (output_path).
    output: Generates output CSV file with headers complaint_id, category, priority, reason, flag.
    error_handling: Handles invalid or corrupt rows gracefully without halting batch processing, writing 'NEEDS_REVIEW' flag for bad rows.

