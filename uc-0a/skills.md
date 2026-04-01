skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a predefined category, assigns a priority level, generates a one-sentence reason quoting specific words from the description, and sets a NEEDS_REVIEW flag for ambiguous cases.
    input: dict with keys — complaint_id (str), description (str), plus any other CSV fields; description must be a non-empty string
    output: dict with keys — complaint_id (str), category (str, exactly one value from the allowed list), priority (str, one of Urgent/Standard/Low), reason (str, one sentence citing specific words), flag (str, either NEEDS_REVIEW or empty string)
    error_handling: If description is blank or missing, output category=Other, priority=Low, reason="No description provided", flag=NEEDS_REVIEW; never raises an exception on a single bad row

  - name: batch_classify
    description: Reads an input CSV file row by row, applies classify_complaint to each row, and writes a results CSV file with classification output for every input row.
    input: input_path (str, path to a CSV file with at least complaint_id and description columns), output_path (str, destination path for the results CSV)
    output: CSV file at output_path with columns — complaint_id, category, priority, reason, flag; function also prints a summary of rows processed and rows flagged NEEDS_REVIEW
    error_handling: Logs a warning and continues on any row that cannot be parsed; never crashes the entire batch due to a single bad row; reports total skipped rows in the printed summary
