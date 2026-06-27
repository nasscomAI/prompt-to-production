# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, reason, and flag using keyword-based rules derived from the complaint description.
    input: A dict representing one CSV row with at minimum the keys complaint_id (str) and description (str).
    output: A dict with keys complaint_id (str), category (str — one of 10 allowed values), priority (str — Urgent/Standard/Low), reason (str — one sentence citing description text), flag (str — NEEDS_REVIEW or empty string).
    error_handling: If description is missing or empty, set category to Other, priority to Low, reason to "No description provided", and flag to NEEDS_REVIEW. Never raise an exception; always return a complete output dict.

  - name: batch_classify
    description: Reads an input CSV of raw complaints, applies classify_complaint to every row, and writes a results CSV with the classification columns appended.
    input: input_path (str — path to test_[city].csv), output_path (str — path for results_[city].csv).
    output: A CSV file at output_path with columns complaint_id, category, priority, reason, flag. One row per input row.
    error_handling: If a row fails to classify (unexpected error), write the row with category=Other, priority=Low, reason="Classification error", flag=NEEDS_REVIEW and continue processing remaining rows. Never crash on a bad row. Report total rows processed and any error rows to stdout on completion.
