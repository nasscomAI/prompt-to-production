skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using UC-0A enforcement rules.
    input: One CSV row as a dictionary with complaint_id and free-text fields such as description/title/location (string values).
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: If text is missing or ambiguous, returns category Other, priority Standard (or Urgent if severity keywords exist), non-empty reason, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint row-by-row, and writes a stable output CSV without crashing.
    input: input_path string for source CSV and output_path string for destination CSV.
    output: CSV file with columns complaint_id, category, priority, reason, flag for every row processed.
    error_handling: Handles bad rows with safe fallbacks, preserves complaint_id when available, sets NEEDS_REVIEW when needed, and continues processing remaining rows.
