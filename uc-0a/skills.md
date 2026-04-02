skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a specific category, priority, reason, and flag.
    input: A single citizen complaint record (text description).
    output: A structured record containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the complaint description is ambiguous and cannot be confidently assigned a category, 'flag' is set to 'NEEDS_REVIEW' and 'category' to 'Other' if applicable.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: A CSV file containing citizen complaints with stripped category and priority flags.
    output: A newly generated CSV file with populated 'category', 'priority', 'reason', and 'flag' columns for each row.
    error_handling: Skips processing invalid rows and logs an error, ensuring unaffected valid rows are processed and written to the output CSV.
