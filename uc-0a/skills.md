skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using the keyword rules defined in agents.md.
    input: dict containing keys complaint_id (string), location (string), description (string) from one CSV row
    output: dict with keys complaint_id (string), category (one of 10 allowed strings), priority (Urgent/Standard/Low), reason (string, one sentence quoting source words), flag (NEEDS_REVIEW or empty string)
    error_handling: If description is empty or None, set category to Other, priority to Low, reason to "No description provided.", flag to NEEDS_REVIEW. If no keyword from the allowed category list matches, set category to Other and flag to NEEDS_REVIEW. Never raise an unhandled exception on a single row.

  - name: batch_classify
    description: Reads all complaint rows from an input CSV, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: input_path (string, path to CSV with complaint rows), output_path (string, path where results CSV will be written)
    output: CSV file at output_path with columns complaint_id, category, priority, reason, flag; one row per input row, no rows skipped
    error_handling: If a row is missing required fields, write it with flag NEEDS_REVIEW and reason "Missing required fields." — never skip a row silently. If input_path does not exist, raise FileNotFoundError with the path. If an individual row raises an unexpected error, write the row with flag NEEDS_REVIEW and a reason describing the error.
