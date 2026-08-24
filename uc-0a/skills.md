# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Assigns a category, priority, one-sentence justification and optional NEEDS_REVIEW flag to a single complaint row.
    input: One complaint row as a dict; required key is description (string), plus complaint_id for traceability.
    output: A dict with keys complaint_id, category, priority, reason, flag — where category is one of the ten exact schema strings, priority is one of Urgent/Standard/Low, reason is a single sentence quoting the description, and flag is NEEDS_REVIEW or empty.
    error_handling: Missing or empty description yields category Other with flag NEEDS_REVIEW instead of failing; ambiguous evidence yields NEEDS_REVIEW with the best-supported category rather than a confident guess; never raises on unexpected field values.

  - name: batch_classify
    description: Reads a city test CSV, applies classify_complaint to every row, and writes the classified results to an output CSV.
    input: Path to an input CSV (header row, UTF-8) containing at least complaint_id and description columns, and the path to write the results CSV.
    output: A results CSV with columns complaint_id, category, priority, reason, flag — exactly one output row per input row in the same order.
    error_handling: A malformed row is emitted as category Other with flag NEEDS_REVIEW instead of aborting the batch; a missing or unreadable input file exits with a clear error before any output is written.
