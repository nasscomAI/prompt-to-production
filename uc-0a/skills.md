- name: classify_complaint
  description: Classifies a single complaint into category, priority, reason, and flag.
  input: 
    type: string
    format: complaint description text
  output:
    type: object
    format: category, priority, reason, flag
  error_handling: >
    If the complaint is ambiguous or does not clearly match a category, assign category as "Other"
    and set flag to NEEDS_REVIEW. If severity keywords are unclear, default to Standard priority.

- name: batch_classify
  description: Reads complaints from a CSV file, classifies each row, and writes results to output CSV.
  input:
    type: CSV file
    format: rows containing complaint descriptions
  output:
    type: CSV file
    format: rows with category, priority, reason, flag added
  error_handling: >
    If input file is missing or malformed, raise an error. If a row is empty, skip it.
    Ensure all rows are processed even if some fail classification.