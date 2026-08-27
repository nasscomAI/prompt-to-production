# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint description string to determine its category, priority, reason, and flag status.
    input: String (the raw text description of the citizen complaint)
    output: Dict/JSON containing category (String), priority (String), reason (String), and flag (String)
    error_handling: Return category 'Other', set flag to 'NEEDS_REVIEW', and state the ambiguity in the reason field if the input is invalid or genuinely ambiguous.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Dictionary containing input_csv_path (String) and output_csv_path (String)
    output: Writes an output CSV file and returns a boolean indicating success
    error_handling: If the file is not found or cannot be written, error gracefully and log the issue. If a single row fails, log the failure, flag the row with 'NEEDS_REVIEW', and continue processing remaining rows.
