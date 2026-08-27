skills:

- name: classify_complaint
  description: Classifies a single complaint into category, priority, reason, and flag.
  input: A dictionary containing complaint_id and description text.
  output: A dictionary with complaint_id, category, priority, reason, and flag.
  error_handling:
  If description is missing or unclear, assign category as "Other", priority as "Low", and flag as "NEEDS_REVIEW".

- name: batch_classify
  description: Processes an input CSV file and applies classification to each complaint row.
  input: Input CSV file path containing complaint data.
  output: Output CSV file with classified results.
  error_handling:
  Skips invalid rows safely, ensures output file is still generated, and logs or flags problematic entries.
