skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using keyword-based enforcement rules.
    input: A dict with keys complaint_id and description (both strings).
    output: A dict with keys complaint_id, category, priority, reason, flag — all strings; flag is NEEDS_REVIEW or empty string.
    error_handling: If description is missing or empty, sets category to Other, priority to Low, reason to "No description provided", and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each, and writes results to an output CSV.
    input: input_path (str) path to CSV with columns complaint_id and description; output_path (str) path for results CSV.
    output: A CSV file at output_path with columns complaint_id, category, priority, reason, flag.
    error_handling: Skips rows missing complaint_id with a warning; catches per-row exceptions and writes category=Other, flag=NEEDS_REVIEW for failed rows so the output file always completes.
