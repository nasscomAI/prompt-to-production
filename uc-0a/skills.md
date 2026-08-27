# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag fields.
    input: A dict with keys: complaint_id, description, city, ward, location, days_open.
    output: A dict with keys: complaint_id, category, priority, reason, flag.
    error_handling: If description is empty or missing, set category to Other, flag to NEEDS_REVIEW, and reason to "No description provided."

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Two file paths — input CSV path and output CSV path.
    output: A CSV file with columns: complaint_id, category, priority, reason, flag.
    error_handling: If a row is malformed or missing required fields, skip classification for that row, set category to Other, flag to NEEDS_REVIEW, and continue processing remaining rows.
