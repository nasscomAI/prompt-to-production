skills:

- name: classify_complaint
  description: Classifies a single complaint into category, priority, reason, and flag.
  input: A dictionary representing one complaint row with complaint description.
  output: A dictionary with complaint_id, category, priority, reason, and flag.
  error_handling: If description is missing or unclear, classify as Other and flag as NEEDS_REVIEW.

- name: batch_classify
  description: Processes a CSV file of complaints and applies classification to each row.
  input: Input CSV file path containing complaint data.
  output: Output CSV file with classified complaints.
  error_handling: Skips invalid rows, logs errors, and continues processing remaining rows.
