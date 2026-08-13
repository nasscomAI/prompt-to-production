skills:
  - name: classify_complaint
    description: Classifies a single complaint into a predefined category, assigns priority, extracts a reason, and flags ambiguity.
    input: A dictionary representing one complaint row (e.g., containing 'complaint_id' and 'description').
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is missing or completely unparseable, defaults category to 'Other', priority to 'Low', reason to 'Invalid input', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Two strings representing the input file path and output file path.
    output: None (writes a CSV file to disk).
    error_handling: Gracefully handles malformed rows by skipping them or flagging them, and ensures the output file is produced even if some individual rows fail to process.
