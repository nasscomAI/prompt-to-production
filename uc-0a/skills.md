# skills.md

skills:

- name: classify_complaint
  description: Classifies one citizen complaint into a category and priority with a reason and review flag.
  input: One complaint row as a dictionary containing complaint_id and description.
  output: A dictionary containing complaint_id, category, priority, reason, and flag.
  error_handling: If the description is missing, invalid, or genuinely ambiguous, return category Other and flag NEEDS_REVIEW without crashing.

- name: batch_classify
  description: Reads complaint rows from an input CSV, classifies each row, and writes the results to an output CSV.
  input: Input CSV file path containing complaint records.
  output: Output CSV file containing complaint_id, category, priority, reason, and flag for every input row.
  error_handling: Handle missing or malformed rows without crashing and produce an output CSV with NEEDS_REVIEW for problematic rows.