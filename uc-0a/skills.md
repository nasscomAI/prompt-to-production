skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag adhering strictly to the UC-0A classification schema.
    input: Single complaint dictionary/row containing complaint_id and description text.
    output: Dictionary containing complaint_id, category (exact string), priority (Urgent/Standard/Low), reason (one sentence citing description words), and flag (NEEDS_REVIEW or blank).
    error_handling: If input description is missing, corrupt, or genuinely ambiguous, assigns category 'Other', sets flag to 'NEEDS_REVIEW', and provides a descriptive single-sentence reason.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, executes classify_complaint for each row, and writes the structured classification results to an output CSV file.
    input: File path string for input CSV (e.g., test_[city].csv) and file path string for output CSV (e.g., results_[city].csv).
    output: Written CSV file with columns complaint_id, category, priority, reason, and flag populated for all input rows.
    error_handling: Validates CSV existence and headers before processing; handles invalid or corrupt rows gracefully by writing them with flag 'NEEDS_REVIEW' without failing the batch execution.
