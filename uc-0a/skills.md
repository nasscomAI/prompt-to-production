

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into a category and priority with a reason and review flag.
    input: Dictionary (CSV row) containing complaint data.
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: Return category 'Other' and flag 'NEEDS_REVIEW' if the input is genuinely ambiguous.

  - name: batch_classify
    description: Read an input CSV, classify each row using classify_complaint, and write results to an output CSV.
    input: input_path (str), output_path (str).
    output: None (writes to CSV).
    error_handling: Must flag nulls, not crash on bad rows, and produce output even if some rows fail.
