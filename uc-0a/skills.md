skills:
  - name: classify_complaint
    description: Classifies a single complaint row by assigning a category, priority, reason, and flag.
    input: A dictionary representing a single complaint row, including the complaint description and ID.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the complaint category is genuinely ambiguous, set 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path (string, path to input CSV) and output_path (string, path to write results CSV).
    output: Writes a CSV file containing the classification results for all processed rows.
    error_handling: Must flag nulls, not crash on bad rows, and ensure an output file is produced even if individual rows fail.
