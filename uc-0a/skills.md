skills:
  - name: classify_complaint
    description: Takes one row of complaint data and computes the category, priority, reason, and flag fields strictly based on predefined rules.
    input: Dictionary of CSV row data containing at least 'description' and 'location'.
    output: Dictionary with original data plus new fields 'category', 'priority', 'reason', and 'flag'.
    error_handling: Output category as 'Other' and set flag 'NEEDS_REVIEW' if ambiguity or missing data is encountered.

  - name: batch_classify
    description: Reads an input CSV containing complaints, applies classify_complaint to each row, and writes to an output CSV.
    input: file path to input CSV and output CSV
    output: Writes processed CSV file on disk.
    error_handling: Logs failing rows but does not crash, processing the rest cleanly.
