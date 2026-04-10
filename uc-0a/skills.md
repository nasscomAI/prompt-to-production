# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based on schema rules.
    input: Dictionary representing a CSV row with at least a 'description' field.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If input is missing or category is unclear, returns category 'Other' and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates reading an input CSV, applying classification to each row, and writing results to an output CSV.
    input: String path to input CSV file and string path to output CSV file.
    output: Writes to disk; returns completion status or log of processed rows.
    error_handling: Skips malformed rows with a warning, ensuring the rest of the batch is processed and written.
