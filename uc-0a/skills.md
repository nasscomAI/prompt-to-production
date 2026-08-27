# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag.
    input: dict with keys: complaint_id, description (and other row fields from the input CSV).
    output: dict with keys: complaint_id, category, priority, reason, flag.
    error_handling: If description is empty or missing, set category=Other, priority=Standard, reason="No description provided", flag=NEEDS_REVIEW. If category is genuinely ambiguous, set category=Other and flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV of complaints, classify every row using classify_complaint, write an output CSV with results.
    input: input_path (string path to CSV), output_path (string path for results CSV).
    output: Writes a CSV file to output_path. Prints a completion message. Returns nothing.
    error_handling: Skips rows with missing complaint_id (logs to stderr). Collects all valid results and writes them. Does not crash on bad rows — produces partial output with remaining rows.
