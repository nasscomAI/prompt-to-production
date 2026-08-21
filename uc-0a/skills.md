# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify one citizen complaint row into category, priority, reason, and flag.
    input: A single complaint row as a dict/CSV row with fields: complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dict with exactly four keys — complaint_id, category, priority, reason, flag — following the enforcement rules in agents.md.
    error_handling: If the description is empty or the category is ambiguous, set category to Other and flag to NEEDS_REVIEW. Never crash on a missing field.

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to every row, and write a results CSV.
    input: Path to a test_[city].csv file (comma-separated, header row present) and a path to write results.
    output: A CSV file at the given output path with columns: complaint_id, category, priority, reason, flag.
    error_handling: Skip malformed rows gracefully, leave their flag as NEEDS_REVIEW, produce the output file even if some rows fail, and never crash on a single bad row.
