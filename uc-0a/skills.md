skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag using weighted keyword matching against the fixed 10-category taxonomy.
    input: A dict representing one CSV row with keys 'complaint_id', 'description', and optionally 'days_open'.
    output: A dict with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Returns category 'Other', priority 'Low', and flag 'NEEDS_REVIEW' for empty or missing descriptions. On ambiguity between categories, picks the highest-scoring category and sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row, and writes classified results to an output CSV.
    input: Two strings — input_path (source CSV) and output_path (destination CSV).
    output: None; writes results CSV to output_path.
    error_handling: Reports FileNotFoundError for missing input. Per-row errors produce a fallback row with flag 'NEEDS_REVIEW' so one bad row does not crash the batch.
