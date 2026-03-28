- name: classify_complaint
  description: Classifies a single complaint into category, priority, reason, and flag.
  input:
    type: string
    format: complaint description text
  output:
    type: object
    format: category, priority, reason, flag
  error_handling:
    - If complaint is ambiguous or lacks sufficient detail, set flag to NEEDS_REVIEW
    - If no matching category is found, assign category as Other
    - If severity keywords are unclear, default priority to Standard

- name: batch_classify
  description: Processes a CSV file of complaints and applies classification to each row.
  input:
    type: CSV file
    format: multiple complaint descriptions
  output:
    type: CSV file
    format: classified rows with category, priority, reason, and flag
  error_handling:
    - If input file is missing or corrupted, raise an error
    - If a row is empty, skip or mark as NEEDS_REVIEW
    - Ensure output file is always generated even if some rows fail