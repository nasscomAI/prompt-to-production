# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into the required UC-0A schema.
    input: One CSV row as a dictionary with complaint text fields (must include complaint_id and description or equivalent text field).
    output: Dictionary with keys complaint_id, category, priority, reason, and flag.
    error_handling: If text is missing/empty or category is ambiguous, return category as Other, set flag to NEEDS_REVIEW, and provide a reason citing available text or missing-data condition.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint row-by-row, and writes UC-0A output CSV.
    input: input_path string to test_[city].csv and output_path string for results_[city].csv.
    output: Output CSV with one row per input complaint containing complaint_id, category, priority, reason, and flag.
    error_handling: Handles malformed rows without crashing by emitting a fallback row (Other + NEEDS_REVIEW + reason), continues processing remaining rows, and always writes an output file.
