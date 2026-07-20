skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a standardized category, priority, reason, and review flag.
    input: A dictionary representing a row from the complaint CSV, containing at least the keys 'complaint_id' and 'description'.
    output: A dictionary containing the keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If 'description' is missing or null, return category: 'Other', priority: 'Low', reason: 'Missing complaint description.', flag: 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill on each row, and writes the results to an output CSV file.
    input: Paths to the input CSV file and the output CSV file as strings.
    output: None (writes results directly to output file).
    error_handling: Logs warning and continues processing other rows if a single row is corrupt or malformed, and refuses to run if the input file does not exist.
