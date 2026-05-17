# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag using the enforcement rules from agents.md.
    input: A dictionary containing one complaint row with keys: complaint_id, description (and optionally other metadata fields).
    output: A dictionary with keys: complaint_id, category (exact string from allowed list), priority (Urgent/Standard/Low), reason (one sentence citing description words), flag (NEEDS_REVIEW or empty string).
    error_handling: If the description field is empty or missing, returns category: Other, priority: Standard, reason: "No description provided", flag: NEEDS_REVIEW. If the description is too ambiguous to classify, returns category: Other and flag: NEEDS_REVIEW with reason explaining the ambiguity.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Path to input CSV file with columns including complaint_id and description.
    output: Path to output CSV file with columns: complaint_id, category, priority, reason, flag. One row per input complaint.
    error_handling: If the input file does not exist or is not a valid CSV, raises a FileNotFoundError with a clear message. If individual rows fail classification, they are output with category: Other, flag: NEEDS_REVIEW, and the error noted in the reason field — the batch never crashes on a single bad row.
