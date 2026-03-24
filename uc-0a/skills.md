skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using keyword matching against the approved taxonomy and severity trigger list.
    input: A dict with keys complaint_id (str) and description (str).
    output: A dict with keys complaint_id (str), category (str — one of 10 allowed values), priority (str — Urgent/Standard/Low), reason (str — one sentence citing description words), flag (str — NEEDS_REVIEW or blank).
    error_handling: If description is empty or missing, output category Other, priority Standard, reason "No description provided", flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the classified output to a new CSV file.
    input: input_path (str — path to CSV with complaint_id and description columns), output_path (str — path to write results CSV).
    output: A CSV file at output_path with columns complaint_id, category, priority, reason, flag. One row per input row.
    error_handling: If a row fails classification, write category Other, flag NEEDS_REVIEW, and reason "Classification error" for that row — do not crash the entire batch. Log the error to stderr.
