skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into structured category, priority, reason, and flag fields.
    input: A dictionary representing a single row from the citizen complaint CSV (keys match CSV columns like complaint_id, description, etc.).
    output: A dictionary containing keys: complaint_id, category, priority, reason, flag.
    error_handling: If input fields are missing or null, defaults to category: Other, priority: Standard, reason: "Missing input data.", flag: NEEDS_REVIEW. If the description is empty, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads citizen complaints from a source CSV file, classifies each row, and writes the structured classification output to a destination CSV file.
    input: input_path (string path to the source CSV file), output_path (string path to write the output CSV file).
    output: Writes a CSV file containing columns: complaint_id, category, priority, reason, flag.
    error_handling: If the input file is missing, raises FileNotFoundError. If any rows are malformed or have errors during classification, logs/flags the error, sets category to Other and flag to NEEDS_REVIEW for that row, and continues processing other rows without crashing.
