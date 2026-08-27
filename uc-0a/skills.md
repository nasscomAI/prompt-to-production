# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag.
    input: Dictionary mapping complaint fields (complaint_id, description, etc.) to values.
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: Map category to 'Other' and set flag to 'NEEDS_REVIEW' if classification is ambiguous or details are missing.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to each row, and writes results to output CSV.
    input: Paths to input CSV and output CSV.
    output: None (writes results file).
    error_handling: Log/skip row parse errors without crashing the batch run, ensuring all valid rows are processed.
