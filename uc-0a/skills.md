# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into a standardized category, priority, reason, and flag.
    input: A dictionary representing a row from the input CSV, containing at least the complaint 'description'.
    output: A dictionary containing keys - complaint_id, category, priority, reason, and flag.
    error_handling: If input is invalid or ambiguous, return category as 'Other', flag as 'NEEDS_REVIEW', and note the issue in the reason field.

  - name: batch_classify
    description: Process an entire CSV file of complaints, applying classify_complaint to each row, and save the results.
    input: String file paths for the input CSV and the output CSV.
    output: A newly written CSV file at the specified output path containing all classified results.
    error_handling: Catch exceptions per row to avoid crashing the whole batch. Flag null/bad rows with 'NEEDS_REVIEW' and continue to the next row.
