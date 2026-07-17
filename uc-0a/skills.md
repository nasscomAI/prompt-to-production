# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dictionary with key "description" containing the complaint text (string).
    output: A dictionary with keys: category (string from allowed list), priority (Urgent/Standard/Low), reason (one sentence citing description words), flag (NEEDS_REVIEW or blank).
    error_handling: If description is empty or unreadable, set category to Other and flag to NEEDS_REVIEW with reason noting invalid input.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: File path to input CSV (string) containing at least a "description" column; file path to output CSV (string).
    output: A new CSV file with columns: category, priority, reason, flag — one row per input complaint.
    error_handling: If input file is missing or has no description column, raise a clear error. If individual rows fail classification, classify them as Other with NEEDS_REVIEW flag and continue processing remaining rows.
