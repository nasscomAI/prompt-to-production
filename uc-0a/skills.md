skills:
- name: classify_complaint
  description: Classify one citizen complaint into an allowed category and priority, provide an evidence-based reason, and flag genuine ambiguity.
  input: One complaint row containing complaint_id and description.
  output: A result containing complaint_id, category, priority, reason, and flag.
  error_handling: Invalid or ambiguous input must not crash the process and should be flagged as NEEDS_REVIEW.

- name: batch_classify
  description: Read complaint rows from an input CSV, classify each row, and write the results to an output CSV.
  input: A CSV file containing complaint rows.
  output: A CSV containing complaint_id, category, priority, reason, and flag for every row.
  error_handling: Bad rows must be handled without stopping the complete batch and should be flagged as NEEDS_REVIEW.
