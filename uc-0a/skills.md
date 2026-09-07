skills:
  - name: classify_complaint
    description: Classifies a single complaint record into exact category, priority, reason citing verbatim words, and flag.
    input: Dictionary containing complaint fields (complaint_id, description, location, ward, etc.)
    output: Dictionary with keys (complaint_id, category, priority, reason, flag)
    error_handling: Flags missing/corrupt rows with flag=NEEDS_REVIEW, category=Other, and safety priority=Urgent.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint to each row safely, and writes results CSV.
    input: Input CSV file path and Output CSV file path strings
    output: Written CSV file with classified complaints
    error_handling: Handles empty files, missing columns, and bad rows without crashing the batch execution.
