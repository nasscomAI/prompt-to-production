skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and determines category, priority, quoted reason, and ambiguity flag.
    input: Dictionary containing complaint fields including complaint_id, location, and description.
    output: Dictionary with keys complaint_id, category, priority, reason, and flag.
    error_handling: Falls back to category 'Other' and sets flag to 'NEEDS_REVIEW' if description is empty, corrupted, or cannot be categorized.

  - name: batch_classify
    description: Reads a CSV file of complaints, classifies each row using classify_complaint, and writes results to an output CSV file.
    input: input_path (str) path to the input CSV file, output_path (str) path to write the output CSV file.
    output: List of classified row dictionaries and writes output CSV to disk.
    error_handling: Handles missing fields gracefully, logs warnings for unparseable rows, and guarantees complete CSV output generation without crashing.
