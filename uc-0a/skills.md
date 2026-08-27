skills:
  - name: classify_complaint
    description: Processes a single citizen complaint row and applies strict categorization and priority rules.
    input: Dictionary containing a single complaint row with fields like description, location, etc.
    output: Dictionary containing category, priority, reason, and flag fields.
    error_handling: If the input is fundamentally invalid or missing a description, default the category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results out to a CSV file.
    input: String path to the input CSV and String path to the output CSV.
    output: A CSV file written to disk with new classification columns.
    error_handling: Catch row-level errors gracefully to ensure the batch doesn't crash on corrupted individual rows.
