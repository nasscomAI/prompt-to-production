skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row based on its description into category, priority, reason, and flag.
    input: A dictionary representing a single complaint row with keys including 'complaint_id' and 'description'.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is empty, null, or ambiguous, assign category as 'Other', priority as 'Low', and flag as 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Read citizen complaints from an input CSV file, classify each row, and write the outputs to a result CSV file.
    input: String path to the input CSV file, and String path to the output CSV file.
    output: Writes a CSV file containing columns 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Flags rows with null/missing values, does not crash on bad rows, and produces output even if some rows fail.
