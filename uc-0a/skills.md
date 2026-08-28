skills:
  - name: classify_complaint
    description: "Classify one citizen complaint into the fixed category and priority taxonomy with an evidence-based reason."
    input: "A dict-like row containing complaint_id and description strings."
    output: "A dict containing complaint_id, category, priority, reason, and flag."
    error_handling: "For missing or null fields, preserve the complaint_id when available, use Other with NEEDS_REVIEW for an undetermined category, use a non-urgent priority unless a severity keyword is present, and always return a reason that identifies the missing or ambiguous input. Never raise for a malformed row."

  - name: batch_classify
    description: "Read complaint rows from a CSV, classify each row, and write one result row per input row to a CSV."
    input: "An input CSV path containing complaint_id and description columns, plus an output CSV path."
    output: "A CSV containing complaint_id, category, priority, reason, and flag for every input row."
    error_handling: "Do not crash on nulls or malformed rows; emit a flagged result for each bad row and continue processing the remaining rows so an output file is produced."
