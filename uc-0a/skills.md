skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint record to determine its canonical category, priority level, justification reason citing text, and review flag.
    input: Dictionary representing a single CSV row with fields complaint_id, description, location, etc.
    output: Dictionary containing complaint_id, category, priority, reason, flag.
    error_handling: If description is missing or ambiguous, sets category to 'Other' and flag to 'NEEDS_REVIEW' with explanation in reason.

  - name: batch_classify
    description: Ingests an input CSV file containing raw citizen complaints, processes each complaint through classify_complaint, and writes formatted results to an output CSV.
    input: File path to input CSV (str) and destination file path for results CSV (str).
    output: Output CSV written to disk and summary statistics of classified complaints.
    error_handling: Handles malformed rows gracefully, reports errors per row without crashing the batch job, and ensures all valid rows are classified.
