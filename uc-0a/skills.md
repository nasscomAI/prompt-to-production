skills:
  - name: classify_complaint
    description: Processes a single complaint row to output the category, priority, reason, and flag.
    input: Dictionary representation of a single complaint row containing descriptions.
    output: Dictionary containing the assigned 'category', 'priority', 'reason', and 'flag'.
    error_handling: Handles ambiguous complaints by classifying as best effort or 'Other', while setting the 'flag' field to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Path to the input CSV file.
    output: Path to the written output CSV file.
    error_handling: Raises errors on missing files and handles row processing failures gracefully by skipping or logging the error.
