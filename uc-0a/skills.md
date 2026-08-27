# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using the fixed schema.
    input: A dict with at least complaint_id and description (free text).
    output: A dict with keys complaint_id, category, priority, reason, flag.
    error_handling: >
      If the description is empty or the category cannot be inferred, returns
      category "Other", flag "NEEDS_REVIEW", priority "Low", and a reason stating
      the ambiguity. Never raises on a single bad row.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row, and writes a results CSV.
    input: Path to input CSV (columns include complaint_id, description, ...).
    output: Path to output CSV with columns complaint_id, category, priority, reason, flag.
    error_handling: >
      Skips and logs malformed rows instead of crashing; writes whatever valid rows
      it produced. Reports the count of rows flagged NEEDS_REVIEW at the end.
