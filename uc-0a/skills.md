# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dict representing one CSV row with at minimum a `description` field and a `complaint_id` field.
    output: A dict with keys complaint_id, category (one of 10 allowed values), priority (Urgent/Standard/Low), reason (one sentence citing description text), flag (NEEDS_REVIEW or blank).
    error_handling: If description is missing, empty, or whitespace-only, returns category=Other, priority=Standard, flag=NEEDS_REVIEW, reason="No description was provided." Never raises an exception or skips the row.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes a results CSV.
    input: input_path (str, path to test_[city].csv) and output_path (str, path to write results CSV).
    output: A CSV file with columns complaint_id, category, priority, reason, flag — one row per input complaint.
    error_handling: If a row fails classification, it is included in output with category=Other, priority=Standard, flag=NEEDS_REVIEW, and reason describing the error. The batch never crashes on a single bad row. FileNotFoundError on input prints an error and exits.
