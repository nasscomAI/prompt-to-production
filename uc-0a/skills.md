# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using the enforcement rules in agents.md.
    input: A dict with keys complaint_id (str), description (str), location (str), ward (str), city (str) — sourced from one CSV row.
    output: A dict with keys complaint_id (str), category (str), priority (str), reason (str), flag (str).
    error_handling: >
      If description is empty or None, return category="Other", priority="Low",
      reason="No description provided", flag="NEEDS_REVIEW".
      If any unexpected exception occurs during classification, return the complaint_id
      with all classification fields set to "ERROR" and flag="NEEDS_REVIEW" so the row
      is preserved in output and not silently dropped.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes a results CSV with classification columns appended.
    input: input_path (str) — path to a CSV with columns complaint_id, date_raised, city, ward, location, description, reported_by, days_open; output_path (str) — path to write the results CSV.
    output: A CSV file at output_path with all original columns plus category, priority, reason, flag; one row per input complaint.
    error_handling: >
      If a row is malformed or missing required fields, classify it as an error row
      (category="ERROR", flag="NEEDS_REVIEW") and continue — never crash the entire batch.
      If the input file is not found or unreadable, raise a clear FileNotFoundError with the path.
      Log a warning to stderr for every row that fails or receives NEEDS_REVIEW.
