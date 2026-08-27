# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and optional review flag using only the complaint description.
    input: A Python dict with at minimum the keys complaint_id (str) and description (str); all other CSV fields are ignored by this skill.
    output: A Python dict with exactly four keys — category (str, one of the 10 allowed values), priority (str: Urgent / Standard / Low), reason (str, one sentence quoting words from description), flag (str: NEEDS_REVIEW or empty string).
    error_handling: If description is missing or empty, set category to Other, priority to Low, reason to "Description was empty or missing — cannot classify.", and flag to NEEDS_REVIEW. Never raise an unhandled exception; always return a dict.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to every row, and writes a results CSV containing the original complaint_id plus the four classification fields.
    input: Two file-path strings — input_path pointing to a CSV with a header row containing at minimum complaint_id and description columns, and output_path for the results file.
    output: A CSV file at output_path with columns: complaint_id, category, priority, reason, flag. Rows that fail classification individually are written with category Other, priority Low, and flag NEEDS_REVIEW rather than crashing the batch.
    error_handling: If the input file is not found or is malformed, print a clear error message and exit with a non-zero status code. If an individual row raises an unexpected exception, catch it, log the complaint_id and error to stderr, write a NEEDS_REVIEW row for that complaint, and continue processing remaining rows.
