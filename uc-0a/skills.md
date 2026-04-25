# skills.md

skills:
  - name: classify_complaint
    description: Processes a single citizen complaint to extract category, priority, justification, and review flag.
    input: A single complaint row data (including 'complaint_id').
    output: A dictionary where the key is 'complaint_id' and the value is a dictionary of classification fields.
    error_handling: If the description is ambiguous, set flag to 'NEEDS_REVIEW' and category to 'Other'.

  - name: batch_classify
    description: Orchestrates the classification process for an entire dataset, reading from a source CSV and generating a comprehensive dictionary of results.
    input: Path to the input CSV file.
    output: A master dictionary containing all complaints, keyed by 'complaint_id', including original data and classifications.
    error_handling: Ensure the final structure maintains consistent keys and handles file I/O or schema mismatches.
