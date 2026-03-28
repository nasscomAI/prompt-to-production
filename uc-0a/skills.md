- # updated
name: classify_complaint
  description: Classifies a complaint into category and priority based on text
  input:
    type: string
    format: complaint text
  output:
    type: object
    format: category, priority_flag, justification
  error_handling: >
    If the complaint text is empty or unclear, assign category as "Other",
    priority_flag as "Low", and provide a generic justification.

- name: batch_classify
  description: Processes a CSV file of complaints and applies classification
  input:
    type: CSV file
    format: rows containing complaint descriptions
  output:
    type: CSV file
    format: original data with added category, priority_flag, justification columns
  error_handling: >
    If rows are missing complaint text, skip or assign default classification.
    Ensure output file is always generated.