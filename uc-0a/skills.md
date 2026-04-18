# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category and priority based on strict rules.
    input: A dictionary containing the row data, including 'description', 'complaint_id', etc.
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is ambiguous, missing, or cannot be mapped exactly, returns category 'Other' and sets 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of complaints, applies classify_complaint to each row, and writes the results to a new CSV.
    input: Two strings representing file paths: input_path and output_path.
    output: A written CSV file at output_path. Returns nothing.
    error_handling: Skips malformed rows gracefully and logs the error, ensuring the output file is still generated for valid rows.
