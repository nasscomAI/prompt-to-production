skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and review flag.
    input: A dictionary representing a row from the input CSV containing a 'description' field.
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If description is empty or missing, set category to Other, priority to Low, reason to 'No description provided.', and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV file, processes each row using classify_complaint, and writes the results to an output CSV file.
    input: Paths to the input CSV and output CSV files.
    output: Writes a CSV file with headers: complaint_id, category, priority, reason, flag.
    error_handling: Handles missing files or format issues gracefully, flags nulls, and continues processing subsequent rows.
