# skills.md

skills:
  - name: classify_complaint
    description: Receives a single complaint row and classifies it into predefined category, priority, reason, and flag out.
    input: Dictionary of complaint fields (id, location, description, etc).
    output: Dictionary with keys (complaint_id, category, priority, reason, flag).
    error_handling: Return category 'Other' and flag 'NEEDS_REVIEW' if input is invalid or extremely ambiguous.

  - name: batch_classify
    description: Reads a CSV of multiple complaints, applies classify_complaint to each row, and writes an output CSV.
    input: Input file path and output file path as strings.
    output: None directly, writes a CSV file to disk.
    error_handling: Skips rows that cannot be parsed, logs an error, and continues processing the rest.
