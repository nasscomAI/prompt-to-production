# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dict representing one CSV row with keys including complaint_id and description.
    output: A dict with keys complaint_id, category, priority, reason, flag.
    error_handling: >
      If description is empty or missing, returns category=Other, priority=Low,
      reason="No description provided", flag=NEEDS_REVIEW. Never raises an
      exception — always returns a valid output dict.

  - name: batch_classify
    description: Reads an input CSV, classifies every row using classify_complaint, and writes a results CSV.
    input: input_path (str) path to test CSV, output_path (str) path for results CSV.
    output: A CSV file at output_path with columns complaint_id, category, priority, reason, flag.
    error_handling: >
      Skips rows that cause unexpected errors, logs them to stderr, and
      continues processing. Always produces an output file even if some rows
      fail. Reports total processed and failed counts to stdout.
