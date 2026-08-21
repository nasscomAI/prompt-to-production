skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into an allowed category, priority level, single-sentence justification citing description text, and review flag.
    input: Dictionary representing a single complaint row with keys (complaint_id, date_raised, city, ward, location, description, reported_by, days_open).
    output: Dictionary with keys (complaint_id, category, priority, reason, flag).
    error_handling: If description is missing or category is genuinely ambiguous, set category to Other, flag to NEEDS_REVIEW, and state ambiguity in reason. Enforce Urgent priority if any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) is present.

  - name: batch_classify
    description: Reads an input CSV of complaints, classifies each record using classify_complaint, and writes the structured classification results to an output CSV file.
    input: String input_path (path to input CSV file) and string output_path (path to destination results CSV file).
    output: CSV file written at output_path containing columns complaint_id, category, priority, reason, flag.
    error_handling: Handles missing files, unreadable records, and missing/null fields gracefully without crashing, flagging bad rows as NEEDS_REVIEW so complete output is produced for all rows.
