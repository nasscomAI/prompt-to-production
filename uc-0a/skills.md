# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into category, priority, reason, and flag.
    input: A dict with complaint_id, ward, and description (strings).
    output: A dict with complaint_id, category, priority, reason, flag.
    error_handling: If description is empty or no category keyword matches, returns category "Other" and flag "NEEDS_REVIEW" instead of guessing; never raises on missing optional fields.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: input_path (str, path to test_[city].csv), output_path (str).
    output: Writes a CSV with columns complaint_id, ward, description, category, priority, reason, flag; returns nothing.
    error_handling: If a single row cannot be processed, it is written with category "Other", flag "NEEDS_REVIEW", and a reason explaining the failure — the whole batch never crashes because of one bad row.
