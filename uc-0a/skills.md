skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag using strict RICE enforcement rules.
    input: A dict with at minimum the keys 'complaint_id' and 'description' (strings). Location is optional context.
    output: A dict with keys — complaint_id (str), category (str, exact enum), priority (str: Urgent/Standard/Low), reason (str, one sentence citing description words), flag (str: NEEDS_REVIEW or empty).
    error_handling: If description is missing or empty, set category to Other, priority to Low, reason to 'No description provided', flag to NEEDS_REVIEW. Never raise an exception; always return a complete dict.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with the classification fields appended.
    input: input_path (str) — path to a CSV file with columns including complaint_id and description. output_path (str) — path for the results CSV file.
    output: A CSV file at output_path containing all original columns plus category, priority, reason, and flag. Rows that fail classification individually are written with error values and NEEDS_REVIEW flag rather than crashing the whole batch.
    error_handling: If a row is malformed (missing required columns), write that row with category=Other, priority=Low, reason='Row error — missing fields', flag=NEEDS_REVIEW and continue to next row. If the input file cannot be read, raise FileNotFoundError with a descriptive message.
