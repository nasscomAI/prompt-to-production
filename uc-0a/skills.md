# skills.md

skills:

- name: classify_complaint
  description: Classify a single citizen complaint row into an exact UC-0A category, priority, reason, and review flag.
  input: A dictionary representing one complaint row with fields: complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
  output: A dictionary with fields: complaint_id, category, priority, reason, flag.
  error_handling: If required complaint fields are missing or empty, return category: Other, priority: Low, reason explaining the missing input, and flag: NEEDS_REVIEW. If the complaint is ambiguous, set category: Other and flag: NEEDS_REVIEW.

- name: batch_classify
  description: Process a CSV of complaint rows, apply classify_complaint to each row, and produce output rows for UC-0A results.
  input: A list of complaint row dictionaries or a path to a CSV file with the same input fields used by classify_complaint.
  output: A list of dictionaries or CSV rows with fields: complaint_id, category, priority, reason, flag.
  error_handling: Skip rows that cannot be parsed and include a diagnostics entry if applicable. For ambiguous rows, rely on classify_complaint to return category: Other and flag: NEEDS_REVIEW.
