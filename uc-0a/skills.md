# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and review flag using only the description text.
    input: >
      A dict with keys: complaint_id (str), description (str), location (str), date (str).
      Only description is used for classification.
    output: >
      A dict with keys: complaint_id (str), category (str — one of 10 allowed values), priority (str — Urgent, Standard, or Low), reason (str — one sentence citing description words), flag (str — NEEDS_REVIEW or empty string).
    error_handling: >
      If description is empty or null, return category "Other", priority "Low", reason citing the empty state, and flag "NEEDS_REVIEW". If description contains ambiguous keywords spanning multiple categories, flag "NEEDS_REVIEW" and pick the strongest match for category.

  - name: batch_classify
    description: Read an input CSV of complaint rows, apply classify_complaint to each, and write results to an output CSV.
    input: >
      Two file paths: input_path (str) pointing to a CSV with columns complaint_id, description, location, date; output_path (str) for the results CSV.
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority, reason, flag. One row per input row, preserving original order.
    error_handling: >
      Never crash on bad rows — if a row is malformed or missing required fields, classify it as category "Other", priority "Low", reason "Row data incomplete or malformed", flag "NEEDS_REVIEW". Produce output even if every row fails. Print a count of failed rows to stdout.
