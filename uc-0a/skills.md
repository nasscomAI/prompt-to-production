skills:

* name: classify_complaint
  description: Classify one citizen complaint into an allowed category and priority, provide a description-based reason, and flag genuine ambiguity.
  input: A complaint row as a dictionary containing complaint_id and description.
  output: A dictionary containing complaint_id, category, priority, reason, and flag.
  error_handling: If the description is missing, invalid, or genuinely ambiguous, do not crash; use category Other where appropriate and set flag to NEEDS_REVIEW.

* name: batch_classify
  description: Read complaints from an input CSV, classify each complaint, and write the classification results to an output CSV.
  input: Input CSV file path and output CSV file path as strings.
  output: CSV containing complaint_id, category, priority, reason, and flag for every input row.
  error_handling: Continue processing when an individual row is invalid or fails classification, flag the affected row for review, and still produce the output CSV.
