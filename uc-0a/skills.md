skills:
  - name: classify_complaint
    description: Classify a single civic complaint row into category, priority, reason, and flag.
    input: A dictionary representing a CSV row with keys like 'complaint_id', 'description', etc.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Return category 'Other', priority 'Standard', and flag 'NEEDS_REVIEW' if the input row lacks a description or is completely corrupted.

  - name: batch_classify
    description: Read input CSV containing complaints, classify each row, and write output CSV.
    input: Input CSV filepath (str) and output CSV filepath (str).
    output: None (writes results to output CSV file).
    error_handling: Handles empty files gracefully, logs row-level errors without crashing, and ensures all successfully processed rows are written to output.
