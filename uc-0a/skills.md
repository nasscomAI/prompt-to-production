# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag
    input: dict with keys complaint_id (str) and description (str)
    output: dict with keys complaint_id (str), category (str: one of 10 allowed), priority (str: Urgent/Standard/Low), reason (str: one sentence citing description words), flag (str: "NEEDS_REVIEW" or "")
    error_handling: Returns category "Other", priority "Low", reason with error message, flag "NEEDS_REVIEW"

  - name: batch_classify
    description: Read input CSV, apply classify_complaint to each row, write results CSV
    input: input_path (str: path to test_[city].csv), output_path (str: path to write results)
    output: Writes CSV with columns complaint_id, category, priority, reason, flag
    error_handling: Skips bad rows, writes error results with NEEDS_REVIEW flag, continues processing