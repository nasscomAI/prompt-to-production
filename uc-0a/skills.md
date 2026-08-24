# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: Dictionary containing complaint details, specifically the 'description' field.
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If input is missing or malformed, return category 'Other' and flag 'NEEDS_REVIEW'. If ambiguous, flag as 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the output CSV.
    input: String path to input CSV and String path to output CSV.
    output: None (writes a CSV file to disk).
    error_handling: Must flag nulls, skip bad rows without crashing, and produce output even if some rows fail.
