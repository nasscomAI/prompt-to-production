skills:
  - name: classify_complaint
    description: Classifies one complaint row into schema-compliant category, priority, reason, and flag.
    input: "object with complaint_id (string/int) and description (string, non-empty plain text)."
    output: "object with category (allowed enum), priority (Urgent|Standard|Low), reason (one sentence citing source words), and flag (NEEDS_REVIEW or blank)."
    error_handling: "If description is missing/empty, return category=Other, priority=Standard, reason='Description missing; unable to classify from evidence.', flag=NEEDS_REVIEW; if ambiguous, use category=Other and flag=NEEDS_REVIEW; never invent labels or sub-categories."

  - name: batch_classify
    description: Reads the UC input CSV, applies classify_complaint to each row, and writes results CSV with required columns.
    input: "input_csv_path (string path) to a CSV where category and priority_flag are absent and each row has complaint text."
    output: "output_csv_path (string path) containing one row per input record with columns including category, priority, reason, and flag."
    error_handling: "If file path is invalid or CSV is malformed, stop and return a clear processing error; if a row is invalid, classify it as Other with NEEDS_REVIEW instead of dropping it; enforce exact taxonomy to prevent taxonomy drift and reject non-schema category values before writing output."
