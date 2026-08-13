# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify one complaint row into category, priority, reason, and flag.
    input: dict — one CSV row (complaint_id, description, ward, location, ...)
    output: dict — {complaint_id, category, priority, reason, flag}
    error_handling: No keyword match → category "Other" + flag NEEDS_REVIEW; matches for two or more distinct categories → best-guess category + flag NEEDS_REVIEW; severity keyword present → priority Urgent.

  - name: batch_classify
    description: Read input CSV, apply classify_complaint to every row, write results CSV.
    input: input_path (path to test_[city].csv), output_path (path to results_[city].csv)
    output: Writes results CSV with columns complaint_id, category, priority, reason, flag — one row per input row.
    error_handling: Never crashes on a bad row — mark it category Other + flag NEEDS_REVIEW and continue; always produces an output file even if some rows fail.
