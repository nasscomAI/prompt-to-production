# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into a standardized category and assign priority.
    input: Dictionary containing at least `complaint_id` and the text description.
    output: A dictionary containing exact keys - `complaint_id`, `category`, `priority`, `reason`, `flag`.
    error_handling: For null, missing, or unparseable inputs, return category 'Other', priority 'Low', and flag 'NEEDS_REVIEW' safely without raising an exception.

  - name: batch_classify
    description: Ingest an entire CSV of complaints and run classify_complaint sequentially to output a compiled results CSV.
    input: Two strings representing the file paths, one for input CSV and one for output CSV.
    output: None (writes the classified output rows to the target CSV file).
    error_handling: If a specific row fails processing severely, skip the failure, log it, and continue the batch process to ensure the overall pipeline doesn't crash.
