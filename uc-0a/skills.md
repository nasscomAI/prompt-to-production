# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into one of the predefined categories and priorities based on input description.
    input: One complaint row (from CSV) containing the description field and associated metadata.
    output: A structure containing 'category', 'priority', 'reason', and 'flag' (NEEDS_REVIEW or empty).
    error_handling: If the description is blank or invalid, the category should be set to 'Other' and the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, iterates through each row to classify it, and outputs a consolidated CSV.
    input: Input CSV file path (system-specific city file).
    output: Output CSV file path containing the additional 'category', 'priority', 'reason', and 'flag' columns.
    error_handling: Logs any rows that failed to parse correctly for later manual review.
