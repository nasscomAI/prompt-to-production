# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single civic complaint to determine category, priority, justification, and flag status.
    input: dict with keys 'complaint_id' and 'description' (and other row metadata)
    output: dict with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'
    error_handling: If description is missing or empty, output category 'Other', priority 'Low', reason 'Missing description', flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV file of complaints, processes each row using classify_complaint, and writes the output to a new CSV.
    input: input_path (string) representing path to input CSV, output_path (string) representing path to output CSV
    output: void (writes a CSV file to disk)
    error_handling: Skips rows that fail to parse without completely crashing, but ensures the process completes and outputs valid rows alongside error logging.
