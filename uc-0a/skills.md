# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: >
      Classify a single civic complaint row into category, priority, reason, and flag.
    input: >
      dict — A single complaint row with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open.
    output: >
      dict — Keys: complaint_id (str, copied from input), category (str, one of 10 allowed values),
      priority (str, Urgent or Standard), reason (str, one sentence citing words from description),
      flag (str, NEEDS_REVIEW or empty string).
    error_handling: >
      If description is missing or empty, set category: Other, priority: Standard,
      reason: "Description missing or empty", flag: NEEDS_REVIEW.
      If description doesn't clearly map to any category, set category: Other and flag: NEEDS_REVIEW.
      Never raise an exception — always return a dict with the five required keys.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, classify every row using classify_complaint,
      and write a results CSV with columns: complaint_id, category, priority, reason, flag.
    input: >
      Two paths: input_path (str, path to CSV with complaint rows) and
      output_path (str, path to write results CSV).
    output: >
      Writes a CSV file at output_path with header and one row per input row.
      Prints "Done. Results written to {output_path}" on success.
    error_handling: >
      If a row has missing or corrupt data, classify it with flag: NEEDS_REVIEW and
      reason describing the problem, then continue processing remaining rows.
      If the input CSV cannot be read, print an error and exit with code 1.
      Never crash on a single bad row — produce output for all rows that can be processed.
