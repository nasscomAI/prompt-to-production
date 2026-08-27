# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dict with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: A dict with keys: complaint_id, category, priority, reason, flag
    error_handling: If description is missing or empty, set category to Other, flag to NEEDS_REVIEW, and reason to "Description missing — cannot classify."

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Two file paths — input CSV path and output CSV path
    output: A CSV file with columns: complaint_id, category, priority, reason, flag
    error_handling: If a row is malformed or missing required fields, skip classification for that row, write category as Other, flag as NEEDS_REVIEW, and continue processing remaining rows without crashing.
