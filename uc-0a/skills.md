# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: One row as a dict with keys including description, ward, location, reported_by, days_open.
    output: A dict with keys complaint_id, category, priority, reason, flag.
    error_handling: If the category is ambiguous, returns category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Input CSV path (test_[city].csv) and output CSV path (results_[city].csv).
    output: A results CSV with one row per input complaint, all fields present.
    error_handling: Flags nulls, does not crash on bad rows, and still produces output even if some rows fail.
