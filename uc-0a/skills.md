# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into category + priority + reason + flag using the fixed taxonomy and severity keywords.
    input: dict — a single row from the input CSV (complaint_id, date_raised, city, ward, location, description, reported_by, days_open)
    output: dict — keys complaint_id, category, priority, reason, flag
    error_handling: Never crashes on a malformed row; falls back to category Other, flag NEEDS_REVIEW and a reason that says the row needs manual review.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to every row, and write a results CSV with the five output columns.
    input: input_path (str) and output_path (str)
    output: writes results CSV with header complaint_id, category, priority, reason, flag and one row per input row
    error_handling: A bad row is flagged NEEDS_REVIEW and skipped from crashing the run; output is always produced even if some rows fail.