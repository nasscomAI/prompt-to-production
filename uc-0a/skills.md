# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag according to enforcement rules.
    input: Dictionary or row object containing complaint description and metadata.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If complaint description is ambiguous, missing, or null, sets flag to 'NEEDS_REVIEW' and defaults category to 'Other'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies classify_complaint row by row, and writes results to an output CSV file.
    input: File path to input CSV (e.g., test_[city].csv) and file path for output CSV (e.g., results_[city].csv).
    output: Writes output CSV file containing classified results with columns 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Handles missing files, null/bad rows, and processing errors without crashing, flagging bad rows with 'NEEDS_REVIEW' and producing complete output CSV.
