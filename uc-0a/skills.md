# skills.md

skills:
  - name: classify_complaint
    description: Assigns one civic complaint a category, priority, cited reason, and ambiguity flag using deterministic keyword rules.
    input: dict with keys complaint_id (str) and description (str); may contain extra fields which are ignored.
    output: dict with keys complaint_id (str), category (one of the ten exact taxonomy strings), priority (Urgent | Standard | Low), reason (one sentence quoting words from the description), flag ("NEEDS_REVIEW" or empty string).
    error_handling: Does not raise for dict rows; missing/null/empty description returns category Other with flag NEEDS_REVIEW; multi-category matches resolve to the highest-precedence category but set flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: Path to a UTF-8 CSV with a header row including complaint_id and description columns; plus the output path.
    output: Writes a UTF-8 CSV with columns complaint_id, category, priority, reason, flag — one row per input row, same order.
    error_handling: A per-row exception is caught and recorded as Other / Standard / NEEDS_REVIEW instead of aborting the batch; the output file is always produced even if some rows fail.
