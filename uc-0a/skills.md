skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, reason, and flag.
    input: Dictionary representing a single CSV row of complaint data with keys like complaint_id, description, reported_by, days_open.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Logs invalid or empty fields, marks category as Other, sets flag to NEEDS_REVIEW, and defaults priority to Standard.

  - name: batch_classify
    description: Reads complaints from an input CSV, processes each row using classify_complaint, and writes results to an output CSV.
    input: Input CSV file path containing raw complaint data, and output CSV file path to write results.
    output: Writes output CSV with headers complaint_id, category, priority, reason, flag.
    error_handling: Handles malformed rows and file errors gracefully to ensure the whole batch does not fail if individual rows fail.
