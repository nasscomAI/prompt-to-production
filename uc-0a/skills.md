skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag using pre-defined heuristic rules.
    input: dict containing complaint row details with a 'description' key.
    output: dict containing keys: complaint_id, category, priority, reason, flag.
    error_handling: If the input is missing the 'description' key, or if the description is null or empty, it returns category: 'Other', priority: 'Low', reason: 'Missing or empty description', and flag: 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Read an input CSV file, classify each complaint row sequentially, and write the classified results to an output CSV file.
    input: Paths to the input CSV file and the output CSV file as strings.
    output: None (writes results to output CSV file).
    error_handling: Handles empty files, invalid CSV formats, or missing columns by logging warnings/errors, and ensures it continues processing other rows if a single row processing fails.
