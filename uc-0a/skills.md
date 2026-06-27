skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using keyword-based enforcement rules from agents.md.
    input: dict with keys complaint_id (str), description (str) — other fields are passed through unchanged.
    output: dict with keys complaint_id, category (str, one of 10 allowed values), priority (Urgent/Standard/Low), reason (str quoting words from description), flag (NEEDS_REVIEW or empty string).
    error_handling: If description is empty or None, output category=Other, priority=Standard, reason="No description provided", flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes a results CSV with the four added fields.
    input: input_path (str, path to test_[city].csv), output_path (str, path to write results CSV).
    output: CSV file at output_path with all original columns plus category, priority, reason, flag. Also prints a summary to stdout showing row count, Urgent count, and NEEDS_REVIEW count.
    error_handling: Skips rows where description is missing and marks them NEEDS_REVIEW; never crashes on a single bad row — logs the error and continues.
