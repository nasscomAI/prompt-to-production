skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and flag.
    input: A dictionary representing a single complaint row (keys: complaint_id, description, etc.).
    output: A dictionary containing classified fields (keys: complaint_id, category, priority, reason, flag).
    error_handling: If description is missing or invalid, or if category is ambiguous, defaults category to Other and flags as NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to each row, and writes results to output CSV.
    input: Path to the input CSV file (string) and path to the output CSV file (string).
    output: None. Writes the output CSV file containing the classifications.
    error_handling: Gracefully handles missing input files or formatting errors, skipping or logging corrupt rows rather than crashing.
