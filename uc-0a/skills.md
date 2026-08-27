skills:
  - name: classify_complaint
    description: Classify a single complaint row based on the description text, determining its category, priority, citation-based reason, and review flag.
    input: dict representing a single complaint record containing at least 'complaint_id' and 'description' keys.
    output: dict containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is blank or null, set category to Other, priority to Low, reason to 'Empty complaint description.', and flag to NEEDS_REVIEW. If the classification is ambiguous, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV file containing citizen complaints, classify each row, and write the formatted results to an output CSV file.
    input: input_path (str to the source CSV) and output_path (str to the destination CSV).
    output: Writes a CSV file containing columns for complaint_id, category, priority, reason, and flag. Returns None.
    error_handling: Handles missing fields or formatting issues in individual rows without crashing, processes all valid rows, and flags invalid rows in the final output.
