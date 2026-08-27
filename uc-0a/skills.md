# skills.md — UC-0A

skills:
  - name: classify_complaint
    description: Maps one complaint dict to category, priority, reason, and optional NEEDS_REVIEW flag using the locked taxonomy and severity list.
    input: "dict with at least keys complaint_id and description (string); other columns ignored."
    output: "dict with keys complaint_id, category, priority, reason, flag — all strings."
    error_handling: "On missing description, treat as empty string and classify as Other with NEEDS_REVIEW. Exceptions are caught in batch_classify and written as Other with a reason noting the error."

  - name: batch_classify
    description: Streams an input CSV of complaints and writes a results CSV with one classified row per input row in order.
    input: "Filesystem paths: input CSV (UTF-8), output CSV path to create or overwrite."
    output: "CSV with columns complaint_id, category, priority, reason, flag."
    error_handling: "Per-row failures do not stop the batch; failed rows become Other / NEEDS_REVIEW with an error note in reason."
