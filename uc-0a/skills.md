# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint by category, priority, reason, and review flag based on the description text.
    input: A dictionary representing one complaint row with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: A dictionary with keys: complaint_id, category, priority, reason, flag
    error_handling: If description is empty or missing, set category to Other, priority to Low, reason to "No description provided", flag to NEEDS_REVIEW

  - name: batch_classify
    description: Reads an input CSV file containing complaint rows, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: Path to input CSV file (test_[city].csv format), path to output CSV file
    output: A CSV file with columns: complaint_id, category, priority, reason, flag
    error_handling: If a row cannot be parsed, skip it and log a warning. Output file is always written even if some rows fail.
