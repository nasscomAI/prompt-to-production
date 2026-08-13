skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and flag using exact schema rules.
    input: Dictionary containing complaint fields including complaint_id, date_raised, city, ward, location, description, reported_by, and days_open.
    output: Dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If description is missing, empty, or genuinely ambiguous, returns category 'Other', flag 'NEEDS_REVIEW', and a reason explaining the issue.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies classify_complaint row by row, and writes the enriched results CSV file.
    input: String input_path (path to input CSV file) and string output_path (path to write output CSV file).
    output: Writes output CSV file containing original fields enriched with category, priority, reason, and flag.
    error_handling: Handles missing columns or corrupt rows per-row without halting execution, ensuring all valid rows are processed into the output file.
