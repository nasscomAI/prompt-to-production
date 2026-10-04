# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based on its description.
    input: A dict with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: A dict with keys: complaint_id, category, priority, reason, flag
    error_handling: If description is empty or missing, return category: Other, priority: Low, reason: "No description provided", flag: NEEDS_REVIEW

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes a results CSV.
    input: Path to a CSV file with columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: Path to write a CSV file with columns: complaint_id, category, priority, reason, flag
    error_handling: Skips rows with critical parse errors (logs them) but continues processing remaining rows. Always produces an output file even if some rows fail.
