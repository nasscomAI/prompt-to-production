skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using only that row's own description text.
    input: A dict/row with at least a complaint_id and description field (and any other original columns from the input CSV).
    output: A dict with keys complaint_id, category (one of the 10 fixed values), priority (Urgent/Standard/Low), reason (one sentence citing words from the description), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty, missing, or too short/vague to support any specific category, sets category to Other, flag to NEEDS_REVIEW, and reason explains that the description was insufficient to classify -- never fabricates a specific category in this case.

  - name: batch_classify
    description: Reads the per-city input CSV, applies classify_complaint to every row, and writes a results CSV without crashing on any individual bad row.
    input: A file path (string) to the input CSV (test_[city].csv) and an output file path (string).
    output: A results CSV file with one row per input complaint, containing complaint_id, category, priority, reason, and flag columns, written to the given output path.
    error_handling: If a given row is malformed (e.g. missing complaint_id or description entirely), the row is still written to the output with category Other, flag NEEDS_REVIEW, and a reason noting the row was malformed, rather than skipping the row silently or crashing the whole batch.
