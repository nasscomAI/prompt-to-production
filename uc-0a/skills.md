# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using the UC-0A schema.
    input: One complaint row as a dict with a description field (string).
    output: dict with exactly the keys complaint_id, category, priority, reason, flag, where category is one of the ten exact schema strings, priority is Urgent/Standard/Low, reason is one sentence citing verbatim words from the description, and flag is blank or NEEDS_REVIEW.
    error_handling: If a severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) appears, forces priority to Urgent; if the category is genuinely ambiguous from the description alone, outputs category Other and flag NEEDS_REVIEW, never guessing with false confidence; if reason cannot cite exact description words, flags the row instead of fabricating justification.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Path to the input CSV (test_[city].csv) with 15 rows and a description column.
    output: Path to the output CSV (uc-0a/results_[city].csv) with exactly one row per input row and header complaint_id, category, priority, reason, flag.
    error_handling: Never crashes or drops a row on malformed input — marks the offending row with flag NEEDS_REVIEW and continues so output is still produced; preserves the full 15-row count and valid CSV format even when some rows fail.