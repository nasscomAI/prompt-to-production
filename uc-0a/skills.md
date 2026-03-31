skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to determine category, priority, reason, and flag.
    input: Dictionary containing a 'description' field.
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: Falls back to 'Other' category and sets 'NEEDS_REVIEW' flag if input is empty or incomprehensible.

  - name: batch_classify
    description: Reads a CSV file of complaints, processes each through classify_complaint, and writes results to a new CSV.
    input: String path to input CSV and string path to output CSV.
    output: A CSV file containing classified results.
    error_handling: Continues processing if a single row fails; logs errors but does not halt.
