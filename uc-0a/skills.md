# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Takes a single complaint description and returns its classification (category, priority, reason, flag).
    input: A string containing the complaint description.
    output: A dictionary with keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the input is empty or invalid, returns category 'Other', priority 'Low', reason 'Invalid input', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths for the input CSV and output CSV.
    output: None (writes to file).
    error_handling: Raises an error if the input file is not found or cannot be read.
