# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag.
    input: A dict with at least complaint_id and description (strings from the input CSV).
    output: A dict with complaint_id, category, priority, reason, flag. Category is always one of the
      fixed 10-value enum; priority is Urgent or Standard; reason quotes words from the description;
      flag is NEEDS_REVIEW only when the category is genuinely ambiguous, otherwise blank.
    error_handling: If description is missing or unreadable, return category Other, priority Standard,
      reason "Description unavailable", flag NEEDS_REVIEW rather than raising.

  - name: batch_classify
    description: Read an input complaints CSV, apply classify_complaint to every row, write the results CSV.
    input: Path to the input CSV (test_[city].csv) and the output path for results_[city].csv.
    output: Writes a CSV with columns complaint_id, category, priority, reason, flag — one row per input row,
      in the same order, preserving every row even if one row is malformed.
    error_handling: Skips malformed rows by still emitting a flagged row, never crashes the batch; reports
      a summary of how many rows were classified and how many were flagged.
