# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row to determine category, priority, reason, and review flag.
    input: A dictionary containing the keys 'complaint_id', 'description', and other metadata fields.
    output: A dictionary containing the keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is empty or ambiguous, categorize as 'Other' and set the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Read an input CSV file of citizen complaints, classify each row using classify_complaint, and write the output CSV.
    input: Absolute paths to input CSV and output CSV.
    output: A generated CSV file containing the original columns plus 'category', 'priority', 'reason', and 'flag'.
    error_handling: Handles missing data, ignores malformed rows without crashing, and generates the output file even if some classifications fail.
