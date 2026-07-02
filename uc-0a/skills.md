skills:
- name: classify_complaint
  description: Classifies a single citizen complaint into category, priority, reason and review flag.
  input: >
  Dictionary containing complaint details including description.
  output: >
  Dictionary containing complaint_id, category, priority, reason and flag.
  error_handling: >
  If description is missing, empty or ambiguous, return category=Other,
  flag=NEEDS_REVIEW and a reason explaining the uncertainty.

- name: batch_classify
  description: Reads an input CSV file, classifies all complaints and writes results to an output CSV.
  input: >
  CSV file containing complaint records.
  output: >
  CSV file containing complaint_id, category, priority, reason and flag.
  error_handling: >
  Invalid rows should not stop processing. Rows that cannot be classified
  should be marked as category=Other and flag=NEEDS_REVIEW.