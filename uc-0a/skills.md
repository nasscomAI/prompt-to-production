skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a standardized category, priority level, justification reason, and review flag based on strict enforcement rules.
    input: A dictionary containing complaint record fields (complaint_id, description, days_open, etc.).
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: Flags missing or ambiguous descriptions as NEEDS_REVIEW, sets category to Other, and provides an explanatory reason.

  - name: batch_classify
    description: Reads an input CSV file containing raw complaint records, applies classify_complaint to each record, and writes structured results to an output CSV file.
    input: File path to input CSV (input_path) and destination file path for output CSV (output_path).
    output: Writes an output CSV file containing complaint_id, category, priority, reason, and flag for each processed row.
    error_handling: Handles missing files, unparseable CSV rows, and null fields gracefully without crashing, tagging bad or incomplete rows with NEEDS_REVIEW.
