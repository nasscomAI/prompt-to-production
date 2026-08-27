skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dictionary representing a single row from the complaint CSV.
    output: A dictionary containing the keys complaint_id, category, priority, reason, and flag.
    error_handling: If input fields are missing or empty, default category to Other, priority to Standard, and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV file of complaints, runs the single classifier on each row, and writes the results to an output CSV file.
    input: Path to input CSV file and path to output CSV file.
    output: Writes a CSV file containing headers: complaint_id, category, priority, reason, flag.
    error_handling: Skips completely empty lines, flags rows with missing columns, and continues processing other rows if a single row fails.
