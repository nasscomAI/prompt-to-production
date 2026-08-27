skills:
  - name: classify_complaint
    description: Classifies a single complaint row based on keywords and severity indicators, returning category, priority, reason, and review flags.
    input: Dictionary containing complaint details (complaint_id, description, etc.).
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: Handles empty description or invalid fields by categorizing as 'Other' and flagging for review.

  - name: batch_classify
    description: Reads a CSV of complaints, runs the classification logic on each row, and writes the results to an output CSV.
    input: Input CSV path (string), Output CSV path (string).
    output: None (writes results file).
    error_handling: Continues processing if individual rows are invalid and logs warnings.
