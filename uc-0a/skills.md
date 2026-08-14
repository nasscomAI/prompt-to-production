# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: One row from test_[city].csv as a dict (complaint_id, date_raised, city, ward, location, description, reported_by, days_open).
    output: A dict with exactly: complaint_id, category, priority, reason, flag (NEEDS_REVIEW or blank).
    error_handling: If the description cannot determine a category, returns category: Other with flag: NEEDS_REVIEW. If the row is missing the description field, returns flag: NEEDS_REVIEW instead of guessing.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Path to test_[city].csv and path to the output CSV file.
    output: results_[city].csv with one row per input row; every row has the 5 required columns (complaint_id, category, priority, reason, flag).
    error_handling: Skips null/blank rows and records them with flag: NEEDS_REVIEW. Never crashes on a bad row — it must produce an output file even if some rows fail. Verifies each output row against the 10 allowed category strings and the severity keyword list before writing.
