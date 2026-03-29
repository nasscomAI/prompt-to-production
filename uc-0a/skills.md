# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to assign category, priority, reason, and flag.
    input: Dictionary with keys: complaint_id, ward, location, description.
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If description is null, set category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Processes a CSV file of complaints, applying classify_complaint to each row.
    input: Path to test_[city].csv.
    output: Writes results to results_[city].csv.
    error_handling: Skips malformed rows, logs errors to console, ensures output is produced for valid rows.
