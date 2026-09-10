# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into a category, priority, reason, and review flag using only its description field.
    input: A dict for one CSV row, must include complaint_id (str) and description (str). Other columns (city, ward, location, reported_by, days_open) are ignored.
    output: A dict with complaint_id (str), category (one of the 10 allowed values), priority (Urgent | Standard | Low), reason (one sentence citing words from the description), flag (NEEDS_REVIEW or "").
    error_handling: If description is missing/empty, returns category "Other", priority "Low", flag "NEEDS_REVIEW" with a reason stating no description was provided — never raises, never guesses a category from other fields.

  - name: batch_classify
    description: Reads an input complaint CSV, applies classify_complaint to every row, and writes a results CSV with one classified row per input row.
    input: input_path (str, path to test_[city].csv), output_path (str, path to write results_[city].csv).
    output: Writes output_path as a CSV with columns complaint_id, category, priority, reason, flag — one row per input row, same order as input.
    error_handling: If a single row raises an exception during classification, that row is still written to the output as category "Other", priority "Low", flag "NEEDS_REVIEW" with the error message in reason — one bad row never aborts the batch or drops the row from the output.
