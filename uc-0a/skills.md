# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using the fixed enum and severity keyword rules.
    input: A dict (one row from test_[city].csv) with at least the keys complaint_id and description.
    output: A dict with keys complaint_id, category, priority, reason, flag. category is one of the 10 allowed strings; priority is Urgent/Standard/Low; reason quotes words from the description; flag is NEEDS_REVIEW or blank.
    error_handling: If description is missing or empty, returns category: Other, priority: Standard, reason quoting that no description was provided, flag: NEEDS_REVIEW. Never raises on malformed input.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, writes the results CSV with one output row per input row.
    input: input_path (path to test_[city].csv) and output_path (path to write results_[city].csv).
    output: Writes a CSV with columns complaint_id, category, priority, reason, flag; prints the total row count on completion.
    error_handling: Flags rows with missing/blank description as NEEDS_REVIEW instead of crashing; continues on bad rows and always produces an output file even if some rows fail.
