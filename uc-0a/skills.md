# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Maps one CSV row to category, priority, reason, and optional NEEDS_REVIEW flag per agents.md enforcement.
    input: A dict representing one row; must include `description` (string) and `complaint_id` (string). Other columns are passed through or ignored by the classifier.
    output: A dict with keys `complaint_id`, `category`, `priority`, `reason`, `flag` — all string values; `flag` is either empty or exactly `NEEDS_REVIEW`.
    error_handling: If `description` is missing or blank, set category to Other, priority Standard, reason noting missing text, flag NEEDS_REVIEW. On unexpected internal errors, do not crash the batch: surface a safe fallback row (Other, NEEDS_REVIEW) and continue.

  - name: batch_classify
    description: Reads an input CSV, runs classify_complaint on each row, and writes the classification result CSV.
    input: File paths — `input_path` to a UTF-8 CSV with headers including `complaint_id` and `description`; `output_path` for the results file.
    output: A CSV file with columns `complaint_id`, `category`, `priority`, `reason`, `flag` (one row per input row, same order as input unless a row is skipped with documented behavior).
    error_handling: Skip or recover malformed rows without terminating the whole job; log or encode failures in output using Other + NEEDS_REVIEW when a row cannot be classified. Ensure the output file is written even if some rows fail.
