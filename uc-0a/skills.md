# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: >
      A dictionary with keys: complaint_id (str), date_raised (str), city (str),
      ward (str), location (str), description (str), reported_by (str), days_open (str).
    output: >
      A dictionary with keys: complaint_id (str), category (str — one of 10 allowed values),
      priority (str — Urgent | Standard | Low), reason (str — one sentence citing description words),
      flag (str — NEEDS_REVIEW or empty string).
    error_handling: >
      If description is empty or missing, returns category=Other, priority=Standard,
      reason="No description provided", flag=NEEDS_REVIEW.
      If multiple categories match equally, returns category=Other, flag=NEEDS_REVIEW
      with reason explaining the ambiguity.

  - name: batch_classify
    description: Reads an input CSV file, classifies each row using classify_complaint, and writes results to an output CSV file.
    input: >
      input_path (str) — path to the source CSV file with complaint rows.
      output_path (str) — path to write the results CSV file.
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority, reason, flag.
      One row per input complaint. Console summary of total rows processed, errors, and flags.
    error_handling: >
      Skips rows that cause exceptions (logs a warning to stderr).
      Always produces an output file even if some rows fail.
      Reports count of failed rows at the end.
