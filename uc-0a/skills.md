# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: dict with keys complaint_id, description (text field from complaint), and other metadata.
    output: dict with keys complaint_id, category (one of 10 allowed), priority (Urgent/Standard/Low), reason (one sentence citing description), flag (NEEDS_REVIEW or blank).
    error_handling: If description is empty or malformed, set category to Other with flag NEEDS_REVIEW and reason "Insufficient complaint text for classification".

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint to each row, writes output CSV with all rows including failures.
    input: path to CSV file with columns complaint_id, description, and other fields.
    output: CSV file with columns complaint_id, category, priority, reason, flag. Preserves input row order.
    error_handling: Skips malformed rows and logs them; continues processing remaining rows. Output file includes all rows attempted, with failures marked by flag=NEEDS_REVIEW or reason="Failed to parse row".
