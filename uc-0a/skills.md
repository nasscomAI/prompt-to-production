# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: A dictionary representing one CSV row with at minimum a 'description' field (string) and 'complaint_id' field (string).
    output: A dictionary with keys — complaint_id (str), category (str from allowed list), priority (str: Urgent|Standard|Low), reason (str: one sentence), flag (str: NEEDS_REVIEW or empty string).
    error_handling: If description is empty/null/unintelligible, returns category=Other, priority=Low, reason='Description insufficient for classification', flag=NEEDS_REVIEW. Never raises an exception — always returns a valid output dict.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes a results CSV.
    input: input_path (str) — path to a CSV file with columns including complaint_id and description; output_path (str) — path where results CSV will be written.
    output: A CSV file written to output_path with columns — complaint_id, category, priority, reason, flag. Also prints a summary of total/succeeded/failed rows to stdout.
    error_handling: Rows that fail classification (malformed data, missing columns) are logged to stderr and skipped — they do not crash the batch. The output CSV is written even if some rows fail. Exit code 0 if all rows succeed, exit code 3 if some rows fail (partial failure).
