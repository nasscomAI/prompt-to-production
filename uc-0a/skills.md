# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint by category, priority, reason, and review flag based on the complaint description.
    input: A dictionary with keys: complaint_id (string), description (string), ward (string), location (string), reported_by (string).
    output: A dictionary with keys: complaint_id (string), category (string — one of 10 allowed values), priority (string — Urgent/Standard/Low), reason (string — one sentence citing description words), flag (string — NEEDS_REVIEW or blank).
    error_handling: If the description is empty or too short to classify, set category to Other and flag to NEEDS_REVIEW. If the description contains severity keywords, always set priority to Urgent regardless of other factors.

  - name: batch_classify
    description: Reads an input CSV file of civic complaints, applies classify_complaint to each row, and writes the classified results to an output CSV file.
    input: Two string arguments: input_path (path to test_[city].csv) and output_path (path to write results CSV).
    output: A CSV file at output_path containing columns: complaint_id, category, priority, reason, flag. One row per input complaint.
    error_handling: If a row has missing or malformed data, classify it with category: Other and flag: NEEDS_REVIEW. Never crash on bad rows — produce output for all valid rows and flag problematic ones. If the input file does not exist or cannot be read, print an error message and exit with a non-zero status code.
