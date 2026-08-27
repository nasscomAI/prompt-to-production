- name: classify_complaint
  description: >
    Classifies a single complaint into category, priority, reason, and flag.

  input:
    type: CSV row
    format: Complaint description text

  output:
    type: Classification result
    format: category, priority, reason, flag

  error_handling: >
    If complaint is ambiguous, assign category as Other and set flag to
    NEEDS_REVIEW. If severity keywords are present, priority must be Urgent.

- name: batch_classify
  description: >
    Reads input CSV, applies complaint classification to each row,
    and writes results to output CSV.

  input:
    type: CSV file
    format: Complaint dataset

  output:
    type: CSV file
    format: Classified complaint dataset

  error_handling: >
    Skip empty rows safely and preserve output structure even if
    some complaints are ambiguous.