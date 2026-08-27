# skills.md

skills:
  - name: classify_complaint
    description: Applies heuristic rules based on keywords to categorize complaints, assess priority, and construct justification.
    input: Dictionary representing a single complaint row.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Raises an exception internally if input malformed, but safely returns default 'Other'/'NEEDS_REVIEW' if attributes are missing or parsing fails.

  - name: batch_classify
    description: Reads a CSV input, applies classify_complaint iterating over all rows securely, and saves to an output CSV file.
    input: Input CSV file path string, output CSV file path string.
    output: None (writes to standard output side-effects).
    error_handling: Handles empty files gracefully, logs warnings but continues processing if specific rows throw unexpected errors.
