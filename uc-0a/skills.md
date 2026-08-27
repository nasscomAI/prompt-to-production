# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag fields using RICE enforcement rules.
    input: Dictionary with keys {complaint_id, description, ...} from CSV row. Description field is required.
    output: Dictionary with keys {complaint_id, category, priority, reason, flag}. All fields populated as strings.
    error_handling: If description is null/empty, set category=Other, priority=Low, reason="No description provided", flag=NEEDS_REVIEW. If category is ambiguous, default to Other and set flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Read input CSV, apply classify_complaint to each row, write results CSV with all classifications.
    input: File path to CSV with columns {complaint_id, date_raised, city, ward, location, description, reported_by, days_open}.
    output: File path to write results CSV with columns {complaint_id, category, priority, reason, flag}. File is written even if some rows fail.
    error_handling: Log malformed rows to stderr with complaint_id and error reason. Continue processing remaining rows. Ensure output file is created regardless of partial failures.
