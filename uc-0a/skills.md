skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row by extracting category, priority, reason, and flag.
    input: Dictionary representing a single row from the CSV (e.g., {"complaint_id": "123", "description": "..."})
    output: Dictionary with keys complaint_id, category, priority, reason, and flag.
    error_handling: Return a dictionary with category="Other", flag="NEEDS_REVIEW", reason="Classification failed or ambiguous." if input is completely unusable.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Two strings representing the input file path and output file path.
    output: None (writes to output CSV file).
    error_handling: Skips rows with null descriptions, flags them, and ensures the whole process does not crash on bad rows.
